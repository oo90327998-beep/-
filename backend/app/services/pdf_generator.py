import io
from typing import Any, List

import fitz


def generate_resume_pdf(sections: List[dict]) -> bytes:
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    shape = page.new_shape()

    y = 50
    margin_left = 50
    page_width = 595 - 2 * margin_left

    for section in sections:
        name = section.get("name", "")
        content = section.get("content", "")

        if y > 780:
            page = doc.new_page(width=595, height=842)
            shape = page.new_shape()
            y = 50

        shape.insert_text(
            fitz.Point(margin_left, y + 12),
            name,
            fontname="hebo",
            fontsize=14,
        )
        y += 28

        lines = content.split("\n")
        for line in lines:
            if not line.strip():
                y += 8
                continue
            if y > 780:
                page = doc.new_page(width=595, height=842)
                shape = page.new_shape()
                y = 50
            shape.insert_text(
                fitz.Point(margin_left, y + 10),
                line.strip(),
                fontname="china-s",
                fontsize=10,
            )
            y += 16

        y += 16
        shape.commit()

    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    return buf.getvalue()
