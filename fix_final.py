import pathlib
import re

# ── THE REAL FIX: patch blocks.py get_api_info to never crash ────────────────
bp = pathlib.Path("venv311/Lib/site-packages/gradio/blocks.py")
bt = bp.read_text(encoding="utf-8")

old = "            python_type = client_utils.json_schema_to_python_type(info)"
new = ("            try:\n"
       "                python_type = client_utils.json_schema_to_python_type(info)\n"
       "            except Exception:\n"
       "                python_type = 'Any'")

if old in bt:
    bt = bt.replace(old, new)
    bp.write_text(bt, encoding="utf-8")
    print("Fixed blocks.py get_api_info")
else:
    idx = bt.find("json_schema_to_python_type")
    print("blocks.py context:", repr(bt[max(0,idx-60):idx+80]))

# ── Also fix routes.py to not crash the whole page ───────────────────────────
rp = pathlib.Path("venv311/Lib/site-packages/gradio/routes.py")
rt = rp.read_text(encoding="utf-8")

old2 = "        api_info = cast(dict[str, Any], app.get_blocks().get_api_info())"
new2 = ("        try:\n"
        "            api_info = cast(dict[str, Any], app.get_blocks().get_api_info())\n"
        "        except Exception:\n"
        "            api_info = {}")

if old2 in rt:
    rt = rt.replace(old2, new2)
    rp.write_text(rt, encoding="utf-8")
    print("Fixed routes.py")
else:
    print("routes.py: pattern not found, may already be patched")

print("Done. Restart your app.")
