#!/usr/bin/env python3
"""
TERRAE — Smart India Hackathon 2026 Master 6-Slide Presentation Generator
Problem Statement: SIH26227
Theme: Space Technology | Category: Software
Client Mandate: Ministry of Defence / Indian Army — DGIS
Team: Quantumcrew

Strictly generates EXACTLY 6 slides following the Lanezy SIH finalist structure:
01 — PROBLEM STATEMENT
02 — SOLUTION
03 — TECHNICAL APPROACH / METHODOLOGY & PROCESS OF IMPLEMENTATION
04 — FEASIBILITY & VIABILITY
05 — IMPACT & BENEFITS
06 — RESEARCH & REFERENCES

Enforces 100% data authenticity, locked 6-stage investigation workflow,
locked 3-verdict model, locked 5-state MECE trajectories, authentic satellite imagery,
and live workstation evidence.
"""

import os
import sys
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# ---------------------------------------------------------------------------
# COLOR PALETTE (Geospatial Intelligence / Defense Command Aesthetic)
# ---------------------------------------------------------------------------
BG_DARK = RGBColor(10, 14, 23)           # #0A0E17 Deep Obsidian Navy
CARD_BG = RGBColor(17, 23, 36)           # #111724 Slate Navy Container
CARD_INNER = RGBColor(23, 31, 48)        # #171F30 Elevated Inner Card
CARD_BORDER = RGBColor(37, 50, 74)       # #25324A Crisp Structural Border
BORDER_ACTIVE = RGBColor(197, 168, 105)  # #C5A869 Muted Brass / Gold
GOLD_ACCENT = RGBColor(197, 168, 105)    # #C5A869 Primary Accent Gold
CYAN_ACCENT = RGBColor(78, 168, 222)     # #4EA8DE High-Tech Pale Teal
GREEN_ACCENT = RGBColor(82, 183, 136)    # #52B788 Verified Green
AMBER_ACCENT = RGBColor(224, 159, 62)    # #E09F3E Warning/Review Amber
RED_ACCENT = RGBColor(239, 68, 68)       # #EF4444 Abstain Red
TEXT_WHITE = RGBColor(245, 243, 237)     # #F5F3ED Crisp Soft Ivory
TEXT_MUTED = RGBColor(148, 163, 184)     # #94A3B8 Slate Gray
TEXT_SUBTLE = RGBColor(100, 116, 139)    # #64748B Dim Slate
PILL_BG = RGBColor(15, 23, 38)           # #0F1726 Tag Pill Background

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
    """Draws deep obsidian canvas background (16:9 widescreen)."""
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = BG_DARK
    bg.line.fill.background()
    return bg


def add_sih_header(slide, slide_num_str, section_title, subtitle):
    """Draws standardized, authoritative SIH banner header."""
    set_canvas_background(slide)

    # Top thin gold/brass accent line
    top_line = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0.65), Inches(0.28), Inches(12.033), Inches(0.025)
    )
    top_line.fill.solid()
    top_line.fill.fore_color.rgb = GOLD_ACCENT
    top_line.line.fill.background()

    # Mandate line (Top Left)
    tb_tag = slide.shapes.add_textbox(Inches(0.65), Inches(0.33), Inches(8.5), Inches(0.28))
    tf_tag = tb_tag.text_frame
    tf_tag.word_wrap = True
    tf_tag.margin_left = tf_tag.margin_top = tf_tag.margin_right = tf_tag.margin_bottom = 0
    p_tag = tf_tag.paragraphs[0]
    p_tag.text = f"SMART INDIA HACKATHON 2026 · PS: {PS_ID} · {THEME.upper()} · {CATEGORY.upper()} · {MINISTRY.upper()}"
    p_tag.font.name = FONT_MONO
    p_tag.font.size = Pt(8.0)
    p_tag.font.bold = True
    p_tag.font.color.rgb = GOLD_ACCENT

    # Tracker & Team (Top Right)
    tb_track = slide.shapes.add_textbox(Inches(9.2), Inches(0.33), Inches(3.48), Inches(0.28))
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
    r_num.font.color.rgb = CYAN_ACCENT

    # Main Section Title (Georgia, SIH Section Format)
    tb_title = slide.shapes.add_textbox(Inches(0.65), Inches(0.60), Inches(12.033), Inches(0.62))
    tf_title = tb_title.text_frame
    tf_title.word_wrap = True
    tf_title.margin_left = tf_title.margin_top = tf_title.margin_right = tf_title.margin_bottom = 0
    
    p_t = tf_title.paragraphs[0]
    p_t.text = section_title.upper()
    p_t.font.name = FONT_TITLE
    p_t.font.size = Pt(16.5)
    p_t.font.bold = True
    p_t.font.color.rgb = TEXT_WHITE

    p_sub = tf_title.add_paragraph()
    p_sub.text = subtitle
    p_sub.font.name = FONT_BODY
    p_sub.font.size = Pt(9.5)
    p_sub.font.color.rgb = TEXT_MUTED

    add_sih_footer(slide)


def add_sih_footer(slide):
    """Draws standardized footer with project credentials and links."""
    f_box = slide.shapes.add_textbox(Inches(0.65), Inches(7.18), Inches(12.033), Inches(0.22))
    tf = f_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    
    r1 = p.add_run()
    r1.text = f"{PROJECT_NAME} — Earth Intelligence Satellite Investigation Console  |  {MINISTRY}  |  SIH 2026 Submission"
    r1.font.name = FONT_BODY
    r1.font.size = Pt(7.8)
    r1.font.color.rgb = TEXT_SUBTLE

    r2 = p.add_run()
    r2.text = "                                                         Live Console: "
    r2.font.name = FONT_BODY
    r2.font.size = Pt(7.8)
    r2.font.color.rgb = TEXT_SUBTLE

    r3 = p.add_run()
    r3.text = URL_WEB
    r3.font.name = FONT_BODY
    r3.font.size = Pt(7.8)
    r3.font.color.rgb = CYAN_ACCENT
    r3.hyperlink.address = URL_WEB


