
# runtime_loader.py — Win-amd64, GPU-only, release-manifest driven
"""
Loads layered dependencies for your application by reading release-manifest.json.
Pure-Python layers (DEFLATE/STORED) are added as ZIPs to sys.path (zipimport).
Native or non-DEFLATE layers are extracted once to a content-addressed store and
then added as directories to sys.path.

Environment variables:
  APP_RELEASE_MANIFEST  : Path to release-manifest.json (default ./release-manifest.json)
  APP_VERIFY_HASH       : '1' to verify SHA256 (default 1)
  APP_STRICT            : '1' to raise on errors, else log and continue (default 1)
  APP_LAYER_STORE       : Destination for extracted layers (default:
                          Windows → ./store)
  APP_FORCE_EXTRACT     : '1' to re-extract even if store/<sha>/ exists (default 0)
"""

from __future__ import annotations
import json
import os
import sys
import hashlib
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

# ------------------------------ Utilities -----------------------------------

def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def _normpath(p: str | Path) -> Path:
    return Path(p).resolve()

def _is_windows() -> bool:
    return os.name == "nt"

def _default_store_dir() -> Path:
    return Path("./store")

# ------------------------------ Data types ----------------------------------

@dataclass
class LayerEntry:
    name: str
    path_on_sys: Path        # path actually inserted into sys.path (zip or directory)
    sha256: Optional[str]
    source_zip: Optional[Path]
    inner_manifest: Optional[Dict[str, Any]]

# ------------------------------ Loader --------------------------------------

class RuntimeLoader:
    """
    Release-manifest driven layer loader with extract-on-demand for native/LZMA layers.

    Parameters
    ----------
    verify_hash : bool|None
        Verify ZIP sha256 against manifest (default: True or APP_VERIFY_HASH=='1').
    strict : bool|None
        Raise on errors (default: True or APP_STRICT=='1'), else just log.
    logger : callable|None
        Function to receive log strings (default: print).
    """

    def __init__(self, verify_hash: Optional[bool] = None, strict: Optional[bool] = None, logger=None) -> None:
        env_verify = os.environ.get("APP_VERIFY_HASH")
        env_strict = os.environ.get("APP_STRICT")
        self.verify_hash = (env_verify == "1") if env_verify is not None else (True if verify_hash is None else verify_hash)
        self.strict = (env_strict == "1") if env_strict is not None else (True if strict is None else strict)
        self._log = logger or (lambda msg: print(msg))

        env_store = os.environ.get("APP_LAYER_STORE")
        self.store_dir = _normpath(env_store) if env_store else _default_store_dir()
        self.force_extract = os.environ.get("APP_FORCE_EXTRACT") == "1"

        # ensure store dir exists
        self.store_dir.mkdir(parents=True, exist_ok=True)

    # -------------------------- Public API ---------------------------------

    def load_release(self, manifest_path: str | Path) -> List[LayerEntry]:
        """
        Read release-manifest.json and load layers into sys.path in manifest order.
        Returns a list of LayerEntry describing what was loaded.
        """
        manifest_file = _normpath(manifest_path)
        mdir = manifest_file.parent
        data = self._read_json(manifest_file)

        app = data.get("app", {}) or {}
        layers: List[Dict[str, Any]] = data.get("layers", []) or []
        if not isinstance(layers, list):
            self._error("Invalid release manifest: 'layers' must be a list")
            return []

        self._log(
            f"RuntimeLoader: app={app.get('name')} version={app.get('version')} "
            f"python={app.get('python')} strict={self.strict} verify_hash={self.verify_hash}"
        )

        loaded: List[LayerEntry] = []
        for entry in layers:
            layer_name = str(entry.get("name"))
            sha = entry.get("sha256") or entry.get("zip_sha256")

            # Resolve ZIP path: prefer explicit 'path', then layers/<zip>, then local <zip>
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
                    f"Layer '{layer_name}' not found. Provide 'path' or ensure ZIP exists "
                    f"next to manifest (layers/<zip> or <zip>)."
                )
                continue

            # Verify hash if requested
            if self.verify_hash and sha:
                actual = _sha256(zpath)
                if actual != sha:
                    self._error(f"Hash mismatch for {zpath.name}: manifest={sha} actual={actual}")
                    # If non-strict, continue but warn
                    if not self.strict:
                        self._log(f"WARNING: proceeding despite hash mismatch for {zpath.name}")

            # Decide whether to extract or load zip directly
            if self._needs_extraction(zpath):
                if not sha:
                    self._error(f"Layer '{layer_name}' requires extraction but manifest has no sha256.")
                    if not self.strict:
                        # Try to compute live hash for store key
                        sha = _sha256(zpath)
                target = self._extract_once(zpath, sha or _sha256(zpath))
                sys.path.insert(0, str(target))
                loaded.append(LayerEntry(
                    name=layer_name,
                    path_on_sys=target,
                    sha256=sha,
                    source_zip=zpath,
                    inner_manifest=entry.get("manifest")
                ))
                self._log(f"Extracted native/non-DEFLATE layer: {layer_name} → {target}")
            else:
                sys.path.insert(0, str(zpath))
                loaded.append(LayerEntry(
                    name=layer_name,
                    path_on_sys=zpath,
                    sha256=sha,
                    source_zip=zpath,
                    inner_manifest=entry.get("manifest")
                ))
                self._log(f"Loaded pure layer via ZIP: {layer_name} ← {zpath.name}")

        return loaded

    # -------------------------- Helpers -----------------------------------

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

    # Extraction decisions
    def _needs_extraction(self, zpath: Path) -> bool:
        """
        Return True if the ZIP contains native binaries or any entry compressed
        with a method other than DEFLATE (8) or STORED (0).
        """
        try:
            with zipfile.ZipFile(zpath, "r") as z:
                for info in z.infolist():
                    n = info.filename.lower()
                    # Native binaries must be extracted (zipimport can't load them)
                    if n.endswith((".pyd", ".dll", ".so")):
                        return True
                    # zipimport expects DEFLATE/STORED for importable .py/.pyc
                    if info.compress_type not in (zipfile.ZIP_DEFLATED, zipfile.ZIP_STORED):
                        return True
            return False
        except Exception as e:
            # If we can't inspect reliably, be conservative and extract
            self._log(f"WARNING: Failed to inspect ZIP compression for {zpath}: {e}. Extracting.")
            return True

    def _extract_once(self, zpath: Path, sha: str) -> Path:
        """
        Extract zpath into store/<sha>/ if not already present.
        Respects APP_FORCE_EXTRACT to re-extract even if present.
        """
        target = self.store_dir / sha
        if target.exists() and not self.force_extract:
            return target

        # Optional integrity test before extraction
        with zipfile.ZipFile(zpath, "r") as z:
            bad = z.testzip()
            if bad is not None:
                self._error(f"ZIP integrity check failed: {zpath.name}: bad member {bad}")
            # Re-extract if forced
            if target.exists() and self.force_extract:
                # clean directory
                for p in sorted(target.rglob("*"), reverse=True):
                    try:
                        p.unlink()
                    except IsADirectoryError:
                        pass
                try:
                    target.rmdir()
                except Exception:
                    pass
            target.mkdir(parents=True, exist_ok=True)
            z.extractall(target)
        return target

