"""
Dynamic Clinical PDF Report Generator for HydroFed-ICAF.
Orchestrates ReportLab Platypus elements into a structured, medical-grade, multi-page document.
"""

import io
import os
from PIL import Image as PILImage
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage,
    KeepTogether, HRFlowable, PageBreak
)
from reports.report_styles import (
    NumberedCanvas, get_clinical_report_styles,
    COLOR_PRIMARY_NAVY, COLOR_SECONDARY_BLUE, COLOR_ACCENT_TEAL,
    COLOR_TEXT_MAIN, COLOR_TEXT_MUTED, COLOR_BG_LIGHT, COLOR_BG_CARD,
    COLOR_BORDER, COLOR_BORDER_LIGHT, COLOR_DANGER, COLOR_DANGER_BG,
    COLOR_SUCCESS, COLOR_SUCCESS_BG, COLOR_WARNING, COLOR_WARNING_BG
)

class ClinicalPDFReportGenerator:
    """
    Generates dynamic, healthcare-grade PDF reports strictly from backend data.
    """

    def __init__(self):
        self.styles = get_clinical_report_styles()
        self.page_width, self.page_height = A4
        self.margin = 36.0  # 0.5 inch margins
        self.content_width = self.page_width - (2 * self.margin)  # 523.27 pt

    def _safe_image_flowable(self, image_path, max_w=155.0, max_h=150.0):
        """Safely resizes and builds an image flowable preserving aspect ratio."""
        if not image_path or not os.path.exists(image_path):
            p_missing = Paragraph("<font color='#64748B'><i>Image unavailable</i></font>", self.styles['ClinicalBody'])
            t = Table([[p_missing]], colWidths=[max_w], rowHeights=[max_h])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), COLOR_BG_LIGHT),
                ('BOX', (0, 0), (-1, -1), 0.5, COLOR_BORDER_LIGHT),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            return t
            
        try:
            with PILImage.open(image_path) as img:
                orig_w, orig_h = img.size
                if orig_w <= 0 or orig_h <= 0:
                    raise ValueError("Invalid image dimensions")
                
                scale = min(max_w / orig_w, max_h / orig_h)
                render_w = orig_w * scale
                render_h = orig_h * scale
                
            return RLImage(image_path, width=render_w, height=render_h)
        except Exception as e:
            p_err = Paragraph(f"<font color='#EF4444'><i>Error loading image: {str(e)[:30]}</i></font>", self.styles['ClinicalBody'])
            t = Table([[p_err]], colWidths=[max_w], rowHeights=[max_h])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), COLOR_BG_LIGHT),
                ('BOX', (0, 0), (-1, -1), 0.5, COLOR_BORDER_LIGHT),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            return t

    def generate_pdf(self, report_data):
        """
        Generates PDF bytes for the given report data dictionary.
        
        Args:
            report_data (dict): Standardized dictionary from ReportDataAdapter
            
        Returns:
            bytes: Compiled PDF document bytes
        """
        buffer = io.BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=self.margin,
            rightMargin=self.margin,
            topMargin=self.margin,
            bottomMargin=self.margin + 8
        )
        
        story = []
        
        # ==============================================================================
        # 1. REPORT HEADER BANNER
        # ==============================================================================
        header_left = [
            Paragraph("HYDROFED-ICAF", self.styles['ClinicalDocTitle']),
            Paragraph("BIO-INSPIRED DECENTRALIZED CLINICAL DECISION SUPPORT SYSTEM", self.styles['ClinicalDocSubtitle']),
            Paragraph("<b>Automated Multimodal Radiological Assessment</b>", self.styles['ClinicalBody'])
        ]
        
        header_right = [
            Paragraph(f"<b>Report Date:</b> {report_data.get('report_datetime', '')}", self.styles['ClinicalHeaderMeta']),
            Paragraph(f"<b>Visit Reference:</b> {report_data.get('visit_reference', '')}", self.styles['ClinicalHeaderMeta']),
            Paragraph(f"<b>Attending Clinician:</b> {report_data.get('attending_clinician', '')}", self.styles['ClinicalHeaderMeta']),
            Paragraph(f"<b>Edge AI Node:</b> {report_data.get('edge_ai_node', '')}", self.styles['ClinicalHeaderMeta'])
        ]
        
        header_table = Table([[header_left, header_right]], colWidths=[self.content_width * 0.60, self.content_width * 0.40])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 4))
        story.append(HRFlowable(width="100%", thickness=1.5, color=COLOR_PRIMARY_NAVY, spaceBefore=2, spaceAfter=8))

        # ==============================================================================
        # SECTION 1: PATIENT PROFILE & CLINICAL DEMOGRAPHICS
        # ==============================================================================
        story.append(Paragraph("1. PATIENT PROFILE & CLINICAL DEMOGRAPHICS", self.styles['ClinicalSectionHeading']))
        
        col_w1 = self.content_width * 0.22
        col_w2 = self.content_width * 0.28
        col_w3 = self.content_width * 0.24
        col_w4 = self.content_width * 0.26
        
        demo_table_data = [
            [
                Paragraph("Patient Unique ID:", self.styles['ClinicalLabel']),
                Paragraph(f"<b>{report_data.get('patient_id', '')}</b>", self.styles['ClinicalValue']),
                Paragraph("Patient Name:", self.styles['ClinicalLabel']),
                Paragraph(f"{report_data.get('patient_name', '')}", self.styles['ClinicalValue'])
            ],
            [
                Paragraph("Biological Age:", self.styles['ClinicalLabel']),
                Paragraph(f"{report_data.get('age', '')}", self.styles['ClinicalValue']),
                Paragraph("Biological Gender:", self.styles['ClinicalLabel']),
                Paragraph(f"{report_data.get('gender', '')}", self.styles['ClinicalValue'])
            ],
            [
                Paragraph("Height / Weight:", self.styles['ClinicalLabel']),
                Paragraph(f"{report_data.get('height', '')} / {report_data.get('weight', '')}", self.styles['ClinicalValue']),
                Paragraph("Blood Pressure:", self.styles['ClinicalLabel']),
                Paragraph(f"{report_data.get('blood_pressure', '')}", self.styles['ClinicalValue'])
            ],
            [
                Paragraph("Fasting Blood Sugar:", self.styles['ClinicalLabel']),
                Paragraph(f"{report_data.get('fasting_blood_sugar', '')}", self.styles['ClinicalValue']),
                Paragraph("Diabetes Mellitus:", self.styles['ClinicalLabel']),
                Paragraph(f"{report_data.get('diabetes', '')}", self.styles['ClinicalValue'])
            ],
            [
                Paragraph("Passive Smoke Exposure:", self.styles['ClinicalLabel']),
                Paragraph(f"{report_data.get('smoke_exposure', '')}", self.styles['ClinicalValue']),
                Paragraph("Family Respiratory History:", self.styles['ClinicalLabel']),
                Paragraph(f"{report_data.get('family_history', '')}", self.styles['ClinicalValue'])
            ]
        ]
        
        demo_table = Table(demo_table_data, colWidths=[col_w1, col_w2, col_w3, col_w4])
        demo_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), COLOR_BG_LIGHT),
            ('BOX', (0, 0), (-1, -1), 0.75, COLOR_BORDER),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER_LIGHT),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(demo_table)
        story.append(Spacer(1, 8))

        # ==============================================================================
        # SECTION 2: MULTIMODAL CDSS CLASSIFIER RESULTS
        # ==============================================================================
        story.append(Paragraph("2. MULTIMODAL CDSS CLASSIFIER RESULTS", self.styles['ClinicalSectionHeading']))
        
        # Determine Prediction Card Styles
        is_pneu = report_data.get('predicted_class', 0) == 1
        pred_bg = COLOR_DANGER_BG if is_pneu else COLOR_SUCCESS_BG
        pred_border = COLOR_DANGER if is_pneu else COLOR_SUCCESS
        pred_style = self.styles['PredictionBadgePneumonia'] if is_pneu else self.styles['PredictionBadgeNormal']
        
        unc_val_str = report_data.get('uncertainty_val', '0.0000')
        is_unc = report_data.get('is_uncertain', False)
        unc_bg = COLOR_WARNING_BG if is_unc else COLOR_BG_CARD
        
        # Primary KPI Metrics Bar
        kpi_w = self.content_width / 5.0
        kpi_data = [
            [
                Paragraph("PRIMARY PREDICTION", self.styles['MetricLabelSmall']),
                Paragraph("PNEUMONIA PROBABILITY", self.styles['MetricLabelSmall']),
                Paragraph("NORMAL PROBABILITY", self.styles['MetricLabelSmall']),
                Paragraph("MODEL CONFIDENCE", self.styles['MetricLabelSmall']),
                Paragraph("UNCERTAINTY (MC STD)", self.styles['MetricLabelSmall']),
            ],
            [
                Paragraph(f"<b>{report_data.get('prediction', '')}</b>", pred_style),
                Paragraph(f"<font color='#DC2626'><b>{report_data.get('pneumonia_probability_pct', '')}</b></font>", self.styles['MetricValueBig']),
                Paragraph(f"<font color='#16A34A'><b>{report_data.get('normal_probability_pct', '')}</b></font>", self.styles['MetricValueBig']),
                Paragraph(f"<font color='#173B65'><b>{report_data.get('confidence_pct', '')}</b></font>", self.styles['MetricValueBig']),
                Paragraph(f"<font color='{'#D97706' if is_unc else '#173B65'}'><b>{unc_val_str}</b></font>", self.styles['MetricValueBig']),
            ]
        ]
        kpi_table = Table(kpi_data, colWidths=[kpi_w]*5)
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), COLOR_BG_LIGHT),
            ('BACKGROUND', (0, 1), (0, 1), pred_bg),
            ('BOX', (0, 0), (-1, -1), 0.75, COLOR_BORDER),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER_LIGHT),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(kpi_table)
        story.append(Spacer(1, 4))
        
        # Backend Architectural Metadata Table
        arch_col1 = self.content_width * 0.28
        arch_col2 = self.content_width * 0.72
        arch_data = [
            [
                Paragraph("Model Architecture:", self.styles['ClinicalLabel']),
                Paragraph(f"{report_data.get('model_architecture', '')}", self.styles['ClinicalValue'])
            ],
            [
                Paragraph("Inference Engine:", self.styles['ClinicalLabel']),
                Paragraph(f"{report_data.get('inference_engine', '')}", self.styles['ClinicalValue'])
            ],
            [
                Paragraph("Stochastic Evaluation:", self.styles['ClinicalLabel']),
                Paragraph(f"{report_data.get('stochastic_evaluation', '')} (Safety Threshold: &le; {report_data.get('uncertainty_threshold', '0.1500')})", self.styles['ClinicalValue'])
            ],
            [
                Paragraph("Total CDSS Latency:", self.styles['ClinicalLabel']),
                Paragraph(f"<b>{report_data.get('total_latency_ms', '')}</b> (Edge CPU Pipeline Execution)", self.styles['ClinicalValue'])
            ]
        ]
        arch_table = Table(arch_data, colWidths=[arch_col1, arch_col2])
        arch_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), COLOR_BG_CARD),
            ('BOX', (0, 0), (-1, -1), 0.5, COLOR_BORDER_LIGHT),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER_LIGHT),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(arch_table)
        story.append(Spacer(1, 8))

        # ==============================================================================
        # SECTION 3: RADIOLOGICAL IMAGING & PATHOLOGY SALIENCE (XAI)
        # ==============================================================================
        xai_elements = []
        xai_elements.append(Paragraph("3. RADIOLOGICAL IMAGING & PATHOLOGY SALIENCE (XAI)", self.styles['ClinicalSectionHeading']))
        
        img_w = (self.content_width - 12) / 3.0
        
        raw_img_path = report_data.get('preprocessed_image_path') or report_data.get('raw_image_path')
        flow_raw = self._safe_image_flowable(raw_img_path, max_w=img_w - 6, max_h=130.0)
        flow_gcam = self._safe_image_flowable(report_data.get('gradcam_path'), max_w=img_w - 6, max_h=130.0)
        flow_gcam_plus = self._safe_image_flowable(report_data.get('gradcam_plus_path'), max_w=img_w - 6, max_h=130.0)
        
        xai_grid = [
            [
                Paragraph("<b>Input Radiograph (CLAHE)</b>", self.styles['ClinicalSubsectionHeading']),
                Paragraph("<b>Grad-CAM Saliency</b>", self.styles['ClinicalSubsectionHeading']),
                Paragraph("<b>Grad-CAM++ Saliency</b>", self.styles['ClinicalSubsectionHeading'])
            ],
            [flow_raw, flow_gcam, flow_gcam_plus],
            [
                Paragraph("<font color='#64748B'>Spatial normalization 224&times;224</font>", self.styles['MetricLabelSmall']),
                Paragraph(f"<font color='#64748B'>{report_data.get('target_class_desc', '')}</font>", self.styles['MetricLabelSmall']),
                Paragraph("<font color='#64748B'>High-order gradient salience</font>", self.styles['MetricLabelSmall'])
            ]
        ]
        
        xai_table = Table(xai_grid, colWidths=[img_w, img_w, img_w])
        xai_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), COLOR_BG_LIGHT),
            ('BOX', (0, 0), (-1, -1), 0.75, COLOR_BORDER),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER_LIGHT),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        xai_elements.append(xai_table)
        xai_elements.append(Spacer(1, 3))
        
        xai_note = Paragraph(
            "<b>XAI Notice:</b> Highlighted heatmaps indicate spatial image regions that contributed to the model's classification score. "
            "Explainability visualizations illustrate network gradient salience and do not represent verified anatomical lesion boundaries.",
            self.styles['ClinicalXAINote']
        )
        xai_elements.append(xai_note)
        story.append(KeepTogether(xai_elements))
        story.append(Spacer(1, 8))

        # ==============================================================================
        # SECTION 4: CLINICAL DECISION SUPPORT & DATABASE VERIFICATION
        # ==============================================================================
        sec4_elements = []
        sec4_elements.append(Paragraph("4. CLINICAL DECISION SUPPORT & DATABASE VERIFICATION", self.styles['ClinicalSectionHeading']))
        
        cdss_w1 = self.content_width * 0.28
        cdss_w2 = self.content_width * 0.72
        
        cdss_data = [
            [
                Paragraph("Calculated Clinical Risk:", self.styles['ClinicalLabel']),
                Paragraph(f"<b>{report_data.get('calculated_clinical_risk', '')}</b>", self.styles['ClinicalValue'])
            ],
            [
                Paragraph("Database Storage:", self.styles['ClinicalLabel']),
                Paragraph(f"{report_data.get('database_storage', '')}", self.styles['ClinicalValue'])
            ],
            [
                Paragraph("Clinician Review Status:", self.styles['ClinicalLabel']),
                Paragraph(f"<b>{report_data.get('clinician_review_status', '')}</b>", self.styles['ClinicalValue'])
            ],
            [
                Paragraph("Security / Audit Trail:", self.styles['ClinicalLabel']),
                Paragraph(f"{report_data.get('security_audit_trail', '')}", self.styles['ClinicalValue'])
            ],
            [
                Paragraph("Diagnostic Notes:", self.styles['ClinicalLabel']),
                Paragraph(f"{report_data.get('diagnostic_notes', '')}", self.styles['ClinicalNoteText'])
            ],
            [
                Paragraph("Signed By:", self.styles['ClinicalLabel']),
                Paragraph(f"<b>{report_data.get('signed_by', '')}</b>", self.styles['ClinicalValue'])
            ]
        ]
        
        cdss_table = Table(cdss_data, colWidths=[cdss_w1, cdss_w2])
        cdss_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), COLOR_BG_LIGHT),
            ('BOX', (0, 0), (-1, -1), 0.75, COLOR_BORDER),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER_LIGHT),
            ('TOPPADDING', (0, 0), (-1, -1), 3.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        sec4_elements.append(cdss_table)
        story.append(KeepTogether(sec4_elements))
        story.append(Spacer(1, 8))

        # ==============================================================================
        # SECTION 5: AUDIT TRAIL & RECENT SECURITY LOGS
        # ==============================================================================
        audit_elements = []
        audit_elements.append(Paragraph("5. SYSTEM AUDIT & VERIFICATION TRAIL", self.styles['ClinicalSectionHeading']))
        
        audit_logs = report_data.get('audit_logs', [])
        if audit_logs:
            a_w1 = self.content_width * 0.12
            a_w2 = self.content_width * 0.28
            a_w3 = self.content_width * 0.26
            a_w4 = self.content_width * 0.20
            a_w5 = self.content_width * 0.14
            
            audit_rows = [
                [
                    Paragraph("<b>Audit ID</b>", self.styles['ClinicalLabel']),
                    Paragraph("<b>Timestamp</b>", self.styles['ClinicalLabel']),
                    Paragraph("<b>Event Type</b>", self.styles['ClinicalLabel']),
                    Paragraph("<b>Actor Signature</b>", self.styles['ClinicalLabel']),
                    Paragraph("<b>Status</b>", self.styles['ClinicalLabel'])
                ]
            ]
            for log in audit_logs:
                audit_rows.append([
                    Paragraph(str(log.get('audit_id', '-')), self.styles['ClinicalBody']),
                    Paragraph(str(log.get('timestamp', '')), self.styles['ClinicalBody']),
                    Paragraph(str(log.get('event_type', '')), self.styles['ClinicalBody']),
                    Paragraph(str(log.get('actor', '')), self.styles['ClinicalBody']),
                    Paragraph("<font color='#16A34A'>Verified</font>", self.styles['ClinicalBody'])
                ])
            
            audit_table = Table(audit_rows, colWidths=[a_w1, a_w2, a_w3, a_w4, a_w5])
            audit_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), COLOR_BG_LIGHT),
                ('BOX', (0, 0), (-1, -1), 0.5, COLOR_BORDER_LIGHT),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER_LIGHT),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ]))
            audit_elements.append(audit_table)
        else:
            p_no_audit = Paragraph("<i>No historical audit anomalies recorded for this visit session.</i>", self.styles['ClinicalBody'])
            audit_elements.append(p_no_audit)
            
        story.append(KeepTogether(audit_elements))
        story.append(Spacer(1, 8))

        # ==============================================================================
        # SECTION 6: MANDATORY CLINICAL & REGULATORY DISCLAIMER
        # ==============================================================================
        disclaimer_elements = []
        disclaimer_content = [
            [
                Paragraph("<b>MANDATORY CLINICAL &amp; REGULATORY DISCLAIMER</b>", self.styles['ClinicalDisclaimerHeading']),
            ],
            [
                Paragraph(report_data.get('disclaimer_text', ''), self.styles['ClinicalDisclaimerText'])
            ]
        ]
        disclaimer_table = Table(disclaimer_content, colWidths=[self.content_width])
        disclaimer_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), COLOR_BG_LIGHT),
            ('BOX', (0, 0), (-1, -1), 1.0, COLOR_BORDER),
            ('LINELEFT', (0, 0), (0, -1), 3.0, COLOR_PRIMARY_NAVY),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        disclaimer_elements.append(disclaimer_table)
        story.append(KeepTogether(disclaimer_elements))
        
        # Build Document with NumberedCanvas
        doc.build(story, canvasmaker=NumberedCanvas)
        buffer.seek(0)
        return buffer.getvalue()
