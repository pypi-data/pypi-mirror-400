"""Pydantic models for SyncLangs configuration."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TypeScriptConfig(BaseModel):
    """TypeScript output configuration."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    enabled: bool = True
    out_dir: str = Field("./generated/ts", alias="outDir")
    file_extension: str = Field(".types.ts", alias="fileExtension")
    export_style: str = Field("named", alias="exportStyle")
    generate_validators: bool = Field(False, alias="generateValidators")
    validator_style: Literal["zod"] = Field("zod", alias="validatorStyle")
    validator_file_extension: str = Field(
        ".validators.ts", alias="validatorFileExtension"
    )


class PythonConfig(BaseModel):
    """Python output configuration."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    enabled: bool = True
    out_dir: str = Field("./generated/py", alias="outDir")
    file_extension: str = Field("_types.py", alias="fileExtension")
    use_dataclasses: bool = Field(True, alias="useDataclasses")
    python_version: str = Field("3.10", alias="pythonVersion")
    generate_validators: bool = Field(False, alias="generateValidators")
    validator_style: Literal["pydantic"] = Field("pydantic", alias="validatorStyle")
    validator_file_extension: str = Field(
        "_validators.py", alias="validatorFileExtension"
    )


class GoConfig(BaseModel):
    """Go output configuration."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    enabled: bool = False
    out_dir: str = Field("./generated/go", alias="outDir")
    file_extension: str = Field(".go", alias="fileExtension")
    package_name: str = Field("types", alias="packageName")


class RustConfig(BaseModel):
    """Rust output configuration."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    enabled: bool = False
    out_dir: str = Field("./generated/rust", alias="outDir")
    file_extension: str = Field(".rs", alias="fileExtension")
    crate_name: str = Field("types", alias="crateName")


class JavaConfig(BaseModel):
    """Java output configuration."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    enabled: bool = False
    out_dir: str = Field("./generated/java", alias="outDir")
    file_extension: str = Field(".java", alias="fileExtension")
    package_name: str = Field("types", alias="packageName")


class CppConfig(BaseModel):
    """C++ output configuration."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    enabled: bool = False
    out_dir: str = Field("./generated/cpp", alias="outDir")
    file_extension: str = Field(".hpp", alias="fileExtension")
    namespace_name: str = Field("types", alias="namespaceName")


class CSharpConfig(BaseModel):
    """C# output configuration."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    enabled: bool = False
    out_dir: str = Field("./generated/csharp", alias="outDir")
    file_extension: str = Field(".cs", alias="fileExtension")
    namespace_name: str = Field("Types", alias="namespaceName")


class OutputsConfig(BaseModel):
    """Output configuration for supported languages."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    typescript: TypeScriptConfig = Field(default_factory=TypeScriptConfig)
    python: PythonConfig = Field(default_factory=PythonConfig)
    go: GoConfig = Field(default_factory=GoConfig)
    rust: RustConfig = Field(default_factory=RustConfig)
    java: JavaConfig = Field(default_factory=JavaConfig)
    cpp: CppConfig = Field(default_factory=CppConfig)
    csharp: CSharpConfig = Field(default_factory=CSharpConfig)


class CaseConversionFields(BaseModel):
    """Case conversion settings for fields."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    python: str = "snake_case"
    typescript: str = "camelCase"
    go: str = "PascalCase"
    rust: str = "snake_case"
    java: str = "camelCase"
    cpp: str = "snake_case"
    csharp: str = "PascalCase"


class CaseConversionConfig(BaseModel):
    """Case conversion settings."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    fields: CaseConversionFields = Field(default_factory=CaseConversionFields)


class OptionsConfig(BaseModel):
    """Additional SyncLangs options."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    watch_debounce_ms: int = Field(100, alias="watchDebounceMs", ge=0)
    case_conversion: CaseConversionConfig = Field(
        default_factory=CaseConversionConfig,
        alias="caseConversion",
    )
    generate_index: bool = Field(True, alias="generateIndex")


class SyncLangsConfig(BaseModel):
    """Root SyncLangs configuration."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    schema_url: str = Field(
        "https://synclangs.com/schema/v1.json",
        alias="$schema",
    )
    version: str = "1.0"
    input: str = "./shared"
    outputs: OutputsConfig = Field(default_factory=OutputsConfig)
    options: OptionsConfig = Field(default_factory=OptionsConfig)
