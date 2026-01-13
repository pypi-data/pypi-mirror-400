"""Core SyncLangs workflows shared by CLI commands."""

from __future__ import annotations

import errno
from dataclasses import dataclass
from pathlib import Path

from lark.exceptions import UnexpectedInput

from synclangs.codegen.cpp import CppGenerator
from synclangs.codegen.csharp import CSharpGenerator
from synclangs.codegen.go import GoGenerator
from synclangs.codegen.java import JavaGenerator
from synclangs.codegen.python import PythonGenerator
from synclangs.codegen.python_validators import PydanticGenerator
from synclangs.codegen.rust import RustGenerator
from synclangs.codegen.typescript import TypeScriptGenerator
from synclangs.codegen.typescript_validators import ZodGenerator
from synclangs.config.schema import SyncLangsConfig
from synclangs.errors import SY001, SY020, SY021, SyncLangsError, SyncLangsFailure
from synclangs.parser import parse
from synclangs.parser.ast import Module


@dataclass(frozen=True)
class GenerationResult:
    """Result of a generation pass."""

    ts_written: list[Path]
    py_written: list[Path]
    go_written: list[Path]
    rust_written: list[Path]
    java_written: list[Path]
    cpp_written: list[Path]
    csharp_written: list[Path]
    ts_validators_written: list[Path]
    py_validators_written: list[Path]


def load_modules(input_dir: Path) -> dict[str, Module]:
    """Load and parse all .syln modules from an input directory."""
    modules: dict[str, Module] = {}
    for schema_path in sorted(input_dir.rglob("*.syln")):
        relative_path = schema_path.relative_to(input_dir).as_posix()
        try:
            source = schema_path.read_text(encoding="utf-8")
        except OSError as exc:
            code = SY021 if exc.errno == errno.EACCES else SY020
            raise SyncLangsFailure(
                [
                    SyncLangsError(
                        code=code,
                        message="Failed to read schema file.",
                        file_path=str(schema_path),
                    )
                ]
            ) from exc
        try:
            module = parse(source, path=relative_path)
        except UnexpectedInput as exc:
            raise SyncLangsFailure(
                [
                    SyncLangsError(
                        code=SY001,
                        message=str(exc).strip(),
                        file_path=relative_path,
                        line=getattr(exc, "line", None),
                        column=getattr(exc, "column", None),
                        line_text=_line_at(source, getattr(exc, "line", None)),
                    )
                ]
            ) from exc
        modules[relative_path] = module
    return modules


