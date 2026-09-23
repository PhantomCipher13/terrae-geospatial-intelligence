#!/usr/bin/env python3
"""
TERRAE — Smart India Hackathon 2026 Master Final Presentation Rebuild
Strict Template + Visual-First + Diagram-Heavy (Lanezy Benchmark Architecture)

Visual Rules:
- Plain Light Background (#FFFFFF / #F8F7F3) throughout the deck
- Deep Navy display headings (#163D6B)
- 70% Visual / 30% Text balance (Diagrams, real satellite plates, short labels)
- Exact 6 Slides matching official SIH structure
- Clean top header: Team capsule (left), Centered Display Title, Official SIH 2026 logo (right)
- Bottom footer: Standardized SIH template attribution and slide numbering
- Authentic satellite assets + generated vector diagram elements
- Zero unsupported scientific claims; locked numbers: tau = 0.15, 135/135 tests passing
"""

import os
import sys
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# ---------------------------------------------------------------------------
# COLOR PALETTE (Light Theme / Defense Command Precision)
# ---------------------------------------------------------------------------
BG_WHITE = RGBColor(255, 255, 255)         # #FFFFFF Crisp White Canvas
BG_IVORY = RGBColor(248, 247, 243)         # #F8F7F3 Light Warm Ivory
CARD_BG = RGBColor(248, 250, 252)          # #F8FAFC Very Light Slate Card
CARD_BORDER = RGBColor(203, 213, 225)      # #CBD5E1 Clean Structural Border

NAVY_PRIMARY = RGBColor(22, 61, 107)       # #163D6B Primary Navy Heading
NAVY_DEEP = RGBColor(15, 23, 42)           # #0F172A Very Dark Navy
TEXT_DARK = RGBColor(30, 41, 59)           # #1E293B Charcoal Body
TEXT_MUTED = RGBColor(100, 116, 139)       # #64748B Slate Muted

ACCENT_GREEN = RGBColor(30, 126, 52)       # #1E7E34 Earth Green
ACCENT_GOLD = RGBColor(180, 83, 9)         # #B45309 Muted Gold / Amber
ACCENT_BLUE = RGBColor(37, 99, 235)        # #2563EB Clean Process Blue
ACCENT_TEAL = RGBColor(13, 148, 136)       # #0D9488 Muted Teal
ACCENT_AMBER = RGBColor(217, 119, 6)       # #D97706 Warning / Review Amber
ACCENT_RED = RGBColor(220, 38, 38)         # #DC2626 Abstain Red

FONT_TITLE = "Georgia"
FONT_HEADING = "Segoe UI"
FONT_BODY = "Segoe UI"
FONT_MONO = "Consolas"

# ---------------------------------------------------------------------------
# PROJECT METADATA
# ---------------------------------------------------------------------------
PROJECT_NAME = "TERRAE"
PROJECT_FULL = "TERRAE — Earth Intelligence Satellite Investigation Console"
TEAM_NAME = "Quantumcrew"
TEAM_ID = "[Registered Team ID / SIH2026]"
PS_ID = "SIH26227"
PS_TITLE = "SEMANTIC RETRIEVAL AND MULTI-TEMPORAL CHANGE ANALYSIS OF SATELLITE IMAGERY"
MINISTRY = "Ministry of Defence / Indian Army — DGIS"
THEME = "Space Technology"
CATEGORY = "Software"

URL_WEB = "https://terrae-geospatial-intelligence.vercel.app"
URL_REPO = "https://github.com/PhantomCipher13/terrae-geospatial-intelligence"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
ASSETS_DIR = os.path.join(REPO_ROOT, "assets")
DATA_ASSETS_DIR = os.path.join(REPO_ROOT, "geoai_workstation", "assets")


# ---------------------------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------------------------
def set_slide_background(slide, color=BG_WHITE):
    """Sets a solid plain light background on the slide."""
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def create_panel(slide, left, top, width, height, border_color=CARD_BORDER, bg_color=CARD_BG, border_width=Pt(1.0)):
    """Draws light structural container with crisp outline."""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    card.line.color.rgb = border_color
    card.line.width = border_width
    return card


def safe_add_image(slide, path, left, top, width, height):
    """Safely inserts image with fallback shape if missing."""
    search_paths = [
        path,
        os.path.join(ASSETS_DIR, os.path.basename(path)),
        os.path.join(REPO_ROOT, "data", "ui_assets", os.path.basename(path)),
        os.path.join(DATA_ASSETS_DIR, os.path.basename(path)),
        os.path.join(REPO_ROOT, "frontend", "public", "assets", os.path.basename(path)),
    ]
    for p in search_paths:
        if os.path.exists(p):
            return slide.shapes.add_picture(p, left, top, width, height)
    
    fallback = create_panel(slide, left, top, width, height, border_color=CARD_BORDER, bg_color=CARD_BG)
    tb = slide.shapes.add_textbox(left, top + height/2 - Inches(0.2), width, Inches(0.4))
    p = tb.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.text = f"[{os.path.basename(path)}]"
    p.font.name = FONT_MONO
    p.font.size = Pt(8.0)
    p.font.color.rgb = TEXT_MUTED
    return fallback


def add_lanezy_header(slide, slide_num, title_line1, title_line2=""):
    """
    Standardized Lanezy SIH competition header:
    - Top-Left: Team Capsule Badge (Quantumcrew)
    - Top-Center: Large Navy Serif Title
    - Top-Right: Official SIH 2026 Lightbulb Logo
    - Divider line
    """
    # 1. Top-Left Team Capsule Badge
    badge_x = Inches(0.80)
    badge_y = Inches(0.20)
    badge_w = Inches(2.60)
    badge_h = Inches(0.70)
    badge = create_panel(slide, badge_x, badge_y, badge_w, badge_h, border_color=CARD_BORDER, bg_color=BG_IVORY, border_width=Pt(1.2))
    
    tb_b = slide.shapes.add_textbox(badge_x, badge_y + Inches(0.08), badge_w, badge_h - Inches(0.16))
    tf_b = tb_b.text_frame
    tf_b.word_wrap = True
    tf_b.margin_left = tf_b.margin_top = tf_b.margin_right = tf_b.margin_bottom = 0
    p_b = tf_b.paragraphs[0]
    p_b.alignment = PP_ALIGN.CENTER
    r_b = p_b.add_run()
    r_b.text = f"Team: {TEAM_NAME}\n"
    r_b.font.name = FONT_HEADING
    r_b.font.size = Pt(9.5)
    r_b.font.bold = True
    r_b.font.color.rgb = NAVY_PRIMARY

    p_b2 = tf_b.add_paragraph()
    p_b2.alignment = PP_ALIGN.CENTER
    r_b2 = p_b2.add_run()
    r_b2.text = f"PS: {PS_ID} · {THEME}"
    r_b2.font.name = FONT_MONO
    r_b2.font.size = Pt(7.2)
    r_b2.font.color.rgb = TEXT_MUTED

    # 2. Top-Right Official SIH 2026 Logo
    sih_logo_path = os.path.join(ASSETS_DIR, "sih_logo_2026.png")
    safe_add_image(slide, sih_logo_path, Inches(10.80), Inches(0.16), Inches(1.75), Inches(0.78))

    # 3. Top-Center Large Navy Serif Title
    tb_title = slide.shapes.add_textbox(Inches(3.55), Inches(0.15), Inches(7.10), Inches(0.82))
    tf_title = tb_title.text_frame
    tf_title.word_wrap = True
    tf_title.margin_left = tf_title.margin_top = tf_title.margin_right = tf_title.margin_bottom = 0
    
    p1 = tf_title.paragraphs[0]
    p1.alignment = PP_ALIGN.CENTER
    r1 = p1.add_run()
    r1.text = title_line1.upper()
    r1.font.name = FONT_TITLE
    r1.font.size = Pt(17.0)
    r1.font.bold = True
    r1.font.color.rgb = NAVY_PRIMARY

    if title_line2:
        p2 = tf_title.add_paragraph()
        p2.alignment = PP_ALIGN.CENTER
        p2.space_before = Pt(2)
        r2 = p2.add_run()
        r2.text = title_line2
        r2.font.name = FONT_HEADING
        r2.font.size = Pt(8.8)
        r2.font.bold = False
        r2.font.color.rgb = TEXT_MUTED

    # 4. Subtle Top Divider Line
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.80), Inches(1.00), Inches(11.733), Inches(0.015))
    line.fill.solid()
    line.fill.fore_color.rgb = CARD_BORDER
    line.line.fill.background()

    # Add standard bottom footer
    add_lanezy_footer(slide, slide_num)


def add_lanezy_footer(slide, slide_num):
    """Draws standardized footer with project credentials and Lanezy-style slide numbering."""
    bot_y = Inches(7.08)
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.80), bot_y, Inches(11.733), Inches(0.015))
    line.fill.solid()
    line.fill.fore_color.rgb = CARD_BORDER
    line.line.fill.background()

    # Left / Center text: Template identity & project console
    tb_foot = slide.shapes.add_textbox(Inches(0.80), Inches(7.13), Inches(10.50), Inches(0.24))
    tf_f = tb_foot.text_frame
    tf_f.word_wrap = True
    tf_f.margin_left = tf_f.margin_top = tf_f.margin_right = tf_f.margin_bottom = 0
    p = tf_f.paragraphs[0]
    
    r1 = p.add_run()
    r1.text = "@SIH Idea submission- Template   |   "
    r1.font.name = FONT_BODY
    r1.font.size = Pt(7.5)
    r1.font.color.rgb = TEXT_MUTED

    r2 = p.add_run()
    r2.text = f"{PROJECT_NAME} — {PROJECT_FULL}   |   {MINISTRY}   |   "
    r2.font.name = FONT_BODY
    r2.font.size = Pt(7.5)
    r2.font.color.rgb = TEXT_MUTED

    r3 = p.add_run()
    r3.text = f"Console: {URL_WEB}"
    r3.font.name = FONT_BODY
    r3.font.size = Pt(7.5)
    r3.font.color.rgb = NAVY_PRIMARY
    r3.hyperlink.address = URL_WEB

    # Right text: Slide number (Large clean integer matching Lanezy)
    tb_num = slide.shapes.add_textbox(Inches(11.50), Inches(7.10), Inches(1.033), Inches(0.28))
    tf_n = tb_num.text_frame
    tf_n.word_wrap = True
    tf_n.margin_left = tf_n.margin_top = tf_n.margin_right = tf_n.margin_bottom = 0
    pn = tf_n.paragraphs[0]
    pn.alignment = PP_ALIGN.RIGHT
    rn = pn.add_run()
    rn.text = str(slide_num)
    rn.font.name = FONT_HEADING
    rn.font.size = Pt(11.0)
    rn.font.bold = True
    rn.font.color.rgb = NAVY_PRIMARY


