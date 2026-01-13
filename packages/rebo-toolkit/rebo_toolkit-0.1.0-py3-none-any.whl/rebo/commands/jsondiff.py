\
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from ..core import read_text, write_text, rel


def cmd_jsondiff(args) -> int:
    oldp = Path(args.old).resolve()
    newp = Path(args.new).resolve()

    old = json.loads(read_text(oldp))
    new = json.loads(read_text(newp))

    changes: List[dict] = []
    diff(old, new, path="$", out=changes, limit=args.max_changes)

    summary = {
        "total": len(changes),
        "added": sum(1 for c in changes if c["type"] == "added"),
        "removed": sum(1 for c in changes if c["type"] == "removed"),
        "changed": sum(1 for c in changes if c["type"] == "changed"),
        "type_changed": sum(1 for c in changes if c["type"] == "type_changed"),
    }

    if args.format == "text":
        print("[JSONDIFF] summary:", summary)
        for c in changes[: args.max_changes]:
            print(f"- {c['type']:12} {c['path']}: {c.get('from','')} -> {c.get('to','')}")
        if len(changes) > args.max_changes:
            print(f"... truncated ({len(changes)} total changes)")
        return 0

    if args.format == "json":
        payload = {"summary": summary, "changes": changes}
        out_text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
        if args.out:
            outp = Path(args.out).resolve()
            write_text(outp, out_text, overwrite=True)
            print(f"[OK] wrote {outp}")
        else:
            print(out_text)
        return 0

    if args.format == "html":
        html = render_html(summary, changes)
        if args.out:
            outp = Path(args.out).resolve()
            write_text(outp, html, overwrite=True)
            print(f"[OK] wrote {outp}")
        else:
            print(html)
        return 0

    raise SystemExit("Unknown format")


def diff(a: Any, b: Any, path: str, out: List[dict], limit: int) -> None:
    if len(out) >= limit:
        return

    if type(a) != type(b):
        out.append({"type": "type_changed", "path": path, "from": type_name(a), "to": type_name(b)})
        return

    if isinstance(a, dict):
        a_keys = set(a.keys())
        b_keys = set(b.keys())
        for k in sorted(a_keys - b_keys):
            out.append({"type": "removed", "path": f"{path}.{k}", "from": preview(a[k])})
            if len(out) >= limit:
                return
        for k in sorted(b_keys - a_keys):
            out.append({"type": "added", "path": f"{path}.{k}", "to": preview(b[k])})
            if len(out) >= limit:
                return
        for k in sorted(a_keys & b_keys):
            diff(a[k], b[k], f"{path}.{k}", out, limit)
            if len(out) >= limit:
                return
        return

    if isinstance(a, list):
        # simple list diff: compare by index up to max len
        n = max(len(a), len(b))
        for i in range(n):
            p = f"{path}[{i}]"
            if i >= len(a):
                out.append({"type": "added", "path": p, "to": preview(b[i])})
            elif i >= len(b):
                out.append({"type": "removed", "path": p, "from": preview(a[i])})
            else:
                diff(a[i], b[i], p, out, limit)
            if len(out) >= limit:
                return
        return

    # scalar
    if a != b:
        out.append({"type": "changed", "path": path, "from": preview(a), "to": preview(b)})


def type_name(x: Any) -> str:
    return type(x).__name__


def preview(x: Any, maxlen: int = 120) -> str:
    try:
        s = json.dumps(x, ensure_ascii=False)
    except Exception:
        s = str(x)
    if len(s) > maxlen:
        return s[:maxlen] + "…"
    return s


def render_html(summary: dict, changes: List[dict]) -> str:
    rows = []
    for c in changes:
        rows.append(
            f"<tr><td>{escape(c['type'])}</td><td><code>{escape(c['path'])}</code></td>"
            f"<td><code>{escape(str(c.get('from','')))}</code></td><td><code>{escape(str(c.get('to','')))}</code></td></tr>"
        )
    rows_html = "\n".join(rows)

    return f"""\
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>rebo jsondiff</title>
  <style>
    body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial; padding: 24px; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; vertical-align: top; }}
    th {{ background: #f6f6f6; text-align: left; }}
    code {{ white-space: pre-wrap; }}
  </style>
</head>
<body>
  <h1>JSON Diff Report</h1>
  <p><b>Total:</b> {summary['total']} | <b>Added:</b> {summary['added']} | <b>Removed:</b> {summary['removed']} | <b>Changed:</b> {summary['changed']} | <b>Type changed:</b> {summary['type_changed']}</p>
  <table>
    <thead>
      <tr><th>Type</th><th>Path</th><th>From</th><th>To</th></tr>
    </thead>
    <tbody>
      {rows_html}
    </tbody>
  </table>
</body>
</html>
"""


def escape(s: str) -> str:
    return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
