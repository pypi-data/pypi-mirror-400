"""CLI entry point for SyncLangs."""

from __future__ import annotations

import time
from pathlib import Path

import typer

from synclangs import __version__
from synclangs.config import SyncLangsConfig, load_config, resolve_config_path
from synclangs.core import generate_outputs, load_modules
from synclangs.dependencies import (
    build_dependency_graph,
    build_reverse_graph,
    collect_dependents,
    resolve_import_path,
)
from synclangs.errors import SY010, SY020, SyncLangsError, SyncLangsFailure, format_error
from synclangs.parser.ast import Module
from synclangs.validator import validate_modules
from synclangs.watcher import start_watcher

app = typer.Typer(
    name="syln",
    help="SyncLangs - Centralized types, universal synchronization across codebases",
    no_args_is_help=True,
)


@app.callback()
def cli() -> None:
    """SyncLangs CLI."""


@app.command()
def init(
    path: Path = typer.Argument(Path("."), help="Project path to initialize"),
) -> None:
    """Initialize a new SyncLangs project."""
    config_path = path / "syln.config.json"
    shared_path = path / "shared"

    if not config_path.exists():
        config = SyncLangsConfig()
        config_path.write_text(
            config.model_dump_json(indent=2, by_alias=True) + "\n",
            encoding="utf-8",
        )
        typer.echo(f"Created {config_path}")
    else:
        typer.echo("Config already exists, skipping.")

    shared_path.mkdir(parents=True, exist_ok=True)

    example_path = shared_path / "example.syln"
    if not example_path.exists():
        example_path.write_text(EXAMPLE_SCHEMA, encoding="utf-8")
        typer.echo(f"Created {example_path}")


@app.command()
def generate(
    config: Path | None = typer.Option(
        None, "--config", "-c", help="Config file path"
    ),
    input_override: Path | None = typer.Option(
        None, "--input", "-i", help="Input directory"
    ),
    out_ts: Path | None = typer.Option(
        None, "--out-ts", help="TypeScript output directory"
    ),
    out_py: Path | None = typer.Option(
        None, "--out-py", help="Python output directory"
    ),
    out_go: Path | None = typer.Option(
        None, "--out-go", help="Go output directory"
    ),
    out_rust: Path | None = typer.Option(
        None, "--out-rust", help="Rust output directory"
    ),
    out_java: Path | None = typer.Option(
        None, "--out-java", help="Java output directory"
    ),
    out_cpp: Path | None = typer.Option(
        None, "--out-cpp", help="C++ output directory"
    ),
    out_csharp: Path | None = typer.Option(
        None, "--out-csharp", help="C# output directory"
    ),
    validators: bool = typer.Option(
        False, "--validators", help="Generate runtime validators (Zod for TS, Pydantic for Python)"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Verbose logging"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be generated"
    ),
) -> None:
    """Generate code from .syln files."""
    cfg, config_path = _load_config_or_exit(config)
    cfg = _apply_overrides(cfg, input_override, out_ts, out_py, out_go, out_rust, out_java, out_cpp, out_csharp, validators)
    base_dir = config_path.parent
    input_dir = base_dir / cfg.input

    if verbose:
        _emit_verbose_context(cfg, config_path, base_dir, input_dir)

    if not input_dir.exists():
        _exit_with_errors(
            [
                SyncLangsError(
                    code=SY020,
                    message="Input directory not found.",
                    file_path=str(input_dir),
                )
            ]
        )

    any_output_enabled = (
        cfg.outputs.typescript.enabled
        or cfg.outputs.python.enabled
        or cfg.outputs.go.enabled
        or cfg.outputs.rust.enabled
        or cfg.outputs.java.enabled
        or cfg.outputs.cpp.enabled
        or cfg.outputs.csharp.enabled
    )
    if not any_output_enabled:
        _exit_with_errors(
            [
                SyncLangsError(
                    code=SY010,
                    message="No outputs enabled in config.",
                    file_path=str(config_path),
                )
            ]
        )

    try:
        modules = load_modules(input_dir)
    except SyncLangsFailure as exc:
        _exit_with_errors(exc.errors)

    errors = validate_modules(modules)
    if errors:
        _exit_with_errors(errors)

    if dry_run:
        for planned in _plan_outputs(modules, cfg, base_dir):
            typer.echo(
                f"[syln] Would generate: {_display_path(planned, base_dir)}"
            )
        typer.echo("Dry run complete.")
        return

    try:
        generate_outputs(modules, cfg, base_dir)
    except SyncLangsFailure as exc:
        _exit_with_errors(exc.errors)
    typer.echo("Generation complete.")