# ---------------------------------------------------------------------------
# SLIDE 1: 01 — PROBLEM STATEMENT (Lanezy Opening Slide Format)
# ---------------------------------------------------------------------------
def build_slide_1(slide):
    set_slide_background(slide, BG_WHITE)
    add_lanezy_header(
        slide,
        1,
        "SMART INDIA HACKATHON 2026",
        "SEMANTIC RETRIEVAL AND MULTI-TEMPORAL CHANGE ANALYSIS OF SATELLITE IMAGERY"
    )

    left_x = Inches(0.80)
    left_w = Inches(4.80)

    # 1. Left Side: Official SIH Problem Statement Identification (Matching Lanezy Page 1)
    c_meta = create_panel(slide, left_x, Inches(1.20), left_w, Inches(3.60), border_color=CARD_BORDER, bg_color=CARD_BG)
    tb_m = slide.shapes.add_textbox(left_x + Inches(0.25), Inches(1.35), left_w - Inches(0.50), Inches(3.30))
    tf_m = tb_m.text_frame
    tf_m.word_wrap = True
    tf_m.margin_left = tf_m.margin_top = tf_m.margin_right = tf_m.margin_bottom = 0

    p_mh = tf_m.paragraphs[0]
    p_mh.text = "OFFICIAL PROBLEM STATEMENT METADATA"
    p_mh.font.name = FONT_MONO
    p_mh.font.size = Pt(8.5)
    p_mh.font.bold = True
    p_mh.font.color.rgb = NAVY_PRIMARY

    meta_items = [
        ("Problem Statement ID", f"{PS_ID}"),
        ("Problem Statement Title", f"{PS_TITLE}"),
        ("Ministry / Client", f"{MINISTRY}"),
        ("Theme", f"{THEME}"),
        ("PS Category", f"{CATEGORY}"),
        ("Team Name (Registered)", f"{TEAM_NAME}"),
        ("Team ID", f"{TEAM_ID}")
    ]
    for label, val in meta_items:
        p_it = tf_m.add_paragraph()
        p_it.space_before = Pt(4)
        r1 = p_it.add_run()
        r1.text = f"• {label} — "
        r1.font.name = FONT_HEADING
        r1.font.size = Pt(8.0)
        r1.font.bold = True
        r1.font.color.rgb = TEXT_DARK
        r2 = p_it.add_run()
        r2.text = val
        r2.font.name = FONT_BODY
        r2.font.size = Pt(8.0)
        r2.font.color.rgb = NAVY_PRIMARY if "SIH" in val or "Quantum" in val else TEXT_MUTED

    # 2. Left Side Lower: Operational Defense Mandate
    c_chal = create_panel(slide, left_x, Inches(4.95), left_w, Inches(1.95), border_color=CARD_BORDER, bg_color=BG_IVORY)
    tb_ch = slide.shapes.add_textbox(left_x + Inches(0.20), Inches(5.08), left_w - Inches(0.40), Inches(1.70))
    tf_ch = tb_ch.text_frame
    tf_ch.word_wrap = True
    tf_ch.margin_left = tf_ch.margin_top = tf_ch.margin_right = tf_ch.margin_bottom = 0
    p = tf_ch.paragraphs[0]
    p.text = "OPERATIONAL DEFENSE MANDATE"
    p.font.name = FONT_MONO
    p.font.size = Pt(8.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GOLD

    p_desc = tf_ch.add_paragraph()
    p_desc.space_before = Pt(4)
    r = p_desc.add_run()
    r.text = (
        "Defense intelligence analysts must discover relevant satellite scenes and verify whether "
        "detected changes represent real military activity or natural environmental phenology.\n\n"
        "• Real Analyst Intent: “Show me areas with newly built structures near a river corridor.”\n"
        "• Air-Gapped Mandate: Zero cloud APIs, remote telemetry, or network egress in operational enclaves."
    )
    r.font.name = FONT_BODY
    r.font.size = Pt(7.6)
    r.font.color.rgb = TEXT_DARK

    # 3. Right Side: One Large Authentic Satellite Plate + Simple Workflow Diagram (Lanezy Format)
    right_x = Inches(5.80)
    right_w = Inches(6.733)

    # Large Satellite Image (10m GSD Sentinel-2 Beirut Plate)
    img_h = Inches(3.30)
    img_path = os.path.join(ASSETS_DIR, "hero_beirut_1920x1080.jpg")
    safe_add_image(slide, img_path, right_x, Inches(1.20), right_w, img_h)

    # Image Caption Bar
    c_cap = create_panel(slide, right_x, Inches(4.55), right_w, Inches(0.30), border_color=CARD_BORDER, bg_color=BG_IVORY)
    tb_cap = slide.shapes.add_textbox(right_x + Inches(0.15), Inches(4.58), right_w - Inches(0.30), Inches(0.24))
    tf_cap = tb_cap.text_frame
    tf_cap.margin_left = tf_cap.margin_top = tf_cap.margin_right = tf_cap.margin_bottom = 0
    p_c = tf_cap.paragraphs[0]
    p_c.alignment = PP_ALIGN.CENTER
    r_cap = p_c.add_run()
    r_cap.text = "AUTHENTIC EARTH OBSERVATION: ESA Sentinel-2A Level-2A BOA Reflectance · 10m GSD · Maritime/Urban Basin"
    r_cap.font.name = FONT_MONO
    r_cap.font.size = Pt(7.0)
    r_cap.font.bold = True
    r_cap.font.color.rgb = NAVY_PRIMARY

    # Simple Horizontal Workflow Diagram (Status Quo Bottlenecks)
    flow_top = Inches(4.95)
    c_flow = create_panel(slide, right_x, flow_top, right_w, Inches(1.95), border_color=CARD_BORDER, bg_color=CARD_BG)

    tb_fh = slide.shapes.add_textbox(right_x + Inches(0.20), flow_top + Inches(0.10), right_w - Inches(0.40), Inches(0.22))
    tf_fh = tb_fh.text_frame
    tf_fh.margin_left = tf_fh.margin_top = tf_fh.margin_right = tf_fh.margin_bottom = 0
    p_fh = tf_fh.paragraphs[0]
    p_fh.text = "CURRENT ANALYST WORKFLOW (STATUS QUO BOTTLENECKS)"
    p_fh.font.name = FONT_MONO
    p_fh.font.size = Pt(8.0)
    p_fh.font.bold = True
    p_fh.font.color.rgb = ACCENT_GOLD

    steps = ["01\nMetadata", "02\nCoordinates", "03\nScene Search", "04\nComparison", "05\nInterpretation"]
    step_w = Inches(1.10)
    gap = Inches(0.18)
    start_x = right_x + Inches(0.20)
    for idx, st in enumerate(steps):
        sx = start_x + idx * (step_w + gap)
        c_st = create_panel(slide, sx, flow_top + Inches(0.38), step_w, Inches(0.55), border_color=CARD_BORDER, bg_color=BG_WHITE)
        tb_st = slide.shapes.add_textbox(sx, flow_top + Inches(0.42), step_w, Inches(0.48))
        tf_st = tb_st.text_frame
        tf_st.margin_left = tf_st.margin_top = tf_st.margin_right = tf_st.margin_bottom = 0
        p = tf_st.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        parts = st.split("\n")
        r_num = p.add_run()
        r_num.text = parts[0] + "\n"
        r_num.font.name = FONT_MONO
        r_num.font.size = Pt(7.0)
        r_num.font.bold = True
        r_num.font.color.rgb = ACCENT_GOLD
        r_txt = p.add_run()
        r_txt.text = parts[1]
        r_txt.font.name = FONT_HEADING
        r_txt.font.size = Pt(7.2)
        r_txt.font.bold = True
        r_txt.font.color.rgb = TEXT_DARK

        if idx < len(steps) - 1:
            tb_arr = slide.shapes.add_textbox(sx + step_w, flow_top + Inches(0.48), gap, Inches(0.30))
            tf_arr = tb_arr.text_frame
            tf_arr.margin_left = tf_arr.margin_top = tf_arr.margin_right = tf_arr.margin_bottom = 0
            p_a = tf_arr.paragraphs[0]
            p_a.alignment = PP_ALIGN.CENTER
            r_a = p_a.add_run()
            r_a.text = "➔"
            r_a.font.name = FONT_HEADING
            r_a.font.size = Pt(9.0)
            r_a.font.bold = True
            r_a.font.color.rgb = CARD_BORDER

    # Prominent Central Statement / Flaw Callout
    tb_stmt = slide.shapes.add_textbox(right_x + Inches(0.20), flow_top + Inches(1.02), right_w - Inches(0.40), Inches(0.85))
    tf_stmt = tb_stmt.text_frame
    tf_stmt.word_wrap = True
    tf_stmt.margin_left = tf_stmt.margin_top = tf_stmt.margin_right = tf_stmt.margin_bottom = 0
    p_q = tf_stmt.paragraphs[0]
    r_q = p_q.add_run()
    r_q.text = "“Finding a changed pixel is easy. Knowing whether it matters is harder.”\n"
    r_q.font.name = FONT_TITLE
    r_q.font.size = Pt(10.5)
    r_q.font.bold = True
    r_q.font.color.rgb = NAVY_PRIMARY

    p_fl = tf_stmt.add_paragraph()
    p_fl.space_before = Pt(2)
    r_fl = p_fl.add_run()
    r_fl.text = "CRITICAL DEFENSE FLAW: Naive pixel subtraction triggers severe false alarms from seasonal crop phenology, moisture, and sun angle."
    r_fl.font.name = FONT_HEADING
    r_fl.font.size = Pt(7.2)
    r_fl.font.bold = True
    r_fl.font.color.rgb = ACCENT_GOLD


# ---------------------------------------------------------------------------
# SLIDE 2: 02 — SOLUTION (Lanezy Solution Slide Format)
# ---------------------------------------------------------------------------
def build_slide_2(slide):
    set_slide_background(slide, BG_WHITE)
    add_lanezy_header(
        slide,
        2,
        "02 — SOLUTION",
        "FROM NATURAL-LANGUAGE QUERY TO EVIDENCE-BACKED INVESTIGATION"
    )

    # 1. Left Column: 3 Concise Explanatory Blocks + Prototype (Lanezy Page 2 Format)
    col1_x = Inches(0.80)
    col1_w = Inches(3.00)

    blocks = [
        ("THE ANALYST STARTS WITH INTENT", [
            "“Show me areas with newly built",
            "structures near a river corridor.”",
            "",
            "Analysts query with operational intent,",
            "not manual coordinate bounding boxes."
        ], ACCENT_GOLD),
        ("WHY IT IS HARD", [
            "A difference may come from:",
            "• crop vegetation growth & harvest",
            "• soil moisture & surface water",
            "• cloud shadow & atmospheric drift"
        ], ACCENT_RED),
        ("OUR RESPONSE", [
            "TERRAE combines:",
            "• semantic natural language retrieval",
            "• multi-temporal context (T0/TMID/T1)",
            "• spectral indices + 8-conn topology"
        ], ACCENT_GREEN)
    ]

    b_top = Inches(1.20)
    b_h = Inches(1.42)
    b_gap = Inches(0.12)
    for idx, (b_title, b_lines, b_col) in enumerate(blocks):
        by = b_top + idx * (b_h + b_gap)
        c_b = create_panel(slide, col1_x, by, col1_w, b_h, border_color=CARD_BORDER, bg_color=CARD_BG)
        tb = slide.shapes.add_textbox(col1_x + Inches(0.12), by + Inches(0.08), col1_w - Inches(0.24), b_h - Inches(0.16))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        p = tf.paragraphs[0]
        p.text = b_title
        p.font.name = FONT_MONO
        p.font.size = Pt(7.8)
        p.font.bold = True
        p.font.color.rgb = b_col

        for line in b_lines:
            p_l = tf.add_paragraph()
            p_l.space_before = Pt(1.5)
            r = p_l.add_run()
            r.text = line
            r.font.name = FONT_HEADING
            r.font.size = Pt(7.2)
            r.font.color.rgb = TEXT_DARK

    # Prototype Block at bottom left (matching Lanezy Page 2 Prototype: Video / Website)
    proto_top = b_top + 3 * (b_h + b_gap)
    proto_h = Inches(0.85)
    c_proto = create_panel(slide, col1_x, proto_top, col1_w, proto_h, border_color=CARD_BORDER, bg_color=BG_IVORY)
    tb_pr = slide.shapes.add_textbox(col1_x + Inches(0.12), proto_top + Inches(0.06), col1_w - Inches(0.24), proto_h - Inches(0.12))
    tf_pr = tb_pr.text_frame
    tf_pr.word_wrap = True
    tf_pr.margin_left = tf_pr.margin_top = tf_pr.margin_right = tf_pr.margin_bottom = 0
    p_pr = tf_pr.paragraphs[0]
    p_pr.text = "PROTOTYPE & ACCESS"
    p_pr.font.name = FONT_MONO
    p_pr.font.size = Pt(7.6)
    p_pr.font.bold = True
    p_pr.font.color.rgb = NAVY_PRIMARY

    p_pr2 = tf_pr.add_paragraph()
    p_pr2.space_before = Pt(2)
    r_pr2 = p_pr2.add_run()
    r_pr2.text = f"• Live Console: terrae-geospatial-intelligence.vercel.app\n• GitHub: PhantomCipher13/terrae-geospatial-intelligence\n• Report: REPORT.md (Full Scientific Dossier)"
    r_pr2.font.name = FONT_BODY
    r_pr2.font.size = Pt(6.5)
    r_pr2.font.color.rgb = TEXT_MUTED

    # 2. Center Column: Dominant 6-Stage Circular Investigation Diagram (Width = 5.2")
    col2_x = Inches(3.95)
    col2_w = Inches(5.30)
    col2_h = Inches(5.15)
    
    c_diag = create_panel(slide, col2_x, Inches(1.20), col2_w, col2_h, border_color=CARD_BORDER, bg_color=CARD_BG)

    # Diagram Header
    tb_dh = slide.shapes.add_textbox(col2_x + Inches(0.20), Inches(1.28), col2_w - Inches(0.40), Inches(0.26))
    tf_dh = tb_dh.text_frame
    tf_dh.margin_left = tf_dh.margin_top = tf_dh.margin_right = tf_dh.margin_bottom = 0
    p_dh = tf_dh.paragraphs[0]
    p_dh.alignment = PP_ALIGN.CENTER
    p_dh.text = "SIX-STAGE INVESTIGATION WORKFLOW"
    p_dh.font.name = FONT_MONO
    p_dh.font.size = Pt(8.8)
    p_dh.font.bold = True
    p_dh.font.color.rgb = NAVY_PRIMARY

    # Embedded Generated Vector Diagram Graphic (Clean Circular Loop)
    loop_img_path = os.path.join(ASSETS_DIR, "investigation_loop.jpg")
    img_size = Inches(3.10)
    img_lx = col2_x + (col2_w - img_size) / 2
    img_ly = Inches(2.35)
    safe_add_image(slide, loop_img_path, img_lx, img_ly, img_size, img_size)

    # Center Hub Badge
    hub_w = Inches(1.50)
    hub_h = Inches(0.70)
    hub_x = col2_x + (col2_w - hub_w) / 2
    hub_y = img_ly + (img_size - hub_h) / 2
    hub = create_panel(slide, hub_x, hub_y, hub_w, hub_h, border_color=NAVY_PRIMARY, bg_color=NAVY_PRIMARY)
    tb_hub = slide.shapes.add_textbox(hub_x, hub_y + Inches(0.08), hub_w, hub_h - Inches(0.16))
    tf_hub = tb_hub.text_frame
    tf_hub.word_wrap = True
    tf_hub.margin_left = tf_hub.margin_top = tf_hub.margin_right = tf_hub.margin_bottom = 0
    p_h = tf_hub.paragraphs[0]
    p_h.alignment = PP_ALIGN.CENTER
    r_h = p_h.add_run()
    r_h.text = "TERRAE\nINVESTIGATION"
    r_h.font.name = FONT_MONO
    r_h.font.size = Pt(7.5)
    r_h.font.bold = True
    r_h.font.color.rgb = BG_WHITE

    # 6 Editable Labels around the Circle
    stages = [
        ("01 ASK", "Natural Intent Query", col2_x + Inches(2.65), Inches(1.60), ACCENT_BLUE),
        ("02 DISCOVER", "RemoteCLIP + FAISS", col2_x + Inches(4.35), Inches(2.45), ACCENT_TEAL),
        ("03 COMPARE", "Calibrated Diff (τ=0.15)", col2_x + Inches(4.35), Inches(4.45), ACCENT_GREEN),
        ("04 EXPLAIN", "Spectral + Spatial Math", col2_x + Inches(2.65), Inches(5.50), ACCENT_GOLD),
        ("05 CHALLENGE", "3-Date Trajectory Check", col2_x + Inches(0.95), Inches(4.45), ACCENT_AMBER),
        ("06 DECIDE", "Conservative Verdict", col2_x + Inches(0.95), Inches(2.45), NAVY_PRIMARY)
    ]
    node_w = Inches(1.40)
    node_h = Inches(0.60)
    for st_num, st_desc, nx, ny, ncol in stages:
        c_n = create_panel(slide, nx - node_w/2, ny, node_w, node_h, border_color=ncol, bg_color=BG_WHITE, border_width=Pt(1.2))
        tb_n = slide.shapes.add_textbox(nx - node_w/2, ny + Inches(0.04), node_w, node_h - Inches(0.08))
        tf_n = tb_n.text_frame
        tf_n.word_wrap = True
        tf_n.margin_left = tf_n.margin_top = tf_n.margin_right = tf_n.margin_bottom = 0
        p1 = tf_n.paragraphs[0]
        p1.alignment = PP_ALIGN.CENTER
        r1 = p1.add_run()
        r1.text = f"{st_num}\n"
        r1.font.name = FONT_MONO
        r1.font.size = Pt(7.2)
        r1.font.bold = True
        r1.font.color.rgb = ncol

        p2 = tf_n.add_paragraph()
        p2.alignment = PP_ALIGN.CENTER
        r2 = p2.add_run()
        r2.text = st_desc
        r2.font.name = FONT_HEADING
        r2.font.size = Pt(6.5)
        r2.font.color.rgb = TEXT_DARK

    # 3. Right Column: Problem ↔ TERRAE Response (Matching Lanezy Risk vs Solution)
    col3_x = Inches(9.40)
    col3_w = Inches(3.133)

    tb_rh = slide.shapes.add_textbox(col3_x, Inches(1.20), col3_w, Inches(0.26))
    tf_rh = tb_rh.text_frame
    tf_rh.margin_left = tf_rh.margin_top = tf_rh.margin_right = tf_rh.margin_bottom = 0
    p_rh = tf_rh.paragraphs[0]
    p_rh.text = "ANALYST PROBLEM ➔ TERRAE RESPONSE"
    p_rh.font.name = FONT_MONO
    p_rh.font.size = Pt(8.0)
    p_rh.font.bold = True
    p_rh.font.color.rgb = NAVY_PRIMARY

    comparisons = [
        ("MANUAL SEARCH", "SEMANTIC RETRIEVAL", "RemoteCLIP embeddings query 50+ satellite tiles across archives", ACCENT_BLUE),
        ("SINGLE BEFORE/AFTER", "MULTI-TEMPORAL CONTEXT", "T0 / TMID / T1 triplet stack suppresses seasonal phenology", ACCENT_TEAL),
        ("PIXEL DIFFERENCE", "SPECTRAL + SPATIAL", "NDVI & NDWI indices combined with 8-conn spatial clusters", ACCENT_GREEN),
        ("OPAQUE RESULT", "EVIDENCE CHAIN", "Auditable spatial coherence, trajectory, and pixel breakdown", ACCENT_GOLD),
        ("FORCED DECISION", "SUPPORTED / REVIEW", "Conservative decision rules; abstain routing on low confidence", NAVY_PRIMARY)
    ]
    cb_top = Inches(1.50)
    cb_h = Inches(0.68)
    cb_gap = Inches(0.08)
    for idx, (p_txt, r_txt, desc_txt, col_acc) in enumerate(comparisons):
        cy = cb_top + idx * (cb_h + cb_gap)
        c_cmp = create_panel(slide, col3_x, cy, col3_w, cb_h, border_color=CARD_BORDER, bg_color=CARD_BG)
        tb_c = slide.shapes.add_textbox(col3_x + Inches(0.10), cy + Inches(0.05), col3_w - Inches(0.20), cb_h - Inches(0.10))
        tf_c = tb_c.text_frame
        tf_c.word_wrap = True
        tf_c.margin_left = tf_c.margin_top = tf_c.margin_right = tf_c.margin_bottom = 0

        p = tf_c.paragraphs[0]
        r1 = p.add_run()
        r1.text = f"{p_txt} "
        r1.font.name = FONT_MONO
        r1.font.size = Pt(6.6)
        r1.font.bold = True
        r1.font.color.rgb = TEXT_MUTED

        r2 = p.add_run()
        r2.text = "➔ "
        r2.font.name = FONT_HEADING
        r2.font.size = Pt(7.0)
        r2.font.bold = True
        r2.font.color.rgb = col_acc

        r3 = p.add_run()
        r3.text = f"{r_txt}"
        r3.font.name = FONT_MONO
        r3.font.size = Pt(6.8)
        r3.font.bold = True
        r3.font.color.rgb = col_acc

        p_desc = tf_c.add_paragraph()
        p_desc.space_before = Pt(1.5)
        r4 = p_desc.add_run()
        r4.text = desc_txt
        r4.font.name = FONT_BODY
        r4.font.size = Pt(6.2)
        r4.font.color.rgb = TEXT_DARK

    # Workstation Telemetry Block (Controlled Benchmark Case 01)
    t_box_top = Inches(5.35)
    c_ws = create_panel(slide, col3_x, t_box_top, col3_w, Inches(1.00), border_color=CARD_BORDER, bg_color=BG_IVORY)
    tb_ws = slide.shapes.add_textbox(col3_x + Inches(0.12), t_box_top + Inches(0.08), col3_w - Inches(0.24), Inches(0.84))
    tf_ws = tb_ws.text_frame
    tf_ws.word_wrap = True
    tf_ws.margin_left = tf_ws.margin_top = tf_ws.margin_right = tf_ws.margin_bottom = 0
    p_w = tf_ws.paragraphs[0]
    p_w.text = "CONTROLLED SYNTHETIC TEMPORAL BENCHMARK (CASE 01):"
    p_w.font.name = FONT_MONO
    p_w.font.size = Pt(6.8)
    p_w.font.bold = True
    p_w.font.color.rgb = ACCENT_GREEN

    p_w2 = tf_ws.add_paragraph()
    r = p_w2.add_run()
    r.text = (
        "• 7,549 px Changed (11.5%)  |  Spatial Coherence: 99.7%\n"
        "• Built Surface Support: 97.1%  |  Trajectory: LATE_ONSET_CHANGE\n"
        "• System Verdict: ✔ SUPPORTED (High Spatial Coherence)"
    )
    r.font.name = FONT_BODY
    r.font.size = Pt(6.6)
    r.font.color.rgb = TEXT_DARK

    # Bottom Closing Statement & Access Banner
    bot_y = Inches(6.45)
    c_bot = create_panel(slide, Inches(0.80), bot_y, Inches(11.733), Inches(0.55), border_color=CARD_BORDER, bg_color=BG_IVORY)
    tb_bot = slide.shapes.add_textbox(Inches(0.90), bot_y + Inches(0.06), Inches(11.533), Inches(0.42))
    tf_bot = tb_bot.text_frame
    tf_bot.word_wrap = True
    tf_bot.margin_left = tf_bot.margin_top = tf_bot.margin_right = tf_bot.margin_bottom = 0

    p_b1 = tf_bot.paragraphs[0]
    p_b1.alignment = PP_ALIGN.CENTER
    r_b1 = p_b1.add_run()
    r_b1.text = "“NOT JUST CHANGE DETECTION. INVESTIGATION.”"
    r_b1.font.name = FONT_TITLE
    r_b1.font.size = Pt(10.5)
    r_b1.font.bold = True
    r_b1.font.color.rgb = NAVY_PRIMARY

    p_b2 = tf_bot.add_paragraph()
    p_b2.alignment = PP_ALIGN.CENTER
    r_b2 = p_b2.add_run()
    r_b2.text = f"Live Console: {URL_WEB}   |   GitHub: {URL_REPO}   |   Scientific Report: REPORT.md"
    r_b2.font.name = FONT_MONO
    r_b2.font.size = Pt(7.0)
    r_b2.font.color.rgb = TEXT_MUTED


# ---------------------------------------------------------------------------
# SLIDE 3: 03 — TECHNICAL APPROACH (Lanezy Technical Approach Slide Format)
# ---------------------------------------------------------------------------
def build_slide_3(slide):
    set_slide_background(slide, BG_WHITE)
    add_lanezy_header(
        slide,
        3,
        "03 — TECHNICAL APPROACH",
        "SYSTEM ARCHITECTURE & MULTI-STREAM EVIDENCE PIPELINE"
    )

    # 1. Left Column: Methodology & Process of Implementation (Lanezy Circular Loop Format)
    col1_x = Inches(0.80)
    col1_w = Inches(3.00)
    col1_h = Inches(5.75)

    c_meth = create_panel(slide, col1_x, Inches(1.20), col1_w, col1_h, border_color=CARD_BORDER, bg_color=CARD_BG)
    tb_mh = slide.shapes.add_textbox(col1_x + Inches(0.15), Inches(1.30), col1_w - Inches(0.30), Inches(0.35))
    tf_mh = tb_mh.text_frame
    tf_mh.margin_left = tf_mh.margin_top = tf_mh.margin_right = tf_mh.margin_bottom = 0
    p_mh = tf_mh.paragraphs[0]
    p_mh.text = "METHODOLOGY & PROCESS\nOF IMPLEMENTATION"
    p_mh.font.name = FONT_MONO
    p_mh.font.size = Pt(8.0)
    p_mh.font.bold = True
    p_mh.font.color.rgb = NAVY_PRIMARY

    loop_stages = [
        ("ASK", "Natural Language Query", "Parses operational intent", ACCENT_BLUE),
        ("DISCOVER", "RemoteCLIP + FAISS", "512-dim joint cosine retrieval", ACCENT_TEAL),
        ("COMPARE", "T0 / TMID / T1", "Multi-band spectral shift (τ=0.15)", ACCENT_GREEN),
        ("EXPLAIN", "Spectral + Spatial", "NDVI, NDWI & 8-conn topology", ACCENT_GOLD),
        ("CHALLENGE", "Temporal Evidence", "MECE trajectory persistence", ACCENT_AMBER),
        ("DECIDE", "Conservative Verdict", "Auditable verdict & abstain mode", NAVY_PRIMARY)
    ]

    card_top = Inches(1.75)
    card_h = Inches(0.68)
    card_gap = Inches(0.08)
    for idx, (st_name, st_tech, st_desc, st_col) in enumerate(loop_stages):
        cy = card_top + idx * (card_h + card_gap)
        c_st = create_panel(slide, col1_x + Inches(0.12), cy, col1_w - Inches(0.24), card_h, border_color=st_col, bg_color=BG_WHITE, border_width=Pt(1.2))
        tb_st = slide.shapes.add_textbox(col1_x + Inches(0.20), cy + Inches(0.06), col1_w - Inches(0.40), card_h - Inches(0.12))
        tf_st = tb_st.text_frame
        tf_st.word_wrap = True
        tf_st.margin_left = tf_st.margin_top = tf_st.margin_right = tf_st.margin_bottom = 0
        
        p = tf_st.paragraphs[0]
        r1 = p.add_run()
        r1.text = f"{st_name} · "
        r1.font.name = FONT_MONO
        r1.font.size = Pt(7.2)
        r1.font.bold = True
        r1.font.color.rgb = st_col

        r2 = p.add_run()
        r2.text = st_tech
        r2.font.name = FONT_HEADING
        r2.font.size = Pt(7.0)
        r2.font.bold = True
        r2.font.color.rgb = TEXT_DARK

        p_desc = tf_st.add_paragraph()
        p_desc.space_before = Pt(2)
        r3 = p_desc.add_run()
        r3.text = st_desc
        r3.font.name = FONT_BODY
        r3.font.size = Pt(6.5)
        r3.font.color.rgb = TEXT_MUTED

    # Bottom left: Detailed Report Link block (Lanezy Slide 3 Format)
    tb_rep = slide.shapes.add_textbox(col1_x + Inches(0.15), Inches(6.38), col1_w - Inches(0.30), Inches(0.50))
    tf_rep = tb_rep.text_frame
    tf_rep.word_wrap = True
    tf_rep.margin_left = tf_rep.margin_top = tf_rep.margin_right = tf_rep.margin_bottom = 0
    p_r = tf_rep.paragraphs[0]
    p_r.text = "DETAILED TECHNICAL DOSSIER:"
    p_r.font.name = FONT_MONO
    p_r.font.size = Pt(7.0)
    p_r.font.bold = True
    p_r.font.color.rgb = NAVY_PRIMARY
    p_r2 = tf_rep.add_paragraph()
    r = p_r2.add_run()
    r.text = "• REPORT.md: 6-part scientific report\n• GitHub: Complete reproducible tests"
    r.font.name = FONT_BODY
    r.font.size = Pt(6.5)
    r.font.color.rgb = TEXT_MUTED

    # 2. Center Column: Dual System Pipelines (Top: Retrieval, Bottom: Evidence)
    col2_x = Inches(3.95)
    col2_w = Inches(5.30)
    col2_h = Inches(5.75)

    c_center = create_panel(slide, col2_x, Inches(1.20), col2_w, col2_h, border_color=CARD_BORDER, bg_color=CARD_BG)

    # Center Top: SEMANTIC SATELLITE RETRIEVAL PIPELINE
    tb_p1 = slide.shapes.add_textbox(col2_x + Inches(0.18), Inches(1.30), col2_w - Inches(0.36), Inches(0.24))
    tf_p1 = tb_p1.text_frame
    tf_p1.margin_left = tf_p1.margin_top = tf_p1.margin_right = tf_p1.margin_bottom = 0
    p1 = tf_p1.paragraphs[0]
    p1.text = "SEMANTIC SATELLITE RETRIEVAL PIPELINE"
    p1.font.name = FONT_MONO
    p1.font.size = Pt(8.2)
    p1.font.bold = True
    p1.font.color.rgb = NAVY_PRIMARY

    # Embedded Retrieval Vector Diagram Graphic + Flow Text
    ret_img_path = os.path.join(ASSETS_DIR, "retrieval_pipeline.jpg")
    safe_add_image(slide, ret_img_path, col2_x + Inches(0.20), Inches(1.60), Inches(1.30), Inches(1.30))

    # Text Steps for Retrieval
    ret_steps = [
        ("NATURAL QUERY", "“new construction & buildings”", ACCENT_BLUE),
        ("REMOTECLIP ViT-B-32", "512-dim joint vision-language embedding", ACCENT_TEAL),
        ("FAISS FlatIP", "Nearest satellite tile cosine scan (2.0 ms)", ACCENT_BLUE),
        ("SATELLITE TILE", "MGRS 43RGM / EPSG:32643 10m UTM Grid", ACCENT_GREEN)
    ]
    for i, (sn, sd, sc) in enumerate(ret_steps):
        ry = Inches(1.60) + i * Inches(0.33)
        c_r = create_panel(slide, col2_x + Inches(1.60), ry, col2_w - Inches(1.78), Inches(0.28), border_color=CARD_BORDER, bg_color=BG_WHITE)
        tb_r = slide.shapes.add_textbox(col2_x + Inches(1.68), ry + Inches(0.04), col2_w - Inches(1.94), Inches(0.20))
        tf_r = tb_r.text_frame
        tf_r.margin_left = tf_r.margin_top = tf_r.margin_right = tf_r.margin_bottom = 0
        pr = tf_r.paragraphs[0]
        r_sn = pr.add_run()
        r_sn.text = f"{sn} ➔ "
        r_sn.font.name = FONT_MONO
        r_sn.font.size = Pt(6.8)
        r_sn.font.bold = True
        r_sn.font.color.rgb = sc
        r_sd = pr.add_run()
        r_sd.text = sd
        r_sd.font.name = FONT_BODY
        r_sd.font.size = Pt(6.8)
        r_sd.font.color.rgb = TEXT_DARK

    # Center Divider
    c_mid = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, col2_x + Inches(0.20), Inches(3.02), col2_w - Inches(0.40), Inches(0.015))
    c_mid.fill.solid()
    c_mid.fill.fore_color.rgb = CARD_BORDER
    c_mid.line.fill.background()

    # Center Bottom: MULTI-TEMPORAL EVIDENCE PIPELINE
    tb_p2 = slide.shapes.add_textbox(col2_x + Inches(0.18), Inches(3.12), col2_w - Inches(0.36), Inches(0.24))
    tf_p2 = tb_p2.text_frame
    tf_p2.margin_left = tf_p2.margin_top = tf_p2.margin_right = tf_p2.margin_bottom = 0
    p2 = tf_p2.paragraphs[0]
    p2.text = "MULTI-TEMPORAL EVIDENCE PIPELINE"
    p2.font.name = FONT_MONO
    p2.font.size = Pt(8.2)
    p2.font.bold = True
    p2.font.color.rgb = NAVY_PRIMARY

    # Three Real Satellite Images (T0, TMID, T1)
    dates = [
        ("T0 · 19 MAY 2023", "sentinel2_t0_rgb.jpg"),
        ("TMID · 06 OCT 2023", "sentinel2_tmid_rgb.jpg"),
        ("T1 · 05 DEC 2023", "sentinel2_t1_rgb.jpg")
    ]
    sub_w = Inches(1.50)
    sub_h = Inches(1.10)
    sub_gap = Inches(0.25)
    for idx, (dt_lbl, fn) in enumerate(dates):
        img_x = col2_x + Inches(0.20) + idx * (sub_w + sub_gap)
        safe_add_image(slide, os.path.join(ASSETS_DIR, fn), img_x, Inches(3.40), sub_w, sub_h)
        
        # Caption below image
        c_lbl = create_panel(slide, img_x, Inches(4.55), sub_w, Inches(0.22), border_color=CARD_BORDER, bg_color=BG_IVORY)
        tb_lbl = slide.shapes.add_textbox(img_x, Inches(4.57), sub_w, Inches(0.18))
        tf_lbl = tb_lbl.text_frame
        tf_lbl.margin_left = tf_lbl.margin_top = tf_lbl.margin_right = tf_lbl.margin_bottom = 0
        p_l = tf_lbl.paragraphs[0]
        p_l.alignment = PP_ALIGN.CENTER
        r = p_l.add_run()
        r.text = dt_lbl
        r.font.name = FONT_MONO
        r.font.size = Pt(6.0)
        r.font.bold = True
        r.font.color.rgb = NAVY_PRIMARY

        # Arrow between images
        if idx < 2:
            arr_x = img_x + sub_w + Inches(0.04)
            tb_arr = slide.shapes.add_textbox(arr_x, Inches(3.85), sub_gap - Inches(0.08), Inches(0.30))
            tf_arr = tb_arr.text_frame
            tf_arr.margin_left = tf_arr.margin_top = tf_arr.margin_right = tf_arr.margin_bottom = 0
            pa = tf_arr.paragraphs[0]
            pa.alignment = PP_ALIGN.CENTER
            ra = pa.add_run()
            ra.text = "➔"
            ra.font.name = FONT_HEADING
            ra.font.size = Pt(11)
            ra.font.bold = True
            ra.font.color.rgb = CARD_BORDER

    # Evidence Chain Steps (Spectral -> Spatial -> Attribution -> Trajectory -> Decision)
    # Embedded Evidence Chain Vector Graphic
    ev_img_path = os.path.join(ASSETS_DIR, "evidence_chain.jpg")
    safe_add_image(slide, ev_img_path, col2_x + Inches(0.20), Inches(4.88), Inches(4.90), Inches(0.95))

    ev_sub = slide.shapes.add_textbox(col2_x + Inches(0.20), Inches(5.88), Inches(4.90), Inches(0.95))
    tf_ev = ev_sub.text_frame
    tf_ev.margin_left = tf_ev.margin_top = tf_ev.margin_right = tf_ev.margin_bottom = 0
    p_ev = tf_ev.paragraphs[0]
    p_ev.alignment = PP_ALIGN.CENTER
    r_ev = p_ev.add_run()
    r_ev.text = "SPECTRAL SHIFT (τ=0.15) ➔ 8-CONN SPATIAL TOPOLOGY ➔ ATTRIBUTION SUPPORT ➔ MECE TRAJECTORY ➔ VERDICT"
    r_ev.font.name = FONT_MONO
    r_ev.font.size = Pt(6.2)
    r_ev.font.bold = True
    r_ev.font.color.rgb = NAVY_PRIMARY

    # 3. Right Column: Technologies Used (Lanezy Slide 3 Format)
    col3_x = Inches(9.40)
    col3_w = Inches(3.133)
    col3_h = Inches(5.75)

    c_tech = create_panel(slide, col3_x, Inches(1.20), col3_w, col3_h, border_color=CARD_BORDER, bg_color=CARD_BG)
    tb_th = slide.shapes.add_textbox(col3_x + Inches(0.18), Inches(1.30), col3_w - Inches(0.36), Inches(0.30))
    tf_th = tb_th.text_frame
    tf_th.margin_left = tf_th.margin_top = tf_th.margin_right = tf_th.margin_bottom = 0
    p_th = tf_th.paragraphs[0]
    p_th.text = "TECHNOLOGIES USED"
    p_th.font.name = FONT_MONO
    p_th.font.size = Pt(8.5)
    p_th.font.bold = True
    p_th.font.color.rgb = NAVY_PRIMARY

    tech_bands = [
        ("SEMANTIC RETRIEVAL", "RemoteCLIP + FAISS", "Vision-language cross-modal embeddings + CPU vector indexing", ACCENT_BLUE),
        ("GEOSPATIAL", "Rasterio + NumPy + SciPy", "GDAL bindings, surface reflectance math, 8-conn spatial topology", ACCENT_TEAL),
        ("TEMPORAL / VALIDATION", "Sentinel-2 + OSCD + SQLite", "10m BOA reflectance, MGRS grid, MECE trajectory classifier", ACCENT_GOLD),
        ("OFFLINE-FIRST", "Python + Streamlit + Local Models", "Air-gapped operation with zero external runtime calls", NAVY_PRIMARY)
    ]

    t_top = Inches(1.75)
    t_h = Inches(1.10)
    t_gap = Inches(0.14)
    for idx, (t_cat, t_name, t_desc, t_col) in enumerate(tech_bands):
        ty = t_top + idx * (t_h + t_gap)
        c_tb = create_panel(slide, col3_x + Inches(0.12), ty, col3_w - Inches(0.24), t_h, border_color=CARD_BORDER, bg_color=BG_WHITE)
        tb = slide.shapes.add_textbox(col3_x + Inches(0.22), ty + Inches(0.10), col3_w - Inches(0.44), t_h - Inches(0.20))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        p = tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = f"{t_cat}\n"
        r1.font.name = FONT_MONO
        r1.font.size = Pt(7.0)
        r1.font.bold = True
        r1.font.color.rgb = t_col

        p_name = tf.add_paragraph()
        p_name.space_before = Pt(2)
        r2 = p_name.add_run()
        r2.text = f"{t_name}\n"
        r2.font.name = FONT_HEADING
        r2.font.size = Pt(8.5)
        r2.font.bold = True
        r2.font.color.rgb = TEXT_DARK

        p_desc = tf.add_paragraph()
        p_desc.space_before = Pt(2)
        r3 = p_desc.add_run()
        r3.text = t_desc
        r3.font.name = FONT_BODY
        r3.font.size = Pt(6.8)
        r3.font.color.rgb = TEXT_MUTED


