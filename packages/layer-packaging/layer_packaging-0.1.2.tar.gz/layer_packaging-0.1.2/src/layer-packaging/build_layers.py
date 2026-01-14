from __future__ import annotations

import argparse
import os, sys, json, stat, time, shutil, zipfile, tempfile, subprocess, hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple, Dict, List

try:
    import tomllib
except Exception:
    tomllib = None

INSTALLED_PACKAGES_CACHE = set()

# ---------------------------- subprocess helpers ----------------------------


def run(
    cmd: List[str], cwd: Optional[str] = None, env: Optional[Dict[str, str]] = None
):
    print("$", " ".join(cmd))
    subprocess.check_call(cmd, cwd=cwd, env=env)


def run_capture(cmd: List[str], cwd: Optional[str] = None) -> str:
    print("$", " ".join(cmd))
    return subprocess.check_output(cmd, cwd=cwd, text=True)


# ---------------------------- deterministic zip -----------------------------


def _fixed_zip_timestamp():
    sde = os.environ.get("SOURCE_DATE_EPOCH")
    if sde:
        t = time.gmtime(int(sde))
        return t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec
    return 2000, 1, 1, 0, 0, 0  # stable fallback


def _exclude_from_layer(path: Path, staging_root: Path) -> bool:
    rel = path.relative_to(staging_root)
    if len(rel.parts) == 1:  # site-packages root files
        n = rel.name
        if n in ("_virtualenv.py", "_virtualenv.pth") or n.endswith(".pth"):
            return True
    return False


def zip_reproducible_dir(out_zip: Path, root: Path):
    paths = [
        p
        for p in root.rglob("*")
        if p.is_file() and p.relative_to(root).parts[0] not in INSTALLED_PACKAGES_CACHE
    ]
    paths.sort(key=lambda p: str(p.relative_to(root)).replace("\\", "/"))
    ts = _fixed_zip_timestamp()

    if out_zip.exists():
        out_zip.unlink()
    with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_LZMA) as z:
        for p in paths:
            if _exclude_from_layer(p, root):
                continue
            arc = str(p.relative_to(root)).replace("\\", "/")
            zi = zipfile.ZipInfo(arc, date_time=ts)
            mode = 0o755 if os.access(p, os.X_OK) else 0o644
            zi.external_attr = (stat.S_IFREG | mode) << 16
            zi.compress_type = zipfile.ZIP_LZMA
            with p.open("rb") as f:
                z.writestr(zi, f.read(), compress_type=zipfile.ZIP_LZMA)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------- resolved fingerprint --------------------------

# Regex to extract the base distribution name from a requirement header line.
# Handles:
#   foo==1.2.3
#   foo[extra]==1.2.3
#   foo ; python_version < "3.12"
#   foo @ https://...
REQ_NAME_RE = re.compile(
    r"""
    ^\s*
    (?P<name>[A-Za-z0-9][A-Za-z0-9._-]*)   # distribution name
    (?:\[[^\]]+\])?                        # optional extras
    (?:\s*(==|>=|<=|>|<|!=|~=|===|@)\s*[^;#\s]+)?  # version or direct ref
    (?:\s*;[^\n]+)?                        # optional marker
    \s*$
    """,
    re.VERBOSE,
)


def normalise_name(name: str) -> str:
    """PEP 503 normalized name: lowercase, collapse - _ . to '-'."""
    return re.sub(r"[-_.]+", "-", name).lower().strip()


def requirement_name_from_line(line: str) -> str | None:
    s = line.strip()
    if not s or s.startswith("#"):
        return None
    m = REQ_NAME_RE.match(s)
    if not m:
        return None
    return normalise_name(m.group("name"))