# ------------------------------ CLI -----------------------------------------

def _cli(argv: Sequence[str]) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Load layer ZIPs from a release manifest into sys.path (with extract-on-demand)"
    )
    parser.add_argument("--manifest", default=None,
                        help="Path to release-manifest.json (default: APP_RELEASE_MANIFEST or ./release-manifest.json)")
    parser.add_argument("--list", action="store_true", help="List layers from manifest (no loading)")
    parser.add_argument("--load", action="store_true", help="Load layers into sys.path")
    parser.add_argument("--no-verify", action="store_true", help="Disable hash verification")
    parser.add_argument("--no-strict", action="store_true", help="Do not raise on errors (log and continue)")
    parser.add_argument("--store", default=None, help="Override APP_LAYER_STORE path")
    parser.add_argument("--force-extract", action="store_true", help="Override APP_FORCE_EXTRACT=1")

    args = parser.parse_args(argv)

    manifest = args.manifest or os.environ.get("APP_RELEASE_MANIFEST") or "release-manifest.json"

    loader = RuntimeLoader(
        verify_hash=False if args.no_verify else None,
        strict=False if args.no_strict else None,
    )
    if args.store:
        loader.store_dir = _normpath(args.store)
        loader.store_dir.mkdir(parents=True, exist_ok=True)
    if args.force_extract:
        loader.force_extract = True

    data = loader._read_json(_normpath(manifest))
    layers = data.get("layers", []) if isinstance(data, dict) else []

    if args.list:
        app = data.get("app", {}) if isinstance(data, dict) else {}
        print(f"App: {app.get('name')} v{app.get('version')} (py {app.get('python')})")
        print(f"Manifest: {_normpath(manifest)}")
        for e in layers:
            name = e.get("name")
            sha = e.get("sha256") or e.get("zip_sha256")
            path_hint = e.get("path") or e.get("zip")
            print(f"- {name:12} sha={str(sha)[:12] if sha else '<none>'} path={path_hint}")

    if args.load:
        try:
            loaded = loader.load_release(manifest)
            print(f"\nLoaded {len(loaded)} layers:")
            for le in loaded:
                print(f"- {le.name:12} → {le.path_on_sys}")
        except Exception as e:
            print(f"ERROR: {e}")
            return 1

    if not (args.list or args.load):
        parser.print_help()

    return 0

if __name__ == "__main__":
    raise SystemExit(_cli(sys.argv[1:]))
