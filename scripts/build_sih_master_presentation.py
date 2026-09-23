#!/usr/bin/env python3
"""
TERRAE — Smart India Hackathon 2026 Master 6-Slide Presentation Generator
Visual Reset: Plain Light Background (#FFFFFF / #F8F7F3) + Navy Headings (#163D6B)
Follows Lanezy SIH Finalist Competition Style:
- Plain light background throughout the deck
- Large Navy headings (#163D6B)
- Clear content zones with 15–25% whitespace
- Dominant central diagrams / visuals
- Short bold labels (50–65% text reduction, no paragraph walls)
- Icon + Arrow + Label diagram-first grammar
- Authentic satellite imagery inside intentional visual zones

Exact 6 Slides:
01 — PROBLEM STATEMENT
02 — SOLUTION
03 — TECHNICAL APPROACH / METHODOLOGY & PROCESS OF IMPLEMENTATION
04 — FEASIBILITY & VIABILITY
05 — IMPACT & BENEFITS
06 — RESEARCH & REFERENCES
"""

import os
import sys
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# ---------------------------------------------------------------------------
# COLOR PALETTE (SIH Light Theme / Defense Command Precision)
# ---------------------------------------------------------------------------
BG_WHITE = RGBColor(255, 255, 255)         # #FFFFFF Crisp White Canvas
BG_IVORY = RGBColor(248, 247, 243)         # #F8F7F3 Light Warm Ivory
CARD_BG = RGBColor(248, 250, 252)          # #F8FAFC Very Light Slate Card
CARD_BORDER = RGBColor(203, 213, 225)      # #CBD5E1 Clean Structural Border

NAVY_PRIMARY = RGBColor(22, 61, 107)       # #163D6B Primary Navy Heading
NAVY_DEEP = RGBColor(15, 23, 42)           # #0F172A Very Dark Navy Body
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
URL_REPORT = "https://github.com/PhantomCipher13/terrae-geospatial-intelligence/blob/main/REPORT.md"

# Asset Paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ASSETS_DIR = os.path.join(BASE_DIR, "frontend", "public", "assets")
DATA_ASSETS_DIR = os.path.join(BASE_DIR, "data", "ui_assets")
QA_DIR = r"C:\Users\Admin\.gemini\antigravity\brain\d1a1e5ad-c438-4104-985b-ec757632f80e\terrae_qa"


# ---------------------------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------------------------
def set_canvas_background(slide):
    """Draws plain crisp light canvas background (16:9 widescreen)."""
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = BG_WHITE
    bg.line.fill.background()
    return bg


def add_sih_header(slide, slide_num_str, section_title, subtitle):
    """Draws standardized, clean SIH competition header."""
    set_canvas_background(slide)

    # Top thin Navy accent line
    top_line = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0.80), Inches(0.32), Inches(11.733), Inches(0.025)
    )
    top_line.fill.solid()
    top_line.fill.fore_color.rgb = NAVY_PRIMARY
    top_line.line.fill.background()

    # Mandate line (Top Left)
    tb_tag = slide.shapes.add_textbox(Inches(0.80), Inches(0.38), Inches(8.5), Inches(0.25))
    tf_tag = tb_tag.text_frame
    tf_tag.word_wrap = True
    tf_tag.margin_left = tf_tag.margin_top = tf_tag.margin_right = tf_tag.margin_bottom = 0
    p_tag = tf_tag.paragraphs[0]
    p_tag.text = f"SMART INDIA HACKATHON 2026 · PS: {PS_ID} · {THEME.upper()} · {CATEGORY.upper()} · {MINISTRY.upper()}"
    p_tag.font.name = FONT_MONO
    p_tag.font.size = Pt(8.0)
    p_tag.font.bold = True
    p_tag.font.color.rgb = NAVY_PRIMARY

    # Tracker & Team (Top Right)
    tb_track = slide.shapes.add_textbox(Inches(8.5), Inches(0.38), Inches(4.033), Inches(0.25))
    tf_track = tb_track.text_frame
    tf_track.word_wrap = True
    tf_track.margin_left = tf_track.margin_top = tf_track.margin_right = tf_track.margin_bottom = 0
    p_tr = tf_track.paragraphs[0]
    p_tr.alignment = PP_ALIGN.RIGHT
    
    r_team = p_tr.add_run()
    r_team.text = f"TEAM: {TEAM_NAME}  |  "
    r_team.font.name = FONT_MONO
    r_team.font.size = Pt(8.0)
    r_team.font.color.rgb = TEXT_MUTED

    r_num = p_tr.add_run()
    r_num.text = f"SLIDE {slide_num_str}"
    r_num.font.name = FONT_MONO
    r_num.font.size = Pt(8.0)
    r_num.font.bold = True
    r_num.font.color.rgb = NAVY_PRIMARY

    # Main Section Title (Large Navy Display Font)
    tb_title = slide.shapes.add_textbox(Inches(0.80), Inches(0.65), Inches(11.733), Inches(0.65))
    tf_title = tb_title.text_frame
    tf_title.word_wrap = True
    tf_title.margin_left = tf_title.margin_top = tf_title.margin_right = tf_title.margin_bottom = 0
    
    p_t = tf_title.paragraphs[0]
    p_t.text = section_title.upper()
    p_t.font.name = FONT_TITLE
    p_t.font.size = Pt(17.0)
    p_t.font.bold = True
    p_t.font.color.rgb = NAVY_PRIMARY

    p_sub = tf_title.add_paragraph()
    p_sub.text = subtitle
    p_sub.font.name = FONT_HEADING
    p_sub.font.size = Pt(9.5)
    p_sub.font.color.rgb = TEXT_MUTED

    add_sih_footer(slide)


def add_sih_footer(slide):
    """Draws standardized footer with project credentials and links."""
    # Bottom subtle line
    bot_line = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0.80), Inches(7.08), Inches(11.733), Inches(0.015)
    )
    bot_line.fill.solid()
    bot_line.fill.fore_color.rgb = CARD_BORDER
    bot_line.line.fill.background()

    f_box = slide.shapes.add_textbox(Inches(0.80), Inches(7.14), Inches(11.733), Inches(0.22))
    tf = f_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    
    r1 = p.add_run()
    r1.text = f"{PROJECT_NAME} — Earth Intelligence Satellite Investigation Console  |  {MINISTRY}  |  SIH 2026 Submission"
    r1.font.name = FONT_BODY
    r1.font.size = Pt(7.8)
    r1.font.color.rgb = TEXT_MUTED

    r2 = p.add_run()
    r2.text = "                                                         Live Console: "
    r2.font.name = FONT_BODY
    r2.font.size = Pt(7.8)
    r2.font.color.rgb = TEXT_MUTED

    r3 = p.add_run()
    r3.text = URL_WEB
    r3.font.name = FONT_BODY
    r3.font.size = Pt(7.8)
    r3.font.color.rgb = NAVY_PRIMARY
    r3.hyperlink.address = URL_WEB


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
    if os.path.exists(path):
        return slide.shapes.add_picture(path, left, top, width, height)
    alt_path = os.path.join(DATA_ASSETS_DIR, os.path.basename(path))
    if os.path.exists(alt_path):
        return slide.shapes.add_picture(alt_path, left, top, width, height)
    
    fallback = create_panel(slide, left, top, width, height, border_color=CARD_BORDER, bg_color=CARD_BG)
    tb = slide.shapes.add_textbox(left, top + height/2 - Inches(0.2), width, Inches(0.4))
    p = tb.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.text = f"[{os.path.basename(path)}]"
    p.font.name = FONT_MONO
    p.font.size = Pt(8.0)
    p.font.color.rgb = TEXT_MUTED
    return fallback