@app.command()
def check(
    config: Path | None = typer.Option(
        None, "--config", "-c", help="Config file path"
    ),
    input_override: Path | None = typer.Option(
        None, "--input", "-i", help="Input directory"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Verbose logging"
    ),
) -> None:
    """Validate .syln files without generating output."""
    cfg, config_path = _load_config_or_exit(config)
    cfg = _apply_overrides(cfg, input_override, None, None)
    base_dir = config_path.parent
    input_dir = base_dir / cfg.input

    if verbose:
        _emit_verbose_context(
            cfg, config_path, base_dir, input_dir, show_outputs=False
        )

    if not input_dir.exists():
        _exit_with_errors(
            [
                SyncLangsError(
                    code=SY020,
                    message="Input directory not found.",
                    file_path=str(input_dir),
                )
            ]
        )

    try:
        modules = load_modules(input_dir)
    except SyncLangsFailure as exc:
        _exit_with_errors(exc.errors)

    errors = validate_modules(modules)
    if errors:
        _exit_with_errors(errors)

    typer.echo("Check complete.")


@app.command()
def watch(
    config: Path | None = typer.Option(
        None, "--config", "-c", help="Config file path"
    ),
    input_override: Path | None = typer.Option(
        None, "--input", "-i", help="Input directory"
    ),
    out_ts: Path | None = typer.Option(
        None, "--out-ts", help="TypeScript output directory"
    ),
    out_py: Path | None = typer.Option(
        None, "--out-py", help="Python output directory"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Verbose logging"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be generated"
    ),
) -> None:
    """Watch for changes and regenerate outputs."""
    cfg, config_path = _load_config_or_exit(config)
    cfg = _apply_overrides(cfg, input_override, out_ts, out_py)
    base_dir = config_path.parent
    input_dir = base_dir / cfg.input

    if verbose:
        _emit_verbose_context(cfg, config_path, base_dir, input_dir)

    if not input_dir.exists():
        _exit_with_errors(
            [
                SyncLangsError(
                    code=SY020,
                    message="Input directory not found.",
                    file_path=str(input_dir),
                )
            ]
        )

    any_output_enabled = (
        cfg.outputs.typescript.enabled
        or cfg.outputs.python.enabled
        or cfg.outputs.go.enabled
        or cfg.outputs.rust.enabled
        or cfg.outputs.java.enabled
        or cfg.outputs.cpp.enabled
        or cfg.outputs.csharp.enabled
    )
    if not any_output_enabled:
        _exit_with_errors(
            [
                SyncLangsError(
                    code=SY010,
                    message="No outputs enabled in config.",
                    file_path=str(config_path),
                )
            ]
        )

    typer.echo(f"[syln] Watching {cfg.input} for changes...")

    def _regenerate(changed: Path | None) -> None:
        start = time.monotonic()
        rel_changed = None
        if changed is not None:
            try:
                rel_changed = changed.relative_to(input_dir).as_posix()
            except ValueError:
                rel_changed = changed.as_posix()
            typer.echo(f"[syln] Changed: {rel_changed}")

        try:
            modules = load_modules(input_dir)
        except SyncLangsFailure as exc:
            _print_errors(exc.errors)
            return

        errors = validate_modules(modules)
        if errors:
            _print_errors(errors)
            return

        targets = set(modules)
        if rel_changed:
            graph = build_dependency_graph(modules)
            reverse = build_reverse_graph(graph)
            if rel_changed in modules:
                targets = collect_dependents(reverse, rel_changed)
                targets.add(rel_changed)
            else:
                direct_dependents = {
                    module.path
                    for module in modules.values()
                    if any(
                        resolve_import_path(module.path, imp.path)
                        == rel_changed
                        for imp in module.imports
                    )
                }
                targets = set()
                for dep in direct_dependents:
                    targets.update(collect_dependents(reverse, dep))
                targets.update(direct_dependents)

        if dry_run:
            for planned in _plan_outputs(modules, cfg, base_dir, targets=targets):
                typer.echo(
                    f"[syln] Would generate: {_display_path(planned, base_dir)}"
                )
        else:
            try:
                result = generate_outputs(modules, cfg, base_dir, targets=targets)
            except SyncLangsFailure as exc:
                _print_errors(exc.errors)
                return
            all_outputs = [
                *result.ts_written,
                *result.py_written,
                *result.go_written,
                *result.rust_written,
                *result.java_written,
                *result.cpp_written,
                *result.csharp_written,
                *result.ts_validators_written,
                *result.py_validators_written,
            ]
            for output in all_outputs:
                typer.echo(f"[syln] Generated: {_display_path(output, base_dir)}")

        duration_ms = (time.monotonic() - start) * 1000
        typer.echo(f"[syln] Done in {duration_ms:.0f}ms")

    _regenerate(None)
    start_watcher(input_dir, cfg.options.watch_debounce_ms, _regenerate)


