"""アーキテクチャ境界テスト。

ADR-0001 (Hexagonal Architecture とインフラ基盤可搬性) で禁止した
依存方向を ast 解析で検証する。違反が混入したら CI が落ちる。
"""

from __future__ import annotations

import ast
from collections.abc import Iterator
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
APP_ROOT = REPO_ROOT / "app"

DOMAIN_DIR = APP_ROOT / "domain"
APPLICATION_DIR = APP_ROOT / "application"
INFRASTRUCTURE_DIR = APP_ROOT / "infrastructure"
MAIN_FILE = APP_ROOT / "main.py"
CONFIG_FILE = APP_ROOT / "config.py"

INFRA_IMPORT_PREFIXES = ("app.infrastructure", "infrastructure")

# 特定クラウド・プロバイダ SDK は domain / application / main / config から import 禁止。
# 該当 SDK が増えたらここに追加する。
CLOUD_SDK_IMPORT_PREFIXES = (
    "google.cloud",
    "google.api_core",
    "google.auth",
    "google.oauth2",
    "googleapiclient",
    "boto3",
    "botocore",
    "aiobotocore",
    "azure",
    "msal",
)


def _iter_python_files(root: Path) -> Iterator[Path]:
    for path in root.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        yield path


def _imported_modules(file_path: Path) -> set[str]:
    tree = ast.parse(file_path.read_text(encoding="utf-8"), filename=str(file_path))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                modules.add(node.module)
    return modules


def _starts_with_any(module: str, prefixes: tuple[str, ...]) -> bool:
    return any(module == p or module.startswith(p + ".") for p in prefixes)


# --- Domain → Infrastructure 依存禁止 ------------------------------------------------


def test_domain_does_not_depend_on_infrastructure() -> None:
    violations: list[tuple[str, str]] = []
    for path in _iter_python_files(DOMAIN_DIR):
        for module in _imported_modules(path):
            if _starts_with_any(module, INFRA_IMPORT_PREFIXES):
                violations.append((str(path.relative_to(REPO_ROOT)), module))
    assert not violations, (
        "domain/ から infrastructure/ への依存は禁止 (ADR-0001):\n"
        + "\n".join(f"  {p} → {m}" for p, m in violations)
    )


def test_application_does_not_depend_on_infrastructure() -> None:
    if not APPLICATION_DIR.exists():
        pytest.skip("application/ ディレクトリ未作成")
    violations: list[tuple[str, str]] = []
    for path in _iter_python_files(APPLICATION_DIR):
        for module in _imported_modules(path):
            if _starts_with_any(module, INFRA_IMPORT_PREFIXES):
                violations.append((str(path.relative_to(REPO_ROOT)), module))
    assert not violations, (
        "application/ から infrastructure/ への依存は禁止 (ADR-0001):\n"
        + "\n".join(f"  {p} → {m}" for p, m in violations)
    )


# --- クラウド SDK の侵入禁止 ----------------------------------------------------------


def test_domain_does_not_import_cloud_sdk() -> None:
    violations: list[tuple[str, str]] = []
    for path in _iter_python_files(DOMAIN_DIR):
        for module in _imported_modules(path):
            if _starts_with_any(module, CLOUD_SDK_IMPORT_PREFIXES):
                violations.append((str(path.relative_to(REPO_ROOT)), module))
    assert not violations, (
        "domain/ からクラウド SDK の直接 import は禁止 (ADR-0001):\n"
        + "\n".join(f"  {p} → {m}" for p, m in violations)
    )


def test_application_does_not_import_cloud_sdk() -> None:
    if not APPLICATION_DIR.exists():
        pytest.skip("application/ ディレクトリ未作成")
    violations: list[tuple[str, str]] = []
    for path in _iter_python_files(APPLICATION_DIR):
        for module in _imported_modules(path):
            if _starts_with_any(module, CLOUD_SDK_IMPORT_PREFIXES):
                violations.append((str(path.relative_to(REPO_ROOT)), module))
    assert not violations, (
        "application/ からクラウド SDK の直接 import は禁止 (ADR-0001):\n"
        + "\n".join(f"  {p} → {m}" for p, m in violations)
    )


def test_main_does_not_import_cloud_sdk() -> None:
    violations: list[str] = []
    for module in _imported_modules(MAIN_FILE):
        if _starts_with_any(module, CLOUD_SDK_IMPORT_PREFIXES):
            violations.append(module)
    assert not violations, (
        "app/main.py はインフラ基盤非依存 (ADR-0001):\n"
        + "\n".join(f"  → {m}" for m in violations)
    )


def test_config_does_not_import_cloud_sdk() -> None:
    violations: list[str] = []
    for module in _imported_modules(CONFIG_FILE):
        if _starts_with_any(module, CLOUD_SDK_IMPORT_PREFIXES):
            violations.append(module)
    assert not violations, (
        "app/config.py はインフラ基盤非依存 (ADR-0001):\n"
        + "\n".join(f"  → {m}" for m in violations)
    )
