from fpdf import FPDF
import os
from ali_integral.config import B0, SNR0

OUTPUT_DIR = "output"

class ScientificPaper(FPDF):
    def footer(self):
        self.set_y(-15)
        try:
            self.set_font('SciFont', '', 8)
        except Exception:
            self.set_font('Arial', '', 8)
        self.cell(0, 10, f'Page {self.page_no()} | Vision Theory V11 (EHT Edition)', 0, 0, 'C')

    def chapter_header(self, txt):
        self.ln(8)
        try:
            self.set_font('SciFont', '', 12)
        except Exception:
            self.set_font('Arial', 'B', 12)
        self.cell(0, 8, txt, 0, 1, 'L')
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)

    def body_text(self, txt):
        try:
            self.set_font('SciFont', '', 10)
        except Exception:
            self.set_font('Arial', '', 10)
        self.multi_cell(0, 5, txt)
        self.ln(2)

    def draw_param_table(self):
        self.ln(5)
        self.set_fill_color(240, 240, 240)
        self.set_font('SciFont', '', 10)
        self.cell(0, 8, "Table 1: Model Parameters", 0, 1, 'L', fill=True)
        data = [
            ("B0", f"{B0/1e9} GHz", "Base Detector Bandwidth"),
            ("SNR0", f"{SNR0}", "Initial Signal-to-Noise Ratio"),
            ("C_limit", "~10^17 ops/s", "Lloyd Bound (Thermal Limit)"),
            ("F_crit", "10^14 W/m^2", "Structural Crash Threshold"),
            ("Metric", "Kerr (Ideal)", "Spacetime Geometry")
        ]
        self.set_font('SciFont', '', 9)
        for name, val, desc in data:
            self.cell(25, 6, name, 1)
            self.cell(35, 6, val, 1)
            self.cell(130, 6, desc, 1)
            self.ln()
        self.ln(5)

def build_pdf(font_path):
    print("[INFO] Compiling PDF Paper (V11)...")
    pdf = ScientificPaper()
    pdf.add_page()
    pdf.add_font('SciFont', '', font_path, uni=True)

    # Title
    pdf.set_font('SciFont', '', 16)
    pdf.cell(0, 10, 'THE ALI INTEGRAL: OBSERVABLE FUTURE INFORMATION', 0, 1, 'C')
    pdf.set_font('SciFont', '', 12)
    pdf.cell(0, 8, 'Quantum-Information Analysis & EHT Predictions', 0, 1, 'C')
    pdf.set_font('SciFont', '', 10)
    pdf.cell(0, 8, 'Author: Ali | Version: 11.0 (EHT Ready)', 0, 1, 'C')
    pdf.ln(5)

    # Abstract
    pdf.set_fill_color(245, 245, 245)
    pdf.cell(0, 6, 'ABSTRACT', 0, 1, 'L')
    abs_txt = (
        "This paper presents the final formulation of 'Vision Theory', introducing the metric I_Ali (Total OFI). "
        "We further propose an observational signature for the Event Horizon Telescope (EHT). "
        "We designate this theoretical horizon deformation as 'Perturbation.A' — a localized bulge "
        "caused by accumulated information pressure at the Cauchy Horizon."
    )
    pdf.set_font('SciFont', '', 10)
    pdf.multi_cell(0, 5, abs_txt, fill=True)
    pdf.draw_param_table()

    # Sections
    pdf.chapter_header('1. Physical Model')
    pdf.body_text("We define capacity via the Shannon-Hartley theorem with dynamic gravitational SNR:")
    pdf.image(f"{OUTPUT_DIR}/eq_snr.png", x=60, w=80)
    
    pdf.chapter_header('2. Fundamental Limits')
    pdf.body_text("Processing speed is bounded by the Lloyd limit (Energy dependent):")
    pdf.image(f"{OUTPUT_DIR}/eq_lloyd.png", x=70, w=60)

    pdf.chapter_header('3. Information Horizon Results')
    pdf.body_text("Fig 1 shows the saturation of the information channel before thermal destruction.")
    pdf.image(f"{OUTPUT_DIR}/fig1_capacity.png", x=25, w=160)
    
    # --- НОВЫЙ РАЗДЕЛ EHT ---
    pdf.chapter_header('4. EHT Prediction: Perturbation.A')
    pdf.body_text(
        "Our model predicts that for ultramassive black holes (like TON 618), the integral I_Ali "
        "reaches values sufficient to exert backreaction pressure on the metric. "
        "This results in a specific deformation of the photon ring."
    )
    pdf.body_text(
        "We designate this theoretical deviation as Perturbation.A. As shown in Fig. 3, "
        "it manifests as a dynamic bulge in the shadow contour, detectable by next-gen EHT arrays."
    )
    # Вставка новой картинки
    if os.path.exists(f"{OUTPUT_DIR}/fig3_perturbation.png"):
        pdf.image(f"{OUTPUT_DIR}/fig3_perturbation.png", x=10, w=190)
    
    pdf.chapter_header('Conclusion')
    pdf.body_text("The I_Ali metric provides a bridge between Information Theory and Observation.")

    pdf.chapter_header('References')
    pdf.set_font('SciFont', '', 9)
    refs = ["1. Shannon, C. E. (1948).", "2. Lloyd, S. (2000).", "3. EHT Collaboration (2019)."]
    for r in refs:
        pdf.cell(0, 5, r, 0, 1)

    pdf.output(f"{OUTPUT_DIR}/Vision_Theory_Ali_V11.pdf")
    print("[SUCCESS] PDF Generated.")