def create_panel(slide, left, top, width, height, border_color=CARD_BORDER, bg_color=CARD_BG, border_width=Pt(1.0)):
    """Draws structural card container."""
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
    
    fallback = create_panel(slide, left, top, width, height, border_color=CARD_BORDER, bg_color=CARD_INNER)
    tb = slide.shapes.add_textbox(left, top + height/2 - Inches(0.2), width, Inches(0.4))
    p = tb.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.text = f"[Image: {os.path.basename(path)}]"
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

    # 1. Central Operational Statement Banner
    banner = create_panel(slide, Inches(0.65), Inches(1.30), Inches(12.033), Inches(0.50), border_color=BORDER_ACTIVE, bg_color=CARD_INNER)
    tb_b = slide.shapes.add_textbox(Inches(0.8), Inches(1.35), Inches(11.733), Inches(0.40))
    tf_b = tb_b.text_frame
    tf_b.margin_left = tf_b.margin_top = tf_b.margin_right = tf_b.margin_bottom = 0
    p_b = tf_b.paragraphs[0]
    p_b.alignment = PP_ALIGN.CENTER
    
    r_b1 = p_b.add_run()
    r_b1.text = "“Finding a changed pixel is easy. Knowing whether it matters is harder.”"
    r_b1.font.name = FONT_TITLE
    r_b1.font.size = Pt(12.5)
    r_b1.font.bold = True
    r_b1.font.color.rgb = GOLD_ACCENT

    # 2. Left Column: Traditional Analyst Workflow (Status Quo Bottlenecks)
    col1_w = Inches(3.60)
    c1 = create_panel(slide, Inches(0.65), Inches(1.90), col1_w, Inches(4.50))
    tb_c1 = slide.shapes.add_textbox(Inches(0.80), Inches(2.00), col1_w - Inches(0.30), Inches(4.30))
    tf_c1 = tb_c1.text_frame
    tf_c1.word_wrap = True
    tf_c1.margin_left = tf_c1.margin_top = tf_c1.margin_right = tf_c1.margin_bottom = 0
    
    p = tf_c1.paragraphs[0]
    p.text = "CURRENT ANALYST WORKFLOW (STATUS QUO)"
    p.font.name = FONT_MONO
    p.font.size = Pt(9.0)
    p.font.bold = True
    p.font.color.rgb = AMBER_ACCENT

    workflow_steps = [
        ("01 / METADATA SEARCH", "Filter sensor catalogs, timestamps, and cloud cover."),
        ("02 / COORDINATES", "Manual geographic bounding-box guesswork."),
        ("03 / SCENE SEARCH", "Download and unpack multi-gigabyte raw GeoTIFF tiles."),
        ("04 / MANUAL COMPARISON", "Flicker/blink inspection of T0 vs T1 images on screen."),
        ("05 / MANUAL INTERPRETATION", "Crude pixel subtraction forces analyst to guess ground cause.")
    ]
    for st_title, st_desc in workflow_steps:
        p_st = tf_c1.add_paragraph()
        p_st.space_before = Pt(4)
        r1 = p_st.add_run()
        r1.text = f"{st_title}\n"
        r1.font.name = FONT_HEADING
        r1.font.size = Pt(8.0)
        r1.font.bold = True
        r1.font.color.rgb = TEXT_WHITE

        r2 = p_st.add_run()
        r2.text = f"  {st_desc}"
        r2.font.name = FONT_BODY
        r2.font.size = Pt(7.5)
        r2.font.color.rgb = TEXT_MUTED

    p_warn = tf_c1.add_paragraph()
    p_warn.space_before = Pt(6)
    r_w = p_warn.add_run()
    r_w.text = "CRITICAL DEFENSE FLAW:\nNaive pixel differencing creates massive false-alarm exhaustion from seasonal phenology, moisture, and sun angle."
    r_w.font.name = FONT_BODY
    r_w.font.size = Pt(7.4)
    r_w.font.bold = True
    r_w.font.color.rgb = AMBER_ACCENT

    # 3. Center Column: Concise Statement & The 5 Defense Bottlenecks
    col2_w = Inches(4.35)
    c2 = create_panel(slide, Inches(4.35), Inches(1.90), col2_w, Inches(4.50))
    tb_c2 = slide.shapes.add_textbox(Inches(4.50), Inches(2.00), col2_w - Inches(0.30), Inches(4.30))
    tf_c2 = tb_c2.text_frame
    tf_c2.word_wrap = True
    tf_c2.margin_left = tf_c2.margin_top = tf_c2.margin_right = tf_c2.margin_bottom = 0

    p = tf_c2.paragraphs[0]
    p.text = "OPERATIONAL DEFENSE CHALLENGE"
    p.font.name = FONT_MONO
    p.font.size = Pt(9.0)
    p.font.bold = True
    p.font.color.rgb = CYAN_ACCENT

    p_stmt = tf_c2.add_paragraph()
    p_stmt.space_before = Pt(3)
    r_s = p_stmt.add_run()
    r_s.text = "Analysts must find relevant satellite scenes and determine whether observed changes are persistent, meaningful, and supported by evidence."
    r_s.font.name = FONT_HEADING
    r_s.font.size = Pt(8.5)
    r_s.font.bold = True
    r_s.font.color.rgb = TEXT_WHITE

    p_q = tf_c2.add_paragraph()
    p_q.space_before = Pt(5)
    r_q1 = p_q.add_run()
    r_q1.text = "REAL ANALYST QUERY:  "
    r_q1.font.name = FONT_MONO
    r_q1.font.size = Pt(7.8)
    r_q1.font.bold = True
    r_q1.font.color.rgb = GOLD_ACCENT

    r_q2 = p_q.add_run()
    r_q2.text = "“Show me areas with newly built structures near a river corridor.”\n"
    r_q2.font.name = FONT_TITLE
    r_q2.font.size = Pt(8.5)
    r_q2.font.bold = True
    r_q2.font.color.rgb = TEXT_WHITE

    bottlenecks = [
        ("1. Semantic Discovery", "Archives lack natural-language retrieval; analysts browse thousands of candidate tiles manually."),
        ("2. Multi-Temporal Scale", "Two-date differencing fails to separate seasonal crop phenology from permanent transformation."),
        ("3. Spectral Attribution", "Difference intensity indicates THAT a change occurred, but cannot prove WHAT changed."),
        ("4. Heterogeneous Sensors", "Varying resolutions, calibrations, and coordinate reference systems (CRS) hinder standardized analysis."),
        ("5. Secure Offline Enclave", "Air-gapped defense workstations require zero cloud APIs, remote tracking, or network egress.")
    ]
    for b_title, b_desc in bottlenecks:
        p_b = tf_c2.add_paragraph()
        p_b.space_before = Pt(3)
        r1 = p_b.add_run()
        r1.text = f"• {b_title}: "
        r1.font.name = FONT_HEADING
        r1.font.size = Pt(8.0)
        r1.font.bold = True
        r1.font.color.rgb = GOLD_ACCENT
        
        r2 = p_b.add_run()
        r2.text = b_desc
        r2.font.name = FONT_BODY
        r2.font.size = Pt(7.4)
        r2.font.color.rgb = TEXT_MUTED

    # 4. Right Column: Authentic Earth Observation Visual Plate (1:1 Ratio Respected)
    col3_w = Inches(3.883)
    c3 = create_panel(slide, Inches(8.80), Inches(1.90), col3_w, Inches(4.50))
    
    img_path = os.path.join(ASSETS_DIR, "hero_beirut_1920x1080.jpg")
    safe_add_image(slide, img_path, Inches(8.92), Inches(2.00), col3_w - Inches(0.24), Inches(2.40))

    tb_c3 = slide.shapes.add_textbox(Inches(8.92), Inches(4.45), col3_w - Inches(0.24), Inches(1.85))
    tf_c3 = tb_c3.text_frame
    tf_c3.word_wrap = True
    tf_c3.margin_left = tf_c3.margin_top = tf_c3.margin_right = tf_c3.margin_bottom = 0
    
    p = tf_c3.paragraphs[0]
    p.text = "DEFENSE OPERATIONAL REALITY"
    p.font.name = FONT_MONO
    p.font.size = Pt(9.0)
    p.font.bold = True
    p.font.color.rgb = GREEN_ACCENT

    points = [
        "Authentic Sentinel-2 L2A BOA reflectance (10m GSD).",
        "High-density urban, coastal, and agricultural terrain.",
        "Change must be physically decomposed across bands (Blue, Green, Red, NIR), not guessed from pixel luminosity.",
        "MGRS Tile 36SYC · Projected CRS EPSG:32636."
    ]
    for pt in points:
        p_pt = tf_c3.add_paragraph()
        p_pt.space_before = Pt(2)
        r = p_pt.add_run()
        r.text = f"▪ {pt}"
        r.font.name = FONT_BODY
        r.font.size = Pt(7.4)
        r.font.color.rgb = TEXT_MUTED

    # 5. Bottom PS Alignment Strip
    ps_bar = create_panel(slide, Inches(0.65), Inches(6.48), Inches(12.033), Inches(0.50), border_color=CARD_BORDER, bg_color=PILL_BG)
    tb_ps = slide.shapes.add_textbox(Inches(0.75), Inches(6.54), Inches(11.833), Inches(0.38))
    tf_ps = tb_ps.text_frame
    tf_ps.margin_left = tf_ps.margin_top = tf_ps.margin_right = tf_ps.margin_bottom = 0
    p_ps = tf_ps.paragraphs[0]
    p_ps.alignment = PP_ALIGN.CENTER
    
    r_hdr = p_ps.add_run()
    r_hdr.text = "PS SIH26227 ALIGNMENT:  "
    r_hdr.font.name = FONT_MONO
    r_hdr.font.size = Pt(8.0)
    r_hdr.font.bold = True
    r_hdr.font.color.rgb = GOLD_ACCENT

    pillars = [
        ("SEMANTIC RETRIEVAL", CYAN_ACCENT),
        ("MULTI-TEMPORAL ANALYSIS", GREEN_ACCENT),
        ("MULTI-SPECTRAL EVIDENCE", GOLD_ACCENT),
        ("PROVENANCE / REVIEW", TEXT_WHITE),
        ("OFFLINE OPERATION", CYAN_ACCENT),
    ]
    for p_name, p_col in pillars:
        r_pil = p_ps.add_run()
        r_pil.text = f"[{p_name}]   "
        r_pil.font.name = FONT_MONO
        r_pil.font.size = Pt(7.8)
        r_pil.font.bold = True
        r_pil.font.color.rgb = p_col


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

    # 1. Horizontal Connected 6-Stage Investigation Workflow (Full Width)
    pipe_top = Inches(1.30)
    pipe_h = Inches(0.85)
    pipe_w = Inches(12.033)
    c_pipe = create_panel(slide, Inches(0.65), pipe_top, pipe_w, pipe_h, border_color=BORDER_ACTIVE, bg_color=CARD_BG)

    # EXACTLY 6 STAGES — NO "LOCATE"
    stages = [
        ("01 ASK", "Natural Intent\nQuery Formulation"),
        ("02 DISCOVER", "RemoteCLIP + FAISS\nSemantic Retrieval"),
        ("03 COMPARE", "Calibrated Multi-Spectral\nDifferencing (τ = 0.15)"),
        ("04 EXPLAIN", "Multi-Band Decomposition\n& Spatial Coherence"),
        ("05 CHALLENGE", "Multi-Date Trajectory\nPersistence Check"),
        ("06 DECIDE", "Conservative Verdict:\nSUPPORTED / REVIEW / ABSTAIN")
    ]
    step_w = Inches(12.033 / 6.0)
    for idx, (st_name, st_sub) in enumerate(stages):
        x = Inches(0.65) + idx * step_w
        tb_st = slide.shapes.add_textbox(x, pipe_top + Inches(0.08), step_w, pipe_h - Inches(0.16))
        tf_st = tb_st.text_frame
        tf_st.word_wrap = True
        tf_st.margin_left = tf_st.margin_top = tf_st.margin_right = tf_st.margin_bottom = 0
        
        p = tf_st.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r1 = p.add_run()
        r1.text = f"{st_name}\n"
        r1.font.name = FONT_MONO
        r1.font.size = Pt(8.5)
        r1.font.bold = True
        r1.font.color.rgb = GOLD_ACCENT if idx == 5 else (CYAN_ACCENT if idx in (0, 1) else TEXT_WHITE)

        p2 = tf_st.add_paragraph()
        p2.alignment = PP_ALIGN.CENTER
        r2 = p2.add_run()
        r2.text = st_sub
        r2.font.name = FONT_BODY
        r2.font.size = Pt(7.0)
        r2.font.color.rgb = TEXT_MUTED

    # 2. Main Area Left: Analyst Investigation Principles & The 3 Verdicts
    left_w = Inches(4.35)
    c_left = create_panel(slide, Inches(0.65), Inches(2.25), left_w, Inches(4.15))
    tb_l = slide.shapes.add_textbox(Inches(0.80), Inches(2.35), left_w - Inches(0.30), Inches(3.95))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True
    tf_l.margin_left = tf_l.margin_top = tf_l.margin_right = tf_l.margin_bottom = 0

    p = tf_l.paragraphs[0]
    p.text = "NOT JUST CHANGE DETECTION. INVESTIGATION."
    p.font.name = FONT_MONO
    p.font.size = Pt(9.0)
    p.font.bold = True
    p.font.color.rgb = GOLD_ACCENT

    p_q = tf_l.add_paragraph()
    p_q.space_before = Pt(3)
    r_qa = p_q.add_run()
    r_qa.text = "ANALYST INTENT: “Show me areas with newly built structures.”\n"
    r_qa.font.name = FONT_HEADING
    r_qa.font.size = Pt(8.0)
    r_qa.font.bold = True
    r_qa.font.color.rgb = TEXT_WHITE

    p_sub = tf_l.add_paragraph()
    r = p_sub.add_run()
    r.text = "The console replaces blind differencing with structured evidence:"
    r.font.name = FONT_BODY
    r.font.size = Pt(7.5)
    r.font.color.rgb = TEXT_MUTED

    questions = [
        ("WHAT changed?", "Exact surface reflectance shifts across Blue, Green, Red, NIR."),
        ("WHERE is it located?", "Canonical MGRS tile EPSG:32643 coordinate frame."),
        ("WHAT supports it?", "ΔNIR, ΔRed, NDVI shifts + connected-component clustering."),
        ("WHAT alternatives exist?", "Competes against crop senescence, water & cloud shadows."),
        ("DOES it persist?", "3-date trajectory check (T0 → Tmid → T1) for permanence."),
        ("WHEN to abstain?", "SCL cloud/snow occlusion, defective pixels, or sub-threshold SNR.")
    ]
    for q_t, q_d in questions:
        p_q = tf_l.add_paragraph()
        p_q.space_before = Pt(2)
        r1 = p_q.add_run()
        r1.text = f"▪ {q_t} "
        r1.font.name = FONT_HEADING
        r1.font.size = Pt(7.6)
        r1.font.bold = True
        r1.font.color.rgb = CYAN_ACCENT
        r2 = p_q.add_run()
        r2.text = q_d
        r2.font.name = FONT_BODY
        r2.font.size = Pt(7.3)
        r2.font.color.rgb = TEXT_WHITE

    # 3 Verdicts Box
    p_v = tf_l.add_paragraph()
    p_v.space_before = Pt(5)
    r_vh = p_v.add_run()
    r_vh.text = "THREE CONSERVATIVE VERDICTS:\n"
    r_vh.font.name = FONT_MONO
    r_vh.font.size = Pt(8.0)
    r_vh.font.bold = True
    r_vh.font.color.rgb = TEXT_WHITE

    verdicts = [
        ("SUPPORTED", GREEN_ACCENT, "Spatial coherence (>0.5) + dominant signature + persistent trajectory."),
        ("REVIEW", AMBER_ACCENT, "Sub-threshold change (f ≤ 5%), ambiguous attribution, or reversible cycle."),
        ("ABSTAIN", RED_ACCENT, "Cloud/shadow corruption, registration failure, or <2 observations.")
    ]
    for v_title, v_col, v_desc in verdicts:
        p_item = tf_l.add_paragraph()
        p_item.space_before = Pt(1)
        r_v1 = p_item.add_run()
        r_v1.text = f"[{v_title}] "
        r_v1.font.name = FONT_MONO
        r_v1.font.size = Pt(7.6)
        r_v1.font.bold = True
        r_v1.font.color.rgb = v_col
        r_v2 = p_item.add_run()
        r_v2.text = v_desc
        r_v2.font.name = FONT_BODY
        r_v2.font.size = Pt(7.2)
        r_v2.font.color.rgb = TEXT_MUTED

    # 3. Main Area Right: Comparison Matrix + Authentic Workstation Visual
    right_w = Inches(7.55)
    c_right = create_panel(slide, Inches(5.13), Inches(2.25), right_w, Inches(4.15), border_color=CARD_BORDER, bg_color=CARD_BG)

    # Workstation Header
    tb_rw = slide.shapes.add_textbox(Inches(5.28), Inches(2.35), right_w - Inches(0.30), Inches(0.35))
    tf_rw = tb_rw.text_frame
    tf_rw.word_wrap = True
    tf_rw.margin_left = tf_rw.margin_top = tf_rw.margin_right = tf_rw.margin_bottom = 0
    p = tf_rw.paragraphs[0]
    p.text = "COMPARISON: STATUS QUO VS. TERRAE INVESTIGATION CONSOLE"
    p.font.name = FONT_MONO
    p.font.size = Pt(9.0)
    p.font.bold = True
    p.font.color.rgb = CYAN_ACCENT

    # Comparison Table
    rows = [
        ("Dimension", "Status Quo Change Detector", "TERRAE Investigation Console"),
        ("Search & Discovery", "Manual coordinate bounding & catalog spreadsheets", "RemoteCLIP natural-language cross-modal search"),
        ("Change Analysis", "Naive 2-date pixel subtraction (T0 - T1)", "Calibrated multi-band differencing (τ = 0.15)"),
        ("Attribution Support", "Uncalibrated binary changed pixel mask", "Decomposed physical support across 6 signatures"),
        ("Temporal Verification", "Single interval; high seasonal false alarms", "3-date MECE trajectory persistence test"),
        ("Decision Integrity", "Forced binary classification (Change / No Change)", "Conservative verdicts: SUPPORTED / REVIEW / ABSTAIN"),
        ("Enclave Security", "Cloud API dependence & telemetry leakage", "100% offline air-gapped on-premises execution")
    ]
    tbl_top = Inches(2.72)
    tbl_h = Inches(2.05)
    tbl_shape = slide.shapes.add_table(len(rows), 3, Inches(5.28), tbl_top, right_w - Inches(0.30), tbl_h)
    tbl = tbl_shape.table
    tbl.columns[0].width = Inches(1.75)
    tbl.columns[1].width = Inches(2.65)
    tbl.columns[2].width = Inches(2.85)

    for r_idx, (c0, c1_txt, c2_txt) in enumerate(rows):
        for c_idx, val in enumerate([c0, c1_txt, c2_txt]):
            cell = tbl.cell(r_idx, c_idx)
            cell.margin_left = cell.margin_right = cell.margin_top = cell.margin_bottom = Inches(0.03)
            cell_p = cell.text_frame.paragraphs[0]
            cell_p.text = val
            cell_p.font.name = FONT_HEADING if r_idx == 0 else FONT_BODY
            cell_p.font.size = Pt(6.8) if r_idx > 0 else Pt(7.4)
            if r_idx == 0:
                cell_p.font.bold = True
                cell_p.font.color.rgb = GOLD_ACCENT
                cell.fill.solid()
                cell.fill.fore_color.rgb = CARD_INNER
            else:
                cell.fill.solid()
                cell.fill.fore_color.rgb = CARD_BG if r_idx % 2 == 1 else CARD_INNER
                if c_idx == 0:
                    cell_p.font.bold = True
                    cell_p.font.color.rgb = TEXT_WHITE
                elif c_idx == 1:
                    cell_p.font.color.rgb = TEXT_MUTED
                else:
                    cell_p.font.color.rgb = CYAN_ACCENT

    # Authentic Workstation Screenshot + Telemetry split at bottom of right card
    split_top = Inches(4.88)
    ws_w = Inches(2.35)
    ws_h = Inches(1.40)
    ws_img_path = os.path.join(QA_DIR, "PROD_09_WORKSTATION_1920.png")
    if not os.path.exists(ws_img_path):
        ws_img_path = os.path.join(ASSETS_DIR, "workstation_case01_annotated.jpg")
    safe_add_image(slide, ws_img_path, Inches(5.28), split_top, ws_w, ws_h)

    tb_bot_strip = slide.shapes.add_textbox(Inches(7.75), split_top, right_w - ws_w - Inches(0.60), ws_h)
    tf_bs = tb_bot_strip.text_frame
    tf_bs.word_wrap = True
    tf_bs.margin_left = tf_bs.margin_top = tf_bs.margin_right = tf_bs.margin_bottom = 0
    p_b1 = tf_bs.paragraphs[0]
    p_b1.text = "AUTHENTIC CONSOLE TELEMETRY (CASE 01):"
    p_b1.font.name = FONT_MONO
    p_b1.font.size = Pt(7.6)
    p_b1.font.bold = True
    p_b1.font.color.rgb = GOLD_ACCENT

    p_b2 = tf_bs.add_paragraph()
    r_b2 = p_b2.add_run()
    r_b2.text = (
        "• Footprint: 256×256 tile | 7,549 px Changed (11.5%)\n"
        "• Spatial Coherence: 99.7% | Connected Components: 24\n"
        "• Attribution Support: Built 97.1% | Veg 0.5% | Seasonal 0.5%\n"
        "• Temporal Trajectory: LATE_ONSET_CHANGE (11.48%)\n"
        "• Final Verdict: ✔ SUPPORTED · AFFIRMATIVE PROOF"
    )
    r_b2.font.name = FONT_BODY
    r_b2.font.size = Pt(7.0)
    r_b2.font.color.rgb = TEXT_WHITE

    # 4. Bottom Access Strip
    bot_bar = create_panel(slide, Inches(0.65), Inches(6.48), Inches(12.033), Inches(0.50), border_color=CARD_BORDER, bg_color=PILL_BG)
    tb_acc = slide.shapes.add_textbox(Inches(0.75), Inches(6.54), Inches(11.833), Inches(0.38))
    tf_acc = tb_acc.text_frame
    tf_acc.margin_left = tf_acc.margin_top = tf_acc.margin_right = tf_acc.margin_bottom = 0
    p_a = tf_acc.paragraphs[0]
    p_a.alignment = PP_ALIGN.CENTER
    
    r_a1 = p_a.add_run()
    r_a1.text = "LIVE SYSTEM ACCESS:   "
    r_a1.font.name = FONT_MONO
    r_a1.font.size = Pt(8.0)
    r_a1.font.bold = True
    r_a1.font.color.rgb = GOLD_ACCENT

    r_a2 = p_a.add_run()
    r_a2.text = f"Console: {URL_WEB}   |   GitHub: {URL_REPO}   |   Report: REPORT.md"
    r_a2.font.name = FONT_MONO
    r_a2.font.size = Pt(7.6)
    r_a2.font.color.rgb = CYAN_ACCENT


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

    # 1. Left Panel: Circular Investigation Loop
    left_w = Inches(3.60)
    c_left = create_panel(slide, Inches(0.65), Inches(1.30), left_w, Inches(5.68), border_color=BORDER_ACTIVE, bg_color=CARD_BG)
    
    tb_lh = slide.shapes.add_textbox(Inches(0.80), Inches(1.42), left_w - Inches(0.30), Inches(0.35))
    tf_lh = tb_lh.text_frame
    tf_lh.margin_left = tf_lh.margin_top = tf_lh.margin_right = tf_lh.margin_bottom = 0
    p_lh = tf_lh.paragraphs[0]
    p_lh.text = "TERRAE INVESTIGATION LOOP"
    p_lh.font.name = FONT_MONO
    p_lh.font.size = Pt(9.0)
    p_lh.font.bold = True
    p_lh.font.color.rgb = GOLD_ACCENT

    loop_steps = [
        ("01 / ASK", "Analyst Natural Intent Formulation", "Parses text query without coordinates."),
        ("02 / DISCOVER", "Cross-Modal Semantic Retrieval", "RemoteCLIP ViT-B-32 + FAISS vector cosine."),
        ("03 / COMPARE", "Multi-Band Spectral Differencing", "B02, B03, B04, B08 calibrated shift (τ = 0.15)."),
        ("04 / EXPLAIN", "Evidence-Based Change Attribution", "NDVI, NDWI & spatial coherence topology."),
        ("05 / CHALLENGE", "Multi-Temporal Persistence Check", "3-date MECE trajectory classification."),
        ("06 / DECIDE", "Conservative Auditable Verdict", "SUPPORTED / REVIEW / ABSTAIN decision layer.")
    ]
    step_y = Inches(1.85)
    box_h = Inches(0.72)
    box_gap = Inches(0.12)
    for idx, (st_num, st_name, st_desc) in enumerate(loop_steps):
        sy = step_y + idx * (box_h + box_gap)
        c_box = create_panel(slide, Inches(0.80), sy, left_w - Inches(0.30), box_h, border_color=CARD_BORDER, bg_color=CARD_INNER)
        tb_box = slide.shapes.add_textbox(Inches(0.90), sy + Inches(0.06), left_w - Inches(0.50), box_h - Inches(0.12))
        tf_box = tb_box.text_frame
        tf_box.word_wrap = True
        tf_box.margin_left = tf_box.margin_top = tf_box.margin_right = tf_box.margin_bottom = 0
        
        p1 = tf_box.paragraphs[0]
        r1 = p1.add_run()
        r1.text = f"{st_num}: {st_name}\n"
        r1.font.name = FONT_MONO
        r1.font.size = Pt(7.8)
        r1.font.bold = True
        r1.font.color.rgb = CYAN_ACCENT if idx in (0, 1) else (GREEN_ACCENT if idx in (2, 3) else GOLD_ACCENT)

        p2 = tf_box.add_paragraph()
        r2 = p2.add_run()
        r2.text = st_desc
        r2.font.name = FONT_BODY
        r2.font.size = Pt(7.0)
        r2.font.color.rgb = TEXT_MUTED

    # 2. Center-Top Panel: Process 1 — Semantic Retrieval Pipeline
    mid_w = Inches(4.75)
    c_p1 = create_panel(slide, Inches(4.35), Inches(1.30), mid_w, Inches(2.75), border_color=CYAN_ACCENT, bg_color=CARD_BG)
    tb_p1 = slide.shapes.add_textbox(Inches(4.50), Inches(1.40), mid_w - Inches(0.30), Inches(0.35))
    tf_p1 = tb_p1.text_frame
    tf_p1.margin_left = tf_p1.margin_top = tf_p1.margin_right = tf_p1.margin_bottom = 0
    p = tf_p1.paragraphs[0]
    p.text = "PROCESS 1: CROSS-MODAL SEMANTIC RETRIEVAL"
    p.font.name = FONT_MONO
    p.font.size = Pt(9.0)
    p.font.bold = True
    p.font.color.rgb = CYAN_ACCENT

    retrieval_flow = [
        ("Query Formulation", "Analyst enters intent in natural English (e.g., “newly built structures”)."),
        ("RemoteCLIP ViT-B-32", "Projects text and GeoTIFF tiles into 512-dim joint space (Sun et al. / Chen et al.)."),
        ("FAISS FlatIP Search", "Exact cosine similarity matching: s(q, v) = q̂ · v̂ = cos(θ). Sub-millisecond scan."),
        ("SQLite Metadata Lookup", "Stable UUID primary keys resolve tile_id to bounds_wgs84 & EPSG:32643 MGRS tile.")
    ]
    tb_p1_body = slide.shapes.add_textbox(Inches(4.50), Inches(1.78), mid_w - Inches(0.30), Inches(2.20))
    tf_p1_b = tb_p1_body.text_frame
    tf_p1_b.word_wrap = True
    tf_p1_b.margin_left = tf_p1_b.margin_top = tf_p1_b.margin_right = tf_p1_b.margin_bottom = 0
    for idx, (f_title, f_desc) in enumerate(retrieval_flow):
        p_fl = tf_p1_b.paragraphs[0] if idx == 0 else tf_p1_b.add_paragraph()
        if idx > 0:
            p_fl.space_before = Pt(3)
        r1 = p_fl.add_run()
        r1.text = f"Step {idx+1} · {f_title}: "
        r1.font.name = FONT_HEADING
        r1.font.size = Pt(7.8)
        r1.font.bold = True
        r1.font.color.rgb = TEXT_WHITE
        r2 = p_fl.add_run()
        r2.text = f"{f_desc}"
        r2.font.name = FONT_BODY
        r2.font.size = Pt(7.3)
        r2.font.color.rgb = TEXT_MUTED

    p_tele = tf_p1_b.add_paragraph()
    p_tele.space_before = Pt(4)
    r_tel = p_tele.add_run()
    r_tel.text = "OFFLINE BENCHMARK: Model load 4.94s | Text embed 48.6ms | FAISS scan 2.0ms | Total 66.1ms"
    r_tel.font.name = FONT_MONO
    r_tel.font.size = Pt(7.0)
    r_tel.font.bold = True
    r_tel.font.color.rgb = GOLD_ACCENT

    # 3. Center-Bottom Panel: Process 2 — Multi-Temporal Evidence & Attribution
    c_p2 = create_panel(slide, Inches(4.35), Inches(4.15), mid_w, Inches(2.83), border_color=GREEN_ACCENT, bg_color=CARD_BG)
    tb_p2 = slide.shapes.add_textbox(Inches(4.50), Inches(4.25), mid_w - Inches(0.30), Inches(0.35))
    tf_p2 = tb_p2.text_frame
    tf_p2.margin_left = tf_p2.margin_top = tf_p2.margin_right = tf_p2.margin_bottom = 0
    p = tf_p2.paragraphs[0]
    p.text = "PROCESS 2: MULTI-TEMPORAL EVIDENCE & ATTRIBUTION"
    p.font.name = FONT_MONO
    p.font.size = Pt(9.0)
    p.font.bold = True
    p.font.color.rgb = GREEN_ACCENT

    detection_flow = [
        ("Spectral Differencing (τ = 0.15)", "Δmean = (1/B) Σ |I_T1(b) - I_T0(b)| across B02, B03, B04, B08."),
        ("Biophysical Indices", "NDVI = (NIR - Red)/(NIR + Red) and NDWI = (Green - NIR)/(Green + NIR)."),
        ("Spatial Coherence Topology", "Connected component labeling: C_spatial = max_component_size / total_changed."),
        ("MECE Trajectory Classification", "3-date stack (T0, Tmid, T1) classified into 5 canonical categories.")
    ]
    tb_p2_body = slide.shapes.add_textbox(Inches(4.50), Inches(4.62), mid_w - Inches(0.30), Inches(2.28))
    tf_p2_b = tb_p2_body.text_frame
    tf_p2_b.word_wrap = True
    tf_p2_b.margin_left = tf_p2_b.margin_top = tf_p2_b.margin_right = tf_p2_b.margin_bottom = 0
    for idx, (f_title, f_desc) in enumerate(detection_flow):
        p_fl = tf_p2_b.paragraphs[0] if idx == 0 else tf_p2_b.add_paragraph()
        if idx > 0:
            p_fl.space_before = Pt(3)
        r1 = p_fl.add_run()
        r1.text = f"Layer {idx+1} · {f_title}: "
        r1.font.name = FONT_HEADING
        r1.font.size = Pt(7.8)
        r1.font.bold = True
        r1.font.color.rgb = TEXT_WHITE
        r2 = p_fl.add_run()
        r2.text = f"{f_desc}"
        r2.font.name = FONT_BODY
        r2.font.size = Pt(7.3)
        r2.font.color.rgb = TEXT_MUTED

    p_mece = tf_p2_b.add_paragraph()
    p_mece.space_before = Pt(4)
    r_mc = p_mece.add_run()
    r_mc.text = "MECE TRAJECTORIES: STABLE | PERSISTENT_CHANGE | TRANSIENT | LATE_ONSET | REVERSIBLE"
    r_mc.font.name = FONT_MONO
    r_mc.font.size = Pt(7.0)
    r_mc.font.bold = True
    r_mc.font.color.rgb = GOLD_ACCENT

    # 4. Right Panel: Technologies Used in 4 Compact Bands
    right_w = Inches(3.483)
    c_right = create_panel(slide, Inches(9.20), Inches(1.30), right_w, Inches(5.68), border_color=BORDER_ACTIVE, bg_color=CARD_BG)
    tb_rh = slide.shapes.add_textbox(Inches(9.35), Inches(1.42), right_w - Inches(0.30), Inches(0.35))
    tf_rh = tb_rh.text_frame
    tf_rh.margin_left = tf_rh.margin_top = tf_rh.margin_right = tf_rh.margin_bottom = 0
    p = tf_rh.paragraphs[0]
    p.text = "TECHNOLOGIES USED"
    p.font.name = FONT_MONO
    p.font.size = Pt(9.0)
    p.font.bold = True
    p.font.color.rgb = GOLD_ACCENT

    tech_bands = [
        ("BAND 1: SEMANTIC RETRIEVAL", CYAN_ACCENT, [
            ("Model", "RemoteCLIP ViT-B-32 (605 MB local checkpoint)"),
            ("Vector Index", "FAISS CPU IndexIDMap(IndexFlatIP)"),
            ("Embedding", "512-dim L2-normalized unit vectors"),
            ("Metadata DB", "SQLite local store (metadata.db)")
        ]),
        ("BAND 2: GEOSPATIAL ANALYSIS", GREEN_ACCENT, [
            ("Raster Engine", "Rasterio & GDAL C-bindings"),
            ("Grid Projection", "EPSG:32643 (UTM Zone 43N)"),
            ("Arrays & Math", "NumPy 2.x vectorized arrays"),
            ("Topology", "SciPy 1.14 (ndimage.label 8-conn)")
        ]),
        ("BAND 3: TEMPORAL & VALIDATION", GOLD_ACCENT, [
            ("Constellation", "Copernicus Sentinel-2 MSI (10m BOA)"),
            ("Threshold", "Fixed calibrated τ = 0.15"),
            ("Persistence", "5-State MECE trajectory engine"),
            ("Validation", "OSCD 5-pair subset (3,025,938 px)")
        ]),
        ("BAND 4: OFFLINE-FIRST CORE", TEXT_WHITE, [
            ("Runtime", "Python 3.11 core analytical engine"),
            ("Interface", "Next.js 14 console & Streamlit UI"),
            ("API Service", "FastAPI local REST microservice"),
            ("Air-Gap Mandate", "Zero runtime network egress")
        ])
    ]
    b_top = Inches(1.85)
    b_h = Inches(1.20)
    b_gap = Inches(0.08)
    for idx, (b_title, b_col, b_items) in enumerate(tech_bands):
        by = b_top + idx * (b_h + b_gap)
        c_tb = create_panel(slide, Inches(9.35), by, right_w - Inches(0.30), b_h, border_color=CARD_BORDER, bg_color=CARD_INNER)
        tb_b = slide.shapes.add_textbox(Inches(9.45), by + Inches(0.05), right_w - Inches(0.50), b_h - Inches(0.10))
        tf_b = tb_b.text_frame
        tf_b.word_wrap = True
        tf_b.margin_left = tf_b.margin_top = tf_b.margin_right = tf_b.margin_bottom = 0
        
        p = tf_b.paragraphs[0]
        p.text = b_title
        p.font.name = FONT_MONO
        p.font.size = Pt(7.6)
        p.font.bold = True
        p.font.color.rgb = b_col

        for k, v in b_items:
            p_it = tf_b.add_paragraph()
            r1 = p_it.add_run()
            r1.text = f"• {k}: "
            r1.font.name = FONT_BODY
            r1.font.size = Pt(7.0)
            r1.font.bold = True
            r1.font.color.rgb = TEXT_WHITE
            r2 = p_it.add_run()
            r2.text = v
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

    # 1. Left Column: Feasibility (3 Visual Blocks)
    col1_w = Inches(3.20)
    c_f = create_panel(slide, Inches(0.65), Inches(1.30), col1_w, Inches(5.05), border_color=BORDER_ACTIVE, bg_color=CARD_BG)
    tb_fh = slide.shapes.add_textbox(Inches(0.80), Inches(1.42), col1_w - Inches(0.30), Inches(0.35))
    tf_fh = tb_fh.text_frame
    tf_fh.margin_left = tf_fh.margin_top = tf_fh.margin_right = tf_fh.margin_bottom = 0
    p = tf_fh.paragraphs[0]
    p.text = "TECHNICAL FEASIBILITY"
    p.font.name = FONT_MONO
    p.font.size = Pt(9.0)
    p.font.bold = True
    p.font.color.rgb = GOLD_ACCENT

    f_blocks = [
        ("BLOCK 1: LOCAL AI RUNTIME", CYAN_ACCENT, [
            ("Model Checkpoint", "RemoteCLIP ViT-B-32 (605 MB)"),
            ("Host Memory", "8–16 GB RAM (CPU sufficient)"),
            ("Vector Index", "FAISS CPU IndexIDMap(FlatIP)"),
            ("Index Latency", "2.0 ms per 24-tile scan"),
            ("Total Inference", "66.1 ms end-to-end query")
        ]),
        ("BLOCK 2: REAL SATELLITE DATA", GREEN_ACCENT, [
            ("Sensor", "ESA Copernicus Sentinel-2 MSI"),
            ("Level & Bands", "Level-2A BOA (B02, B03, B04, B08)"),
            ("Grid Standard", "MGRS 43RGM / EPSG:32643 UTM"),
            ("Spatial Resolution", "10m Ground Sample Distance"),
            ("Cloud Handling", "Scene Classification Layer (SCL)")
        ]),
        ("BLOCK 3: DETERMINISTIC ANALYSIS", GOLD_ACCENT, [
            ("Production Threshold", "Calibrated fixed τ = 0.15"),
            ("Spectral Math", "NDVI & NDWI deterministic shifts"),
            ("Spatial Topology", "scipy.ndimage connected components"),
            ("No Hallucination", "Rule-based attribution support"),
            ("Reproducibility", "Deterministic, repeatable results")
        ])
    ]
    fb_top = Inches(1.85)
    fb_h = Inches(1.38)
    fb_gap = Inches(0.12)
    for idx, (b_title, b_col, b_items) in enumerate(f_blocks):
        by = fb_top + idx * (fb_h + fb_gap)
        c_fb = create_panel(slide, Inches(0.80), by, col1_w - Inches(0.30), fb_h, border_color=CARD_BORDER, bg_color=CARD_INNER)
        tb_b = slide.shapes.add_textbox(Inches(0.90), by + Inches(0.06), col1_w - Inches(0.50), fb_h - Inches(0.12))
        tf_b = tb_b.text_frame
        tf_b.word_wrap = True
        tf_b.margin_left = tf_b.margin_top = tf_b.margin_right = tf_b.margin_bottom = 0
        
        p = tf_b.paragraphs[0]
        p.text = b_title
        p.font.name = FONT_MONO
        p.font.size = Pt(7.6)
        p.font.bold = True
        p.font.color.rgb = b_col

        for k, v in b_items:
            p_it = tf_b.add_paragraph()
            r1 = p_it.add_run()
            r1.text = f"• {k}: "
            r1.font.name = FONT_BODY
            r1.font.size = Pt(7.0)
            r1.font.bold = True
            r1.font.color.rgb = TEXT_WHITE
            r2 = p_it.add_run()
            r2.text = v
            r2.font.name = FONT_BODY
            r2.font.size = Pt(6.8)
            r2.font.color.rgb = TEXT_MUTED

    # 2. Center Column: Real Sentinel-2 Validation (LARGEST VISUAL)
    col2_w = Inches(5.65)
    c_val = create_panel(slide, Inches(3.95), Inches(1.30), col2_w, Inches(5.05), border_color=BORDER_ACTIVE, bg_color=CARD_BG)
    tb_vh = slide.shapes.add_textbox(Inches(4.10), Inches(1.42), col2_w - Inches(0.30), Inches(0.35))
    tf_vh = tb_vh.text_frame
    tf_vh.margin_left = tf_vh.margin_top = tf_vh.margin_right = tf_vh.margin_bottom = 0
    p = tf_vh.paragraphs[0]
    p.text = "REAL SENTINEL-2 MULTI-DATE VALIDATION (MGRS 43RGM · NCR INDIA)"
    p.font.name = FONT_MONO
    p.font.size = Pt(8.8)
    p.font.bold = True
    p.font.color.rgb = GOLD_ACCENT

    # 3 Real Images Side-by-Side (Authentic Rasters)
    img_w = Inches(1.65)
    img_h = Inches(1.65)
    img_gap = Inches(0.15)
    img_top = Inches(1.85)

    tri_data = [
        ("T0 · 19 MAY 2023", "Pre-Monsoon Baseline", "sentinel2_t0_rgb.jpg", "NIR: 0.480 | NDVI: +0.192"),
        ("TMID · 06 OCT 2023", "Post-Monsoon Peak", "sentinel2_tmid_rgb.jpg", "NIR: 0.279 | NDVI: +0.112"),
        ("T1 · 05 DEC 2023", "Winter Post-Harvest", "sentinel2_t1_rgb.jpg", "NIR: 0.254 | NDVI: +0.092")
    ]
    for idx, (t_date, t_phase, t_file, t_stats) in enumerate(tri_data):
        ix = Inches(4.10) + idx * (img_w + img_gap)
        c_sub = create_panel(slide, ix, img_top, img_w, img_h + Inches(0.70), border_color=CARD_BORDER, bg_color=CARD_INNER)
        
        safe_add_image(slide, os.path.join(ASSETS_DIR, t_file), ix + Inches(0.05), img_top + Inches(0.05), img_w - Inches(0.10), img_h - Inches(0.10))

        tb_lbl = slide.shapes.add_textbox(ix + Inches(0.05), img_top + img_h, img_w - Inches(0.10), Inches(0.65))
        tf_lbl = tb_lbl.text_frame
        tf_lbl.word_wrap = True
        tf_lbl.margin_left = tf_lbl.margin_top = tf_lbl.margin_right = tf_lbl.margin_bottom = 0
        p_l = tf_lbl.paragraphs[0]
        p_l.text = t_date
        p_l.font.name = FONT_MONO
        p_l.font.size = Pt(7.2)
        p_l.font.bold = True
        p_l.font.color.rgb = CYAN_ACCENT if idx == 0 else (GREEN_ACCENT if idx == 1 else GOLD_ACCENT)

        p_sub2 = tf_lbl.add_paragraph()
        r = p_sub2.add_run()
        r.text = f"{t_phase}\n{t_stats}"
        r.font.name = FONT_BODY
        r.font.size = Pt(6.5)
        r.font.color.rgb = TEXT_MUTED

    # Validation Empirical Metrics Card
    m_box = create_panel(slide, Inches(4.10), Inches(4.30), col2_w - Inches(0.30), Inches(1.90), border_color=CARD_BORDER, bg_color=CARD_INNER)
    tb_m = slide.shapes.add_textbox(Inches(4.25), Inches(4.38), col2_w - Inches(0.60), Inches(1.75))
    tf_m = tb_m.text_frame
    tf_m.word_wrap = True
    tf_m.margin_left = tf_m.margin_top = tf_m.margin_right = tf_m.margin_bottom = 0

    p = tf_m.paragraphs[0]
    p.text = "EMPIRICAL OBSERVATION METRICS (262,144 VALID PIXELS · 10M GSD):"
    p.font.name = FONT_MONO
    p.font.size = Pt(8.0)
    p.font.bold = True
    p.font.color.rgb = GOLD_ACCENT

    p_frac = tf_m.add_paragraph()
    p_frac.space_before = Pt(2)
    r = p_frac.add_run()
    r.text = (
        "• Interval Change Fractions (τ = 0.15):\n"
        "   T0 → TMID: 0.7% (1,820 px)  |  TMID → T1: 0.2% (619 px)  |  T0 → T1: 1.0% (2,542 px)\n"
        "• 5-State MECE Trajectory Distribution:\n"
        "   STABLE: 98.75% (258,869 px)  |  PERSISTENT: 0.39%  |  TRANSIENT: 0.24%\n"
        "   LATE_ONSET: 0.52%  |  REVERSIBLE: 0.10%  |  Total MECE Sum: 100.0%\n"
        "• Heuristic Attribution Support:\n"
        "   Built-Surface: 51.1%  |  Vegetation: 24.7%  |  Seasonal: 19.9%  |  Unresolved: 3.1%\n"
        "• SYSTEM VERDICT: REVIEW  (1.0% change < 5% threshold; routed to human analyst)"
    )
    r.font.name = FONT_BODY
    r.font.size = Pt(7.0)
    r.font.color.rgb = TEXT_WHITE

    # 3. Right Column: Viability & Sustainability
    col3_w = Inches(3.00)
    c_v = create_panel(slide, Inches(9.70), Inches(1.30), col3_w, Inches(5.05), border_color=BORDER_ACTIVE, bg_color=CARD_BG)
    tb_vh2 = slide.shapes.add_textbox(Inches(9.85), Inches(1.42), col3_w - Inches(0.30), Inches(0.35))
    tf_vh2 = tb_vh2.text_frame
    tf_vh2.margin_left = tf_vh2.margin_top = tf_vh2.margin_right = tf_vh2.margin_bottom = 0
    p = tf_vh2.paragraphs[0]
    p.text = "OPERATIONAL VIABILITY"
    p.font.name = FONT_MONO
    p.font.size = Pt(9.0)
    p.font.bold = True
    p.font.color.rgb = GOLD_ACCENT

    viability_items = [
        ("OFFLINE-FIRST", CYAN_ACCENT, "Air-gapped operation verified via offline_test.py. Zero cloud network egress."),
        ("ANALYST-IN-THE-LOOP", GREEN_ACCENT, "Augments rather than replaces analysts. Transparent physical evidence dossiers."),
        ("MODULAR ARCHITECTURE", GOLD_ACCENT, "Clean decoupled interfaces for index backend, sensor adapters, and persistence engines."),
        ("SCALABILITY POTENTIAL", TEXT_WHITE, "FAISS IndexIVFFlat/HNSW scalable to millions of tiles without changing pipeline code.")
    ]
    vy_top = Inches(1.85)
    vy_h = Inches(1.02)
    vy_gap = Inches(0.10)
    for idx, (v_title, v_col, v_desc) in enumerate(viability_items):
        vy = vy_top + idx * (vy_h + vy_gap)
        c_vb = create_panel(slide, Inches(9.85), vy, col3_w - Inches(0.30), vy_h, border_color=CARD_BORDER, bg_color=CARD_INNER)
        tb_b = slide.shapes.add_textbox(Inches(9.95), vy + Inches(0.06), col3_w - Inches(0.50), vy_h - Inches(0.12))
        tf_b = tb_b.text_frame
        tf_b.word_wrap = True
        tf_b.margin_left = tf_b.margin_top = tf_b.margin_right = tf_b.margin_bottom = 0
        
        p = tf_b.paragraphs[0]
        p.text = v_title
        p.font.name = FONT_MONO
        p.font.size = Pt(7.6)
        p.font.bold = True
        p.font.color.rgb = v_col

        p_d = tf_b.add_paragraph()
        r = p_d.add_run()
        r.text = v_desc
        r.font.name = FONT_BODY
        r.font.size = Pt(7.0)
        r.font.color.rgb = TEXT_MUTED

    # 4. Bottom Mandate Strip
    bot_bar = create_panel(slide, Inches(0.65), Inches(6.48), Inches(12.033), Inches(0.50), border_color=CARD_BORDER, bg_color=PILL_BG)
    tb_b = slide.shapes.add_textbox(Inches(0.75), Inches(6.54), Inches(11.833), Inches(0.38))
    tf_b = tb_b.text_frame
    tf_b.margin_left = tf_b.margin_top = tf_b.margin_right = tf_b.margin_bottom = 0
    p = tf_b.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    
    badges = [
        ("135 / 135 TESTS PASSING (100%)", GREEN_ACCENT),
        ("ZERO RUNTIME EXTERNAL CALLS", CYAN_ACCENT),
        ("262,144 VALID SENTINEL-2 PIXELS", GOLD_ACCENT),
        ("DETERMINISTIC τ = 0.15", TEXT_WHITE),
        ("AIR-GAPPED READY", GREEN_ACCENT)
    ]
    for b_txt, b_col in badges:
        r = p.add_run()
        r.text = f"[{b_txt}]   "
        r.font.name = FONT_MONO
        r.font.size = Pt(7.8)
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

    # 1. Strategic Impact Chain (Full Width)
    top_y = Inches(1.30)
    c_chain = create_panel(slide, Inches(0.65), top_y, Inches(12.033), Inches(0.65), border_color=BORDER_ACTIVE, bg_color=CARD_BG)
    tb_ch = slide.shapes.add_textbox(Inches(0.80), top_y + Inches(0.08), Inches(11.733), Inches(0.50))
    tf_ch = tb_ch.text_frame
    tf_ch.word_wrap = True
    tf_ch.margin_left = tf_ch.margin_top = tf_ch.margin_right = tf_ch.margin_bottom = 0
    
    p = tf_ch.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    
    chain_steps = [
        ("SATELLITE ARCHIVE", TEXT_MUTED),
        (" → ", GOLD_ACCENT),
        ("NATURAL-LANGUAGE DISCOVERY", CYAN_ACCENT),
        (" → ", GOLD_ACCENT),
        ("RELEVANT SCENE", GREEN_ACCENT),
        (" → ", GOLD_ACCENT),
        ("TEMPORAL COMPARISON", AMBER_ACCENT),
        (" → ", GOLD_ACCENT),
        ("EVIDENCE REVIEW", CYAN_ACCENT),
        (" → ", GOLD_ACCENT),
        ("ANALYST DECISION", GOLD_ACCENT),
    ]
    for text_val, text_col in chain_steps:
        r = p.add_run()
        r.text = text_val
        r.font.name = FONT_MONO
        r.font.size = Pt(8.2)
        r.font.bold = True
        r.font.color.rgb = text_col

    # 2. Four Operational Use Cases (2x2 Grid)
    grid_top = Inches(2.10)
    card_w = Inches(5.85)
    card_h = Inches(1.95)
    gap_x = Inches(0.33)
    gap_y = Inches(0.18)

    use_cases = [
        ("01 / INFRASTRUCTURE MONITORING", CYAN_ACCENT,
         "Forward Outpost, Tarmac & Fortified Perimeter Detection",
         "Quickly discover clandestine military construction, border tarmac paving, or forward fortified compounds. Natural-language intent isolates candidate tiles across thousands of square kilometers in seconds without coordinate guessing, decomposing spectral shifts to verify concrete/built signatures."),
        
        ("02 / STRATEGIC SITE DISCOVERY", GREEN_ACCENT,
         "Cross-Theater Facility Pattern Matching",
         "Given an operational requirement or known facility archetype, query the RemoteCLIP FAISS index to discover geographically separated candidate sites with similar visual-semantic features across the operational theater, cutting manual catalog triage by hours."),
        
        ("03 / ROAD / TERRAIN CORRIDOR CHANGE", GOLD_ACCENT,
         "Frontier Logistics Tracks, Earth Clearings & Bridgeheads",
         "Track emerging logistics road corridors and supply clearings across rugged frontier terrain. Spatial coherence analysis confirms contiguous linear infrastructure features while suppressing isolated single-pixel seasonal slope washouts and speckle."),
        
        ("04 / VEGETATION / WATER INTERPRETATION", AMBER_ACCENT,
         "Defending Against False-Alarm Alert Fatigue",
         "Enforces 3-date MECE persistence trajectories to distinguish agricultural crop cycles (monsoon greening to harvest senescence) from permanent ground-cover conversion, protecting command staff from false alarms while monitoring water reservoir expansion.")
    ]

    for idx, (u_title, u_col, u_sub, u_desc) in enumerate(use_cases):
        row = idx // 2
        col = idx % 2
        x = Inches(0.65) + col * (card_w + gap_x)
        y = grid_top + row * (card_h + gap_y)

        c = create_panel(slide, x, y, card_w, card_h, border_color=u_col, bg_color=CARD_BG)
        tb = slide.shapes.add_textbox(x + Inches(0.20), y + Inches(0.12), card_w - Inches(0.40), card_h - Inches(0.24))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p = tf.paragraphs[0]
        p.text = u_title
        p.font.name = FONT_MONO
        p.font.size = Pt(8.5)
        p.font.bold = True
        p.font.color.rgb = u_col

        p2 = tf.add_paragraph()
        p2.space_before = Pt(2)
        r_sub = p2.add_run()
        r_sub.text = u_sub
        r_sub.font.name = FONT_HEADING
        r_sub.font.size = Pt(8.0)
        r_sub.font.bold = True
        r_sub.font.color.rgb = TEXT_WHITE

        p3 = tf.add_paragraph()
        p3.space_before = Pt(2)
        r_desc = p3.add_run()
        r_desc.text = u_desc
        r_desc.font.name = FONT_BODY
        r_desc.font.size = Pt(7.4)
        r_desc.font.color.rgb = TEXT_MUTED

    # 3. Bottom Principles & Closing Mandate
    bot_y = Inches(6.38)
    bot_h = Inches(0.62)
    c_bot = create_panel(slide, Inches(0.65), bot_y, Inches(12.033), bot_h, border_color=BORDER_ACTIVE, bg_color=CARD_BG)

    tb_bot = slide.shapes.add_textbox(Inches(0.80), bot_y + Inches(0.06), Inches(11.733), bot_h - Inches(0.12))
    tf_bot = tb_bot.text_frame
    tf_bot.word_wrap = True
    tf_bot.margin_left = tf_bot.margin_top = tf_bot.margin_right = tf_bot.margin_bottom = 0

    p = tf_bot.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r_hdr = p.add_run()
    r_hdr.text = "CORE DEFENSE PRINCIPLES:   "
    r_hdr.font.name = FONT_MONO
    r_hdr.font.size = Pt(8.0)
    r_hdr.font.bold = True
    r_hdr.font.color.rgb = GOLD_ACCENT

    principles = [
        ("OFFLINE", "Air-gapped on-premises execution"),
        ("AUDITABLE", "Deterministic physical optics & spectral indices"),
        ("CONSERVATIVE", "Ambiguous cases routed to REVIEW")
    ]
    for pr_name, pr_desc in principles:
        r1 = p.add_run()
        r1.text = f"[{pr_name}: {pr_desc}]   "
        r1.font.name = FONT_BODY
        r1.font.size = Pt(7.6)
        r1.font.color.rgb = TEXT_WHITE

    p2 = tf_bot.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    p2.space_before = Pt(2)
    r2 = p2.add_run()
    r2.text = "“The goal is not to make every result positive. The goal is to make the result explainable.”"
    r2.font.name = FONT_TITLE
    r2.font.size = Pt(9.5)
    r2.font.bold = True
    r2.font.color.rgb = GOLD_ACCENT


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

    top_y = Inches(1.30)
    card_h = Inches(4.20)

    # 1. Left Panel: Research Foundation Flow
    col1_w = Inches(3.60)
    c_rf = create_panel(slide, Inches(0.65), top_y, col1_w, card_h, border_color=BORDER_ACTIVE, bg_color=CARD_BG)
    tb_rf = slide.shapes.add_textbox(Inches(0.80), top_y + Inches(0.12), col1_w - Inches(0.30), Inches(0.35))
    tf_rf = tb_rf.text_frame
    tf_rf.margin_left = tf_rf.margin_top = tf_rf.margin_right = tf_rf.margin_bottom = 0
    p = tf_rf.paragraphs[0]
    p.text = "RESEARCH FOUNDATION FLOW"
    p.font.name = FONT_MONO
    p.font.size = Pt(9.0)
    p.font.bold = True
    p.font.color.rgb = GOLD_ACCENT

    flow_nodes = [
        ("RemoteCLIP", "Chen et al., IEEE TGRS 2024", "Vision-language foundation model tailored for remote sensing semantic search."),
        ("Copernicus Sentinel-2", "ESA / European Commission", "Level-2A multispectral surface reflectance products (10m GSD BOA)."),
        ("OSCD Benchmark", "Daudt et al., IEEE IGARSS 2018", "Onera Satellite Change Detection benchmark ground truth."),
        ("Physical Index Math", "Rouse et al. / McFeeters", "NDVI & NDWI normalized band ratios for vegetation & water dynamics."),
        ("TERRAE Console", "Quantumcrew SIH26227", "Unified, evidence-based satellite investigation workstation.")
    ]
    fn_top = top_y + Inches(0.48)
    fn_h = Inches(0.68)
    fn_gap = Inches(0.06)
    for idx, (n_title, n_auth, n_desc) in enumerate(flow_nodes):
        ny = fn_top + idx * (fn_h + fn_gap)
        c_fn = create_panel(slide, Inches(0.80), ny, col1_w - Inches(0.30), fn_h, border_color=CARD_BORDER, bg_color=CARD_INNER)
        tb_fn = slide.shapes.add_textbox(Inches(0.90), ny + Inches(0.04), col1_w - Inches(0.50), fn_h - Inches(0.08))
        tf_fn = tb_fn.text_frame
        tf_fn.word_wrap = True
        tf_fn.margin_left = tf_fn.margin_top = tf_fn.margin_right = tf_fn.margin_bottom = 0
        
        p = tf_fn.paragraphs[0]
        r1 = p.add_run()
        r1.text = f"{idx+1}. {n_title} "
        r1.font.name = FONT_HEADING
        r1.font.size = Pt(7.6)
        r1.font.bold = True
        r1.font.color.rgb = CYAN_ACCENT if idx == 0 else (GREEN_ACCENT if idx == 1 else GOLD_ACCENT)

        r_au = p.add_run()
        r_au.text = f"({n_auth})\n"
        r_au.font.name = FONT_BODY
        r_au.font.size = Pt(6.8)
        r_au.font.color.rgb = TEXT_MUTED

        p2 = tf_fn.add_paragraph()
        r2 = p2.add_run()
        r2.text = n_desc
        r2.font.name = FONT_BODY
        r2.font.size = Pt(6.6)
        r2.font.color.rgb = TEXT_WHITE

    # 2. Center Panel: Validated Empirical Evidence
    col2_w = Inches(4.55)
    c_ev = create_panel(slide, Inches(4.35), top_y, col2_w, card_h, border_color=GREEN_ACCENT, bg_color=CARD_BG)
    tb_ev = slide.shapes.add_textbox(Inches(4.50), top_y + Inches(0.12), col2_w - Inches(0.30), Inches(0.35))
    tf_ev = tb_ev.text_frame
    tf_ev.margin_left = tf_ev.margin_top = tf_ev.margin_right = tf_ev.margin_bottom = 0
    p = tf_ev.paragraphs[0]
    p.text = "VALIDATED EMPIRICAL EVIDENCE"
    p.font.name = FONT_MONO
    p.font.size = Pt(9.0)
    p.font.bold = True
    p.font.color.rgb = GREEN_ACCENT

    tb_ev_body = slide.shapes.add_textbox(Inches(4.50), top_y + Inches(0.50), col2_w - Inches(0.30), card_h - Inches(0.60))
    tf_ev_b = tb_ev_body.text_frame
    tf_ev_b.word_wrap = True
    tf_ev_b.margin_left = tf_ev_b.margin_top = tf_ev_b.margin_right = tf_ev_b.margin_bottom = 0

    p_e1 = tf_ev_b.paragraphs[0]
    p_e1.text = "1. REAL SENTINEL-2 VALIDATION (MGRS 43RGM · NCR INDIA)"
    p_e1.font.name = FONT_MONO
    p_e1.font.size = Pt(8.0)
    p_e1.font.bold = True
    p_e1.font.color.rgb = GOLD_ACCENT

    p_e1_sub = tf_ev_b.add_paragraph()
    r = p_e1_sub.add_run()
    r.text = (
        "• Analysis Tile: 512×512 (262,144 valid pixels, 10m GSD)\n"
        "• Observations: T0 (19 May 2023), TMID (06 Oct 2023), T1 (05 Dec 2023)\n"
        "• Change Fractions: T0→TMID: 0.7% | TMID→T1: 0.2% | T0→T1: 1.0%\n"
        "• Trajectory Distribution: STABLE = 98.75% (258,869 px)\n"
        "• Attribution: Built 51.1% | Veg 24.7% | Seasonal 19.9% | Unresolved 3.1%\n"
        "• System Verdict: REVIEW (Conservative routing on 1.0% change)"
    )
    r.font.name = FONT_BODY
    r.font.size = Pt(7.2)
    r.font.color.rgb = TEXT_WHITE

    p_e2 = tf_ev_b.add_paragraph()
    p_e2.space_before = Pt(5)
    p_e2.text = "2. OSCD BENCHMARK — 5-PAIR VALIDATION SUBSET"
    p_e2.font.name = FONT_MONO
    p_e2.font.size = Pt(8.0)
    p_e2.font.bold = True
    p_e2.font.color.rgb = CYAN_ACCENT

    p_e2_sub = tf_ev_b.add_paragraph()
    r2 = p_e2_sub.add_run()
    r2.text = (
        "• Pairs: Aguas Claras, Beirut, Bordeaux, Cupertino, Mumbai\n"
        "• Valid Pixels Evaluated: 3,025,938 valid pixels | Fixed τ = 0.15\n"
        "• Micro Aggregate: Precision 57.55% | Recall 9.72% | F1 0.1663 | IoU 0.0907\n"
        "• Macro Average: Precision 52.22% | Recall 7.84% | F1 0.1267 | IoU 0.0692\n"
        "• Class Imbalance Note: Accuracy (97.90%) is dominated by 97.64% unchanged ground truth. Low recall reflects conservative noise suppression."
    )
    r2.font.name = FONT_BODY
    r2.font.size = Pt(7.0)
    r2.font.color.rgb = TEXT_MUTED

    # 3. Right Panel: Project Access & Team Details
    col3_w = Inches(3.783)
    c_pa = create_panel(slide, Inches(9.00), top_y, col3_w, card_h, border_color=CYAN_ACCENT, bg_color=CARD_BG)
    tb_pa = slide.shapes.add_textbox(Inches(9.15), top_y + Inches(0.12), col3_w - Inches(0.30), Inches(0.35))
    tf_pa = tb_pa.text_frame
    tf_pa.margin_left = tf_pa.margin_top = tf_pa.margin_right = tf_pa.margin_bottom = 0
    p = tf_pa.paragraphs[0]
    p.text = "PROJECT ACCESS & TEAM DETAILS"
    p.font.name = FONT_MONO
    p.font.size = Pt(9.0)
    p.font.bold = True
    p.font.color.rgb = CYAN_ACCENT

    tb_pa_body = slide.shapes.add_textbox(Inches(9.15), top_y + Inches(0.50), col3_w - Inches(0.30), card_h - Inches(0.60))
    tf_pa_b = tb_pa_body.text_frame
    tf_pa_b.word_wrap = True
    tf_pa_b.margin_left = tf_pa_b.margin_top = tf_pa_b.margin_right = tf_pa_b.margin_bottom = 0

    team_details = [
        ("Team Name", f"{TEAM_NAME}"),
        ("Team ID", f"{TEAM_ID}"),
        ("Problem Statement", f"{PS_ID} (Space Technology)"),
        ("Client Mandate", f"{MINISTRY}"),
        ("Category", f"{CATEGORY}"),
        ("Live Web Console", "terrae-geospatial-intelligence.vercel.app"),
        ("GitHub Repository", "github.com/PhantomCipher13/terrae-geospatial-intelligence"),
        ("Technical Report", "REPORT.md (Full 6-Part Scientific Dossier)"),
        ("Automated Tests", "135 / 135 Tests Passing (pytest)")
    ]
    for idx, (label, val) in enumerate(team_details):
        p_t = tf_pa_b.paragraphs[0] if idx == 0 else tf_pa_b.add_paragraph()
        if idx > 0:
            p_t.space_before = Pt(2)
        r1 = p_t.add_run()
        r1.text = f"• {label}: "
        r1.font.name = FONT_BODY
        r1.font.size = Pt(7.3)
        r1.font.bold = True
        r1.font.color.rgb = TEXT_WHITE
        r2 = p_t.add_run()
        r2.text = val
        r2.font.name = FONT_MONO if any(k in val for k in ["github", "vercel", "REPORT", "135"]) else FONT_BODY
        r2.font.size = Pt(7.0)
        r2.font.color.rgb = CYAN_ACCENT if any(k in val for k in ["github", "vercel"]) else TEXT_MUTED

    # 4. Bottom Literature References Strip
    ref_y = Inches(5.60)
    ref_h = Inches(0.85)
    c_ref = create_panel(slide, Inches(0.65), ref_y, Inches(12.033), ref_h, border_color=CARD_BORDER, bg_color=CARD_INNER)
    tb_rf_txt = slide.shapes.add_textbox(Inches(0.80), ref_y + Inches(0.06), Inches(11.733), ref_h - Inches(0.12))
    tf_rf_t = tb_rf_txt.text_frame
    tf_rf_t.word_wrap = True
    tf_rf_t.margin_left = tf_rf_t.margin_top = tf_rf_t.margin_right = tf_rf_t.margin_bottom = 0

    p_r1 = tf_rf_t.paragraphs[0]
    p_r1.text = "SCIENTIFIC & BENCHMARK REFERENCES:"
    p_r1.font.name = FONT_MONO
    p_r1.font.size = Pt(7.5)
    p_r1.font.bold = True
    p_r1.font.color.rgb = GOLD_ACCENT

    p_r2 = tf_rf_t.add_paragraph()
    r = p_r2.add_run()
    r.text = (
        "[1] Chen et al. (2024), RemoteCLIP: A Vision-Language Foundation Model for Remote Sensing, IEEE TGRS.  "
        "[2] European Space Agency (ESA), Copernicus Sentinel-2 MSI Level-2A ATBD.  "
        "[3] Daudt et al. (2018), Urban Change Detection for Multispectral Earth Observation, IEEE IGARSS (OSCD Benchmark).  "
        "[4] Rouse et al. (1974), Monitoring Vegetation Systems with ERTS, NASA SP-351 (NDVI).  "
        "[5] McFeeters (1996), Use of NDWI in Delineation of Open Water Features, Int. J. Remote Sens."
    )
    r.font.name = FONT_BODY
    r.font.size = Pt(6.8)
    r.font.color.rgb = TEXT_MUTED

    # 5. Final Motto Banner
    c_close = create_panel(slide, Inches(0.65), Inches(6.52), Inches(12.033), Inches(0.46), border_color=BORDER_ACTIVE, bg_color=PILL_BG)
    tb_cl = slide.shapes.add_textbox(Inches(0.80), Inches(6.56), Inches(11.733), Inches(0.38))
    tf_cl = tb_cl.text_frame
    tf_cl.margin_left = tf_cl.margin_top = tf_cl.margin_right = tf_cl.margin_bottom = 0
    p_cl = tf_cl.paragraphs[0]
    p_cl.alignment = PP_ALIGN.CENTER
    r_cl = p_cl.add_run()
    r_cl.text = "“Investigate the change. Follow the evidence. Know when to review.”"
    r_cl.font.name = FONT_TITLE
    r_cl.font.size = Pt(11.5)
    r_cl.font.bold = True
    r_cl.font.color.rgb = GOLD_ACCENT


# ---------------------------------------------------------------------------
# MAIN PRESENTATION COMPILER
# ---------------------------------------------------------------------------
def generate_all():
    print("=== BUILDING SIH 2026 MASTER PRESENTATION (EXACTLY 6 SLIDES) ===")
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
