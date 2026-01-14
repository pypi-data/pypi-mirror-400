# release_manifest.py
"""
Create a release-level manifest that ties a specific application version
(from pyproject.toml) to the exact set of dependency layer ZIPs that
compose the shipped artifact.

Outputs a JSON file (default: ./release-manifest-1.3.1.json) like:

{
  "app": {
    "name": "am100-auto-detection",
    "version": "1.3.1",
    "python": "3.12",
    "platform": "linux-x86_64"
  },
  "built_at": "2026-01-05T01:30:00Z",
  "layers": [
    {
      "name": "platform",
      "variant": null,
      "zip": "platform-linux-x86_64.zip",
      "sha256": "...",
      "manifest": { "name": "platform", "version_set": { ... } }
    },
    {
      "name": "torch",
      "variant": "gpu",
      "zip": "torch-gpu-linux-x86_64.zip",
      "sha256": "...",
      "manifest": { "name": "torch", "version_set": { ... } }
    },
    ...
  ],
  "uv": {
    "indexes": ["pytorch-cu121", "pystereolib"],
    "sources": ["torch", "torchvision", "pystereolib"]
  }
}

Usage:
    python release_manifest.py \
        --layers-dir ./layers \
        --layers platform,torch,heavy,vision,core,albumentations,project-ext,bucket \
        --variants torch=gpu \
        --out ./release-manifest-1.3.1.json

Notes:
- We avoid leaking credentialed index URLs; we only record index names.
- Per-layer manifests are optional; if present inside the ZIP (or as a sibling
  .manifest.json), they are embedded here to make the release self-descriptive.
- Variant selection allows mapping a logical layer name (e.g., "torch") to a
  specific ZIP (e.g., "torch-gpu-linux-x86_64.zip").
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from typing import Dict, List, Optional

# Python 3.11+ has tomllib in stdlib
try:
    import tomllib  # type: ignore[attr-defined]
except Exception:  # pragma: no cover
    tomllib = None


def _compute_platform_id() -> str:
    import platform as _platform

    system = _platform.system()
    machine = _platform.machine().lower()
    if system == "Linux":
        if machine in ("x86_64", "amd64"):
            return "linux-x86_64"
        elif machine in ("aarch64", "arm64"):
            return "linux-aarch64"
        else:
            return f"linux-{machine}"
    elif system == "Windows":
        return "win-amd64" if machine in ("x86_64", "amd64") else f"win-{machine}"
    elif system == "Darwin":
        if machine in ("arm64", "aarch64"):
            return "macos-arm64"
        elif machine in ("x86_64", "amd64"):
            return "macos-x86_64"
        else:
            return f"macos-{machine}"
    else:
        return system.lower()


def _sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _read_pyproject(pyproject_path: str) -> Dict:
    if tomllib is None:
        raise RuntimeError("Python >=3.11 required (tomllib not available)")
    with open(pyproject_path, "rb") as f:
        return tomllib.load(f)


def build_release_manifest(
    pyproject_path: str,
    layer_manifests: List[str],
    variants: Dict[str, str],
) -> Dict:
    cfg = _read_pyproject(pyproject_path)

    project = cfg.get("project", {})
    app_name = project.get("name")
    app_version = project.get("version")

    # Collect uv index names without leaking URLs
    uv_cfg = cfg.get("tool", {}).get("uv", {})
    index_entries = (
        uv_cfg.get("index", []) if isinstance(uv_cfg.get("index"), list) else []
    )
    indexes = [
        e.get("name") for e in index_entries if isinstance(e, dict) and e.get("name")
    ]

    sources = uv_cfg.get("sources", {})
    source_pkgs = sorted(list(sources.keys())) if isinstance(sources, dict) else []

    platform_id = _compute_platform_id()
    py_major_minor = f"{sys.version_info.major}.{sys.version_info.minor}"

    manifest: Dict = {
        "app": {
            "name": app_name,
            "version": app_version,
            "python": py_major_minor,
            "platform": platform_id,
        },
        "built_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat() + "Z",
        "layers": [],
        "uv": {
            "indexes": indexes,
            "sources": source_pkgs,
        },
    }

    for layer_manifest in layer_manifests:
        with open(layer_manifest, "r") as f:
            data = json.load(f)

            entry = {
                "name": data["name"],
                "variant": variants.get(data["name"]),
                "zip": os.path.basename(data["path"]),
                "sha256": data["zip_sha256"],
                "manifest": layer_manifest,
            }
            manifest["layers"].append(entry)

    return manifest


def create_release_manifest(
    pyproject_path: str = "pyproject.toml",
    layer_manifests: Optional[List[str]] = None,
    variants: Optional[Dict[str, str]] = None,
    manifest_output: Optional[str] = None,
) -> Dict:
    """
    Build the release manifest programmatically without CLI parsing.
    This is the recommended API for use from other Python files.

    Args:
        pyproject_path: Path to pyproject.toml.
        layer_manifests: List of layer manifest paths.
        variants: Mapping of layer -> variant, e.g., {"torch": "gpu"}.

    Returns:
        A manifest dictionary.

    Raises:
        ValueError: If the resulting manifest is missing required fields.
    """
    layer_manifests = layer_manifests or []
    variants = variants or {}

    manifest = build_release_manifest(
        pyproject_path=pyproject_path,
        layer_manifests=layer_manifests,
        variants=variants,
    )

    # Basic sanity: must include app name and version
    if not manifest.get("app", {}).get("name") or not manifest.get("app", {}).get(
        "version"
    ):
        raise ValueError("pyproject.toml missing [project].name or [project].version")

    with open(manifest_output, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"Release manifest written: {manifest_output}")

    return manifest


def _parse_variants(variants_arg: Optional[str]) -> Dict[str, str]:
    """
    Parse comma-separated 'layer=variant' pairs (e.g., 'torch=gpu,cv=avx2')
    into a dictionary.
    """
    variants: Dict[str, str] = {}
    if variants_arg:
        for kv in variants_arg.split(","):
            if "=" in kv:
                k, v = kv.split("=", 1)
                variants[k.strip()] = v.strip()
    return variants


def main(argv: Optional[List[str]] = None) -> int:
    """
    CLI entry point. Accepts argv to allow programmatic invocation
    (e.g., main(["--pyproject", "custom.toml"])).
    """
    p = argparse.ArgumentParser(
        description="Create release-level manifest from pyproject + layer ZIPs"
    )
    p.add_argument(
        "--pyproject", default="pyproject.toml", help="Path to pyproject.toml"
    )
    p.add_argument(
        "--layer-manifests",
        nargs="*",
        default=[],
        help="Layer manifests to create the release",
    )
    p.add_argument(
        "--variants",
        default=None,
        help="Comma-separated layer=variant pairs (e.g., 'torch=gpu')",
    )
    p.add_argument("--out", default="release-manifest.json", help="Output JSON path")

    args = p.parse_args(argv)

    try:
        create_release_manifest(
            pyproject_path=args.pyproject,
            layer_manifests=args.layer_manifests,
            variants=_parse_variants(args.variants),
        )
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())


if __name__ == "__main__":
    raise SystemExit(main())