def compute_group_fingerprint(
    pyproject_dir: Path,
    group: str,
    include_hashes: bool = False,
    installed_cache: set[str] | None = None,
) -> str:
    """
    Create a stable fingerprint for the locked dependency *set* of a group.
    Includes only the overlapping entries from installed_cache in the hash,
    so unrelated cached packages do not affect the fingerprint.
    """
    cmd = ["uv", "export", "--group", group, "--locked"]
    if not include_hashes:
        cmd.append("--no-hashes")  # single-line entries; still locked to exact versions

    out = run_capture(cmd, cwd=str(pyproject_dir))

    # Keep non-comment, non-empty lines verbatim for hashing stability
    export_lines = [
        ln.strip()
        for ln in out.splitlines()
        if ln.strip() and not ln.strip().startswith("#")
    ]

    # Extract normalised package names present in export
    export_names: set[str] = set()
    for ln in export_lines:
        name = requirement_name_from_line(ln)
        if name:
            export_names.add(name)

    # Normalise installed cache and intersect with export names
    # Only overlapping cached packages should influence the fingerprint.
    cache_lines: list[str] = []
    if installed_cache:
        normalized_cache = {normalise_name(x) for x in installed_cache}
        overlap = sorted(export_names.intersection(normalized_cache))
        print(overlap)
        # Prefix for disambiguation in hash domain
        cache_lines = [f"INSTALLED:{pkg}" for pkg in overlap]

    combined = sorted(export_lines + cache_lines)
    norm = "\n".join(combined).encode("utf-8")
    return hashlib.sha256(norm).hexdigest()


def find_cached_layer(
    layers_dir: Path, layer_name: str, resolved_fingerprint: str
) -> Optional[Tuple[Path, Path]]:
    """
    Search existing manifests for same resolved fingerprint; if found, return (zip, manifest).
    """
    for mf in layers_dir.glob(f"{layer_name}.*.manifest.json"):
        try:
            data = json.loads(mf.read_text(encoding="utf-8"))
        except Exception:
            continue
        if (
            data.get("name") == layer_name
            and data.get("resolved_fingerprint") == resolved_fingerprint
        ):
            z = layers_dir / Path(data.get("path", "")).name
            if z.exists():
                print(
                    f"{layer_name}: cache hit (resolved_fingerprint match) → {z.name}"
                )
                return z, mf
    return None


# ---------------------------- build layer (with skip) ------------------------


def collect_versions(py_interpreter: Path) -> Dict[str, str]:
    code = r"""
import json
from importlib.metadata import distributions
out={}
for d in distributions():
    try: out[d.metadata['Name']] = d.version
    except Exception: pass
print(json.dumps(out))
"""
    data = subprocess.check_output([str(py_interpreter), "-c", code], text=True)
    return json.loads(data)