@app.command()
def version() -> None:
    """Show the current SyncLangs version."""
    typer.echo(f"syln {__version__}")


def main() -> None:
    """Run the SyncLangs CLI application."""
    app()


def _load_config_or_exit(config: Path | None) -> tuple[SyncLangsConfig, Path]:
    config_path = resolve_config_path(config)
    try:
        cfg = load_config(config_path)
    except SyncLangsFailure as exc:
        _exit_with_errors(exc.errors)
    return cfg, config_path


def _apply_overrides(
    cfg: SyncLangsConfig,
    input_override: Path | None,
    out_ts: Path | None,
    out_py: Path | None,
    out_go: Path | None = None,
    out_rust: Path | None = None,
    out_java: Path | None = None,
    out_cpp: Path | None = None,
    out_csharp: Path | None = None,
    validators: bool = False,
) -> SyncLangsConfig:
    updated = cfg.model_copy(deep=True)
    if input_override is not None:
        updated.input = input_override.as_posix()
    if out_ts is not None:
        updated.outputs.typescript.out_dir = out_ts.as_posix()
        updated.outputs.typescript.enabled = True
    if out_py is not None:
        updated.outputs.python.out_dir = out_py.as_posix()
        updated.outputs.python.enabled = True
    if out_go is not None:
        updated.outputs.go.out_dir = out_go.as_posix()
        updated.outputs.go.enabled = True
    if out_rust is not None:
        updated.outputs.rust.out_dir = out_rust.as_posix()
        updated.outputs.rust.enabled = True
    if out_java is not None:
        updated.outputs.java.out_dir = out_java.as_posix()
        updated.outputs.java.enabled = True
    if out_cpp is not None:
        updated.outputs.cpp.out_dir = out_cpp.as_posix()
        updated.outputs.cpp.enabled = True
    if out_csharp is not None:
        updated.outputs.csharp.out_dir = out_csharp.as_posix()
        updated.outputs.csharp.enabled = True
    if validators:
        updated.outputs.typescript.generate_validators = True
        updated.outputs.python.generate_validators = True
    return updated


def _emit_verbose_context(
    cfg: SyncLangsConfig,
    config_path: Path,
    base_dir: Path,
    input_dir: Path,
    show_outputs: bool = True,
) -> None:
    typer.echo(f"[syln] Config: {_display_path(config_path, base_dir)}")
    typer.echo(f"[syln] Input: {_display_path(input_dir, base_dir)}")
    if not show_outputs:
        return
    if cfg.outputs.typescript.enabled:
        ts_out = base_dir / cfg.outputs.typescript.out_dir
        typer.echo(f"[syln] TypeScript out: {_display_path(ts_out, base_dir)}")
    if cfg.outputs.python.enabled:
        py_out = base_dir / cfg.outputs.python.out_dir
        typer.echo(f"[syln] Python out: {_display_path(py_out, base_dir)}")
    if cfg.outputs.go.enabled:
        go_out = base_dir / cfg.outputs.go.out_dir
        typer.echo(f"[syln] Go out: {_display_path(go_out, base_dir)}")
    if cfg.outputs.rust.enabled:
        rust_out = base_dir / cfg.outputs.rust.out_dir
        typer.echo(f"[syln] Rust out: {_display_path(rust_out, base_dir)}")
    if cfg.outputs.java.enabled:
        java_out = base_dir / cfg.outputs.java.out_dir
        typer.echo(f"[syln] Java out: {_display_path(java_out, base_dir)}")
    if cfg.outputs.cpp.enabled:
        cpp_out = base_dir / cfg.outputs.cpp.out_dir
        typer.echo(f"[syln] C++ out: {_display_path(cpp_out, base_dir)}")
    if cfg.outputs.csharp.enabled:
        csharp_out = base_dir / cfg.outputs.csharp.out_dir
        typer.echo(f"[syln] C# out: {_display_path(csharp_out, base_dir)}")