# ---------------------------------------------------------------------------
# SLIDE 1: 01 — PROBLEM STATEMENT
# ---------------------------------------------------------------------------
def build_slide_1(slide):
    add_sih_header(
        slide,
        "01 / 06",
        "01 — PROBLEM STATEMENT",
        "SEMANTIC RETRIEVAL AND MULTI-TEMPORAL CHANGE ANALYSIS OF SATELLITE IMAGERY"
    )

    left_x = Inches(0.80)
    
    # Core Callout Statement (Light Warm Ivory Box)
    callout = create_panel(slide, left_x, Inches(1.45), Inches(4.70), Inches(0.95), border_color=ACCENT_GOLD, bg_color=BG_IVORY)
    tb_c = slide.shapes.add_textbox(left_x + Inches(0.15), Inches(1.52), Inches(4.40), Inches(0.80))
    tf_c = tb_c.text_frame
    tf_c.word_wrap = True
    tf_c.margin_left = tf_c.margin_top = tf_c.margin_right = tf_c.margin_bottom = 0
    p_c = tf_c.paragraphs[0]
    r_c = p_c.add_run()
    r_c.text = "“Finding a changed pixel is easy.\nKnowing whether it matters is harder.”"
    r_c.font.name = FONT_TITLE
    r_c.font.size = Pt(12.5)
    r_c.font.bold = True
    r_c.font.color.rgb = NAVY_PRIMARY

    # Official SIH Identification Card
    c_meta = create_panel(slide, left_x, Inches(2.55), Inches(4.70), Inches(2.35), border_color=CARD_BORDER, bg_color=CARD_BG)
    tb_m = slide.shapes.add_textbox(left_x + Inches(0.20), Inches(2.65), Inches(4.30), Inches(2.15))
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
        ("Problem Statement ID", "SIH26227"),
        ("Ministry / Client", "Ministry of Defence / Indian Army — DGIS"),
        ("Theme", "Space Technology"),
        ("Category", "Software"),
        ("Team Name", f"{TEAM_NAME} (Registered on portal)"),
        ("Team ID", f"{TEAM_ID}")
    ]
    for label, val in meta_items:
        p_it = tf_m.add_paragraph()
        p_it.space_before = Pt(3)
        r1 = p_it.add_run()
        r1.text = f"{label}: "
        r1.font.name = FONT_HEADING
        r1.font.size = Pt(8.0)
        r1.font.bold = True
        r1.font.color.rgb = TEXT_DARK
        r2 = p_it.add_run()
        r2.text = val
        r2.font.name = FONT_BODY
        r2.font.size = Pt(8.0)
        r2.font.color.rgb = NAVY_PRIMARY if "SIH" in val or "Quantum" in val else TEXT_MUTED

    # Core Challenge Summary Block
    c_chal = create_panel(slide, left_x, Inches(5.05), Inches(4.70), Inches(1.85), border_color=CARD_BORDER, bg_color=CARD_BG)
    tb_ch = slide.shapes.add_textbox(left_x + Inches(0.20), Inches(5.15), Inches(4.30), Inches(1.65))
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
    p_desc.space_before = Pt(3)
    r = p_desc.add_run()
    r.text = (
        "Analysts must find relevant satellite scenes and determine whether "
        "observed changes are persistent, meaningful, and supported by evidence.\n\n"
        "• Real Analyst Intent: “Show me areas with newly built structures near a river corridor.”\n"
        "• Offline Mandate: Zero cloud APIs, remote tracking, or network egress in defense enclaves."
    )
    r.font.name = FONT_BODY
    r.font.size = Pt(7.8)
    r.font.color.rgb = TEXT_DARK

    # 2. Right Side: Large Authentic Satellite Plate & Current Workflow Diagram
    right_x = Inches(5.75)
    right_w = Inches(6.783)

    # Large Satellite Image (10m GSD Sentinel-2 Beirut Plate)
    img_h = Inches(3.20)
    img_path = os.path.join(ASSETS_DIR, "hero_beirut_1920x1080.jpg")
    safe_add_image(slide, img_path, right_x, Inches(1.45), right_w, img_h)

    # Image Caption Strip
    c_cap = create_panel(slide, right_x, Inches(4.68), right_w, Inches(0.32), border_color=CARD_BORDER, bg_color=BG_IVORY)
    tb_cp = slide.shapes.add_textbox(right_x + Inches(0.15), Inches(4.72), right_w - Inches(0.30), Inches(0.25))
    tf_cp = tb_cp.text_frame
    tf_cp.margin_left = tf_cp.margin_top = tf_cp.margin_right = tf_cp.margin_bottom = 0
    p_cp = tf_cp.paragraphs[0]
    r_cp = p_cp.add_run()
    r_cp.text = "AUTHENTIC EARTH OBSERVATION: ESA Sentinel-2A Level-2A BOA Reflectance · 10m GSD · Maritime/Urban Basin"
    r_cp.font.name = FONT_MONO
    r_cp.font.size = Pt(7.4)
    r_cp.font.bold = True
    r_cp.font.color.rgb = NAVY_PRIMARY

    # CURRENT WORKFLOW DIAGRAM (5 Horizontal Connected Blocks)
    flow_top = Inches(5.15)
    flow_h = Inches(1.75)
    c_flow = create_panel(slide, right_x, flow_top, right_w, flow_h, border_color=CARD_BORDER, bg_color=CARD_BG)
    
    tb_fh = slide.shapes.add_textbox(right_x + Inches(0.20), flow_top + Inches(0.10), right_w - Inches(0.40), Inches(0.30))
    tf_fh = tb_fh.text_frame
    tf_fh.margin_left = tf_fh.margin_top = tf_fh.margin_right = tf_fh.margin_bottom = 0
    p_f = tf_fh.paragraphs[0]
    p_f.text = "CURRENT ANALYST WORKFLOW (STATUS QUO BOTTLENECKS)"
    p_f.font.name = FONT_MONO
    p_f.font.size = Pt(8.5)
    p_f.font.bold = True
    p_f.font.color.rgb = ACCENT_AMBER

    # 5 Connected Nodes
    wf_steps = ["Metadata", "Coordinates", "Scene Search", "Comparison", "Interpretation"]
    step_w = Inches(1.15)
    step_gap = Inches(0.18)
    for idx, st_name in enumerate(wf_steps):
        bx = right_x + Inches(0.20) + idx * (step_w + step_gap)
        by = flow_top + Inches(0.45)
        node = create_panel(slide, bx, by, step_w, Inches(0.55), border_color=CARD_BORDER, bg_color=BG_WHITE)
        tb_n = slide.shapes.add_textbox(bx, by + Inches(0.08), step_w, Inches(0.40))
        tf_n = tb_n.text_frame
        tf_n.word_wrap = True
        tf_n.margin_left = tf_n.margin_top = tf_n.margin_right = tf_n.margin_bottom = 0
        p_n = tf_n.paragraphs[0]
        p_n.alignment = PP_ALIGN.CENTER
        
        r1 = p_n.add_run()
        r1.text = f"0{idx+1}\n"
        r1.font.name = FONT_MONO
        r1.font.size = Pt(7.0)
        r1.font.bold = True
        r1.font.color.rgb = ACCENT_AMBER

        r2 = p_n.add_run()
        r2.text = st_name
        r2.font.name = FONT_HEADING
        r2.font.size = Pt(7.2)
        r2.font.bold = True
        r2.font.color.rgb = TEXT_DARK

        # Connector arrow
        if idx < len(wf_steps) - 1:
            arr_x = bx + step_w + Inches(0.03)
            tb_arr = slide.shapes.add_textbox(arr_x, by + Inches(0.12), step_gap - Inches(0.06), Inches(0.30))
            tf_a = tb_arr.text_frame
            tf_a.margin_left = tf_a.margin_top = tf_a.margin_right = tf_a.margin_bottom = 0
            p_a = tf_a.paragraphs[0]
            p_a.alignment = PP_ALIGN.CENTER
            r_a = p_a.add_run()
            r_a.text = "→"
            r_a.font.name = FONT_HEADING
            r_a.font.size = Pt(12)
            r_a.font.bold = True
            r_a.font.color.rgb = CARD_BORDER

    # Bottom workflow flaw statement
    tb_ff = slide.shapes.add_textbox(right_x + Inches(0.20), flow_top + Inches(1.15), right_w - Inches(0.40), Inches(0.50))
    tf_ff = tb_ff.text_frame
    tf_ff.word_wrap = True
    tf_ff.margin_left = tf_ff.margin_top = tf_ff.margin_right = tf_ff.margin_bottom = 0
    p_ff = tf_ff.paragraphs[0]
    r_ff = p_ff.add_run()
    r_ff.text = "CRITICAL DEFENSE FLAW: Naive pixel subtraction triggers severe false-alarm fatigue from seasonal crop phenology, moisture, and sun angle."
    r_ff.font.name = FONT_BODY
    r_ff.font.size = Pt(7.5)
    r_ff.font.bold = True
    r_ff.font.color.rgb = ACCENT_AMBER