def build_group_layer(
    pyproject: Path,
    layers_dir: Path,
    group: str,
    layer_name: Optional[str],
    variant: Optional[str],
) -> Tuple[Path, Path]:
    """
    Record-and-skip logic:
      1) Compute resolved_fingerprint from uv.lock for this group.
      2) If a manifest with the same fingerprint exists, return it (skip build).
      3) Else: create temp venv, uv-install this group's locked set into it,
               vendor site-packages to deterministic ZIP, write manifest.
    """
    pyproject_dir = pyproject.parent
    name = layer_name or group

    # 1) Pre-install fingerprint (from lock)
    resolved_fp = compute_group_fingerprint(
        pyproject_dir,
        group,
        include_hashes=False,
        installed_cache=INSTALLED_PACKAGES_CACHE,
    )

    # 2) Cache lookup
    layers_dir.mkdir(parents=True, exist_ok=True)
    cached = find_cached_layer(layers_dir, name, resolved_fp)
    if cached:
        _, cached_manifest = cached
        with open(cached_manifest, "r") as f:
            data = json.load(f)
            version_set = data["version_set"]
            # Update installed packages set
            INSTALLED_PACKAGES_CACHE.update(version_set.keys())
        return cached  # (zip, manifest)

    # 3) Build fresh
    tmp = Path(tempfile.mkdtemp(prefix=f"build-{group}-"))
    try:
        venv = tmp / ".venv"
        run(["uv", "venv", str(venv)])

        py = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")

        shutil.copy(pyproject_dir / "pyproject.toml", tmp)
        shutil.copy(pyproject_dir / "uv.lock", tmp)

        # Install from lock into this venv (exact versions; respects indexes & sources)
        run(
            [
                "uv",
                "sync",
                "--frozen",
                "--no-default-groups",
                "--group",
                group,
                "--python",
                str(py),  # install into tmp venv
            ],
            cwd=str(tmp),
        )
        # (Refs: groups installation & arbitrary env targeting)  # [3](https://www.sarahglasmacher.com/how-to-build-python-package-uv/)[4](https://github.com/astral-sh/uv/issues/1517)

        # Stage site-packages
        sp = subprocess.check_output(
            [
                str(py),
                "-c",
                "import sysconfig; print(sysconfig.get_paths()['purelib'])",
            ],
            text=True,
        ).strip()
        staging = tmp / f"{group}-staging"
        if staging.exists():
            shutil.rmtree(staging)
        staging.mkdir(parents=True, exist_ok=True)

        run(
            [
                str(py),
                "-c",
                f"import shutil; shutil.copytree(r'{sp}', r'{staging}', dirs_exist_ok=True)",
            ]
        )

        # Clean noisy caches (pyc are usually not present, but just in case)
        for p in staging.rglob("__pycache__"):
            shutil.rmtree(p, ignore_errors=True)

        # Deterministic ZIP
        base = f"{name}" + (f"-{variant}" if variant else "")
        tmp_zip = layers_dir / (base + ".zip")
        zip_reproducible_dir(tmp_zip, staging)
        sha = sha256(tmp_zip)
        final_zip = layers_dir / (base + f".{sha[:12]}.zip")

        try:
            tmp_zip.rename(final_zip)
        except FileExistsError:
            tmp_zip.unlink()  # someone else already built the same blob
            print(f"{name} layer unchanged: keeping {final_zip}")

        # Manifest
        versions = collect_versions(py)
        skipped_packages = INSTALLED_PACKAGES_CACHE.intersection(versions.keys())
        INSTALLED_PACKAGES_CACHE.update(versions.keys())
        manifest = {
            "name": name,
            "variant": variant,
            "built_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat()
            + "Z",
            "python": f"{sys.version_info.major}.{sys.version_info.minor}",
            "version_set": versions,
            "skipped": list(skipped_packages),
            "zip_sha256": sha,
            "path": str(final_zip),
            "resolved_fingerprint": resolved_fp,
        }
        mf = layers_dir / (base + f".{sha[:12]}.manifest.json")
        mf.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        print(f"Built {final_zip.name} ({sha[:12]}…)")
        return final_zip, mf
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ------------------------------- code layer ----------------------------------


def gather_code_files(base_dir: Path) -> List[Path]:
    """Resolve a list of globs relative to base_dir and return file paths."""
    files: List[Path] = []
    for p in base_dir.rglob("*"):
        if p.is_file():
            files.append(p)
    # Deduplicate while keeping order
    seen = set()
    unique_files = []
    for f in files:
        if f not in seen:
            unique_files.append(f)
            seen.add(f)
    return unique_files