def _plan_outputs(
    modules: dict[str, Module],
    cfg: SyncLangsConfig,
    base_dir: Path,
    targets: set[str] | None = None,
) -> list[Path]:
    ts_paths: list[Path] = []
    py_paths: list[Path] = []
    go_paths: list[Path] = []
    rust_paths: list[Path] = []
    java_paths: list[Path] = []
    cpp_paths: list[Path] = []
    csharp_paths: list[Path] = []

    ts_enabled = cfg.outputs.typescript.enabled
    py_enabled = cfg.outputs.python.enabled
    go_enabled = cfg.outputs.go.enabled
    rust_enabled = cfg.outputs.rust.enabled
    java_enabled = cfg.outputs.java.enabled
    cpp_enabled = cfg.outputs.cpp.enabled
    csharp_enabled = cfg.outputs.csharp.enabled

    ts_ext = cfg.outputs.typescript.file_extension
    py_ext = cfg.outputs.python.file_extension
    go_ext = cfg.outputs.go.file_extension
    rust_ext = cfg.outputs.rust.file_extension
    java_ext = cfg.outputs.java.file_extension
    cpp_ext = cfg.outputs.cpp.file_extension
    csharp_ext = cfg.outputs.csharp.file_extension

    ts_out_dir = base_dir / cfg.outputs.typescript.out_dir
    py_out_dir = base_dir / cfg.outputs.python.out_dir
    go_out_dir = base_dir / cfg.outputs.go.out_dir
    rust_out_dir = base_dir / cfg.outputs.rust.out_dir
    java_out_dir = base_dir / cfg.outputs.java.out_dir
    cpp_out_dir = base_dir / cfg.outputs.cpp.out_dir
    csharp_out_dir = base_dir / cfg.outputs.csharp.out_dir

    paths = targets if targets is not None else set(modules)
    for relative_path in sorted(paths):
        if relative_path not in modules:
            continue
        rel_path = Path(relative_path)
        rel_no_ext = Path(rel_path.as_posix()[: -len(rel_path.suffix)])
        if ts_enabled:
            ts_paths.append(ts_out_dir / Path(f"{rel_no_ext}{ts_ext}"))
        if py_enabled:
            py_paths.append(py_out_dir / Path(f"{rel_no_ext}{py_ext}"))
        if go_enabled:
            go_paths.append(go_out_dir / Path(f"{rel_no_ext}{go_ext}"))
        if rust_enabled:
            rust_paths.append(rust_out_dir / Path(f"{rel_no_ext}{rust_ext}"))
        if java_enabled:
            java_paths.append(java_out_dir / Path(f"{rel_no_ext}{java_ext}"))
        if cpp_enabled:
            cpp_paths.append(cpp_out_dir / Path(f"{rel_no_ext}{cpp_ext}"))
        if csharp_enabled:
            csharp_paths.append(csharp_out_dir / Path(f"{rel_no_ext}{csharp_ext}"))

    if cfg.options.generate_index:
        if ts_enabled:
            ts_paths.append(ts_out_dir / "index.ts")
        if py_enabled:
            py_paths.extend(_plan_python_indexes(modules, py_out_dir))

    return sorted(
        {*ts_paths, *py_paths, *go_paths, *rust_paths, *java_paths, *cpp_paths, *csharp_paths}, key=lambda path: path.as_posix()
    )


def _plan_python_indexes(
    modules: dict[str, Module],
    py_out_dir: Path,
) -> list[Path]:
    modules_by_dir: dict[Path, set[str]] = {}
    subpackages_by_dir: dict[Path, set[str]] = {}

    for rel in modules:
        rel_path = Path(rel)
        rel_dir = rel_path.parent
        modules_by_dir.setdefault(rel_dir, set()).add(rel_path.stem)
        parent = rel_dir
        while parent != Path(".") and parent != Path(""):
            subpackages_by_dir.setdefault(parent.parent, set()).add(parent.name)
            parent = parent.parent

    all_dirs = {Path(".")} | set(modules_by_dir) | set(subpackages_by_dir)
    return [py_out_dir / rel_dir / "__init__.py" for rel_dir in sorted(all_dirs)]


def _exit_with_errors(errors: list[SyncLangsError]) -> None:
    _print_errors(errors)
    raise typer.Exit(1)


def _print_errors(errors: list[SyncLangsError]) -> None:
    for index, error in enumerate(errors):
        if index:
            typer.echo("")
        typer.echo(format_error(error))


def _display_path(path: Path, base_dir: Path) -> str:
    try:
        return path.relative_to(base_dir).as_posix()
    except ValueError:
        return str(path)


EXAMPLE_SCHEMA = (
    "# Example SyncLangs schema\n"
    "# Edit this file or create new .syln files in this directory\n"
    "\n"
    "## Represents a user in the system\n"
    "type User {\n"
    "  ## Unique identifier\n"
    "  id: string\n"
    "\n"
    "  ## User's email address\n"
    "  email: string\n"
    "\n"
    "  ## Display name (optional)\n"
    "  name: string?\n"
    "\n"
    "  ## Account active status\n"
    "  isActive: bool\n"
    "\n"
    "  ## User tags\n"
    "  tags: list<string>\n"
    "\n"
    "  ## Arbitrary metadata\n"
    "  metadata: map<string, any>\n"
    "}\n"
)


if __name__ == "__main__":
    main()