# ---------------------------------------------------------------------------
# SLIDE 2: 02 — SOLUTION
# ---------------------------------------------------------------------------
def build_slide_2(slide):
    add_sih_header(
        slide,
        "02 / 06",
        "02 — SOLUTION",
        "FROM NATURAL-LANGUAGE QUERY TO EVIDENCE-BACKED INVESTIGATION"
    )

    # 1. Left Side: 3 Short Problem/Response Blocks (Width = 3.0")
    col1_x = Inches(0.80)
    col1_w = Inches(3.00)
    
    blocks = [
        ("REAL-WORLD PROBLEM", ACCENT_AMBER, [
            "Large satellite archives",
            "+ multi-temporal imagery",
            "+ multi-spectral data"
        ]),
        ("WHY IT IS HARD", ACCENT_RED, [
            "A difference may be caused by:",
            "vegetation, moisture,",
            "shadow, or atmosphere"
        ]),
        ("OUR RESPONSE", ACCENT_GREEN, [
            "TERRAE combines:",
            "semantic retrieval + temporal analysis",
            "+ spectral evidence + spatial topology"
        ])
    ]
    b_top = Inches(1.45)
    b_h = Inches(1.55)
    b_gap = Inches(0.14)
    for idx, (b_title, b_col, b_lines) in enumerate(blocks):
        by = b_top + idx * (b_h + b_gap)
        c = create_panel(slide, col1_x, by, col1_w, b_h, border_color=CARD_BORDER, bg_color=CARD_BG)
        tb = slide.shapes.add_textbox(col1_x + Inches(0.18), by + Inches(0.12), col1_w - Inches(0.36), b_h - Inches(0.24))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        p = tf.paragraphs[0]
        p.text = b_title
        p.font.name = FONT_MONO
        p.font.size = Pt(8.2)
        p.font.bold = True
        p.font.color.rgb = b_col

        for line in b_lines:
            p_l = tf.add_paragraph()
            p_l.space_before = Pt(2)
            r = p_l.add_run()
            r.text = line
            r.font.name = FONT_HEADING
            r.font.size = Pt(7.8)
            r.font.color.rgb = TEXT_DARK

    # 2. Center Column: Dominant 6-Stage Circular Investigation Diagram (Width = 5.2")
    col2_x = Inches(4.00)
    col2_w = Inches(5.20)
    col2_h = Inches(4.90)
    
    c_diag = create_panel(slide, col2_x, Inches(1.45), col2_w, col2_h, border_color=CARD_BORDER, bg_color=CARD_BG)

    # Diagram Header
    tb_dh = slide.shapes.add_textbox(col2_x + Inches(0.20), Inches(1.55), col2_w - Inches(0.40), Inches(0.30))
    tf_dh = tb_dh.text_frame
    tf_dh.margin_left = tf_dh.margin_top = tf_dh.margin_right = tf_dh.margin_bottom = 0
    p_dh = tf_dh.paragraphs[0]
    p_dh.alignment = PP_ALIGN.CENTER
    p_dh.text = "SIX-STAGE INVESTIGATION WORKFLOW"
    p_dh.font.name = FONT_MONO
    p_dh.font.size = Pt(9.0)
    p_dh.font.bold = True
    p_dh.font.color.rgb = NAVY_PRIMARY

    # Center Hub
    hub_w = Inches(2.10)
    hub_h = Inches(1.05)
    hub_x = col2_x + (col2_w - hub_w) / 2
    hub_y = Inches(3.38)
    hub = create_panel(slide, hub_x, hub_y, hub_w, hub_h, border_color=NAVY_PRIMARY, bg_color=NAVY_PRIMARY)
    tb_hub = slide.shapes.add_textbox(hub_x, hub_y + Inches(0.16), hub_w, hub_h - Inches(0.32))
    tf_hub = tb_hub.text_frame
    tf_hub.word_wrap = True
    tf_hub.margin_left = tf_hub.margin_top = tf_hub.margin_right = tf_hub.margin_bottom = 0
    p_h = tf_hub.paragraphs[0]
    p_h.alignment = PP_ALIGN.CENTER
    r_h = p_h.add_run()
    r_h.text = "TERRAE\nSATELLITE\nINVESTIGATION"
    r_h.font.name = FONT_MONO
    r_h.font.size = Pt(8.5)
    r_h.font.bold = True
    r_h.font.color.rgb = BG_WHITE

    # 6 Surrounding Nodes (Properly nested inside the container)
    stages = [
        ("01 ASK", "Natural Intent Query", col2_x + Inches(2.60), Inches(1.95), ACCENT_BLUE),
        ("02 DISCOVER", "RemoteCLIP + FAISS", col2_x + Inches(4.25), Inches(2.70), ACCENT_TEAL),
        ("03 COMPARE", "Calibrated Diff (τ=0.15)", col2_x + Inches(4.25), Inches(4.25), ACCENT_GREEN),
        ("04 EXPLAIN", "Spectral + Spatial Math", col2_x + Inches(2.60), Inches(5.10), ACCENT_GOLD),
        ("05 CHALLENGE", "3-Date Trajectory Check", col2_x + Inches(0.95), Inches(4.25), ACCENT_AMBER),
        ("06 DECIDE", "Conservative Verdict", col2_x + Inches(0.95), Inches(2.70), NAVY_PRIMARY)
    ]
    node_w = Inches(1.40)
    node_h = Inches(0.70)
    for st_num, st_desc, nx, ny, ncol in stages:
        c_n = create_panel(slide, nx - node_w/2, ny, node_w, node_h, border_color=ncol, bg_color=BG_WHITE, border_width=Pt(1.5))
        tb_n = slide.shapes.add_textbox(nx - node_w/2, ny + Inches(0.06), node_w, node_h - Inches(0.12))
        tf_n = tb_n.text_frame
        tf_n.word_wrap = True
        tf_n.margin_left = tf_n.margin_top = tf_n.margin_right = tf_n.margin_bottom = 0
        p1 = tf_n.paragraphs[0]
        p1.alignment = PP_ALIGN.CENTER
        r1 = p1.add_run()
        r1.text = f"{st_num}\n"
        r1.font.name = FONT_MONO
        r1.font.size = Pt(7.5)
        r1.font.bold = True
        r1.font.color.rgb = ncol

        p2 = tf_n.add_paragraph()
        p2.alignment = PP_ALIGN.CENTER
        r2 = p2.add_run()
        r2.text = st_desc
        r2.font.name = FONT_HEADING
        r2.font.size = Pt(6.8)
        r2.font.color.rgb = TEXT_DARK

    # Subtle Directional Flow Arrows between Stages
    loop_arrows = [
        (col2_x + Inches(3.55), Inches(2.25), "↘"),
        (col2_x + Inches(4.35), Inches(3.60), "↓"),
        (col2_x + Inches(3.55), Inches(4.85), "↙"),
        (col2_x + Inches(1.65), Inches(4.85), "↖"),
        (col2_x + Inches(0.85), Inches(3.60), "↑"),
        (col2_x + Inches(1.65), Inches(2.25), "↗"),
    ]
    for ax, ay, arr_sym in loop_arrows:
        tb_arr = slide.shapes.add_textbox(ax, ay, Inches(0.30), Inches(0.30))
        tf_arr = tb_arr.text_frame
        tf_arr.margin_left = tf_arr.margin_top = tf_arr.margin_right = tf_arr.margin_bottom = 0
        p_arr = tf_arr.paragraphs[0]
        p_arr.alignment = PP_ALIGN.CENTER
        r_arr = p_arr.add_run()
        r_arr.text = arr_sym
        r_arr.font.name = FONT_HEADING
        r_arr.font.size = Pt(13)
        r_arr.font.bold = True
        r_arr.font.color.rgb = CARD_BORDER

    # 3. Right Column: Problem ↔ TERRAE Response (Width = 3.1")
    col3_x = Inches(9.40)
    col3_w = Inches(3.133)

    tb_rh = slide.shapes.add_textbox(col3_x, Inches(1.45), col3_w, Inches(0.30))
    tf_rh = tb_rh.text_frame
    tf_rh.margin_left = tf_rh.margin_top = tf_rh.margin_right = tf_rh.margin_bottom = 0
    p_rh = tf_rh.paragraphs[0]
    p_rh.text = "PROBLEM ↔ TERRAE RESPONSE"
    p_rh.font.name = FONT_MONO
    p_rh.font.size = Pt(8.5)
    p_rh.font.bold = True
    p_rh.font.color.rgb = NAVY_PRIMARY

    comparisons = [
        ("MANUAL SEARCH", "SEMANTIC RETRIEVAL", "RemoteCLIP embeddings query 50+ satellite tiles across archives", ACCENT_BLUE),
        ("SINGLE BEFORE/AFTER", "MULTI-TEMPORAL CONTEXT", "T0 / TMID / T1 triplet stack suppresses seasonal phenology", ACCENT_TEAL),
        ("PIXEL DIFFERENCE", "SPECTRAL + SPATIAL", "NDVI, NDWI, NDBI indices combined with 8-conn spatial clusters", ACCENT_GREEN),
        ("OPAQUE RESULT", "EVIDENCE CHAIN", "Auditable spatial coherence, trajectory, and pixel breakdown", ACCENT_GOLD),
        ("FORCED DECISION", "SUPPORTED / REVIEW", "Conservative decision rules; abstain routing on low confidence", NAVY_PRIMARY)
    ]
    cb_top = Inches(1.80)
    cb_h = Inches(0.62)
    cb_gap = Inches(0.08)
    for idx, (p_txt, r_txt, desc_txt, col_acc) in enumerate(comparisons):
        cy = cb_top + idx * (cb_h + cb_gap)
        c_cmp = create_panel(slide, col3_x, cy, col3_w, cb_h, border_color=CARD_BORDER, bg_color=CARD_BG)
        tb_c = slide.shapes.add_textbox(col3_x + Inches(0.10), cy + Inches(0.04), col3_w - Inches(0.20), cb_h - Inches(0.08))
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

    # Workstation Telemetry Block
    t_box_top = Inches(5.35)
    c_ws = create_panel(slide, col3_x, t_box_top, col3_w, Inches(1.00), border_color=CARD_BORDER, bg_color=BG_IVORY)
    tb_ws = slide.shapes.add_textbox(col3_x + Inches(0.12), t_box_top + Inches(0.08), col3_w - Inches(0.24), Inches(0.84))
    tf_ws = tb_ws.text_frame
    tf_ws.word_wrap = True
    tf_ws.margin_left = tf_ws.margin_top = tf_ws.margin_right = tf_ws.margin_bottom = 0
    p_w = tf_ws.paragraphs[0]
    p_w.text = "VERIFIED CASE 01 TELEMETRY:"
    p_w.font.name = FONT_MONO
    p_w.font.size = Pt(7.2)
    p_w.font.bold = True
    p_w.font.color.rgb = ACCENT_GREEN

    p_w2 = tf_ws.add_paragraph()
    r = p_w2.add_run()
    r.text = (
        "• 7,549 px Changed (11.5%)  |  Spatial Coherence: 99.7%\n"
        "• Built Support: 97.1%  |  Trajectory: LATE_ONSET\n"
        "• System Verdict: ✔ SUPPORTED (High Coherence)"
    )
    r.font.name = FONT_BODY
    r.font.size = Pt(6.8)
    r.font.color.rgb = TEXT_DARK

    # Bottom Closing Statement & Access
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
    r_b1.font.size = Pt(11.0)
    r_b1.font.bold = True
    r_b1.font.color.rgb = NAVY_PRIMARY

    p_b2 = tf_bot.add_paragraph()
    p_b2.alignment = PP_ALIGN.CENTER
    r_b2 = p_b2.add_run()
    r_b2.text = f"Live Console: {URL_WEB}   |   GitHub: {URL_REPO}   |   Report: REPORT.md"
    r_b2.font.name = FONT_MONO
    r_b2.font.size = Pt(7.2)
    r_b2.font.color.rgb = TEXT_MUTED


