"""
ReportLab Styles and Page Layout Configuration for HydroFed-ICAF Reports.
Provides medical-grade typography, standardized color palette, and dynamic two-pass page numbering.
"""

from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from datetime import datetime

# ==============================================================================
# 1. STANDARDIZED CLINICAL COLOR PALETTE
# ==============================================================================
COLOR_PRIMARY_NAVY   = HexColor("#173B65")  # Deep institutional navy
COLOR_SECONDARY_BLUE = HexColor("#2563EB")  # Clinical tech blue
COLOR_ACCENT_TEAL    = HexColor("#0D9488")  # Medical teal
COLOR_TEXT_MAIN      = HexColor("#1E293B")  # Slate 800 - dark readable text
COLOR_TEXT_MUTED     = HexColor("#64748B")  # Slate 500 - secondary text
COLOR_BG_LIGHT       = HexColor("#F8FAFC")  # Slate 50 - soft light gray
COLOR_BG_CARD        = HexColor("#FFFFFF")  # Pure white card background
COLOR_BORDER         = HexColor("#CBD5E1")  # Slate 300 - crisp table borders
COLOR_BORDER_LIGHT   = HexColor("#E2E8F0")  # Slate 200 - light divider borders

# Diagnostic Status Colors
COLOR_DANGER         = HexColor("#DC2626")  # Red 600 - Pneumonia / Critical
COLOR_DANGER_BG      = HexColor("#FEE2E2")  # Red 100 - Soft danger fill
COLOR_SUCCESS        = HexColor("#16A34A")  # Green 600 - Normal / Confirmed
COLOR_SUCCESS_BG     = HexColor("#DCFCE7")  # Green 100 - Soft success fill
COLOR_WARNING        = HexColor("#D97706")  # Amber 600 - Uncertainty / Review
COLOR_WARNING_BG     = HexColor("#FEF3C7")  # Amber 100 - Soft warning fill