# ---------------------------------------------------------------------------
# SLIDE 4: 04 — FEASIBILITY & VIABILITY (Lanezy Feasibility Slide Format)
# ---------------------------------------------------------------------------
def build_slide_4(slide):
    set_slide_background(slide, BG_WHITE)
    add_lanezy_header(
        slide,
        4,
        "04 — FEASIBILITY AND VIABILITY",
        "BUILT TO RUN LOCALLY. VALIDATED ON REAL SENTINEL-2."
    )

    # 1. Left Column: Feasibility Analysis (Lanezy Page 4 Format)
    col1_x = Inches(0.80)
    col1_w = Inches(3.00)

    tb_fh = slide.shapes.add_textbox(col1_x, Inches(1.20), col1_w, Inches(0.26))
    tf_fh = tb_fh.text_frame
    tf_fh.margin_left = tf_fh.margin_top = tf_fh.margin_right = tf_fh.margin_bottom = 0
    pf = tf_fh.paragraphs[0]
    pf.text = "FEASIBILITY ANALYSIS"
    pf.font.name = FONT_MONO
    pf.font.size = Pt(8.5)
    pf.font.bold = True
    pf.font.color.rgb = NAVY_PRIMARY

    feas_items = [
        ("LOCAL AI", "RemoteCLIP + FAISS", "Runs on standard CPU\n8–16 GB RAM footprint\nZero GPU dependencies", ACCENT_BLUE),
        ("REAL DATA", "Sentinel-2A · 10m", "Level-2A BOA Surface\nB02, B03, B04, B08\nCalibrated reflectance", ACCENT_TEAL),
        ("DETERMINISTIC", "Fixed Threshold τ = 0.15", "NDVI & NDWI spectral math\n8-conn morphological cluster\nZero model hallucination", ACCENT_GOLD)
    ]
    f_top = Inches(1.50)
    f_h = Inches(1.50)
    f_gap = Inches(0.12)
    for idx, (title, sub, body, col) in enumerate(feas_items):
        fy = f_top + idx * (f_h + f_gap)
        c_f = create_panel(slide, col1_x, fy, col1_w, f_h, border_color=CARD_BORDER, bg_color=CARD_BG)
        tb = slide.shapes.add_textbox(col1_x + Inches(0.15), fy + Inches(0.10), col1_w - Inches(0.30), f_h - Inches(0.20))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        p = tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = f"{title}\n"
        r1.font.name = FONT_MONO
        r1.font.size = Pt(7.2)
        r1.font.bold = True
        r1.font.color.rgb = col

        p2 = tf.add_paragraph()
        p2.space_before = Pt(2)
        r2 = p2.add_run()
        r2.text = f"{sub}\n"
        r2.font.name = FONT_HEADING
        r2.font.size = Pt(8.2)
        r2.font.bold = True
        r2.font.color.rgb = TEXT_DARK

        p3 = tf.add_paragraph()
        p3.space_before = Pt(2)
        r3 = p3.add_run()
        r3.text = body
        r3.font.name = FONT_BODY
        r3.font.size = Pt(7.0)
        r3.font.color.rgb = TEXT_MUTED

    # 2. Center Column: Real Sentinel-2 Multi-Date Validation (3-Panel Visual)
    col2_x = Inches(3.95)
    col2_w = Inches(5.30)

    tb_vh = slide.shapes.add_textbox(col2_x, Inches(1.20), col2_w, Inches(0.26))
    tf_vh = tb_vh.text_frame
    tf_vh.margin_left = tf_vh.margin_top = tf_vh.margin_right = tf_vh.margin_bottom = 0
    pv = tf_vh.paragraphs[0]
    pv.text = "REAL SENTINEL-2 MULTI-DATE VALIDATION (MGRS 43RGM · NCR INDIA)"
    pv.font.name = FONT_MONO
    pv.font.size = Pt(8.0)
    pv.font.bold = True
    pv.font.color.rgb = NAVY_PRIMARY

    # Three-Panel Satellite Images
    triplet = [
        ("T0 · 19 MAY 2023", "Pre-Monsoon Dry Baseline", "sentinel2_t0_rgb.jpg"),
        ("TMID · 06 OCT 2023", "Post-Monsoon Green Peak", "sentinel2_tmid_rgb.jpg"),
        ("T1 · 05 DEC 2023", "Winter Post-Harvest", "sentinel2_t1_rgb.jpg")
    ]
    img_w = Inches(1.64)
    img_h = Inches(1.64)
    gap_i = Inches(0.19)
    for idx, (dt_title, dt_sub, fn) in enumerate(triplet):
        ix = col2_x + idx * (img_w + gap_i)
        safe_add_image(slide, os.path.join(ASSETS_DIR, fn), ix, Inches(1.50), img_w, img_h)
        
        # Caption below each panel
        c_cap = create_panel(slide, ix, Inches(3.18), img_w, Inches(0.48), border_color=CARD_BORDER, bg_color=BG_WHITE)
        tb_c = slide.shapes.add_textbox(ix, Inches(3.22), img_w, Inches(0.40))
        tf_c = tb_c.text_frame
        tf_c.margin_left = tf_c.margin_top = tf_c.margin_right = tf_c.margin_bottom = 0
        p = tf_c.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r1 = p.add_run()
        r1.text = f"{dt_title}\n"
        r1.font.name = FONT_MONO
        r1.font.size = Pt(6.5)
        r1.font.bold = True
        r1.font.color.rgb = NAVY_PRIMARY

        p2 = tf_c.add_paragraph()
        p2.alignment = PP_ALIGN.CENTER
        r2 = p2.add_run()
        r2.text = dt_sub
        r2.font.name = FONT_BODY
        r2.font.size = Pt(5.8)
        r2.font.color.rgb = TEXT_MUTED

        if idx < 2:
            arr_x = ix + img_w + Inches(0.02)
            tb_arr = slide.shapes.add_textbox(arr_x, Inches(2.20), gap_i - Inches(0.04), Inches(0.30))
            tf_arr = tb_arr.text_frame
            tf_arr.margin_left = tf_arr.margin_top = tf_arr.margin_right = tf_arr.margin_bottom = 0
            pa = tf_arr.paragraphs[0]
            pa.alignment = PP_ALIGN.CENTER
            ra = pa.add_run()
            ra.text = "➔"
            ra.font.name = FONT_HEADING
            ra.font.size = Pt(11)
            ra.font.bold = True
            ra.font.color.rgb = CARD_BORDER

    # Empirical Observation Metrics Box
    c_met = create_panel(slide, col2_x, Inches(3.78), col2_w, Inches(1.50), border_color=CARD_BORDER, bg_color=CARD_BG)
    tb_m = slide.shapes.add_textbox(col2_x + Inches(0.18), Inches(3.86), col2_w - Inches(0.36), Inches(1.34))
    tf_m = tb_m.text_frame
    tf_m.word_wrap = True
    tf_m.margin_left = tf_m.margin_top = tf_m.margin_right = tf_m.margin_bottom = 0

    p_mh = tf_m.paragraphs[0]
    p_mh.text = "EMPIRICAL OBSERVATION METRICS (262,144 VALID PIXELS · 10m GSD)"
    p_mh.font.name = FONT_MONO
    p_mh.font.size = Pt(7.2)
    p_mh.font.bold = True
    p_mh.font.color.rgb = NAVY_PRIMARY

    p_d = tf_m.add_paragraph()
    p_d.space_before = Pt(2)
    r_d = p_d.add_run()
    r_d.text = "0.7% (T0 ➔ TMID)     |     0.2% (TMID ➔ T1)     |     1.0% (T0 ➔ T1)"
    r_d.font.name = FONT_MONO
    r_d.font.size = Pt(7.8)
    r_d.font.bold = True
    r_d.font.color.rgb = ACCENT_GOLD

    p_res = tf_m.add_paragraph()
    p_res.space_before = Pt(3)
    r_res = p_res.add_run()
    r_res.text = "98.75% STABLE    "
    r_res.font.name = FONT_HEADING
    r_res.font.size = Pt(11.0)
    r_res.font.bold = True
    r_res.font.color.rgb = ACCENT_GREEN

    r_vrd = p_res.add_run()
    r_vrd.text = "VERDICT: REVIEW (Ambiguous phenology routed to human analyst)"
    r_vrd.font.name = FONT_HEADING
    r_vrd.font.size = Pt(7.5)
    r_vrd.font.bold = True
    r_vrd.font.color.rgb = ACCENT_AMBER

    p_att = tf_m.add_paragraph()
    p_att.space_before = Pt(2)
    r_att = p_att.add_run()
    r_att.text = "Attribution Support:  Built 51.1%   |   Vegetation 24.7%   |   Seasonal 19.9%   |   Unresolved 3.1%"
    r_att.font.name = FONT_BODY
    r_att.font.size = Pt(7.0)
    r_att.font.color.rgb = TEXT_DARK

    # Horizontal Attribution Breakdown Bar
    bar_y = Inches(5.05)
    bar_x = col2_x + Inches(0.18)
    bar_w = col2_w - Inches(0.36)
    bar_h = Inches(0.12)

    b_built = bar_w * 0.511
    b_veg = bar_w * 0.247
    b_sea = bar_w * 0.199
    b_unr = bar_w * 0.031

    seg1 = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, bar_x, bar_y, b_built, bar_h)
    seg1.fill.solid(); seg1.fill.fore_color.rgb = ACCENT_AMBER; seg1.line.fill.background()

    seg2 = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, bar_x + b_built, bar_y, b_veg, bar_h)
    seg2.fill.solid(); seg2.fill.fore_color.rgb = ACCENT_GREEN; seg2.line.fill.background()

    seg3 = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, bar_x + b_built + b_veg, bar_y, b_sea, bar_h)
    seg3.fill.solid(); seg3.fill.fore_color.rgb = ACCENT_GOLD; seg3.line.fill.background()

    seg4 = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, bar_x + b_built + b_veg + b_sea, bar_y, b_unr, bar_h)
    seg4.fill.solid(); seg4.fill.fore_color.rgb = CARD_BORDER; seg4.line.fill.background()

    # 3. Right Column: Viability Analysis (Lanezy Page 4 Format)
    col3_x = Inches(9.40)
    col3_w = Inches(3.133)

    tb_vh2 = slide.shapes.add_textbox(col3_x, Inches(1.20), col3_w, Inches(0.26))
    tf_vh2 = tb_vh2.text_frame
    tf_vh2.margin_left = tf_vh2.margin_top = tf_vh2.margin_right = tf_vh2.margin_bottom = 0
    pv2 = tf_vh2.paragraphs[0]
    pv2.text = "VIABILITY & POTENTIAL"
    pv2.font.name = FONT_MONO
    pv2.font.size = Pt(8.5)
    pv2.font.bold = True
    pv2.font.color.rgb = NAVY_PRIMARY

    viab_items = [
        ("OFFLINE-FIRST", "Air-gapped operation; zero cloud egress in defense facilities"),
        ("ANALYST-IN-LOOP", "Review ambiguous evidence; zero black-box automated strikes"),
        ("MODULAR", "Decoupled index, sensor & MECE trajectory persistence engine"),
        ("EXTENSIBLE", "Supports SAR, thermal & dense multi-year temporal time series")
    ]
    v_top = Inches(1.50)
    v_h = Inches(1.10)
    v_gap = Inches(0.12)
    for idx, (title, desc) in enumerate(viab_items):
        vy = v_top + idx * (v_h + v_gap)
        c_v = create_panel(slide, col3_x, vy, col3_w, v_h, border_color=CARD_BORDER, bg_color=CARD_BG)
        tb = slide.shapes.add_textbox(col3_x + Inches(0.15), vy + Inches(0.10), col3_w - Inches(0.30), v_h - Inches(0.20))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        p = tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = f"{title}\n"
        r1.font.name = FONT_MONO
        r1.font.size = Pt(7.2)
        r1.font.bold = True
        r1.font.color.rgb = NAVY_PRIMARY if idx % 2 == 0 else ACCENT_GREEN

        p2 = tf.add_paragraph()
        p2.space_before = Pt(2)
        r2 = p2.add_run()
        r2.text = desc
        r2.font.name = FONT_BODY
        r2.font.size = Pt(7.0)
        r2.font.color.rgb = TEXT_MUTED

    # Bottom Proof Badges Container
    bot_y = Inches(6.45)
    c_badges = create_panel(slide, Inches(0.80), bot_y, Inches(11.733), Inches(0.55), border_color=CARD_BORDER, bg_color=BG_IVORY)
    
    badge_items = [
        ("[135 / 135 TESTS PASSING]", ACCENT_GREEN),
        ("[ZERO RUNTIME EXTERNAL CALLS]", ACCENT_BLUE),
        ("[262,144 VALID PIXELS]", ACCENT_GOLD),
        ("[DETERMINISTIC τ = 0.15]", NAVY_PRIMARY)
    ]
    bw = Inches(2.70)
    for idx, (b_txt, b_col) in enumerate(badge_items):
        bx = Inches(0.95) + idx * bw
        tb_b = slide.shapes.add_textbox(bx, bot_y + Inches(0.14), bw, Inches(0.30))
        tf_b = tb_b.text_frame
        tf_b.margin_left = tf_b.margin_top = tf_b.margin_right = tf_b.margin_bottom = 0
        p = tf_b.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = b_txt
        r.font.name = FONT_MONO
        r.font.size = Pt(8.0)
        r.font.bold = True
        r.font.color.rgb = b_col