# ---------------------------------------------------------------------------
# SLIDE 3: 03 — TECHNICAL APPROACH / METHODOLOGY & PROCESS OF IMPLEMENTATION
# ---------------------------------------------------------------------------
def build_slide_3(slide):
    add_sih_header(
        slide,
        "03 / 06",
        "03 — TECHNICAL APPROACH / METHODOLOGY & PROCESS OF IMPLEMENTATION",
        "SYSTEM ARCHITECTURE & MULTI-STREAM EVIDENCE PIPELINE"
    )

    # 1. Left Side: Investigation Loop (Vertical Flow, Width = 2.9")
    col1_x = Inches(0.80)
    col1_w = Inches(2.90)
    c_left = create_panel(slide, col1_x, Inches(1.45), col1_w, Inches(5.30), border_color=CARD_BORDER, bg_color=CARD_BG)

    tb_lh = slide.shapes.add_textbox(col1_x + Inches(0.15), Inches(1.55), col1_w - Inches(0.30), Inches(0.30))
    tf_lh = tb_lh.text_frame
    tf_lh.margin_left = tf_lh.margin_top = tf_lh.margin_right = tf_lh.margin_bottom = 0
    p = tf_lh.paragraphs[0]
    p.text = "METHODOLOGY LOOP"
    p.font.name = FONT_MONO
    p.font.size = Pt(8.5)
    p.font.bold = True
    p.font.color.rgb = NAVY_PRIMARY

    loop_items = [
        ("ASK", "Natural Language", "Parses operational intent"),
        ("DISCOVER", "RemoteCLIP + FAISS", "512-dim joint cosine retrieval"),
        ("COMPARE", "T0 / TMID / T1", "Multi-band spectral shift (τ=0.15)"),
        ("EXPLAIN", "Spectral + Spatial", "NDVI, NDWI & 8-conn topology"),
        ("CHALLENGE", "Temporal Evidence", "MECE trajectory persistence"),
        ("DECIDE", "Supported / Review", "Auditable conservative verdict")
    ]
    ly_top = Inches(1.95)
    ly_h = Inches(0.65)
    ly_gap = Inches(0.10)
    for idx, (st_name, st_short, st_sub) in enumerate(loop_items):
        cy = ly_top + idx * (ly_h + ly_gap)
        c_item = create_panel(slide, col1_x + Inches(0.15), cy, col1_w - Inches(0.30), ly_h, border_color=CARD_BORDER, bg_color=BG_WHITE)
        tb_i = slide.shapes.add_textbox(col1_x + Inches(0.25), cy + Inches(0.06), col1_w - Inches(0.50), ly_h - Inches(0.12))
        tf_i = tb_i.text_frame
        tf_i.word_wrap = True
        tf_i.margin_left = tf_i.margin_top = tf_i.margin_right = tf_i.margin_bottom = 0
        
        p = tf_i.paragraphs[0]
        r1 = p.add_run()
        r1.text = f"{st_name} "
        r1.font.name = FONT_MONO
        r1.font.size = Pt(7.5)
        r1.font.bold = True
        r1.font.color.rgb = ACCENT_BLUE if idx < 2 else (ACCENT_GREEN if idx < 4 else NAVY_PRIMARY)

        r2 = p.add_run()
        r2.text = f"· {st_short}\n"
        r2.font.name = FONT_HEADING
        r2.font.size = Pt(7.0)
        r2.font.bold = True
        r2.font.color.rgb = TEXT_DARK

        p2 = tf_i.add_paragraph()
        r3 = p2.add_run()
        r3.text = st_sub
        r3.font.name = FONT_BODY
        r3.font.size = Pt(6.5)
        r3.font.color.rgb = TEXT_MUTED

    # 2. Center Column: Main Technical Pipeline (LARGEST VISUAL, Width = 5.4")
    col2_x = Inches(3.90)
    col2_w = Inches(5.40)
    c_mid = create_panel(slide, col2_x, Inches(1.45), col2_w, Inches(5.30), border_color=CARD_BORDER, bg_color=CARD_BG)

    tb_mh = slide.shapes.add_textbox(col2_x + Inches(0.20), Inches(1.55), col2_w - Inches(0.40), Inches(0.30))
    tf_mh = tb_mh.text_frame
    tf_mh.margin_left = tf_mh.margin_top = tf_mh.margin_right = tf_mh.margin_bottom = 0
    p = tf_mh.paragraphs[0]
    p.text = "CORE SYSTEM PIPELINE (END-TO-END DATAFLOW)"
    p.font.name = FONT_MONO
    p.font.size = Pt(8.5)
    p.font.bold = True
    p.font.color.rgb = NAVY_PRIMARY

    # Vertical Step Pipeline
    pipeline_steps = [
        ("NATURAL LANGUAGE", "“new construction and buildings”", ACCENT_BLUE, None),
        ("REMOTECLIP ViT-B-32", "512-dim joint vision-language embedding", ACCENT_BLUE, None),
        ("FAISS FlatIP", "Nearest satellite tile cosine scan (2.0 ms)", ACCENT_TEAL, None),
        ("SATELLITE TILE", "MGRS 43RGM / EPSG:32643 10m UTM Grid", ACCENT_TEAL, "beirut_t1_rgb.jpg"),
        ("T0 / TMID / T1", "Multi-date temporal observation stack", ACCENT_GREEN, "sentinel2_tmid_rgb.jpg"),
        ("SPECTRAL CHANGE", "B02, B03, B04, B08 differencing (τ = 0.15)", ACCENT_GREEN, "evidence_02_mask.jpg"),
        ("SPATIAL COHERENCE", "8-connected topology + NDVI / NDWI math", ACCENT_GOLD, None),
        ("TEMPORAL TRAJECTORY", "MECE persistence classification (5 states)", ACCENT_AMBER, None),
        ("CONSERVATIVE VERDICT", "SUPPORTED / REVIEW / ABSTAIN", NAVY_PRIMARY, None)
    ]
    py_top = Inches(1.90)
    py_h = Inches(0.36)
    py_gap = Inches(0.18)
    for idx, (p_title, p_sub, p_col, img_name) in enumerate(pipeline_steps):
        sy = py_top + idx * (py_h + py_gap)
        c_step = create_panel(slide, col2_x + Inches(0.20), sy, col2_w - Inches(0.40), py_h, border_color=CARD_BORDER, bg_color=BG_WHITE)
        
        # Text box
        text_w = col2_w - Inches(0.80) if img_name is None else col2_w - Inches(1.30)
        tb_st = slide.shapes.add_textbox(col2_x + Inches(0.30), sy + Inches(0.04), text_w, py_h - Inches(0.08))
        tf_st = tb_st.text_frame
        tf_st.word_wrap = True
        tf_st.margin_left = tf_st.margin_top = tf_st.margin_right = tf_st.margin_bottom = 0
        p = tf_st.paragraphs[0]
        
        r1 = p.add_run()
        r1.text = f"{p_title}  "
        r1.font.name = FONT_MONO
        r1.font.size = Pt(7.2)
        r1.font.bold = True
        r1.font.color.rgb = p_col

        r2 = p.add_run()
        r2.text = f"➔  {p_sub}"
        r2.font.name = FONT_BODY
        r2.font.size = Pt(7.0)
        r2.font.color.rgb = TEXT_DARK

        # Real satellite thumbnail chip if available
        if img_name:
            thumb_path = os.path.join(ASSETS_DIR, img_name)
            safe_add_image(slide, thumb_path, col2_x + col2_w - Inches(0.65), sy + Inches(0.02), Inches(0.32), Inches(0.32))

        # Down arrow connector
        if idx < len(pipeline_steps) - 1:
            arr_y = sy + py_h + Inches(0.01)
            tb_a = slide.shapes.add_textbox(col2_x + col2_w/2 - Inches(0.20), arr_y, Inches(0.40), py_gap)
            tf_a = tb_a.text_frame
            tf_a.margin_left = tf_a.margin_top = tf_a.margin_right = tf_a.margin_bottom = 0
            p_a = tf_a.paragraphs[0]
            p_a.alignment = PP_ALIGN.CENTER
            r_a = p_a.add_run()
            r_a.text = "↓"
            r_a.font.name = FONT_HEADING
            r_a.font.size = Pt(9)
            r_a.font.bold = True
            r_a.font.color.rgb = CARD_BORDER

    # 3. Right Column: Technologies Used (4 Simple Illustrated Bands, Width = 3.0")
    col3_x = Inches(9.50)
    col3_w = Inches(3.033)
    c_right = create_panel(slide, col3_x, Inches(1.45), col3_w, Inches(5.30), border_color=CARD_BORDER, bg_color=CARD_BG)

    tb_rh = slide.shapes.add_textbox(col3_x + Inches(0.15), Inches(1.55), col3_w - Inches(0.30), Inches(0.30))
    tf_rh = tb_rh.text_frame
    tf_rh.margin_left = tf_rh.margin_top = tf_rh.margin_right = tf_rh.margin_bottom = 0
    p = tf_rh.paragraphs[0]
    p.text = "TECHNOLOGIES USED"
    p.font.name = FONT_MONO
    p.font.size = Pt(8.5)
    p.font.bold = True
    p.font.color.rgb = NAVY_PRIMARY

    tech_bands = [
        ("SEMANTIC RETRIEVAL", ACCENT_BLUE, "RemoteCLIP + FAISS", "Vision-language cross-modal embeddings + CPU vector indexing"),
        ("GEOSPATIAL", ACCENT_GREEN, "Rasterio + NumPy + SciPy", "GDAL bindings, surface reflectance math, 8-conn topology"),
        ("TEMPORAL / VALIDATION", ACCENT_GOLD, "Sentinel-2 + OSCD + SQLite", "10m BOA reflectance, MGRS grid, MECE trajectory classifier"),
        ("OFFLINE-FIRST", NAVY_PRIMARY, "Python + Streamlit + Local Models", "Air-gapped operation with zero external runtime calls")
    ]
    ty_top = Inches(1.95)
    ty_h = Inches(1.10)
    ty_gap = Inches(0.15)
    for idx, (t_name, t_col, t_tools, t_desc) in enumerate(tech_bands):
        cy = ty_top + idx * (ty_h + ty_gap)
        c_tb = create_panel(slide, col3_x + Inches(0.15), cy, col3_w - Inches(0.30), ty_h, border_color=CARD_BORDER, bg_color=BG_WHITE)
        tb_t = slide.shapes.add_textbox(col3_x + Inches(0.25), cy + Inches(0.10), col3_w - Inches(0.50), ty_h - Inches(0.20))
        tf_t = tb_t.text_frame
        tf_t.word_wrap = True
        tf_t.margin_left = tf_t.margin_top = tf_t.margin_right = tf_t.margin_bottom = 0
        
        p = tf_t.paragraphs[0]
        p.text = t_name
        p.font.name = FONT_MONO
        p.font.size = Pt(7.5)
        p.font.bold = True
        p.font.color.rgb = t_col

        p2 = tf_t.add_paragraph()
        r1 = p2.add_run()
        r1.text = t_tools
        r1.font.name = FONT_HEADING
        r1.font.size = Pt(8.0)
        r1.font.bold = True
        r1.font.color.rgb = TEXT_DARK

        p3 = tf_t.add_paragraph()
        r2 = p3.add_run()
        r2.text = t_desc
        r2.font.name = FONT_BODY
        r2.font.size = Pt(6.8)
        r2.font.color.rgb = TEXT_MUTED


