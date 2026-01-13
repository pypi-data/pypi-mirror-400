import os
import shutil
import hashlib
from concurrent.futures import ThreadPoolExecutor
import stat


def new_report():
    return {
        "copied": [],
        "skipped": [],
        "unreadable": [],
        "invalid": []
    }


def sha256(path):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
    except (PermissionError, FileNotFoundError):
        return None


def scan_dir(base):
    files = {}
    dirs = set()

    for root, _, fnames in os.walk(base, followlinks=False):
        rel = os.path.relpath(root, base)

        # ❗ remove "." do conjunto de diretórios
        if rel != ".":
            dirs.add(rel)

        for f in fnames:
            full = os.path.join(root, f)
            relf = os.path.normpath(os.path.join(rel, f))

            try:
                st = os.lstat(full)

                # ignora tudo que não for arquivo regular
                if not stat.S_ISREG(st.st_mode):
                    continue

                files[relf] = {
                    "path": full,
                    "mtime": st.st_mtime,
                }

            except FileNotFoundError:
                # arquivo sumiu durante o scan
                continue
            except PermissionError:
                # leitura negada no scan
                continue

    return files, dirs


def compute_hashes(files, report):
    with ThreadPoolExecutor() as ex:
        results = ex.map(
            lambda p: (p, sha256(files[p]["path"])),
            files
        )

        for path, h in results:
            if h is None:
                files[path]["hash"] = "UNREADABLE"
                report["unreadable"].append(path)
            else:
                files[path]["hash"] = h


def diff_dirs(a, b, use_hash=False):
    fa, da = scan_dir(a)
    fb, db = scan_dir(b)

    report = new_report()

    if use_hash:
        compute_hashes(fa, report)
        compute_hashes(fb, report)

    diff = {
        "missing_dirs": sorted(da - db),
        "extra_dirs": sorted(db - da),
        "new_files": [],
        "updated_files": [],
        "extra_files": []
    }

    for f in fa:
        if f not in fb:
            diff["new_files"].append(f)
        else:
            if use_hash:
                ha = fa[f].get("hash")
                hb = fb[f].get("hash")

                # ❗ não trata UNREADABLE como updated
                if "UNREADABLE" in (ha, hb):
                    continue

                if ha != hb:
                    diff["updated_files"].append(f)
            else:
                if fa[f]["mtime"] > fb[f]["mtime"]:
                    diff["updated_files"].append(f)

    for f in fb:
        if f not in fa:
            diff["extra_files"].append(f)

    return diff, report


def apply_sync(a, b, diff, report, delete=False, dry=False, strict_fs=False):
    # criação de diretórios ausentes
    for d in diff["missing_dirs"]:
        target = os.path.join(b, d)
        if not dry:
            os.makedirs(target, exist_ok=True)

    # cópia de arquivos
    for f in diff["new_files"] + diff["updated_files"]:
        src = os.path.join(a, f)
        dst = os.path.join(b, f)

        filename = os.path.basename(f)
        if filename.rstrip() != filename:
            report["invalid"].append(f)
            if strict_fs:
                raise RuntimeError("Invalid filename detected")
            continue

        if dry:
            report["copied"].append(f)
            continue

        try:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            report["copied"].append(f)

        except PermissionError:
            report["unreadable"].append(f)
            if strict_fs:
                raise

        except OSError:
            report["invalid"].append(f)
            if strict_fs:
                raise

    # ❗ delete blindado
    if delete:
        for f in diff["extra_files"]:
            path = os.path.join(b, f)

            if dry:
                continue

            try:
                os.remove(path)
            except FileNotFoundError:
                continue
            except PermissionError:
                report["unreadable"].append(f)
                if strict_fs:
                    raise

        for d in reversed(diff["extra_dirs"]):
            path = os.path.join(b, d)
            if os.path.isdir(path):
                try:
                    if not dry:
                        os.rmdir(path)
                except OSError:
                    if strict_fs:
                        raise
