# runtime_loader.py (Win-amd64, GPU-only, release-manifest driven)
"""
Runtime loader for layered dependencies (Windows-only, GPU Torch runtime)
=========================================================================

This loader reflects the decisions we made:
  • Windows-only support (no platform/variant selection logic at runtime)
  • Always Torch GPU; no CPU/CUDA variant switching
  • Content-addressed layer ZIPs (e.g., torch.<sha12>.zip)
  • Deterministic builds verified by SHA-256
  • Loads layers **by reading the release-manifest.json** produced at build time

Typical layout on client:

    app/
      runtime_loader.py
      release-manifest.json
      layers/
        core.<sha12>.zip
        heavy.<sha12>.zip
        vision-io.<sha12>.zip
        ops.<sha12>.zip
        torch.<sha12>.zip
        code.<sha12>.zip
        ...

Usage (programmatic):

    from runtime_loader import RuntimeLoader
    loader = RuntimeLoader()
    loader.load_release("./release-manifest.json")
    # Now import your app
    from your_app.main import run
    run()

Usage (CLI for diagnostics):

    python -m runtime_loader --manifest ./release-manifest.json --list
    python -m runtime_loader --manifest ./release-manifest.json --load

Environment variables (optional):
  • APP_RELEASE_MANIFEST : path to release-manifest.json (default ./release-manifest.json)
  • APP_VERIFY_HASH      : '1' to verify ZIP sha256 (default 1 / True)
  • APP_STRICT           : '1' to raise on errors (default 1 / True)

Notes
-----
• The release-manifest.json should include entries like:

  {
    "app": {"name": "am100-auto-detection", "version": "1.3.2", "python": "3.12", "platform": "win-amd64"},
    "layers": [
      {"name": "core",  "zip": "core.1a2b3c4d5e6f.zip",  "sha256": "<full-hash>", "manifest": {...}},
      {"name": "torch", "zip": "torch.abcdefabcdef.zip", "sha256": "<full-hash>", "manifest": {...}},
      ...
    ]
  }

• We honour either `path` (absolute or relative) or `zip` entries in the manifest.
  Resolution order per layer:
    1) entry["path"] if exists (absolute or relative to manifest dir)
    2) manifest_dir / "layers" / entry["zip"]
    3) manifest_dir / entry["zip"]

• Earlier paths inserted into sys.path take precedence; we load in the order the
  manifest lists layers. Keep optional/plotting layers later if you want them to
  be shadowed by more specific ones.
"""

from __future__ import annotations

import json
import os
import sys
import hashlib
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence
from pathlib import Path


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _normpath(p: str | Path) -> Path:
    return Path(p).resolve()


@dataclass
class LayerEntry:
    name: str
    zip_path: Path
    sha256: Optional[str]
    inner_manifest: Optional[Dict[str, Any]]