# ---------------------------------------------------------------------------
# SLIDE 4: 04 — FEASIBILITY & VIABILITY
# ---------------------------------------------------------------------------
def build_slide_4(slide):
    add_sih_header(
        slide,
        "04 / 06",
        "04 — FEASIBILITY & VIABILITY",
        "BUILT TO RUN LOCALLY. VALIDATED ON REAL SENTINEL-2."
    )

    # 1. Left Side: Feasibility (3 Large Blocks, Width = 2.6")
    col1_x = Inches(0.80)
    col1_w = Inches(2.60)

    tb_fh = slide.shapes.add_textbox(col1_x, Inches(1.45), col1_w, Inches(0.30))
    tf_fh = tb_fh.text_frame
    tf_fh.margin_left = tf_fh.margin_top = tf_fh.margin_right = tf_fh.margin_bottom = 0
    p = tf_fh.paragraphs[0]
    p.text = "FEASIBILITY"
    p.font.name = FONT_MONO
    p.font.size = Pt(8.5)
    p.font.bold = True
    p.font.color.rgb = NAVY_PRIMARY

    f_blocks = [
        ("LOCAL AI", ACCENT_BLUE, "RemoteCLIP + FAISS", "Runs on standard CPU\n8–16 GB RAM footprint"),
        ("REAL DATA", ACCENT_GREEN, "Sentinel-2A · 10m", "Level-2A BOA Surface\nB02, B03, B04, B08"),
        ("DETERMINISTIC", ACCENT_GOLD, "Threshold τ = 0.15", "NDVI & NDWI math\nZero hallucination")
    ]
    fb_top = Inches(1.80)
    fb_h = Inches(1.45)
    fb_gap = Inches(0.14)
    for idx, (b_title, b_col, b_main, b_sub) in enumerate(f_blocks):
        by = fb_top + idx * (fb_h + fb_gap)
        c = create_panel(slide, col1_x, by, col1_w, fb_h, border_color=CARD_BORDER, bg_color=CARD_BG)
        tb = slide.shapes.add_textbox(col1_x + Inches(0.15), by + Inches(0.12), col1_w - Inches(0.30), fb_h - Inches(0.24))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p = tf.paragraphs[0]
        p.text = b_title
        p.font.name = FONT_MONO
        p.font.size = Pt(7.5)
        p.font.bold = True
        p.font.color.rgb = b_col

        p2 = tf.add_paragraph()
        r1 = p2.add_run()
        r1.text = b_main
        r1.font.name = FONT_HEADING
        r1.font.size = Pt(8.5)
        r1.font.bold = True
        r1.font.color.rgb = TEXT_DARK

        p3 = tf.add_paragraph()
        p3.space_before = Pt(2)
        r2 = p3.add_run()
        r2.text = b_sub
        r2.font.name = FONT_BODY
        r2.font.size = Pt(7.0)
        r2.font.color.rgb = TEXT_MUTED

    # 2. Center Column: Real Sentinel-2 Validation Timeline (HERO OF SLIDE 4, Width = 6.2")
    col2_x = Inches(3.60)
    col2_w = Inches(6.15)

    tb_vh = slide.shapes.add_textbox(col2_x, Inches(1.45), col2_w, Inches(0.30))
    tf_vh = tb_vh.text_frame
    tf_vh.margin_left = tf_vh.margin_top = tf_vh.margin_right = tf_vh.margin_bottom = 0
    p = tf_vh.paragraphs[0]
    p.text = "REAL SENTINEL-2 MULTI-DATE VALIDATION (MGRS 43RGM · NCR INDIA)"
    p.font.name = FONT_MONO
    p.font.size = Pt(8.5)
    p.font.bold = True
    p.font.color.rgb = NAVY_PRIMARY

    # 3 Large Real Images Side-by-Side (1:1 Proportions, Width = 1.85" each)
    img_w = Inches(1.85)
    img_h = Inches(1.85)
    img_gap = Inches(0.18)
    img_top = Inches(1.80)

    tri_data = [
        ("T0 · 19 MAY 2023", "Pre-Monsoon Dry Baseline", "sentinel2_t0_rgb.jpg"),
        ("TMID · 06 OCT 2023", "Post-Monsoon Green Peak", "sentinel2_tmid_rgb.jpg"),
        ("T1 · 05 DEC 2023", "Winter Post-Harvest", "sentinel2_t1_rgb.jpg")
    ]
    for idx, (t_date, t_desc, t_file) in enumerate(tri_data):
        ix = col2_x + idx * (img_w + img_gap)
        safe_add_image(slide, os.path.join(ASSETS_DIR, t_file), ix, img_top, img_w, img_h)

        # Label box underneath image
        c_lbl = create_panel(slide, ix, img_top + img_h + Inches(0.06), img_w, Inches(0.55), border_color=CARD_BORDER, bg_color=CARD_BG)
        tb_l = slide.shapes.add_textbox(ix + Inches(0.05), img_top + img_h + Inches(0.08), img_w - Inches(0.10), Inches(0.50))
        tf_l = tb_l.text_frame
        tf_l.word_wrap = True
        tf_l.margin_left = tf_l.margin_top = tf_l.margin_right = tf_l.margin_bottom = 0
        p_l = tf_l.paragraphs[0]
        p_l.alignment = PP_ALIGN.CENTER
        
        r1 = p_l.add_run()
        r1.text = f"{t_date}\n"
        r1.font.name = FONT_MONO
        r1.font.size = Pt(7.0)
        r1.font.bold = True
        r1.font.color.rgb = NAVY_PRIMARY

        r2 = p_l.add_run()
        r2.text = t_desc
        r2.font.name = FONT_BODY
        r2.font.size = Pt(6.5)
        r2.font.color.rgb = TEXT_MUTED

    # Connecting arrows between images
    for idx in range(2):
        arr_x = col2_x + img_w + idx * (img_w + img_gap) + Inches(0.03)
        tb_a = slide.shapes.add_textbox(arr_x, img_top + Inches(0.80), img_gap - Inches(0.06), Inches(0.30))
        tf_a = tb_a.text_frame
        tf_a.margin_left = tf_a.margin_top = tf_a.margin_right = tf_a.margin_bottom = 0
        p_a = tf_a.paragraphs[0]
        p_a.alignment = PP_ALIGN.CENTER
        r_a = p_a.add_run()
        r_a.text = "➔"
        r_a.font.name = FONT_HEADING
        r_a.font.size = Pt(12)
        r_a.font.bold = True
        r_a.font.color.rgb = ACCENT_GOLD

    # Empirical Results Banner Underneath
    res_top = Inches(4.35)
    c_res = create_panel(slide, col2_x, res_top, col2_w, Inches(2.05), border_color=CARD_BORDER, bg_color=CARD_BG)
    tb_r = slide.shapes.add_textbox(col2_x + Inches(0.20), res_top + Inches(0.12), col2_w - Inches(0.40), Inches(1.85))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True
    tf_r.margin_left = tf_r.margin_top = tf_r.margin_right = tf_r.margin_bottom = 0

    p = tf_r.paragraphs[0]
    p.text = "EMPIRICAL OBSERVATION METRICS (262,144 VALID PIXELS · 10M GSD)"
    p.font.name = FONT_MONO
    p.font.size = Pt(8.0)
    p.font.bold = True
    p.font.color.rgb = NAVY_PRIMARY

    p_deltas = tf_r.add_paragraph()
    p_deltas.space_before = Pt(3)
    r = p_deltas.add_run()
    r.text = "0.7% (T0 → TMID)    |    0.2% (TMID → T1)    |    1.0% (T0 → T1)"
    r.font.name = FONT_MONO
    r.font.size = Pt(8.5)
    r.font.bold = True
    r.font.color.rgb = ACCENT_AMBER

    p_main = tf_r.add_paragraph()
    p_main.space_before = Pt(3)
    r1 = p_main.add_run()
    r1.text = "98.75% STABLE    "
    r1.font.name = FONT_HEADING
    r1.font.size = Pt(11.0)
    r1.font.bold = True
    r1.font.color.rgb = ACCENT_GREEN

    r2 = p_main.add_run()
    r2.text = "VERDICT: REVIEW (Ambiguous phenology routed to human analyst)"
    r2.font.name = FONT_MONO
    r2.font.size = Pt(8.0)
    r2.font.bold = True
    r2.font.color.rgb = ACCENT_AMBER

    p_attr = tf_r.add_paragraph()
    p_attr.space_before = Pt(4)
    r3 = p_attr.add_run()
    r3.text = "Attribution Support:  Built 51.1%  |  Vegetation 24.7%  |  Seasonal 19.9%  |  Unresolved 3.1%"
    r3.font.name = FONT_MONO
    r3.font.size = Pt(7.5)
    r3.font.color.rgb = TEXT_DARK

    # Horizontal color breakdown bar
    bar_y = res_top + Inches(1.65)
    bar_total_w = col2_w - Inches(0.40)
    bar_x = col2_x + Inches(0.20)
    bar_h = Inches(0.12)
    # Segments: Built 51.1%, Veg 24.7%, Seasonal 19.9%, Unresolved 3.1%
    segs = [
        (0.511, ACCENT_GOLD),
        (0.247, ACCENT_GREEN),
        (0.199, ACCENT_AMBER),
        (0.043, CARD_BORDER)
    ]
    cur_x = bar_x
    for frac, seg_col in segs:
        seg_w = bar_total_w * frac
        s_rect = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, cur_x, bar_y, seg_w, bar_h)
        s_rect.fill.solid()
        s_rect.fill.fore_color.rgb = seg_col
        s_rect.line.fill.background()
        cur_x += seg_w

    # 3. Right Side: Viability (4 Clean Blocks, Width = 2.6")
    col3_x = Inches(9.95)
    col3_w = Inches(2.583)

    tb_vh2 = slide.shapes.add_textbox(col3_x, Inches(1.45), col3_w, Inches(0.30))
    tf_vh2 = tb_vh2.text_frame
    tf_vh2.margin_left = tf_vh2.margin_top = tf_vh2.margin_right = tf_vh2.margin_bottom = 0
    p = tf_vh2.paragraphs[0]
    p.text = "VIABILITY"
    p.font.name = FONT_MONO
    p.font.size = Pt(8.5)
    p.font.bold = True
    p.font.color.rgb = NAVY_PRIMARY

    v_blocks = [
        ("OFFLINE-FIRST", ACCENT_BLUE, "Air-gapped operation; zero cloud egress"),
        ("ANALYST-IN-LOOP", ACCENT_GREEN, "Review ambiguous evidence; no black box"),
        ("MODULAR", ACCENT_GOLD, "Decoupled index, sensor & persistence code"),
        ("EXTENSIBLE", NAVY_PRIMARY, "Supports SAR, thermal & dense time series")
    ]
    vb_top = Inches(1.80)
    vb_h = Inches(1.04)
    vb_gap = Inches(0.12)
    for idx, (v_title, v_col, v_desc) in enumerate(v_blocks):
        by = vb_top + idx * (vb_h + vb_gap)
        c = create_panel(slide, col3_x, by, col3_w, vb_h, border_color=CARD_BORDER, bg_color=CARD_BG)
        tb = slide.shapes.add_textbox(col3_x + Inches(0.15), by + Inches(0.10), col3_w - Inches(0.30), vb_h - Inches(0.20))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p = tf.paragraphs[0]
        p.text = v_title
        p.font.name = FONT_MONO
        p.font.size = Pt(7.5)
        p.font.bold = True
        p.font.color.rgb = v_col

        p2 = tf.add_paragraph()
        r = p2.add_run()
        r.text = v_desc
        r.font.name = FONT_BODY
        r.font.size = Pt(7.0)
        r.font.color.rgb = TEXT_DARK

    # 4. Bottom Proof Strip (Full Width)
    bot_y = Inches(6.50)
    c_bot = create_panel(slide, Inches(0.80), bot_y, Inches(11.733), Inches(0.48), border_color=CARD_BORDER, bg_color=BG_IVORY)
    tb_b = slide.shapes.add_textbox(Inches(0.90), bot_y + Inches(0.06), Inches(11.533), Inches(0.36))
    tf_b = tb_b.text_frame
    tf_b.margin_left = tf_b.margin_top = tf_b.margin_right = tf_b.margin_bottom = 0
    p = tf_b.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER

    proof_badges = [
        ("135 / 135 TESTS PASSING", ACCENT_GREEN),
        ("ZERO RUNTIME EXTERNAL CALLS", ACCENT_BLUE),
        ("262,144 VALID PIXELS", ACCENT_GOLD),
        ("DETERMINISTIC τ = 0.15", NAVY_PRIMARY)
    ]
    for b_txt, b_col in proof_badges:
        r = p.add_run()
        r.text = f"[{b_txt}]   "
        r.font.name = FONT_MONO
        r.font.size = Pt(8.0)
        r.font.bold = True
        r.font.color.rgb = b_col