def generate_outputs(
    modules: dict[str, Module],
    config: SyncLangsConfig,
    base_dir: Path,
    targets: set[str] | None = None,
) -> GenerationResult:
    """Generate code for modules, optionally limited to targets."""
    ts_written: list[Path] = []
    py_written: list[Path] = []
    go_written: list[Path] = []
    rust_written: list[Path] = []
    java_written: list[Path] = []
    cpp_written: list[Path] = []
    csharp_written: list[Path] = []
    ts_validators_written: list[Path] = []
    py_validators_written: list[Path] = []

    ts_config = config.outputs.typescript
    py_config = config.outputs.python
    go_config = config.outputs.go
    rust_config = config.outputs.rust
    java_config = config.outputs.java
    cpp_config = config.outputs.cpp
    csharp_config = config.outputs.csharp

    ts_enabled = ts_config.enabled
    py_enabled = py_config.enabled
    go_enabled = go_config.enabled
    rust_enabled = rust_config.enabled
    java_enabled = java_config.enabled
    cpp_enabled = cpp_config.enabled
    csharp_enabled = csharp_config.enabled
    ts_validators_enabled = ts_config.generate_validators and ts_enabled
    py_validators_enabled = py_config.generate_validators and py_enabled

    ts_ext = ts_config.file_extension
    py_ext = py_config.file_extension
    go_ext = go_config.file_extension
    rust_ext = rust_config.file_extension
    java_ext = java_config.file_extension
    cpp_ext = cpp_config.file_extension
    csharp_ext = csharp_config.file_extension
    ts_validator_ext = ts_config.validator_file_extension
    py_validator_ext = py_config.validator_file_extension

    ts_generator = TypeScriptGenerator(file_extension=ts_ext)
    py_generator = PythonGenerator(file_extension=py_ext)
    go_generator = GoGenerator(
        file_extension=go_ext, package_name=go_config.package_name
    )
    rust_generator = RustGenerator(
        file_extension=rust_ext, crate_name=rust_config.crate_name
    )
    java_generator = JavaGenerator(
        file_extension=java_ext, package_name=java_config.package_name
    )
    cpp_generator = CppGenerator(
        file_extension=cpp_ext, namespace_name=cpp_config.namespace_name
    )
    csharp_generator = CSharpGenerator(
        file_extension=csharp_ext, namespace_name=csharp_config.namespace_name
    )
    ts_validator_generator = ZodGenerator(file_extension=ts_validator_ext)
    py_validator_generator = PydanticGenerator(file_extension=py_validator_ext)

    ts_out_dir = base_dir / ts_config.out_dir
    py_out_dir = base_dir / py_config.out_dir
    go_out_dir = base_dir / go_config.out_dir
    rust_out_dir = base_dir / rust_config.out_dir
    java_out_dir = base_dir / java_config.out_dir
    cpp_out_dir = base_dir / cpp_config.out_dir
    csharp_out_dir = base_dir / csharp_config.out_dir

    for relative_path, module in modules.items():
        if targets is not None and relative_path not in targets:
            continue
        rel_path = Path(relative_path)
        rel_no_ext = Path(rel_path.as_posix()[: -len(rel_path.suffix)])

        # Generate TypeScript types
        if ts_enabled:
            ts_out_path = ts_out_dir / Path(f"{rel_no_ext}{ts_ext}")
            _mkdir_safe(ts_out_path.parent)
            _write_text_safe(
                ts_out_path,
                ts_generator.generate(module),
                message="Failed to write TypeScript output.",
            )
            ts_written.append(ts_out_path)

        # Generate TypeScript validators (Zod)
        if ts_validators_enabled:
            ts_validator_path = ts_out_dir / Path(f"{rel_no_ext}{ts_validator_ext}")
            _mkdir_safe(ts_validator_path.parent)
            _write_text_safe(
                ts_validator_path,
                ts_validator_generator.generate(module),
                message="Failed to write TypeScript validators.",
            )
            ts_validators_written.append(ts_validator_path)

        # Generate Python types
        if py_enabled:
            py_out_path = py_out_dir / Path(f"{rel_no_ext}{py_ext}")
            _mkdir_safe(py_out_path.parent)
            _ensure_python_packages(py_out_dir, Path(relative_path).parent)
            _write_text_safe(
                py_out_path,
                py_generator.generate(module),
                message="Failed to write Python output.",
            )
            py_written.append(py_out_path)

        # Generate Python validators (Pydantic)
        if py_validators_enabled:
            py_validator_path = py_out_dir / Path(f"{rel_no_ext}{py_validator_ext}")
            _mkdir_safe(py_validator_path.parent)
            _ensure_python_packages(py_out_dir, Path(relative_path).parent)
            _write_text_safe(
                py_validator_path,
                py_validator_generator.generate(module),
                message="Failed to write Python validators.",
            )
            py_validators_written.append(py_validator_path)

        # Generate Go structs
        if go_enabled:
            go_out_path = go_out_dir / Path(f"{rel_no_ext}{go_ext}")
            _mkdir_safe(go_out_path.parent)
            _write_text_safe(
                go_out_path,
                go_generator.generate(module),
                message="Failed to write Go output.",
            )
            go_written.append(go_out_path)

        # Generate Rust structs
        if rust_enabled:
            rust_out_path = rust_out_dir / Path(f"{rel_no_ext}{rust_ext}")
            _mkdir_safe(rust_out_path.parent)
            _write_text_safe(
                rust_out_path,
                rust_generator.generate(module),
                message="Failed to write Rust output.",
            )
            rust_written.append(rust_out_path)

        # Generate Java classes
        if java_enabled:
            java_out_path = java_out_dir / Path(f"{rel_no_ext}{java_ext}")
            _mkdir_safe(java_out_path.parent)
            _write_text_safe(
                java_out_path,
                java_generator.generate(module),
                message="Failed to write Java output.",
            )
            java_written.append(java_out_path)

        # Generate C++ structs
        if cpp_enabled:
            cpp_out_path = cpp_out_dir / Path(f"{rel_no_ext}{cpp_ext}")
            _mkdir_safe(cpp_out_path.parent)
            _write_text_safe(
                cpp_out_path,
                cpp_generator.generate(module),
                message="Failed to write C++ output.",
            )
            cpp_written.append(cpp_out_path)

        # Generate C# classes
        if csharp_enabled:
            csharp_out_path = csharp_out_dir / Path(f"{rel_no_ext}{csharp_ext}")
            _mkdir_safe(csharp_out_path.parent)
            _write_text_safe(
                csharp_out_path,
                csharp_generator.generate(module),
                message="Failed to write C# output.",
            )
            csharp_written.append(csharp_out_path)

    if config.options.generate_index:
        if ts_enabled:
            ts_rel = [
                _output_relative_path(path, ts_ext) for path in modules
            ]
            _write_ts_index(ts_out_dir, ts_rel)
        if py_enabled:
            py_rel = [
                _output_relative_path(path, py_ext) for path in modules
            ]
            _write_python_indexes(py_out_dir, py_rel)

    return GenerationResult(
        ts_written=ts_written,
        py_written=py_written,
        go_written=go_written,
        rust_written=rust_written,
        java_written=java_written,
        cpp_written=cpp_written,
        csharp_written=csharp_written,
        ts_validators_written=ts_validators_written,
        py_validators_written=py_validators_written,
    )