# ==============================================================================
# 2. DYNAMIC TWO-PASS NUMBERED CANVAS (PAGE X OF Y & RUNNING HEADERS/FOOTERS)
# ==============================================================================
class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas that accumulates total page count and prints running
    headers, footers, confidentiality notices, and 'Page X of Y' on every page.
    """
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        
        # Geometry constants (A4 is 595.27 x 841.89 pt)
        page_width, page_height = 595.27, 841.89
        margin_left = 36  # 0.5 inch
        margin_right = page_width - 36
        
        # --- RUNNING HEADER (Only on page 2 and later) ---
        if self._pageNumber > 1:
            self.setFont("Helvetica-Bold", 7.5)
            self.setFillColor(COLOR_PRIMARY_NAVY)
            self.drawString(margin_left, page_height - 25, "HYDROFED-ICAF | CLINICAL DECISION SUPPORT REPORT")
            
            self.setFont("Helvetica", 7.5)
            self.setFillColor(COLOR_TEXT_MUTED)
            self.drawRightString(margin_right, page_height - 25, "CONFIDENTIAL MEDICAL RECORD")
            
            self.setStrokeColor(COLOR_BORDER_LIGHT)
            self.setLineWidth(0.5)
            self.line(margin_left, page_height - 28, margin_right, page_height - 28)

        # --- RUNNING FOOTER (On all pages) ---
        footer_y = 25
        self.setStrokeColor(COLOR_BORDER_LIGHT)
        self.setLineWidth(0.5)
        self.line(margin_left, footer_y + 12, margin_right, footer_y + 12)

        # Left footer: System identifier & Confidentiality notice
        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(COLOR_PRIMARY_NAVY)
        self.drawString(margin_left, footer_y, "HYDROFED-ICAF")
        
        self.setFont("Helvetica", 7.0)
        self.setFillColor(COLOR_TEXT_MUTED)
        self.drawString(margin_left + 78, footer_y, "|  Bio-Inspired Edge CDSS  |  Confidential Medical Record")

        # Right footer: Page X of Y
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(COLOR_PRIMARY_NAVY)
        self.drawRightString(margin_right, footer_y, page_str)
        
        self.restoreState()

# ==============================================================================
# 3. REPORTLAB PARAGRAPH STYLESHEET
# ==============================================================================
def get_clinical_report_styles():
    """Generates a comprehensive dictionary of clinical ReportLab ParagraphStyles."""
    styles = getSampleStyleSheet()
    
    # Document Main Header
    styles.add(ParagraphStyle(
        name='ClinicalDocTitle',
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=COLOR_PRIMARY_NAVY,
        alignment=TA_LEFT,
        spaceAfter=2
    ))
    
    styles.add(ParagraphStyle(
        name='ClinicalDocSubtitle',
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=COLOR_SECONDARY_BLUE,
        alignment=TA_LEFT,
        spaceAfter=4
    ))
    
    styles.add(ParagraphStyle(
        name='ClinicalHeaderMeta',
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=COLOR_TEXT_MAIN,
        alignment=TA_RIGHT
    ))
    
    styles.add(ParagraphStyle(
        name='ClinicalHeaderMetaBold',
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=10,
        textColor=COLOR_PRIMARY_NAVY,
        alignment=TA_RIGHT
    ))

    # Section Headers
    styles.add(ParagraphStyle(
        name='ClinicalSectionHeading',
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=COLOR_PRIMARY_NAVY,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    ))

    styles.add(ParagraphStyle(
        name='ClinicalSubsectionHeading',
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=COLOR_SECONDARY_BLUE,
        spaceBefore=4,
        spaceAfter=3,
        keepWithNext=True
    ))

    # Body Text & Cells
    styles.add(ParagraphStyle(
        name='ClinicalBody',
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=COLOR_TEXT_MAIN
    ))

    styles.add(ParagraphStyle(
        name='ClinicalBodyBold',
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10.5,
        textColor=COLOR_TEXT_MAIN
    ))

    styles.add(ParagraphStyle(
        name='ClinicalLabel',
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=COLOR_TEXT_MUTED
    ))

    styles.add(ParagraphStyle(
        name='ClinicalValue',
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=COLOR_TEXT_MAIN
    ))

    # Prediction Badges
    styles.add(ParagraphStyle(
        name='PredictionBadgePneumonia',
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=14,
        textColor=COLOR_DANGER,
        alignment=TA_CENTER
    ))

    styles.add(ParagraphStyle(
        name='PredictionBadgeNormal',
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=14,
        textColor=COLOR_SUCCESS,
        alignment=TA_CENTER
    ))

    styles.add(ParagraphStyle(
        name='MetricValueBig',
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=13,
        textColor=COLOR_PRIMARY_NAVY,
        alignment=TA_CENTER
    ))

    styles.add(ParagraphStyle(
        name='MetricLabelSmall',
        fontName='Helvetica',
        fontSize=7,
        leading=9,
        textColor=COLOR_TEXT_MUTED,
        alignment=TA_CENTER
    ))

    # Notes & Disclaimer Text
    styles.add(ParagraphStyle(
        name='ClinicalNoteText',
        fontName='Helvetica-Oblique',
        fontSize=7.5,
        leading=10,
        textColor=COLOR_TEXT_MAIN
    ))

    styles.add(ParagraphStyle(
        name='ClinicalXAINote',
        fontName='Helvetica-Oblique',
        fontSize=7.0,
        leading=9.0,
        textColor=COLOR_TEXT_MUTED,
        alignment=TA_JUSTIFY
    ))

    styles.add(ParagraphStyle(
        name='ClinicalDisclaimerText',
        fontName='Helvetica',
        fontSize=6.8,
        leading=8.8,
        textColor=COLOR_TEXT_MAIN,
        alignment=TA_JUSTIFY
    ))

    styles.add(ParagraphStyle(
        name='ClinicalDisclaimerHeading',
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=COLOR_PRIMARY_NAVY,
        alignment=TA_LEFT,
        spaceAfter=2
    ))

    return styles
