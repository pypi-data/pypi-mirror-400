from __future__ import annotations

from html import escape

from code_periscope.renderers.markdown import render_markdown
from code_periscope.core.report_model import ReportModel


def render_html(report: ReportModel) -> str:
    """Render the risk report as a standalone HTML document.

    Implementation note:
    We purposely keep this dependency-free by converting a known Markdown shape
    (headers + markdown tables + bullet list) into a clean, readable HTML page.
    """

    md = render_markdown(report)
    return _markdownish_to_html(md)


def _markdownish_to_html(md: str) -> str:
    lines = (md or "").splitlines()

    body_parts: list[str] = []

    i = 0
    while i < len(lines):
        line = lines[i].rstrip("\n")

        # Headings
        if line.startswith("# "):
            body_parts.append(f"<h1>{escape(line[2:].strip())}</h1>")
            i += 1
            continue
        if line.startswith("## "):
            body_parts.append(f"<h2>{escape(line[3:].strip())}</h2>")
            i += 1
            continue
        if line.startswith("### "):
            body_parts.append(f"<h3>{escape(line[4:].strip())}</h3>")
            i += 1
            continue

        # Markdown tables
        if line.startswith("|") and i + 1 < len(lines) and lines[i + 1].lstrip().startswith("|---"):
            header_cells = [c.strip() for c in line.strip("|").split("|")]
            i += 2  # skip header + separator
            rows: list[list[str]] = []
            while i < len(lines) and lines[i].startswith("|"):
                row_cells = [c.strip() for c in lines[i].strip("|").split("|")]
                rows.append(row_cells)
                i += 1

            body_parts.append("<table>")
            body_parts.append("<thead><tr>" + "".join(f"<th>{escape(c)}</th>" for c in header_cells) + "</tr></thead>")
            body_parts.append("<tbody>")
            for row in rows:
                body_parts.append("<tr>" + "".join(f"<td>{_render_inline_cell(c)}</td>" for c in row) + "</tr>")
            body_parts.append("</tbody></table>")
            continue

        # Bullet list
        if line.startswith("- "):
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append(lines[i][2:].strip())
                i += 1
            body_parts.append("<ul>" + "".join(f"<li>{_render_inline(escape(it))}</li>" for it in items) + "</ul>")
            continue

        # Paragraphs / blanks
        if not line.strip():
            i += 1
            continue

        body_parts.append(f"<p>{_render_inline(escape(line.strip()))}</p>")
        i += 1

    body = "\n".join(body_parts)
    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Code Periscope Risk Report</title>
  <style>
    :root {{
      --bg: #0b1020;
      --fg: #e8eef7;
      --muted: #a8b3cf;
      --panel: #121a33;
      --border: #233059;
      --accent: #7aa2ff;
    }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      background: var(--bg);
      color: var(--fg);
      line-height: 1.5;
    }}
    main {{
      max-width: 1100px;
      margin: 32px auto;
      padding: 0 20px 80px;
    }}
    h1, h2, h3 {{
      line-height: 1.2;
    }}
    h1 {{
      margin: 0 0 10px;
      font-size: 32px;
    }}
    h2 {{
      margin: 28px 0 10px;
      font-size: 22px;
      color: var(--accent);
    }}
    h3 {{
      margin: 18px 0 8px;
      font-size: 18px;
      color: var(--fg);
    }}
    p {{
      margin: 10px 0;
      color: var(--muted);
    }}
    code {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
      font-size: 0.95em;
      background: rgba(255,255,255,0.06);
      border: 1px solid rgba(255,255,255,0.10);
      padding: 2px 6px;
      border-radius: 6px;
      color: var(--fg);
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 10px 0 18px;
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 10px;
      overflow: hidden;
      display: block;
    }}
    thead {{
      background: rgba(255,255,255,0.03);
    }}
    th, td {{
      padding: 10px 12px;
      border-bottom: 1px solid rgba(255,255,255,0.06);
      vertical-align: top;
      text-align: left;
      white-space: nowrap;
    }}
    td {{
      white-space: normal;
      color: var(--muted);
    }}
    tr:last-child td {{
      border-bottom: none;
    }}
    .cell-wrap {{
      white-space: normal;
    }}
    td ul.cell-wrap {{
      margin: 0;
      padding-left: 18px;
    }}
    td ul.cell-wrap li {{
      margin: 2px 0;
    }}
    a {{
      color: var(--accent);
    }}
  </style>
</head>
<body>
  <main>
{body}
  </main>
</body>
</html>
"""


def _render_inline_cell(cell: str) -> str:
    # Cells may contain backtick-wrapped values from markdown renderer.
  raw = (cell or "").strip()

  # In Markdown, list-like fields are rendered as a single table cell joined
  # with "; ". For HTML, a bullet list reads better.
  parts = [p.strip() for p in raw.split(";") if p.strip()]
  if len(parts) >= 2:
    items = "".join(f"<li>{_render_inline(escape(p))}</li>" for p in parts)
    return f"<ul class=\"cell-wrap\">{items}</ul>"

  return f"<span class=\"cell-wrap\">{_render_inline(escape(raw))}</span>"


def _render_inline(text: str) -> str:
  """Render a tiny subset of Markdown inline formatting.

  Supported:
    - inline code: `foo` -> <code>foo</code>
    - bold: **foo** -> <strong>foo</strong>
  """

  # Handle inline code first (so we don't bold inside code spans).
  parts = text.split("`")
  chunks: list[str] = []
  for idx, part in enumerate(parts):
    if idx % 2 == 1:
      chunks.append(f"<code>{part}</code>")
    else:
      chunks.append(_render_bold(part))
  return "".join(chunks)


def _render_bold(text: str) -> str:
  if "**" not in text:
    return text
  parts = text.split("**")
  out: list[str] = []
  for idx, part in enumerate(parts):
    if idx % 2 == 1:
      out.append(f"<strong>{part}</strong>")
    else:
      out.append(part)
  return "".join(out)