class RuntimeLoader:
    """Load per-layer ZIPs listed in a release manifest into sys.path.

    Parameters
    ----------
    verify_hash : bool
        Verify ZIP sha256 against the manifest (default: True or APP_VERIFY_HASH=="1").
    strict : bool
        Raise on missing files or hash mismatch (default: True or APP_STRICT=="1").
    logger : callable
        Function to receive log strings (default: print).
    """

    def __init__(
        self,
        verify_hash: Optional[bool] = None,
        strict: Optional[bool] = None,
        logger=None,
    ) -> None:
        env_verify = os.environ.get("APP_VERIFY_HASH")
        env_strict = os.environ.get("APP_STRICT")
        self.verify_hash = (
            (env_verify == "1")
            if env_verify is not None
            else (True if verify_hash is None else verify_hash)
        )
        self.strict = (
            (env_strict == "1")
            if env_strict is not None
            else (True if strict is None else strict)
        )
        self._log = logger or (lambda msg: print(msg))

    def load_release(self, manifest_path: str | Path) -> List[LayerEntry]:
        """Read a release manifest and load its layers into sys.path (in order).

        Returns a list of LayerEntry for the loaded layers.
        """
        manifest_file = _normpath(manifest_path)
        mdir = manifest_file.parent

        data = self._read_json(manifest_file)
        app = data.get("app", {})
        layers: List[Dict[str, Any]] = data.get("layers", [])
        if not isinstance(layers, list):
            self._error("Invalid release manifest: 'layers' must be a list")
            return []

        self._log(
            f"RuntimeLoader: app={app.get('name')} version={app.get('version')} python={app.get('python')} strict={self.strict} verify_hash={self.verify_hash}"
        )

        loaded: List[LayerEntry] = []
        for entry in layers:
            layer_name = str(entry.get("name"))
            sha = entry.get("sha256") or entry.get("zip_sha256")

            # Resolve path: prefer explicit 'path', then layers/<zip>, then local <zip>
            zpath: Optional[Path] = None
            if entry.get("path"):
                p = Path(entry["path"]).expanduser()
                zpath = p if p.is_absolute() else (mdir / p)
            elif entry.get("zip"):
                z = Path(entry["zip"]).name
                candidate1 = mdir / "layers" / z
                candidate2 = mdir / z
                if candidate1.exists():
                    zpath = candidate1
                elif candidate2.exists():
                    zpath = candidate2

            if not zpath or not zpath.exists():
                self._error(
                    f"Layer '{layer_name}' not found. Provide 'path' or ensure ZIP exists next to manifest (layers/<zip> or <zip>)."
                )
                continue

            if self.verify_hash and sha:
                actual = _sha256(zpath)
                if actual != sha:
                    self._error(
                        f"Hash mismatch for {zpath.name}: manifest={sha} actual={actual}"
                    )

            sys.path.insert(0, str(zpath))
            loaded.append(
                LayerEntry(
                    name=layer_name,
                    zip_path=zpath,
                    sha256=sha,
                    inner_manifest=entry.get("manifest"),
                )
            )
            self._log(f"Loaded layer: {layer_name} ← {zpath.name}")

        return loaded

    def _read_json(self, path: Path) -> Dict[str, Any]:
        try:
            with path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            self._error(f"Failed to read JSON: {path}: {e}")
            return {}

    def _error(self, msg: str) -> None:
        if self.strict:
            raise RuntimeError(msg)
        else:
            self._log("ERROR: " + msg)


def main(argv: Sequence[str]) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Load layer ZIPs from a release manifest into sys.path"
    )
    parser.add_argument(
        "--manifest",
        default=None,
        help="Path to release-manifest.json (default: APP_RELEASE_MANIFEST or ./release-manifest.json)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List resolved layers without mutating sys.path",
    )
    parser.add_argument("--load", action="store_true", help="Load layers into sys.path")
    parser.add_argument(
        "--no-verify", action="store_true", help="Disable hash verification"
    )
    parser.add_argument(
        "--no-strict",
        action="store_true",
        help="Do not raise on errors (log and continue)",
    )

    args = parser.parse_args(argv)

    manifest = (
        args.manifest
        or os.environ.get("APP_RELEASE_MANIFEST")
        or "release-manifest.json"
    )

    loader = RuntimeLoader(
        verify_hash=False if args.no_verify else None,
        strict=False if args.no_strict else None,
    )

    data = loader._read_json(_normpath(manifest))
    layers = data.get("layers", []) if isinstance(data, dict) else []

    if args.list:
        app = data.get("app", {}) if isinstance(data, dict) else {}
        print(
            f"App: {app.get('name')} v{app.get('version')} (py {app.get('python')})\nManifest: {Path(manifest).resolve()}\n"
        )
        for e in layers:
            name = e.get("name")
            sha = e.get("sha256") or e.get("zip_sha256")
            path_hint = e.get("path") or e.get("zip")
            print(
                f"- {name:12} sha={str(sha)[:12] if sha else '<none>'} path={path_hint}"
            )

    if args.load:
        try:
            loader.load_release(manifest)
        except Exception as e:
            print(f"ERROR: {e}")
            return 1

    if not (args.list or args.load):
        parser.print_help()

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
