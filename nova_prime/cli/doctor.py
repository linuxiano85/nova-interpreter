from __future__ import annotations
import json
import os
import platform
import sys
import traceback

def _try_import(mod: str):
    try:
        __import__(mod)
        return True, None
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"

def main():
    checks = {}
    checks["python_version"] = {
        "ok": (sys.version_info.major == 3 and 9 <= sys.version_info.minor <= 12),
        "value": platform.python_version(),
        "want": "3.9–3.12",
    }
    for mod in ["PySide6", "sounddevice", "openwakeword", "faster_whisper"]:
        ok, err = _try_import(mod)
        checks[f"import:{mod}"] = {"ok": ok, "error": err}
    qt_platform = os.environ.get("QT_QPA_PLATFORM", "")
    checks["qt_offscreen"] = {"ok": (qt_platform == "offscreen" or platform.system() != "Linux"), "value": qt_platform or "(default)"}
    try:
        from nova_prime.services.steam import _steam_root  # type: ignore
        root = _steam_root()
        checks["steam_detected"] = {"ok": bool(root), "path": root}
    except Exception as e:
        checks["steam_detected"] = {"ok": False, "error": str(e)}

    all_ok = all(v.get("ok", True) for v in checks.values())

    human = ["Nova Prime Doctor"]
    for k, v in checks.items():
        status = "OK" if v.get("ok", False) else "FAIL"
        detail = v.get("value") or v.get("path") or v.get("error") or ""
        human.append(f"- {k}: {status} {detail}")

    print("\n".join(human))
    print("\nJSON:", json.dumps(checks, ensure_ascii=False, indent=2))
    sys.exit(0 if all_ok else 1)

if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        print("Doctor crashed:\n", traceback.format_exc())
        sys.exit(2)