# ---------------------------------------------------------------------------
# SLIDE 5: 05 — IMPACT & BENEFITS (Lanezy Impact Slide Format)
# ---------------------------------------------------------------------------
def build_slide_5(slide):
    set_slide_background(slide, BG_WHITE)
    add_lanezy_header(
        slide,
        5,
        "05 — IMPACT AND BENEFITS",
        "TURNING SATELLITE ARCHIVES INTO AN INVESTIGATION WORKBENCH"
    )

    # 1. Center-Top: ONE LARGE HORIZONTAL IMPACT JOURNEY (Lanezy Slide 5 Style)
    flow_top = Inches(1.20)
    flow_h = Inches(1.05)
    c_flow = create_panel(slide, Inches(0.80), flow_top, Inches(11.733), flow_h, border_color=CARD_BORDER, bg_color=CARD_BG)
    
    flow_steps = [
        ("SATELLITE ARCHIVE", "Sentinel-2 & SAR tiles", NAVY_PRIMARY, "impact_step_1.png"),
        ("SEMANTIC DISCOVERY", "RemoteCLIP prompt", ACCENT_BLUE, "impact_step_2.png"),
        ("RELEVANT SCENE", "Ranked candidates", ACCENT_TEAL, "impact_step_3.png"),
        ("TEMPORAL COMPARISON", "Calibrated change", ACCENT_GREEN, "impact_step_4.png"),
        ("EVIDENCE REVIEW", "Spectral attribution", ACCENT_GOLD, "impact_step_5.png"),
        ("ANALYST DECISION", "Actionable verdict", NAVY_PRIMARY, "impact_step_6.png")
    ]
    step_w = Inches(1.72)
    gap = Inches(0.23)
    start_x = Inches(0.95)
    for idx, (st_name, st_sub, st_col, icon_fn) in enumerate(flow_steps):
        bx = start_x + idx * (step_w + gap)
        c_node = create_panel(slide, bx, flow_top + Inches(0.16), step_w, Inches(0.74), border_color=st_col, bg_color=BG_WHITE, border_width=Pt(1.2))
        
        # Crisp square vector icon
        safe_add_image(slide, os.path.join(ASSETS_DIR, icon_fn), bx + Inches(0.08), flow_top + Inches(0.23), Inches(0.60), Inches(0.60))
        
        # Text label next to icon
        tb = slide.shapes.add_textbox(bx + Inches(0.72), flow_top + Inches(0.20), step_w - Inches(0.76), Inches(0.66))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        r = p.add_run()
        r.text = f"{st_name}\n"
        r.font.name = FONT_MONO
        r.font.size = Pt(6.2)
        r.font.bold = True
        r.font.color.rgb = st_col

        p2 = tf.add_paragraph()
        p2.alignment = PP_ALIGN.LEFT
        p2.space_before = Pt(1.5)
        r2 = p2.add_run()
        r2.text = st_sub
        r2.font.name = FONT_BODY
        r2.font.size = Pt(5.6)
        r2.font.color.rgb = TEXT_DARK

        if idx < len(flow_steps) - 1:
            arr_x = bx + step_w + Inches(0.02)
            tb_a = slide.shapes.add_textbox(arr_x, flow_top + Inches(0.33), gap - Inches(0.04), Inches(0.30))
            tf_a = tb_a.text_frame
            tf_a.margin_left = tf_a.margin_top = tf_a.margin_right = tf_a.margin_bottom = 0
            p_a = tf_a.paragraphs[0]
            p_a.alignment = PP_ALIGN.CENTER
            r_a = p_a.add_run()
            r_a.text = "➔"
            r_a.font.name = FONT_HEADING
            r_a.font.size = Pt(11)
            r_a.font.bold = True
            r_a.font.color.rgb = CARD_BORDER

    # 2. Four Operational Use Cases with Real Satellite Thumbnails (2x2 Grid)
    grid_top = Inches(2.40)
    card_w = Inches(5.72)
    card_h = Inches(1.90)
    gap_x = Inches(0.29)
    gap_y = Inches(0.16)

    use_cases = [
        (
            "01 / INFRASTRUCTURE MONITORING",
            "Forward Outpost, Tarmac & Fortified Perimeter Detection",
            "Quickly discovers clandestine military construction, border tarmac paving, and fortified forward compounds. Natural-language intent isolates candidate tiles across thousands of sq km without coordinate guessing.",
            "controlled_t2_rgb.jpg",
            ACCENT_BLUE
        ),
        (
            "02 / STRATEGIC SITE DISCOVERY",
            "Cross-Theater Facility Pattern Matching",
            "Query the RemoteCLIP FAISS vector index to discover geographically separated candidate sites sharing identical visual-semantic patterns across the theater, cutting manual catalog triage by hours.",
            "bordeaux_t1_rgb.jpg",
            ACCENT_TEAL
        ),
        (
            "03 / ROAD / TERRAIN CORRIDOR CHANGE",
            "Frontier Logistics Tracks, Earth Clearings & Bridgeheads",
            "Tracks emerging logistics road corridors and supply clearings across rugged terrain. Spatial coherence analysis confirms contiguous linear infrastructure while suppressing single-pixel seasonal slope washouts.",
            "mumbai_t1_rgb.jpg",
            ACCENT_GREEN
        ),
        (
            "04 / VEGETATION / WATER INTERPRETATION",
            "Defending Against False-Alarm Alert Fatigue",
            "Enforces 3-date MECE persistence trajectories to distinguish agricultural crop cycles (monsoon greening to harvest senescence) from permanent land-cover conversion, protecting command staff from false alarms.",
            "sentinel2_tmid_rgb.jpg",
            ACCENT_GOLD
        ),
    ]

    for idx, (tag, title, body, img_fn, tag_col) in enumerate(use_cases):
        row = idx // 2
        col = idx % 2
        cx = Inches(0.80) + col * (card_w + gap_x)
        cy = grid_top + row * (card_h + gap_y)

        c = create_panel(slide, cx, cy, card_w, card_h, border_color=CARD_BORDER, bg_color=CARD_BG)
        
        # Real authentic satellite image
        img_x = cx + Inches(0.14)
        img_y = cy + Inches(0.14)
        safe_add_image(slide, os.path.join(ASSETS_DIR, img_fn), img_x, img_y, Inches(1.62), Inches(1.62))

        # Text side
        tb_x = cx + Inches(1.88)
        tb_w = card_w - Inches(2.02)
        tb = slide.shapes.add_textbox(tb_x, cy + Inches(0.12), tb_w, card_h - Inches(0.24))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p_tag = tf.paragraphs[0]
        p_tag.text = tag
        p_tag.font.name = FONT_MONO
        p_tag.font.size = Pt(7.0)
        p_tag.font.bold = True
        p_tag.font.color.rgb = tag_col

        p_ti = tf.add_paragraph()
        p_ti.space_before = Pt(2)
        r_ti = p_ti.add_run()
        r_ti.text = title
        r_ti.font.name = FONT_HEADING
        r_ti.font.size = Pt(8.2)
        r_ti.font.bold = True
        r_ti.font.color.rgb = TEXT_DARK

        p_bo = tf.add_paragraph()
        p_bo.space_before = Pt(3)
        r_bo = p_bo.add_run()
        r_bo.text = body
        r_bo.font.name = FONT_BODY
        r_bo.font.size = Pt(6.8)
        r_bo.font.color.rgb = TEXT_MUTED

    # Bottom Core Defense Principles & Quote
    bot_y = Inches(6.45)
    c_bot = create_panel(slide, Inches(0.80), bot_y, Inches(11.733), Inches(0.55), border_color=CARD_BORDER, bg_color=BG_IVORY)
    tb_b = slide.shapes.add_textbox(Inches(0.90), bot_y + Inches(0.06), Inches(11.533), Inches(0.42))
    tf_b = tb_b.text_frame
    tf_b.word_wrap = True
    tf_b.margin_left = tf_b.margin_top = tf_b.margin_right = tf_b.margin_bottom = 0

    p_p = tf_b.paragraphs[0]
    p_p.alignment = PP_ALIGN.CENTER
    r_p = p_p.add_run()
    r_p.text = "CORE DEFENSE PRINCIPLES:   [OFFLINE]   [AUDITABLE]   [CONSERVATIVE]"
    r_p.font.name = FONT_MONO
    r_p.font.size = Pt(7.2)
    r_p.font.bold = True
    r_p.font.color.rgb = NAVY_PRIMARY

    p_q = tf_b.add_paragraph()
    p_q.alignment = PP_ALIGN.CENTER
    r_q = p_q.add_run()
    r_q.text = "“The goal is not to make every result positive. The goal is to make the result explainable.”"
    r_q.font.name = FONT_TITLE
    r_q.font.size = Pt(9.5)
    r_q.font.bold = True
    r_q.font.color.rgb = ACCENT_GOLD


