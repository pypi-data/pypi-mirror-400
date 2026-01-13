\
from __future__ import annotations

from pathlib import Path
import re

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted, ListFlowable, ListItem
from reportlab.lib.units import inch
from reportlab.lib import utils

from ..core import read_text


def cmd_md2pdf(args) -> int:
    inp = Path(args.input).resolve()
    out = Path(args.output).resolve()
    text = read_text(inp)

    story = markdown_to_story(text)
    doc = SimpleDocTemplate(str(out), pagesize=A4, leftMargin=0.9*inch, rightMargin=0.9*inch,
                            topMargin=0.9*inch, bottomMargin=0.9*inch)
    doc.build(story)
    print(f"[OK] wrote {out}")
    return 0


def markdown_to_story(md: str):
    """
    Very small Markdown subset:
    - #, ##, ### headings
    - paragraphs
    - fenced code blocks ```
    - unordered lists starting with '-', '*'
    """
    styles = getSampleStyleSheet()
    normal = styles["BodyText"]
    h1 = styles["Heading1"]
    h2 = styles["Heading2"]
    h3 = styles["Heading3"]
    code_style = styles["Code"]

    story = []

    lines = md.splitlines()
    i = 0
    in_code = False
    code_buf = []

    list_buf = []

    def flush_paragraph(buf):
        txt = "\n".join(buf).strip()
        if not txt:
            return
        # escape basic XML
        esc = (txt.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
        story.append(Paragraph(esc, normal))
        story.append(Spacer(1, 8))

    para_buf = []

    def flush_list():
        nonlocal list_buf
        if not list_buf:
            return
        items = []
        for it in list_buf:
            esc = (it.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
            items.append(ListItem(Paragraph(esc, normal)))
        story.append(ListFlowable(items, bulletType="bullet", leftIndent=18))
        story.append(Spacer(1, 8))
        list_buf = []

    while i < len(lines):
        line = lines[i]

        if line.strip().startswith("```"):
            if in_code:
                # closing
                in_code = False
                flush_list()
                flush_paragraph(para_buf)
                para_buf = []
                code_txt = "\n".join(code_buf)
                story.append(Preformatted(code_txt, code_style))
                story.append(Spacer(1, 10))
                code_buf = []
            else:
                # opening
                in_code = True
                flush_list()
                flush_paragraph(para_buf)
                para_buf = []
            i += 1
            continue

        if in_code:
            code_buf.append(line)
            i += 1
            continue

        # headings
        if line.startswith("# "):
            flush_list()
            flush_paragraph(para_buf); para_buf = []
            story.append(Paragraph(escape_xml(line[2:].strip()), h1))
            story.append(Spacer(1, 10))
            i += 1
            continue
        if line.startswith("## "):
            flush_list()
            flush_paragraph(para_buf); para_buf = []
            story.append(Paragraph(escape_xml(line[3:].strip()), h2))
            story.append(Spacer(1, 8))
            i += 1
            continue
        if line.startswith("### "):
            flush_list()
            flush_paragraph(para_buf); para_buf = []
            story.append(Paragraph(escape_xml(line[4:].strip()), h3))
            story.append(Spacer(1, 6))
            i += 1
            continue

        # lists
        m = re.match(r"^\s*([-*])\s+(.*)$", line)
        if m:
            flush_paragraph(para_buf); para_buf = []
            list_buf.append(m.group(2).strip())
            i += 1
            continue
        else:
            if list_buf and (not line.strip()):
                flush_list()
                i += 1
                continue

        # blank line = paragraph boundary
        if not line.strip():
            flush_list()
            flush_paragraph(para_buf)
            para_buf = []
            i += 1
            continue

        para_buf.append(line)
        i += 1

    # end
    if in_code and code_buf:
        story.append(Preformatted("\n".join(code_buf), code_style))
        story.append(Spacer(1, 10))

    flush_list()
    flush_paragraph(para_buf)

    return story


def escape_xml(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
