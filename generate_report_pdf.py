from pathlib import Path

from docx import Document as DocxDocument
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, PageBreak


DOCX_PATH = Path(r"E:\Dev Microsoft\ChatGPT\RadiologyAI\Clg\RadiologyAI_Final_Project_Report.docx")
PDF_PATH = Path(r"E:\Dev Microsoft\ChatGPT\RadiologyAI\Clg\RadiologyAI_Final_Project_Report.pdf")


def _clean(text: str) -> str:
    return (
        (text or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .strip()
    )


def build_pdf() -> None:
    source = DocxDocument(str(DOCX_PATH))
    styles = getSampleStyleSheet()

    normal = ParagraphStyle(
        "ReportNormal",
        parent=styles["BodyText"],
        fontName="Times-Roman",
        fontSize=12,
        leading=18,
        alignment=TA_JUSTIFY,
        spaceAfter=10,
    )
    heading1 = ParagraphStyle(
        "ReportHeading1",
        parent=styles["Heading1"],
        fontName="Times-Bold",
        fontSize=16,
        leading=22,
        alignment=TA_CENTER,
        spaceBefore=8,
        spaceAfter=12,
    )
    heading2 = ParagraphStyle(
        "ReportHeading2",
        parent=styles["Heading2"],
        fontName="Times-Bold",
        fontSize=14,
        leading=20,
        alignment=TA_LEFT,
        spaceBefore=8,
        spaceAfter=8,
    )
    centered = ParagraphStyle(
        "ReportCentered",
        parent=normal,
        alignment=TA_CENTER,
        spaceAfter=8,
    )

    story = []
    prev_blank = False

    for para in source.paragraphs:
        text = _clean(para.text)
        if not text:
            if not prev_blank:
                story.append(Spacer(1, 0.14 * inch))
            prev_blank = True
            continue

        prev_blank = False
        upper = text.upper()
        if upper.startswith("CHAPTER ") or text in {
            "Certificate",
            "Declaration",
            "Acknowledgement",
            "Abstract",
            "References",
            "Appendix",
            "TO WHOM IT MAY CONCERN",
        }:
            story.append(Paragraph(text, heading1))
            continue

        if (
            text[:3].count(".") >= 1
            and text[:1].isdigit()
            or upper in {"LIST OF FIGURES", "LIST OF TABLES", "LIST OF ABBREVIATIONS", "TABLE OF CONTENTS"}
        ):
            story.append(Paragraph(text, heading2))
            continue

        if len(text) < 90 and (
            upper == text
            or "Submitted by" in text
            or "Gujarat Technological University" in text
            or "Academic Year" in text
            or "DEV THAKAR" in text
            or "230673107042" in text
            or "SAL INSTITUTE" in text
            or "Ahmedabad" == text
            or "PROJECT REPORT" == upper
            or text in {"A", "in", "IN"}
        ):
            story.append(Paragraph(text, centered))
            continue

        story.append(Paragraph(text, normal))

    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=A4,
        leftMargin=1.25 * inch,
        rightMargin=1.0 * inch,
        topMargin=1.0 * inch,
        bottomMargin=1.0 * inch,
        title="Radiology AI Platform",
        author="Dev Thakar",
    )
    doc.build(story)


if __name__ == "__main__":
    build_pdf()
    print(f"Created: {PDF_PATH}")