# ---------------------------------------------------------------------------
# SLIDE 6: 06 — RESEARCH & REFERENCES (Lanezy Research Slide Format)
# ---------------------------------------------------------------------------
def build_slide_6(slide):
    set_slide_background(slide, BG_WHITE)
    add_lanezy_header(
        slide,
        6,
        "06 — RESEARCH AND REFERENCES",
        "EMPIRICAL BENCHMARKS, RESEARCH FOUNDATIONS & PROJECT ACCESS"
    )

    # 1. Left Column: Research Foundation Flow (Lanezy Page 6 Format)
    col1_x = Inches(0.80)
    col1_w = Inches(3.20)
    col1_h = Inches(5.15)

    c_rf = create_panel(slide, col1_x, Inches(1.20), col1_w, col1_h, border_color=CARD_BORDER, bg_color=CARD_BG)
    tb_rh = slide.shapes.add_textbox(col1_x + Inches(0.15), Inches(1.30), col1_w - Inches(0.30), Inches(0.24))
    tf_rh = tb_rh.text_frame
    tf_rh.margin_left = tf_rh.margin_top = tf_rh.margin_right = tf_rh.margin_bottom = 0
    p_rh = tf_rh.paragraphs[0]
    p_rh.text = "RESEARCH FOUNDATION FLOW"
    p_rh.font.name = FONT_MONO
    p_rh.font.size = Pt(8.5)
    p_rh.font.bold = True
    p_rh.font.color.rgb = NAVY_PRIMARY

    # Embedded Research Flow Vector Graphic
    res_img_path = os.path.join(ASSETS_DIR, "research_flow.jpg")
    safe_add_image(slide, res_img_path, col1_x + Inches(0.15), Inches(1.60), Inches(1.10), Inches(3.20))

    # Flow Cards next to graphic
    r_steps = [
        ("REMOTECLIP", "Chen et al., IEEE TGRS 2024", "Vision-language foundation model", ACCENT_BLUE),
        ("SENTINEL-2", "ESA Copernicus 10m BOA", "Calibrated multispectral reflectance", ACCENT_TEAL),
        ("OSCD BENCHMARK", "Daudt et al., IEEE IGARSS", "Standardized ground truth", ACCENT_GREEN),
        ("NDVI / NDWI", "Rouse et al. / McFeeters", "Biophysical difference band indices", ACCENT_GOLD),
        ("TERRAE CONSOLE", "Quantumcrew SIH26227", "Evidence-based investigation", NAVY_PRIMARY)
    ]
    r_top = Inches(1.60)
    r_h = Inches(0.58)
    r_gap = Inches(0.08)
    for idx, (title, sub, desc, col) in enumerate(r_steps):
        ry = r_top + idx * (r_h + r_gap)
        c_step = create_panel(slide, col1_x + Inches(1.35), ry, col1_w - Inches(1.48), r_h, border_color=CARD_BORDER, bg_color=BG_WHITE)
        tb = slide.shapes.add_textbox(col1_x + Inches(1.42), ry + Inches(0.04), col1_w - Inches(1.62), r_h - Inches(0.08))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        p = tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = f"{title}\n"
        r1.font.name = FONT_MONO
        r1.font.size = Pt(6.8)
        r1.font.bold = True
        r1.font.color.rgb = col

        p2 = tf.add_paragraph()
        p2.space_before = Pt(1)
        r2 = p2.add_run()
        r2.text = f"{sub}"
        r2.font.name = FONT_HEADING
        r2.font.size = Pt(6.2)
        r2.font.color.rgb = TEXT_DARK

    # 2. Center Column: Validated Empirical Evidence (Lanezy Format)
    col2_x = Inches(4.15)
    col2_w = Inches(4.90)

    tb_eh = slide.shapes.add_textbox(col2_x, Inches(1.20), col2_w, Inches(0.24))
    tf_eh = tb_eh.text_frame
    tf_eh.margin_left = tf_eh.margin_top = tf_eh.margin_right = tf_eh.margin_bottom = 0
    p_eh = tf_eh.paragraphs[0]
    p_eh.text = "VALIDATION PROOF & BENCHMARKS"
    p_eh.font.name = FONT_MONO
    p_eh.font.size = Pt(8.5)
    p_eh.font.bold = True
    p_eh.font.color.rgb = NAVY_PRIMARY

    # Sentinel-2 Box
    c_s2 = create_panel(slide, col2_x, Inches(1.50), col2_w, Inches(2.20), border_color=CARD_BORDER, bg_color=CARD_BG)
    tb_s2 = slide.shapes.add_textbox(col2_x + Inches(0.18), Inches(1.60), col2_w - Inches(0.36), Inches(2.00))
    tf_s2 = tb_s2.text_frame
    tf_s2.word_wrap = True
    tf_s2.margin_left = tf_s2.margin_top = tf_s2.margin_right = tf_s2.margin_bottom = 0
    
    p = tf_s2.paragraphs[0]
    p.text = "1. REAL SENTINEL-2 (MGRS 43RGM · NCR INDIA)"
    p.font.name = FONT_MONO
    p.font.size = Pt(8.0)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN

    p_s2_lines = [
        "• Analysis Tile: 512×512 (262,144 valid pixels · 10m GSD)",
        "• Observations: T0 (19 May 2023), TMID (06 Oct 2023), T1 (05 Dec 2023)",
        "• Change Fractions: T0➔TMID: 0.7% | TMID➔T1: 0.2% | T0➔T1: 1.0%",
        "• Trajectory Distribution: STABLE = 98.75% (258,869 px)",
        "• Attribution: Built 51.1% | Veg 24.7% | Seasonal 19.9% | Unresolved 3.1%",
        "• System Verdict: REVIEW (Conservative routing on 1.0% change)"
    ]
    for line in p_s2_lines:
        pl = tf_s2.add_paragraph()
        pl.space_before = Pt(2)
        r = pl.add_run()
        r.text = line
        r.font.name = FONT_BODY
        r.font.size = Pt(7.0)
        r.font.color.rgb = TEXT_DARK

    # OSCD Benchmark Box
    c_oscd = create_panel(slide, col2_x, Inches(3.82), col2_w, Inches(2.53), border_color=CARD_BORDER, bg_color=CARD_BG)
    tb_os = slide.shapes.add_textbox(col2_x + Inches(0.18), Inches(3.92), col2_w - Inches(0.36), Inches(2.33))
    tf_os = tb_os.text_frame
    tf_os.word_wrap = True
    tf_os.margin_left = tf_os.margin_top = tf_os.margin_right = tf_os.margin_bottom = 0

    p = tf_os.paragraphs[0]
    p.text = "2. OSCD BENCHMARK — 5-PAIR VALIDATION SUBSET"
    p.font.name = FONT_MONO
    p.font.size = Pt(8.0)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE

    p_os_lines = [
        "• Pairs: Aguas Claras, Beirut, Bordeaux, Cupertino, Mumbai",
        "• Valid Pixels Evaluated: 3,025,938 valid pixels | Fixed τ = 0.15",
        "",
        "QUANTITATIVE BENCHMARK METRICS:",
        "• Micro Aggregate: Precision 57.55% | Recall 9.72% | F1 0.1663 | IoU 0.0907",
        "• Macro Average:   Precision 52.22% | Recall 7.84% | F1 0.1267 | IoU 0.0692",
        "",
        "Class Imbalance Note: Accuracy (97.90%) is dominated by 97.64% unchanged",
        "ground truth. Low recall reflects conservative noise suppression."
    ]
    for line in p_os_lines:
        pl = tf_os.add_paragraph()
        pl.space_before = Pt(1.5)
        r = pl.add_run()
        r.text = line
        r.font.name = FONT_MONO if "Precision" in line else FONT_BODY
        r.font.size = Pt(6.8) if "Precision" in line else Pt(6.5)
        r.font.bold = True if "QUANTITATIVE" in line else False
        r.font.color.rgb = NAVY_PRIMARY if "QUANTITATIVE" in line else (TEXT_DARK if "•" in line else TEXT_MUTED)

    # 3. Right Column: Project Access & Compact References (Lanezy Page 6 Format)
    col3_x = Inches(9.20)
    col3_w = Inches(3.333)

    tb_ah = slide.shapes.add_textbox(col3_x, Inches(1.20), col3_w, Inches(0.24))
    tf_ah = tb_ah.text_frame
    tf_ah.margin_left = tf_ah.margin_top = tf_ah.margin_right = tf_ah.margin_bottom = 0
    p_ah = tf_ah.paragraphs[0]
    p_ah.text = "PROJECT ACCESS & REFERENCES"
    p_ah.font.name = FONT_MONO
    p_ah.font.size = Pt(8.5)
    p_ah.font.bold = True
    p_ah.font.color.rgb = NAVY_PRIMARY

    # Project Access Box
    c_acc = create_panel(slide, col3_x, Inches(1.50), col3_w, Inches(2.50), border_color=CARD_BORDER, bg_color=BG_IVORY)
    tb_ac = slide.shapes.add_textbox(col3_x + Inches(0.18), Inches(1.60), col3_w - Inches(0.36), Inches(2.30))
    tf_ac = tb_ac.text_frame
    tf_ac.word_wrap = True
    tf_ac.margin_left = tf_ac.margin_top = tf_ac.margin_right = tf_ac.margin_bottom = 0
    
    p = tf_ac.paragraphs[0]
    p.text = "PROJECT ACCESS"
    p.font.name = FONT_MONO
    p.font.size = Pt(8.0)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GOLD

    access_items = [
        ("Live Console", "terrae-geospatial-intelligence.vercel.app", URL_WEB),
        ("GitHub Repository", "github.com/PhantomCipher13/terrae-geospatial-intelligence", URL_REPO),
        ("Technical Report", "REPORT.md (6-Part Scientific Dossier)", None),
        ("Automated Tests", "135 / 135 Tests Passing", None),
        ("Team", f"{TEAM_NAME} ({PS_ID})", None)
    ]
    for label, val, link in access_items:
        pl = tf_ac.add_paragraph()
        pl.space_before = Pt(3)
        r1 = pl.add_run()
        r1.text = f"• {label}: "
        r1.font.name = FONT_HEADING
        r1.font.size = Pt(7.2)
        r1.font.bold = True
        r1.font.color.rgb = TEXT_DARK

        r2 = pl.add_run()
        r2.text = val
        r2.font.name = FONT_BODY
        r2.font.size = Pt(7.0)
        r2.font.color.rgb = NAVY_PRIMARY if link else TEXT_MUTED
        if link:
            r2.hyperlink.address = link

    # Compact References Box
    c_ref = create_panel(slide, col3_x, Inches(4.12), col3_w, Inches(2.23), border_color=CARD_BORDER, bg_color=CARD_BG)
    tb_rf = slide.shapes.add_textbox(col3_x + Inches(0.18), Inches(4.20), col3_w - Inches(0.36), Inches(2.05))
    tf_rf = tb_rf.text_frame
    tf_rf.word_wrap = True
    tf_rf.margin_left = tf_rf.margin_top = tf_rf.margin_right = tf_rf.margin_bottom = 0
    
    p = tf_rf.paragraphs[0]
    p.text = "COMPACT REFERENCES"
    p.font.name = FONT_MONO
    p.font.size = Pt(7.5)
    p.font.bold = True
    p.font.color.rgb = NAVY_PRIMARY

    refs = [
        "[1] RemoteCLIP: Chen et al., IEEE TGRS 2024.",
        "[2] Sentinel-2: ESA Level-2A ATBD (10m BOA).",
        "[3] OSCD: Daudt et al., IEEE IGARSS 2018.",
        "[4] NDVI: Rouse et al., NASA SP-351, 1974.",
        "[5] NDWI: McFeeters, Int. J. Remote Sens., 1996."
    ]
    for ref in refs:
        pl = tf_rf.add_paragraph()
        pl.space_before = Pt(2)
        r = pl.add_run()
        r.text = ref
        r.font.name = FONT_BODY
        r.font.size = Pt(6.8)
        r.font.color.rgb = TEXT_DARK

    # Bottom Closing Motto Banner
    bot_y = Inches(6.45)
    c_bot = create_panel(slide, Inches(0.80), bot_y, Inches(11.733), Inches(0.55), border_color=CARD_BORDER, bg_color=BG_IVORY)
    tb_b = slide.shapes.add_textbox(Inches(0.90), bot_y + Inches(0.12), Inches(11.533), Inches(0.35))
    tf_b = tb_b.text_frame
    tf_b.margin_left = tf_b.margin_top = tf_b.margin_right = tf_b.margin_bottom = 0
    p = tf_b.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "“INVESTIGATE THE CHANGE. FOLLOW THE EVIDENCE. KNOW WHEN TO REVIEW.”"
    r.font.name = FONT_TITLE
    r.font.size = Pt(11.0)
    r.font.bold = True
    r.font.color.rgb = NAVY_PRIMARY