def build_code_layer(
    pyproject: Path, layers_dir: Path, layer_name: str
) -> Tuple[Path, Path]:
    base_dir = pyproject.parent / "pyinstaller" / "local_dependencies"
    selected = gather_code_files(base_dir)

    # Build manifest: file list + per-file hashes
    per_file: List[Tuple[str, str]] = []
    for f in selected:
        print(str(f.relative_to(base_dir)))
        per_file.append((str(f.relative_to(base_dir)).replace("\\", "/"), sha256(f)))
    print(selected)

    manifest = {
        "name": layer_name,
        "variant": None,
        "built_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat() + "Z",
        "python": f"{sys.version_info.major}.{sys.version_info.minor}",
        "files": [{"path": p, "sha256": h} for p, h in per_file],
        "version_set": {},  # code layer carries app code, not site-packages
    }

    out_zip = layers_dir / f"{layer_name}.zip"
    layers_dir.mkdir(parents=True, exist_ok=True)

    # Create zip
    if out_zip.exists():
        out_zip.unlink()
    with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_LZMA) as z:
        for path, (arcpath, _) in zip(selected, per_file):
            z.write(path, arcpath, compress_type=zipfile.ZIP_LZMA)
        # z.writestr("MANIFEST.json", json.dumps(manifest, indent=2).encode("utf-8"))

    sha = sha256(out_zip)
    out_sha_zip = layers_dir / out_zip.name.replace(".zip", f".{sha[:12]}.zip")
    try:
        out_zip.rename(out_sha_zip)
    except FileExistsError:
        out_zip.unlink()
        print(f"{layer_name} layer unchanged: keeping {out_sha_zip}")
        return out_sha_zip, layers_dir / (out_sha_zip.stem + f".manifest.json")

    manifest["zip_sha256"] = sha
    manifest["path"] = str(out_sha_zip)

    manifest_file = layers_dir / (out_zip.stem + f".{sha[:12]}.manifest.json")
    manifest_file.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(
        f"Built {out_zip.name} ({manifest['zip_sha256'][:12]}…) with {len(selected)} files"
    )
    return out_zip, manifest_file


# ------------------------------- CLI -----------------------------------------


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(
        description="Build per-layer ZIPs from uv groups and a code layer; generate release manifest"
    )
    p.add_argument(
        "--pyproject", default="pyproject.toml", help="Path to pyproject.toml"
    )
    p.add_argument(
        "--layers-dir", default="./layers", help="Output directory for layer ZIPs"
    )
    p.add_argument(
        "--manifests-dir",
        default="./manifests",
        help="Output directory for release manifests",
    )
    p.add_argument(
        "--groups",
        nargs="*",
        default=[],
        help="uv dependency group names to build (in precedence order)",
    )
    p.add_argument(
        "--variant",
        default=None,
        help="Single layer=variant mapping (e.g., 'torch=gpu')",
    )
    p.add_argument(
        "--name-map",
        default=None,
        help="JSON mapping of group->layer name (if group name differs from layer name)",
    )

    args = p.parse_args(argv)

    pyproject = Path(args.pyproject)
    layers_dir = Path(args.layers_dir)
    groups = args.groups

    pyproject_data = tomllib.loads(Path("../../pyproject.toml").read_text())
    version = pyproject_data["project"]["version"]

    variant_map: Dict[str, str] = {}
    if args.variant and "=" in args.variant:
        k, v = args.variant.split("=", 1)
        variant_map[k.strip()] = v.strip()

    name_map: Dict[str, str] = {}
    if args.name_map:
        name_map = json.loads(args.name_map)

    built: List[Tuple[Path, Path]] = []

    # Run uv lock
    run(["uv", "lock"])

    # Build code layer
    if "code" in groups:
        layer_name = name_map.get("code", "code")
        built.append(build_code_layer(pyproject, layers_dir, layer_name))
        groups = [group for group in groups if group != "code"]

    # Build uv dependency layers
    for group in groups:
        layer_name = name_map.get(group, group)
        variant = variant_map.get(layer_name) or variant_map.get(group)
        out_zip = build_group_layer(pyproject, layers_dir, group, layer_name, variant)
        built.append(out_zip)

    if args.manifests_dir:
        os.makedirs(args.manifests_dir, exist_ok=True)
        variants_arg = (
            ",".join(f"{k}={v}" for k, v in variant_map.items()) if variant_map else ""
        )
        run(
            [
                sys.executable,
                "release_manifest.py",
                "--pyproject",
                str(pyproject),
                "--layer-manifests",
                *(str(manifest) for _, manifest in built),
                "--variants",
                variants_arg,
                "--out",
                f"{args.manifests_dir}/release_manifest_{version}.json",
            ]
        )

    print("All layers built.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