# ---------------------------------------------------------------------------
# SLIDE 5: 05 — IMPACT & BENEFITS
# ---------------------------------------------------------------------------
def build_slide_5(slide):
    add_sih_header(
        slide,
        "05 / 06",
        "05 — IMPACT & BENEFITS",
        "TURNING SATELLITE ARCHIVES INTO AN INVESTIGATION WORKBENCH"
    )

    # 1. Center-Top: ONE LARGE IMPACT FLOW (Full Width)
    flow_top = Inches(1.45)
    flow_h = Inches(0.95)
    c_flow = create_panel(slide, Inches(0.80), flow_top, Inches(11.733), flow_h, border_color=CARD_BORDER, bg_color=CARD_BG)
    
    flow_steps = [
        ("SATELLITE ARCHIVE", "Sentinel-2 & SAR tiles", NAVY_PRIMARY, "hero_beirut_1920x1080.jpg"),
        ("SEMANTIC DISCOVERY", "RemoteCLIP prompt", ACCENT_BLUE, None),
        ("RELEVANT SCENE", "Ranked candidates", ACCENT_TEAL, None),
        ("TEMPORAL COMPARISON", "Calibrated change", ACCENT_GREEN, None),
        ("EVIDENCE REVIEW", "Spectral attribution", ACCENT_GOLD, None),
        ("ANALYST DECISION", "Actionable verdict", NAVY_PRIMARY, None)
    ]
    step_w = Inches(1.70)
    gap = Inches(0.25)
    start_x = Inches(0.95)
    for idx, (st_name, st_sub, st_col, thumb_img) in enumerate(flow_steps):
        bx = start_x + idx * (step_w + gap)
        c_node = create_panel(slide, bx, flow_top + Inches(0.18), step_w, Inches(0.58), border_color=st_col, bg_color=BG_WHITE, border_width=Pt(1.5))
        
        # Real satellite thumbnail for stage 1
        if thumb_img:
            safe_add_image(slide, os.path.join(ASSETS_DIR, thumb_img), bx + Inches(0.05), flow_top + Inches(0.23), Inches(0.48), Inches(0.48))
            tb = slide.shapes.add_textbox(bx + Inches(0.56), flow_top + Inches(0.22), step_w - Inches(0.58), Inches(0.50))
        else:
            tb = slide.shapes.add_textbox(bx + Inches(0.04), flow_top + Inches(0.22), step_w - Inches(0.08), Inches(0.50))
        
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT if thumb_img else PP_ALIGN.CENTER
        r = p.add_run()
        r.text = st_name
        r.font.name = FONT_MONO
        r.font.size = Pt(6.4)
        r.font.bold = True
        r.font.color.rgb = st_col

        p2 = tf.add_paragraph()
        p2.alignment = PP_ALIGN.LEFT if thumb_img else PP_ALIGN.CENTER
        p2.space_before = Pt(1.5)
        r2 = p2.add_run()
        r2.text = st_sub
        r2.font.name = FONT_BODY
        r2.font.size = Pt(5.8)
        r2.font.color.rgb = TEXT_DARK

        if idx < len(flow_steps) - 1:
            arr_x = bx + step_w + Inches(0.04)
            tb_a = slide.shapes.add_textbox(arr_x, flow_top + Inches(0.25), gap - Inches(0.08), Inches(0.40))
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
    grid_top = Inches(2.55)
    card_w = Inches(5.72)
    card_h = Inches(1.80)
    gap_x = Inches(0.29)
    gap_y = Inches(0.16)

    use_cases = [
        ("01 / INFRASTRUCTURE MONITORING", ACCENT_BLUE,
         "Forward Outpost, Tarmac & Fortified Perimeter Detection",
         "Quickly discovers clandestine military construction, border tarmac paving, and fortified forward compounds. Natural-language intent isolates candidate tiles across thousands of sq km without coordinate guessing.",
         "controlled_t2_rgb.jpg"),
        
        ("02 / STRATEGIC SITE DISCOVERY", ACCENT_TEAL,
         "Cross-Theater Facility Pattern Matching",
         "Query the RemoteCLIP FAISS vector index to discover geographically separated candidate sites sharing identical visual-semantic patterns across the theater, cutting manual catalog triage by hours.",
         "bordeaux_t1_rgb.jpg"),
        
        ("03 / ROAD / TERRAIN CORRIDOR CHANGE", ACCENT_GREEN,
         "Frontier Logistics Tracks, Earth Clearings & Bridgeheads",
         "Tracks emerging logistics road corridors and supply clearings across rugged terrain. Spatial coherence analysis confirms contiguous linear infrastructure while suppressing single-pixel seasonal slope washouts.",
         "mumbai_t1_rgb.jpg"),
        
        ("04 / VEGETATION / WATER INTERPRETATION", ACCENT_GOLD,
         "Defending Against False-Alarm Alert Fatigue",
         "Enforces 3-date MECE persistence trajectories to distinguish agricultural crop cycles (monsoon greening to harvest senescence) from permanent land-cover conversion, protecting command staff from false alarms.",
         "sentinel2_tmid_rgb.jpg")
    ]

    for idx, (u_title, u_col, u_sub, u_desc, thumb_file) in enumerate(use_cases):
        row = idx // 2
        col = idx % 2
        x = Inches(0.80) + col * (card_w + gap_x)
        y = grid_top + row * (card_h + gap_y)

        c = create_panel(slide, x, y, card_w, card_h, border_color=CARD_BORDER, bg_color=CARD_BG)
        
        # Insert authentic satellite thumbnail inside each use case card
        thumb_dim = Inches(1.20)
        safe_add_image(slide, os.path.join(ASSETS_DIR, thumb_file), x + Inches(0.15), y + Inches(0.30), thumb_dim, thumb_dim)

        tb = slide.shapes.add_textbox(x + Inches(1.45), y + Inches(0.12), card_w - Inches(1.60), card_h - Inches(0.24))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p = tf.paragraphs[0]
        p.text = u_title
        p.font.name = FONT_MONO
        p.font.size = Pt(7.8)
        p.font.bold = True
        p.font.color.rgb = u_col

        p2 = tf.add_paragraph()
        p2.space_before = Pt(2)
        r_sub = p2.add_run()
        r_sub.text = u_sub
        r_sub.font.name = FONT_HEADING
        r_sub.font.size = Pt(8.2)
        r_sub.font.bold = True
        r_sub.font.color.rgb = TEXT_DARK

        p3 = tf.add_paragraph()
        p3.space_before = Pt(2)
        r_desc = p3.add_run()
        r_desc.text = u_desc
        r_desc.font.name = FONT_BODY
        r_desc.font.size = Pt(7.0)
        r_desc.font.color.rgb = TEXT_MUTED

    # 3. Bottom Principles & Closing Philosophy Banner
    bot_y = Inches(6.45)
    c_bot = create_panel(slide, Inches(0.80), bot_y, Inches(11.733), Inches(0.55), border_color=CARD_BORDER, bg_color=BG_IVORY)
    tb_bot = slide.shapes.add_textbox(Inches(0.90), bot_y + Inches(0.06), Inches(11.533), Inches(0.42))
    tf_bot = tb_bot.text_frame
    tf_bot.word_wrap = True
    tf_bot.margin_left = tf_bot.margin_top = tf_bot.margin_right = tf_bot.margin_bottom = 0

    p = tf_bot.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r_hdr = p.add_run()
    r_hdr.text = "CORE DEFENSE PRINCIPLES:   [OFFLINE]   [AUDITABLE]   [CONSERVATIVE]\n"
    r_hdr.font.name = FONT_MONO
    r_hdr.font.size = Pt(7.5)
    r_hdr.font.bold = True
    r_hdr.font.color.rgb = NAVY_PRIMARY

    p2 = tf_bot.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    r2 = p2.add_run()
    r2.text = "“The goal is not to make every result positive. The goal is to make the result explainable.”"
    r2.font.name = FONT_TITLE
    r2.font.size = Pt(9.5)
    r2.font.bold = True
    r2.font.color.rgb = ACCENT_GOLD