def _output_relative_path(relative_path: str, extension: str) -> Path:
    """Return the output-relative path for a module."""
    rel_path = Path(relative_path)
    rel_no_ext = Path(rel_path.as_posix()[: -len(rel_path.suffix)])
    return Path(f"{rel_no_ext}{extension}")


def _ensure_python_packages(base_dir: Path, rel_dir: Path) -> None:
    """Ensure Python package directories exist with __init__.py files."""
    current = base_dir
    _mkdir_safe(current)
    _touch_safe(current / "__init__.py")
    for part in rel_dir.parts:
        if part == ".":
            continue
        current = current / part
        _mkdir_safe(current)
        _touch_safe(current / "__init__.py")


def _write_ts_index(out_dir: Path, rel_files: list[Path]) -> None:
    """Write a TypeScript index.ts file exporting all generated types."""
    lines = ["// Auto-generated by SyncLangs"]
    for rel_path in sorted(rel_files):
        rel_posix = rel_path.as_posix()
        if rel_posix.endswith(".ts"):
            rel_posix = rel_posix[: -len(".ts")]
        if not rel_posix.startswith("."):
            rel_posix = f"./{rel_posix}"
        lines.append(f"export * from '{rel_posix}';")
    out_dir.mkdir(parents=True, exist_ok=True)
    _write_text_safe(
        out_dir / "index.ts",
        "\n".join(lines) + "\n",
        message="Failed to write TypeScript index.",
    )


def _write_python_indexes(out_dir: Path, rel_files: list[Path]) -> None:
    """Write __init__.py files with exports for generated modules."""
    modules_by_dir: dict[Path, set[str]] = {}
    subpackages_by_dir: dict[Path, set[str]] = {}

    for rel_path in rel_files:
        rel_dir = rel_path.parent
        modules_by_dir.setdefault(rel_dir, set()).add(rel_path.stem)
        parent = rel_dir
        while parent != Path(".") and parent != Path(""):
            subpackages_by_dir.setdefault(parent.parent, set()).add(parent.name)
            parent = parent.parent

    all_dirs = {Path(".")} | set(modules_by_dir) | set(subpackages_by_dir)
    for rel_dir in sorted(all_dirs):
        lines = ["# Auto-generated by SyncLangs"]
        for subpkg in sorted(subpackages_by_dir.get(rel_dir, set())):
            lines.append(f"from .{subpkg} import *")
        for module in sorted(modules_by_dir.get(rel_dir, set())):
            lines.append(f"from .{module} import *")
        out_path = out_dir / rel_dir / "__init__.py"
        _mkdir_safe(out_path.parent)
        _write_text_safe(
            out_path,
            "\n".join(lines) + "\n",
            message="Failed to write Python index.",
        )


def _line_at(source: str, line: int | None) -> str | None:
    """Return the source line at a 1-based line number."""
    if line is None or line <= 0:
        return None
    lines = source.splitlines()
    if line > len(lines):
        return None
    return lines[line - 1]


def _mkdir_safe(path: Path) -> None:
    """Create directories, surfacing IO errors as SyncLangs failures."""
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        code = SY021 if exc.errno == errno.EACCES else SY020
        raise SyncLangsFailure(
            [
                SyncLangsError(
                    code=code,
                    message="Failed to create output directory.",
                    file_path=str(path),
                )
            ]
        ) from exc


def _write_text_safe(path: Path, content: str, message: str) -> None:
    """Write output files with SyncLangs error handling."""
    try:
        path.write_text(content, encoding="utf-8")
    except OSError as exc:
        code = SY021 if exc.errno == errno.EACCES else SY020
        raise SyncLangsFailure(
            [
                SyncLangsError(
                    code=code,
                    message=message,
                    file_path=str(path),
                )
            ]
        ) from exc


def _touch_safe(path: Path) -> None:
    """Touch a file while surfacing IO errors as SyncLangs failures."""
    try:
        path.touch(exist_ok=True)
    except OSError as exc:
        code = SY021 if exc.errno == errno.EACCES else SY020
        raise SyncLangsFailure(
            [
                SyncLangsError(
                    code=code,
                    message="Failed to create package file.",
                    file_path=str(path),
                )
            ]
        ) from exc