# ---------------------------------------------------------------------------
# MAIN PRESENTATION BUILDER
# ---------------------------------------------------------------------------
def build_master_presentation():
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.500)
    blank_layout = prs.slide_layouts[6]

    print("=== BUILDING SIH 2026 MASTER FINAL PRESENTATION (LANEZY BENCHMARK REBUILD) ===")
    
    # Slide 1
    print("[1/6] Building Slide 1: 01 — PROBLEM STATEMENT...")
    s1 = prs.slides.add_slide(blank_layout)
    build_slide_1(s1)

    # Slide 2
    print("[2/6] Building Slide 2: 02 — SOLUTION...")
    s2 = prs.slides.add_slide(blank_layout)
    build_slide_2(s2)

    # Slide 3
    print("[3/6] Building Slide 3: 03 — TECHNICAL APPROACH...")
    s3 = prs.slides.add_slide(blank_layout)
    build_slide_3(s3)

    # Slide 4
    print("[4/6] Building Slide 4: 04 — FEASIBILITY & VIABILITY...")
    s4 = prs.slides.add_slide(blank_layout)
    build_slide_4(s4)

    # Slide 5
    print("[5/6] Building Slide 5: 05 — IMPACT & BENEFITS...")
    s5 = prs.slides.add_slide(blank_layout)
    build_slide_5(s5)

    # Slide 6
    print("[6/6] Building Slide 6: 06 — RESEARCH & REFERENCES...")
    s6 = prs.slides.add_slide(blank_layout)
    build_slide_6(s6)

    print(f"Total slides generated: {len(prs.slides)}")

    # Target save paths
    parent_dir = os.path.dirname(REPO_ROOT)
    targets = [
        os.path.join(parent_dir, "TERRAE_SIH2026_Presentation.pptx"),
        os.path.join(REPO_ROOT, "TERRAE_SIH2026_Presentation.pptx"),
        os.path.join(parent_dir, "GEOAI_SIH2026_Presentation.pptx"),
        os.path.join(REPO_ROOT, "GEOAI_SIH2026_Presentation.pptx"),
    ]

    for target in targets:
        prs.save(target)
        print(f"[SUCCESS] Presentation saved: {target}")


if __name__ == "__main__":
    build_master_presentation()