# ---------------------------------------------------------------------------
# SLIDE 6: 06 — RESEARCH & REFERENCES
# ---------------------------------------------------------------------------
def build_slide_6(slide):
    add_sih_header(
        slide,
        "06 / 06",
        "06 — RESEARCH & REFERENCES",
        "EMPIRICAL BENCHMARKS, RESEARCH FOUNDATIONS & PROJECT ACCESS"
    )

    card_top = Inches(1.45)
    card_h = Inches(4.85)

    # 1. Left Column: Research Foundation Diagram (Width = 3.3")
    col1_x = Inches(0.80)
    col1_w = Inches(3.30)
    c_rf = create_panel(slide, col1_x, card_top, col1_w, card_h, border_color=CARD_BORDER, bg_color=CARD_BG)

    tb_rf = slide.shapes.add_textbox(col1_x + Inches(0.15), card_top + Inches(0.12), col1_w - Inches(0.30), Inches(0.30))
    tf_rf = tb_rf.text_frame
    tf_rf.margin_left = tf_rf.margin_top = tf_rf.margin_right = tf_rf.margin_bottom = 0
    p = tf_rf.paragraphs[0]
    p.text = "RESEARCH FOUNDATION FLOW"
    p.font.name = FONT_MONO
    p.font.size = Pt(8.5)
    p.font.bold = True
    p.font.color.rgb = NAVY_PRIMARY

    flow_nodes = [
        ("REMOTECLIP", "Chen et al., IEEE TGRS 2024", "Vision-language foundation model for remote sensing retrieval"),
        ("SENTINEL-2", "ESA Copernicus 10m L2A", "Bottom-Of-Atmosphere calibrated multispectral surface reflectance"),
        ("OSCD BENCHMARK", "Daudt et al., IEEE IGARSS 2018", "Onera Satellite Change Detection standardized ground truth"),
        ("NDVI / NDWI", "Rouse et al. / McFeeters", "Biophysical normalized difference band ratio indices"),
        ("TERRAE CONSOLE", "Quantumcrew SIH26227", "Evidence-based satellite investigation workstation")
    ]
    fn_top = card_top + Inches(0.50)
    fn_h = Inches(0.72)
    fn_gap = Inches(0.12)
    for idx, (n_title, n_auth, n_desc) in enumerate(flow_nodes):
        ny = fn_top + idx * (fn_h + fn_gap)
        c_fn = create_panel(slide, col1_x + Inches(0.15), ny, col1_w - Inches(0.30), fn_h, border_color=CARD_BORDER, bg_color=BG_WHITE)
        tb_fn = slide.shapes.add_textbox(col1_x + Inches(0.22), ny + Inches(0.06), col1_w - Inches(0.44), fn_h - Inches(0.12))
        tf_fn = tb_fn.text_frame
        tf_fn.word_wrap = True
        tf_fn.margin_left = tf_fn.margin_top = tf_fn.margin_right = tf_fn.margin_bottom = 0

        p = tf_fn.paragraphs[0]
        r1 = p.add_run()
        r1.text = f"{n_title} "
        r1.font.name = FONT_MONO
        r1.font.size = Pt(7.5)
        r1.font.bold = True
        r1.font.color.rgb = NAVY_PRIMARY if idx == 4 else ACCENT_BLUE

        r2 = p.add_run()
        r2.text = f"({n_auth})\n"
        r2.font.name = FONT_BODY
        r2.font.size = Pt(6.8)
        r2.font.color.rgb = TEXT_MUTED

        p2 = tf_fn.add_paragraph()
        r3 = p2.add_run()
        r3.text = n_desc
        r3.font.name = FONT_BODY
        r3.font.size = Pt(6.5)
        r3.font.color.rgb = TEXT_DARK

        if idx < len(flow_nodes) - 1:
            arr_y = ny + fn_h
            tb_a = slide.shapes.add_textbox(col1_x + col1_w/2 - Inches(0.20), arr_y, Inches(0.40), fn_gap)
            tf_a = tb_a.text_frame
            tf_a.margin_left = tf_a.margin_top = tf_a.margin_right = tf_a.margin_bottom = 0
            p_a = tf_a.paragraphs[0]
            p_a.alignment = PP_ALIGN.CENTER
            r_a = p_a.add_run()
            r_a.text = "↓"
            r_a.font.name = FONT_HEADING
            r_a.font.size = Pt(8)
            r_a.font.bold = True
            r_a.font.color.rgb = CARD_BORDER

    # 2. Center Column: Validated Evidence (Width = 4.9")
    col2_x = Inches(4.25)
    col2_w = Inches(4.90)
    c_ev = create_panel(slide, col2_x, card_top, col2_w, card_h, border_color=CARD_BORDER, bg_color=CARD_BG)

    tb_eh = slide.shapes.add_textbox(col2_x + Inches(0.18), card_top + Inches(0.12), col2_w - Inches(0.36), Inches(0.30))
    tf_eh = tb_eh.text_frame
    tf_eh.margin_left = tf_eh.margin_top = tf_eh.margin_right = tf_eh.margin_bottom = 0
    p = tf_eh.paragraphs[0]
    p.text = "VALIDATED EMPIRICAL EVIDENCE"
    p.font.name = FONT_MONO
    p.font.size = Pt(8.5)
    p.font.bold = True
    p.font.color.rgb = NAVY_PRIMARY

    # Case 1: Real Sentinel-2 Card
    c_s2 = create_panel(slide, col2_x + Inches(0.15), card_top + Inches(0.48), col2_w - Inches(0.30), Inches(1.75), border_color=CARD_BORDER, bg_color=BG_WHITE)
    tb_s2 = slide.shapes.add_textbox(col2_x + Inches(0.25), card_top + Inches(0.55), col2_w - Inches(0.50), Inches(1.60))
    tf_s2 = tb_s2.text_frame
    tf_s2.word_wrap = True
    tf_s2.margin_left = tf_s2.margin_top = tf_s2.margin_right = tf_s2.margin_bottom = 0
    
    p = tf_s2.paragraphs[0]
    p.text = "1. REAL SENTINEL-2 (MGRS 43RGM · NCR INDIA)"
    p.font.name = FONT_MONO
    p.font.size = Pt(8.0)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN

    p_s2_body = tf_s2.add_paragraph()
    p_s2_body.space_before = Pt(3)
    r = p_s2_body.add_run()
    r.text = (
        "• Analysis Tile: 512×512 (262,144 valid pixels · 10m GSD)\n"
        "• Observations: T0 (19 May 2023), TMID (06 Oct 2023), T1 (05 Dec 2023)\n"
        "• Change Fractions: T0→TMID: 0.7% | TMID→T1: 0.2% | T0→T1: 1.0%\n"
        "• Trajectory Distribution: STABLE = 98.75% (258,869 px)\n"
        "• Attribution: Built 51.1% | Veg 24.7% | Seasonal 19.9% | Unresolved 3.1%\n"
        "• System Verdict: REVIEW (Conservative routing on 1.0% change)"
    )
    r.font.name = FONT_BODY
    r.font.size = Pt(7.0)
    r.font.color.rgb = TEXT_DARK

    # Case 2: OSCD Benchmark Card
    c_oscd = create_panel(slide, col2_x + Inches(0.15), card_top + Inches(2.35), col2_w - Inches(0.30), Inches(2.35), border_color=CARD_BORDER, bg_color=BG_WHITE)
    tb_oscd = slide.shapes.add_textbox(col2_x + Inches(0.25), card_top + Inches(2.42), col2_w - Inches(0.50), Inches(2.20))
    tf_oscd = tb_oscd.text_frame
    tf_oscd.word_wrap = True
    tf_oscd.margin_left = tf_oscd.margin_top = tf_oscd.margin_right = tf_oscd.margin_bottom = 0

    p = tf_oscd.paragraphs[0]
    p.text = "2. OSCD BENCHMARK — 5-PAIR VALIDATION SUBSET"
    p.font.name = FONT_MONO
    p.font.size = Pt(8.0)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE

    p_oscd_body = tf_oscd.add_paragraph()
    p_oscd_body.space_before = Pt(3)
    r = p_oscd_body.add_run()
    r.text = (
        "• Pairs: Aguas Claras, Beirut, Bordeaux, Cupertino, Mumbai\n"
        "• Valid Pixels Evaluated: 3,025,938 valid pixels | Fixed τ = 0.15\n\n"
        "QUANTITATIVE BENCHMARK METRICS:\n"
        "• Micro Aggregate: Precision 57.55% | Recall 9.72% | F1 0.1663 | IoU 0.0907\n"
        "• Macro Average:   Precision 52.22% | Recall 7.84% | F1 0.1267 | IoU 0.0692\n\n"
        "Class Imbalance Note: Accuracy (97.90%) is dominated by 97.64% unchanged ground truth. Low recall reflects conservative noise suppression."
    )
    r.font.name = FONT_BODY
    r.font.size = Pt(7.0)
    r.font.color.rgb = TEXT_DARK

    # 3. Right Column: Project Access & References (Width = 3.283")
    col3_x = Inches(9.30)
    col3_w = Inches(3.233)
    c_pa = create_panel(slide, col3_x, card_top, col3_w, card_h, border_color=CARD_BORDER, bg_color=CARD_BG)

    tb_pah = slide.shapes.add_textbox(col3_x + Inches(0.15), card_top + Inches(0.12), col3_w - Inches(0.30), Inches(0.30))
    tf_pah = tb_pah.text_frame
    tf_pah.margin_left = tf_pah.margin_top = tf_pah.margin_right = tf_pah.margin_bottom = 0
    p = tf_pah.paragraphs[0]
    p.text = "PROJECT ACCESS & REFERENCES"
    p.font.name = FONT_MONO
    p.font.size = Pt(8.5)
    p.font.bold = True
    p.font.color.rgb = NAVY_PRIMARY

    # Project Links Box
    c_pl = create_panel(slide, col3_x + Inches(0.15), card_top + Inches(0.48), col3_w - Inches(0.30), Inches(1.85), border_color=CARD_BORDER, bg_color=BG_WHITE)
    tb_pl = slide.shapes.add_textbox(col3_x + Inches(0.22), card_top + Inches(0.55), col3_w - Inches(0.44), Inches(1.70))
    tf_pl = tb_pl.text_frame
    tf_pl.word_wrap = True
    tf_pl.margin_left = tf_pl.margin_top = tf_pl.margin_right = tf_pl.margin_bottom = 0

    p = tf_pl.paragraphs[0]
    p.text = "PROJECT ACCESS"
    p.font.name = FONT_MONO
    p.font.size = Pt(7.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GOLD

    access_items = [
        ("Live Console", "terrae-geospatial-intelligence.vercel.app"),
        ("GitHub Repository", "github.com/PhantomCipher13/terrae..."),
        ("Technical Report", "REPORT.md (6-Part Scientific Dossier)"),
        ("Automated Tests", "135 / 135 Tests Passing"),
        ("Team", f"{TEAM_NAME} (SIH26227)")
    ]
    for lbl, val in access_items:
        p_it = tf_pl.add_paragraph()
        p_it.space_before = Pt(2)
        r1 = p_it.add_run()
        r1.text = f"• {lbl}: "
        r1.font.name = FONT_HEADING
        r1.font.size = Pt(7.0)
        r1.font.bold = True
        r1.font.color.rgb = TEXT_DARK
        r2 = p_it.add_run()
        r2.text = val
        r2.font.name = FONT_MONO if "github" in val or "vercel" in val else FONT_BODY
        r2.font.size = Pt(6.8)
        r2.font.color.rgb = NAVY_PRIMARY if "github" in val or "vercel" in val else TEXT_MUTED

    # Literature References Box
    c_ref = create_panel(slide, col3_x + Inches(0.15), card_top + Inches(2.45), col3_w - Inches(0.30), Inches(2.25), border_color=CARD_BORDER, bg_color=BG_WHITE)
    tb_ref = slide.shapes.add_textbox(col3_x + Inches(0.22), card_top + Inches(2.52), col3_w - Inches(0.44), Inches(2.10))
    tf_ref = tb_ref.text_frame
    tf_ref.word_wrap = True
    tf_ref.margin_left = tf_ref.margin_top = tf_ref.margin_right = tf_ref.margin_bottom = 0

    p = tf_ref.paragraphs[0]
    p.text = "COMPACT REFERENCES"
    p.font.name = FONT_MONO
    p.font.size = Pt(7.5)
    p.font.bold = True
    p.font.color.rgb = NAVY_PRIMARY

    lit_refs = [
        "[1] RemoteCLIP: Chen et al., IEEE TGRS 2024.",
        "[2] Sentinel-2: ESA Level-2A ATBD (10m BOA).",
        "[3] OSCD: Daudt et al., IEEE IGARSS 2018.",
        "[4] NDVI: Rouse et al., NASA SP-351, 1974.",
        "[5] NDWI: McFeeters, Int. J. Remote Sens., 1996."
    ]
    for ref_str in lit_refs:
        p_r = tf_ref.add_paragraph()
        p_r.space_before = Pt(3)
        r = p_r.add_run()
        r.text = ref_str
        r.font.name = FONT_BODY
        r.font.size = Pt(6.8)
        r.font.color.rgb = TEXT_DARK

    # 4. Bottom Mandate Strip
    bot_y = Inches(6.45)
    c_bot = create_panel(slide, Inches(0.80), bot_y, Inches(11.733), Inches(0.55), border_color=CARD_BORDER, bg_color=BG_IVORY)
    tb_bot = slide.shapes.add_textbox(Inches(0.90), bot_y + Inches(0.10), Inches(11.533), Inches(0.36))
    tf_bot = tb_bot.text_frame
    tf_bot.word_wrap = True
    tf_bot.margin_left = tf_bot.margin_top = tf_bot.margin_right = tf_bot.margin_bottom = 0

    p = tf_bot.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r_cl = p.add_run()
    r_cl.text = "“INVESTIGATE THE CHANGE. FOLLOW THE EVIDENCE. KNOW WHEN TO REVIEW.”"
    r_cl.font.name = FONT_TITLE
    r_cl.font.size = Pt(11.5)
    r_cl.font.bold = True
    r_cl.font.color.rgb = NAVY_PRIMARY


# ---------------------------------------------------------------------------
# MAIN PRESENTATION COMPILER
# ---------------------------------------------------------------------------
def generate_all():
    print("=== BUILDING SIH 2026 MASTER PRESENTATION (PLAIN LIGHT THEME · EXACTLY 6 SLIDES) ===")
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    print("[1/6] Building Slide 1: 01 — PROBLEM STATEMENT...")
    build_slide_1(prs.slides.add_slide(blank_layout))

    print("[2/6] Building Slide 2: 02 — SOLUTION...")
    build_slide_2(prs.slides.add_slide(blank_layout))

    print("[3/6] Building Slide 3: 03 — TECHNICAL APPROACH / METHODOLOGY & PROCESS OF IMPLEMENTATION...")
    build_slide_3(prs.slides.add_slide(blank_layout))

    print("[4/6] Building Slide 4: 04 — FEASIBILITY & VIABILITY...")
    build_slide_4(prs.slides.add_slide(blank_layout))

    print("[5/6] Building Slide 5: 05 — IMPACT & BENEFITS...")
    build_slide_5(prs.slides.add_slide(blank_layout))

    print("[6/6] Building Slide 6: 06 — RESEARCH & REFERENCES...")
    build_slide_6(prs.slides.add_slide(blank_layout))

    slide_count = len(prs.slides)
    print(f"Total slides generated: {slide_count}")
    assert slide_count == 6, f"ERROR: Expected exactly 6 slides, got {slide_count}"

    targets = [
        r"c:\Users\Admin\Downloads\Internal hackathon\TERRAE_SIH2026_Presentation.pptx",
        r"c:\Users\Admin\Downloads\Internal hackathon\terrae\TERRAE_SIH2026_Presentation.pptx",
        r"c:\Users\Admin\Downloads\Internal hackathon\GEOAI_SIH2026_Presentation.pptx",
        r"c:\Users\Admin\Downloads\Internal hackathon\terrae\GEOAI_SIH2026_Presentation.pptx"
    ]
    for tgt in targets:
        os.makedirs(os.path.dirname(tgt), exist_ok=True)
        prs.save(tgt)
        print(f"[SUCCESS] Presentation saved: {tgt}")


if __name__ == '__main__':
    generate_all()
