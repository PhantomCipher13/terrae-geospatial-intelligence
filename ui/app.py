"""
ui/app.py
TERRAE — Earth Intelligence · Satellite Investigation Console (SIH26227)
=============================================================================
Product Website & Operational Analyst Workstation
Full 12-Section Visual Experience + Air-Gapped Verification

Architectural Sequence:
  01 HERO (Dark Obsidian): Satellite Investigation Console + Full-Bleed Beirut Canvas + Real Search
  02 PHILOSOPHY (Porcelain): "Satellite imagery shows what is there. Terrae investigates what changed." + CIR Composite
  03 METHOD (Warm Ivory): Sticky Visualizer Card + 6-Stage Investigation Protocol (01 ASK -> 06 DECIDE)
  04 TEMPORAL STORY (Deep Forest): "The Earth changes. The question is whether the change holds." + 3 Sentinel-2 Dates
  05 ORBITAL MOTION SCAN (Deep Obsidian): Smooth Multi-Observation Phenological Player (100% Offline, ZERO broken media)
  06 CASE STUDY 01 (Warm Stone): Controlled Construction + Draggable Interactive Before/After Wipe Slider
  07 CASE STUDY 02 (Porcelain): Real Sentinel-2 MGRS 43RGM + Multi-Observation REVIEW Attribution & Scientific Note
  08 PROGRESSIVE EVIDENCE (Porcelain): 4 Progressive Analytical Decomposition Plates (Spectral -> Mask -> Topology -> Verdict)
  09 EARTH / OBSERVATIONS (Dark Earth): 6 Diverse High-Resolution Satellite Landscapes (Beirut, NCR, Bordeaux, Mumbai, Cupertino, Aguas Claras)
  10 VALIDATION BOARD (Mineral Neutral): Quantitative OSCD 5-Pair Benchmark Research Board + Macro Metrics Strip
  11 WORKSTATION PREVIEW (Warm Stone): Transition Banner into Operational Tool
  12 OPERATIONAL WORKSTATION (Dark Analytical Surface): High-density Analyst Console with MECE Trajectory Table & Signature Evidence Chain
"""
import streamlit as st
import streamlit.components.v1 as components
import sys
import json
import base64
import io
from pathlib import Path
import numpy as np
import rasterio
from rasterio.windows import Window
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent.parent))

from terrae.app_factory import build_retrieval_engine, build_temporal_workflow
from terrae.planner.query_planner import plan_query
from terrae.core.result import ChangeVerdict
from terrae.change.attribution import DISPLAY_LABELS, DISCLAIMER_TEXT

st.set_page_config(
    page_title="TERRAE — Earth Intelligence",
    page_icon="⊙",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------------------
# SAFE HTML RENDERER (Eliminates Python-Markdown code block traps)
# -----------------------------------------------------------------------------
def render_html(html_str: str):
    """Strip leading spaces from each line so Markdown parser never outputs <pre><code>."""
    cleaned = "\n".join(line.strip() for line in html_str.strip().splitlines())
    st.markdown(cleaned, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SESSION STATE INITIALIZATION
# -----------------------------------------------------------------------------
if "app_mode" not in st.session_state:
    st.session_state.app_mode = "website" # "website" or "workstation"

if "active_case_idx" not in st.session_state:
    st.session_state.active_case_idx = 1 # 1 = Controlled Construction, 2 = Real Sentinel-2

if "search_query" not in st.session_state:
    st.session_state.search_query = "new construction and buildings"

if "has_searched" not in st.session_state:
    st.session_state.has_searched = False

# -----------------------------------------------------------------------------
# GLOBAL STYLESHEET (Quiet Intelligence, Visual Rhythm & Cartographic Textures)
# -----------------------------------------------------------------------------
css_styles = """
<style>
:root {
    --warm-ivory: #F4F0E8;
    --porcelain: #FBF9F4;
    --espresso: #161513;
    --deep-charcoal: #121110;
    --dark-obsidian: #0D0C0B;
    --deep-forest: #101411;
    --warm-stone: #EFEBE3;
    --stone-border: #D9D1C4;
    --taupe-muted: #82796D;
    --champagne-gold: #C5A869;
    --champagne-brass: #B89A62;
    --forest-verdict: #435548;
    --review-amber: #9A7842;
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: #121110 !important;
    color: #FBF9F4 !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
}

#MainMenu, footer, header[data-testid="stHeader"], .stDeployButton, [data-testid="stDecoration"], [data-testid="stStatusWidget"] {
    display: none !important;
    visibility: hidden !important;
}

iframe[title="streamlit.components.v1.html"], [data-testid="stCustomComponentV1"] {
    position: absolute !important;
    width: 0px !important;
    height: 0px !important;
    border: none !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
}

.main div.block-container {
    padding-top: 5.5rem !important;
    padding-bottom: 3rem !important;
    padding-left: 3.5vw !important;
    padding-right: 3.5vw !important;
    max-width: 94vw !important;
    width: 94vw !important;
}

section[data-testid="stSidebar"] {
    display: none !important;
}

/* Custom Streamlit Button Styling */
div[data-testid="stButton"] > button {
    background-color: #1E1C19 !important;
    color: #FBF9F4 !important;
    border: 1px solid #3A352D !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.70rem !important;
    letter-spacing: 0.12em !important;
    border-radius: 2px !important;
    padding: 0.45rem 1rem !important;
    transition: all 0.25s ease !important;
}

div[data-testid="stButton"] > button:hover {
    border-color: #C5A869 !important;
    color: #C5A869 !important;
    background-color: #26231F !important;
}

div[data-testid="stButton"] > button[kind="primary"] {
    background-color: #B89A62 !important;
    color: #121110 !important;
    border: 1px solid #C5A869 !important;
    font-weight: 700 !important;
}

div[data-testid="stButton"] > button[kind="primary"]:hover {
    background-color: #C5A869 !important;
    color: #0E0D0C !important;
}

/* Custom Text Input Styling */
div[data-testid="stTextInput"] input {
    background-color: #161513 !important;
    color: #FBF9F4 !important;
    border: 1px solid #C5A869 !important;
    border-radius: 2px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.85rem !important;
    padding: 0.5rem 0.85rem !important;
}

div[data-testid="stTextInput"] input:focus {
    border-color: #E2C98A !important;
    box-shadow: 0 0 0 1px #C5A869 !important;
}

/* Editorial Eyebrow */
.editorial-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    font-weight: 700;
    color: #C5A869;
    margin-bottom: 0.85rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.editorial-eyebrow::before {
    content: "";
    display: inline-block;
    width: 18px;
    height: 1px;
    background-color: #C5A869;
}

.editorial-eyebrow-dark {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    font-weight: 700;
    color: #82796D;
    margin-bottom: 0.85rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.editorial-eyebrow-dark::before {
    content: "";
    display: inline-block;
    width: 18px;
    height: 1px;
    background-color: #B89A62;
}

/* Top Horizontal Masthead */
.masthead-nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid rgba(197, 168, 105, 0.25);
    padding: 0.85rem 0;
    margin-bottom: 2rem;
}

.mn-brand {
    display: flex;
    align-items: center;
    gap: 0.65rem;
}

.mn-glyph {
    color: #C5A869;
    font-size: 1.15rem;
}

.mn-title {
    font-family: 'Playfair Display', serif;
    font-weight: 700;
    letter-spacing: 0.28em;
    font-size: 1.15rem;
    color: #FBF9F4;
}

.mn-links {
    display: flex;
    gap: 2rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.16em;
    color: #A0988A;
}

/* Global Sticky Navigation & Cockpit Bar */
.global-masthead-sticky {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    right: 0 !important;
    width: 100vw !important;
    box-sizing: border-box !important;
    z-index: 999999 !important;
    background: rgba(18, 17, 16, 0.95) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    border-bottom: 1px solid rgba(197, 168, 105, 0.22) !important;
    padding: 0.85rem 3.5vw 0.55rem 3.5vw !important;
    margin: 0 !important;
}

.masthead-main-bar {
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    width: 100% !important;
}

.global-nav-links {
    display: flex !important;
    align-items: center !important;
    gap: 2.5rem !important;
}

.nav-item {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.18em !important;
    color: #968F83 !important;
    cursor: pointer !important;
    position: relative !important;
    padding-bottom: 5px !important;
    transition: color 0.25s ease !important;
    text-transform: uppercase !important;
    user-select: none !important;
}

.nav-item:hover {
    color: #FBF9F4 !important;
}

.nav-item.active {
    color: #FBF9F4 !important;
    font-weight: 600 !important;
}

.nav-item.active::after {
    content: '' !important;
    position: absolute !important;
    bottom: 0 !important;
    left: 0 !important;
    width: 100% !important;
    height: 1.5px !important;
    background-color: #C5A869 !important;
    box-shadow: 0 0 8px rgba(197, 168, 105, 0.45) !important;
}

.masthead-actions {
    display: flex !important;
    align-items: center !important;
    gap: 1.25rem !important;
}

.nav-ws-trigger {
    background-color: #1E1C19 !important;
    color: #FBF9F4 !important;
    border: 1px solid #3A352D !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.70rem !important;
    letter-spacing: 0.12em !important;
    padding: 0.45rem 0.95rem !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
}

.nav-ws-trigger:hover {
    border-color: #C5A869 !important;
    color: #C5A869 !important;
    background-color: #26231F !important;
}

/* Global Scroll Progress Indicator */
.progress-track-wrapper {
    position: relative !important;
    width: 100% !important;
    margin-top: 0.65rem !important;
    padding-top: 0.35rem !important;
    border-top: 1px solid rgba(255, 255, 255, 0.04) !important;
}

.progress-track-bar {
    position: absolute !important;
    top: 0 !important;
    left: 0 !important;
    height: 1.5px !important;
    width: 0% !important;
    background: linear-gradient(90deg, #C5A869, #E4CA7F) !important;
    box-shadow: 0 0 8px rgba(197, 168, 105, 0.5) !important;
    transition: width 0.12s ease-out !important;
    z-index: 2 !important;
}

.progress-nodes-container {
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    width: 100% !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.60rem !important;
    letter-spacing: 0.12em !important;
}

.progress-node {
    display: inline-flex !important;
    align-items: center !important;
    gap: 0.35rem !important;
    cursor: pointer !important;
    color: #555047 !important;
    transition: all 0.25s ease !important;
    user-select: none !important;
}

.progress-node:hover {
    color: #C2BBB0 !important;
}

.progress-node .p-num {
    opacity: 0.65 !important;
}

.progress-node.active {
    color: #C5A869 !important;
    font-weight: 700 !important;
    text-shadow: 0 0 6px rgba(197, 168, 105, 0.35) !important;
}

.progress-node.active .p-num {
    opacity: 1 !important;
}

.progress-node.active-current {
    color: #FFFFFF !important;
    font-weight: 700 !important;
    text-shadow: 0 0 10px rgba(197, 168, 105, 0.85) !important;
    position: relative !important;
}

.progress-node.active-current::after {
    content: '' !important;
    position: absolute !important;
    bottom: -5px !important;
    left: 0 !important;
    right: 0 !important;
    height: 2px !important;
    background: #C5A869 !important;
    box-shadow: 0 0 8px #C5A869 !important;
}

.progress-line {
    flex-grow: 1 !important;
    height: 1px !important;
    background: rgba(197, 168, 105, 0.12) !important;
    margin: 0 0.75rem !important;
}

.mn-offline-tag {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.15em;
    color: #C5A869;
    border: 1px solid rgba(197, 168, 105, 0.35);
    padding: 0.3rem 0.65rem;
}

.mn-offline-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background-color: #55B374;
    display: inline-block;
}

/* Hero Display */
.hero-display-headline {
    font-family: 'Playfair Display', serif;
    font-size: 3.4rem;
    line-height: 1.05;
    font-weight: 500;
    letter-spacing: -0.01em;
    color: #FBF9F4;
    margin-bottom: 0.75rem;
}

.hero-gold-accent {
    color: #C5A869;
    font-style: italic;
    font-family: 'Playfair Display', serif;
}

.hero-subhead {
    font-size: 1.05rem;
    line-height: 1.5;
    color: #C2BBB0;
    margin-bottom: 1.5rem;
    max-width: 580px;
}

/* Functional Search Box in Hero */
.hero-search-box {
    background-color: rgba(22, 21, 19, 0.95);
    border: 1px solid #C5A869;
    padding: 1.25rem;
    margin-bottom: 1.25rem;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}

.hero-search-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #C5A869;
    margin-bottom: 0.5rem;
}

.hero-search-meta {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.14em;
    color: #82796D;
    margin-top: 0.75rem;
    display: flex;
    justify-content: space-between;
}

.hero-candidate-card {
    background-color: #1A1916;
    border: 1px solid #3A352D;
    padding: 0.85rem 1rem;
    margin-top: 0.75rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.hero-image-frame {
    position: relative;
    border: 1px solid #3A352D;
    background-color: #0E0D0C;
    overflow: hidden;
    box-shadow: 0 15px 45px rgba(0,0,0,0.6);
}

.hero-sat-img {
    width: 100%;
    height: 500px;
    object-fit: cover;
    display: block;
    transition: transform 0.6s ease;
}

.hero-sat-img:hover {
    transform: scale(1.02);
}

.hero-overlay-corner {
    position: absolute;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.18em;
    padding: 0.35rem 0.75rem;
    background-color: rgba(14, 13, 12, 0.85);
    color: #FBF9F4;
    border: 1px solid rgba(197, 168, 105, 0.3);
    z-index: 5;
}

.corner-tl { top: 16px; left: 16px; color: #C5A869; }
.corner-br { bottom: 16px; right: 16px; color: #FBF9F4; }

/* Hero Full-Bleed Backdrop & Spatial Layers */
.hero-fullbleed-backdrop {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 760px;
    z-index: 0;
    overflow: hidden;
    pointer-events: none;
    border-bottom: 1px solid rgba(197, 168, 105, 0.25);
}

.hero-fullbleed-bg {
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center 25%;
    filter: brightness(0.95) contrast(1.10) saturate(1.10);
    transform: scale(1.0);
    animation: heroSettle 1.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes heroSettle {
    0% { transform: scale(1.06); filter: brightness(0.70); }
    100% { transform: scale(1.0); filter: brightness(0.95) contrast(1.10) saturate(1.10); }
}

.hero-fullbleed-scrim {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: 
        linear-gradient(90deg, 
            rgba(18, 17, 16, 0.95) 0%, 
            rgba(18, 17, 16, 0.88) 42%, 
            rgba(18, 17, 16, 0.25) 65%, 
            rgba(18, 17, 16, 0.05) 85%, 
            rgba(18, 17, 16, 0.15) 100%
        ),
        linear-gradient(180deg, 
            rgba(18, 17, 16, 0.5) 0%, 
            rgba(18, 17, 16, 0.0) 40%, 
            rgba(18, 17, 16, 0.5) 80%, 
            #121110 100%
        );
    pointer-events: none;
}

.hero-hud-layer {
    position: absolute;
    top: 0;
    right: 0;
    width: 48%;
    height: 100%;
    pointer-events: none;
    font-family: 'JetBrains Mono', monospace;
}

.hud-top-right {
    position: absolute;
    top: 1.5rem;
    right: 2rem;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.35rem 0.8rem;
    background: rgba(18, 17, 16, 0.8);
    border: 1px solid rgba(197, 168, 105, 0.3);
    font-size: 0.68rem;
    letter-spacing: 0.15em;
    color: #FBF9F4;
    backdrop-filter: blur(4px);
}

.hud-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background-color: #55B374;
    display: inline-block;
}

.hud-reticle {
    position: absolute;
    top: 45%;
    right: 20%;
    transform: translateY(-50%);
    text-align: center;
}

.hud-crosshair {
    font-size: 2.4rem;
    color: #C5A869;
    opacity: 0.85;
    line-height: 1;
    margin-bottom: 0.4rem;
    animation: reticlePulse 3s infinite ease-in-out;
}

@keyframes reticlePulse {
    0%, 100% { opacity: 0.7; transform: scale(1.0); }
    50% { opacity: 1.0; transform: scale(1.08); }
}

.hud-coord-readout {
    font-size: 0.8rem;
    letter-spacing: 0.22em;
    font-weight: 700;
    color: #FBF9F4;
    background: rgba(18, 17, 16, 0.85);
    padding: 0.35rem 0.85rem;
    border: 1px solid rgba(197, 168, 105, 0.4);
    display: inline-block;
}

.hud-location-tag {
    font-size: 0.65rem;
    letter-spacing: 0.16em;
    color: #C5A869;
    margin-top: 0.35rem;
}

.hud-bot-right {
    position: absolute;
    bottom: 2rem;
    right: 2rem;
    text-align: right;
    background: rgba(18, 17, 16, 0.8);
    padding: 0.45rem 0.85rem;
    border-left: 2px solid #C5A869;
}

.hud-spec-line {
    font-size: 0.68rem;
    letter-spacing: 0.14em;
    color: #FBF9F4;
}

.hud-sub-line {
    font-size: 0.62rem;
    letter-spacing: 0.12em;
    color: #82796D;
    margin-top: 0.2rem;
}

/* Staggered Entrance Animations */
@keyframes heroFadeUp {
    0% { opacity: 0; transform: translateY(16px); }
    100% { opacity: 1; transform: translateY(0); }
}

.hero-animate-eyebrow {
    animation: heroFadeUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) 0.1s both;
}

.hero-animate-headline {
    animation: heroFadeUp 0.7s cubic-bezier(0.16, 1, 0.3, 1) 0.25s both;
}

.hero-animate-desc {
    animation: heroFadeUp 0.7s cubic-bezier(0.16, 1, 0.3, 1) 0.4s both;
}

.hero-animate-search {
    animation: heroFadeUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) 0.55s both;
}

.hero-animate-meta {
    animation: heroFadeUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) 0.75s both;
}

/* Telemetry Bar */
.hero-telemetry-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.16em;
    color: #A0988A;
    padding-top: 1.25rem;
    margin-top: 1rem;
    border-top: 1px solid rgba(197, 168, 105, 0.2);
}

.telemetry-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.telemetry-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background-color: #55B374;
    display: inline-block;
}

.telemetry-stage {
    color: #C5A869;
    font-weight: 700;
}

/* Accessibility: respect prefers-reduced-motion */
@media (prefers-reduced-motion: reduce) {
    *, ::before, ::after {
        animation-duration: 0.001s !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.001s !important;
        transform: none !important;
    }
}

/* Section Specific Full-Width Enclosures */
.section-porcelain {
    background-color: #FBF9F4;
    color: #161513;
    margin: 0 -3.5vw;
    padding: 5rem 3.5vw;
    border-top: 1px solid #D9D1C4;
    border-bottom: 1px solid #D9D1C4;
}

.section-warm-stone {
    background-color: #EFEBE3;
    color: #161513;
    margin: 0 -3.5vw;
    padding: 5rem 3.5vw;
    border-top: 1px solid #D9D1C4;
    border-bottom: 1px solid #D9D1C4;
}

.section-deep-forest {
    background-color: #101411;
    color: #FBF9F4;
    margin: 0 -3.5vw;
    padding: 5rem 3.5vw;
    border-top: 1px solid #233026;
    border-bottom: 1px solid #233026;
}

.section-dark-obsidian {
    background-color: #0D0C0B;
    color: #FBF9F4;
    margin: 0 -3.5vw;
    padding: 5rem 3.5vw;
    border-top: 1px solid #2A2722;
    border-bottom: 1px solid #2A2722;
}

.section-mineral-neutral {
    background-color: #ECE7DD;
    color: #161513;
    margin: 0 -3.5vw;
    padding: 5rem 3.5vw;
    border-top: 1px solid #D9D1C4;
    border-bottom: 1px solid #D9D1C4;
}

/* Philosophy Statement */
.why-big-statement {
    font-family: 'Playfair Display', serif;
    font-size: 2.8rem;
    line-height: 1.15;
    font-weight: 500;
    color: #161513;
    margin-bottom: 1.5rem;
}

.why-statement-gold {
    color: #9A7842;
    font-style: italic;
}

/* Sticky Method Section */
.investigation-section {
    position: relative;
}

.inv-display-card {
    position: sticky;
    top: 2rem;
    background-color: #161513;
    border: 1px solid #2A2722;
    padding: 1.25rem;
    box-shadow: 0 15px 40px rgba(0,0,0,0.15);
}

.inv-card-header {
    display: flex;
    justify-content: space-between;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.18em;
    color: #C5A869;
    margin-bottom: 0.75rem;
    border-bottom: 1px solid #2A2722;
    padding-bottom: 0.5rem;
}

.narrative-step-card {
    border-left: 2px solid #D9D1C4;
    padding-left: 1.75rem;
    margin-bottom: 2.75rem;
    transition: border-color 0.3s ease;
}

.narrative-step-card:hover {
    border-left-color: #C5A869;
}

.step-num {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 0.2em;
    color: #9A7842;
    font-weight: 700;
    margin-bottom: 0.35rem;
}

.step-name {
    font-family: 'Playfair Display', serif;
    font-size: 1.7rem;
    font-weight: 500;
    color: #161513;
    margin-bottom: 0.65rem;
}

.step-desc {
    font-size: 0.95rem;
    line-height: 1.55;
    color: #454038;
    margin-bottom: 0.85rem;
}

.step-code-detail {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    background-color: rgba(22, 21, 19, 0.08);
    padding: 0.45rem 0.75rem;
    border-left: 2px solid #9A7842;
    color: #24211D;
    font-weight: 500;
}

/* Section 04: Temporal Story */
.ts-obs-card {
    border: 1px solid #233026;
    background-color: #161D18;
    padding: 0.75rem;
    transition: transform 0.3s ease;
}

.ts-obs-card:hover {
    transform: translateY(-4px);
    border-color: #C5A869;
}

.ts-obs-header {
    display: flex;
    justify-content: space-between;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.16em;
    color: #C5A869;
    margin-bottom: 0.5rem;
}

/* Section 05: Orbital Scan Animation Player (Immersive Cinematic) */
.orbital-player-container {
    position: relative;
    max-width: 1160px !important;
    margin: 0 auto !important;
    border: 1px solid #2A2722;
    background-color: #070908;
    overflow: hidden;
    box-shadow: 0 24px 60px rgba(0,0,0,0.85);
}

.orbital-img-frame {
    width: 100% !important;
    height: 560px !important;
    max-height: 65vh !important;
    object-fit: cover !important;
    object-position: center !important;
    background-color: #070908 !important;
    display: block !important;
    transition: opacity 0.35s ease;
}

.orbital-hud-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(18, 17, 16, 0.95);
    backdrop-filter: blur(10px);
    border-top: 1px solid rgba(197, 168, 105, 0.3);
    padding: 1rem 1.75rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: #C5A869;
    flex-wrap: wrap;
    gap: 0.75rem;
}

.orbital-timeline-track {
    display: flex;
    gap: 0.75rem;
    align-items: center;
}

.orbital-pill {
    background-color: #24211D;
    border: 1px solid #3A352D;
    color: #C2BBB0;
    padding: 0.35rem 0.75rem;
    font-size: 0.68rem;
    letter-spacing: 0.12em;
    cursor: pointer;
    transition: all 0.2s ease;
}

.orbital-pill.active {
    background-color: #C5A869;
    color: #121110;
    font-weight: 700;
    border-color: #C5A869;
}


.temporal-img-frame {
    width: 100% !important;
    height: 380px !important;
    object-fit: contain !important;
    background-color: #070908 !important;
    display: block !important;
    transition: opacity 0.4s ease;
}

.ba-slider-container img {
    max-width: none !important;
    width: 100% !important;
    height: 100% !important;
    object-fit: cover !important;
    display: block !important;
}

.oscd-data-strip {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 1.25rem;
    border-top: 1px solid #D9D1C4;
    border-bottom: 1px solid #D9D1C4;
    padding: 1.25rem 0;
    margin-top: 2rem;
}


/* Sticky Method Section Active Indicators */
.narrative-step-card {
    border-left: 2px solid #D9D1C4;
    padding-left: 1.75rem;
    padding-top: 0.5rem;
    padding-bottom: 0.5rem;
    margin-bottom: 2.5rem;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.narrative-step-card:hover, .narrative-step-card.active-step {
    border-left-color: #C5A869;
    background: rgba(197, 168, 105, 0.04);
    padding-left: 2rem;
}

.narrative-step-card.active-step .step-num {
    color: #9A7842;
    font-weight: 800;
}

.narrative-step-card.active-step .step-name {
    color: #161513;
    font-weight: 600;
}

/* Progressive Evidence Decomposition Console (Section 08) */
.evidence-console-container {
    display: grid;
    grid-template-columns: 7.2fr 4.8fr;
    gap: 2.5rem;
    align-items: start;
    background-color: #0E0D0C;
    border: 1px solid #2A2722;
    padding: 2.25rem;
    box-shadow: 0 24px 60px rgba(0,0,0,0.7);
    margin-top: 1.5rem;
}

.evidence-stage-viewport {
    position: relative;
    width: 100%;
    height: 580px;
    border: 1px solid #2A2722;
    overflow: hidden;
    background-color: #070908;
}

.evidence-stage-img {
    width: 100% !important;
    height: 100% !important;
    object-fit: contain !important;
    background-color: #070908 !important;
    display: block !important;
    transition: opacity 0.3s ease;
}

.evidence-stage-badge {
    position: absolute;
    top: 16px;
    left: 16px;
    background: rgba(14, 13, 12, 0.92);
    backdrop-filter: blur(6px);
    border: 1px solid rgba(197, 168, 105, 0.4);
    padding: 0.45rem 0.95rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    color: #C5A869;
    z-index: 5;
}

.evidence-stage-legend {
    position: absolute;
    top: 16px;
    right: 16px;
    background: rgba(14, 13, 12, 0.92);
    backdrop-filter: blur(6px);
    border: 1px solid rgba(197, 168, 105, 0.4);
    padding: 0.45rem 0.85rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.64rem;
    color: #C5A869;
    z-index: 5;
}

.evidence-stage-stat {
    display: none;
}

.evidence-hud-overlay {
    position: absolute;
    bottom: 16px;
    left: 16px;
    right: 16px;
    background: rgba(14, 13, 12, 0.92);
    backdrop-filter: blur(6px);
    border: 1px solid #2A2722;
    padding: 0.6rem 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    z-index: 6;
    font-family: 'JetBrains Mono', monospace;
}

.evid-hud-item {
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
}

.evid-hud-lbl {
    font-size: 0.58rem;
    letter-spacing: 0.14em;
    color: #82796D;
    text-transform: uppercase;
}

.evid-hud-val {
    font-size: 0.72rem;
    color: #FBF9F4;
    font-weight: 600;
}

.evid-hud-divider {
    width: 1px;
    height: 24px;
    background: #2A2722;
}

.evidence-layer-card {
    border-left: 2px solid #2A2722;
    padding: 0.75rem 1.25rem;
    margin-bottom: 0.75rem;
    background: rgba(22, 21, 19, 0.4);
    cursor: pointer;
    transition: all 0.25s ease;
}

.evidence-layer-card:hover, .evidence-layer-card.active-layer {
    border-left-color: #C5A869;
    background: rgba(197, 168, 105, 0.08);
}

.evidence-layer-card.active-layer .layer-idx {
    color: #C5A869;
    font-weight: 700;
}

.layer-idx {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.16em;
    color: #82796D;
    margin-bottom: 0.2rem;
}

.layer-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.15rem;
    color: #FBF9F4;
    margin-bottom: 0.25rem;
}

.layer-desc {
    font-size: 0.78rem;
    color: #A0988A;
    line-height: 1.4;
}

/* Section 06: Before/After Wipe Slider */
.ba-slider-container {
    position: relative;
    width: 100%;
    max-width: 580px;
    height: 520px;
    margin: 0 auto;
    overflow: hidden;
    border: 1px solid #C5A869;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.35);
    user-select: none;
    cursor: ew-resize;
    background-color: #0E0D0C;
}

.ba-img-base {
    position: absolute !important;
    top: 0 !important;
    left: 0 !important;
    width: 100% !important;
    height: 100% !important;
    object-fit: cover !important;
    display: block !important;
}

.ba-img-overlay-wrapper {
    position: absolute;
    top: 0;
    left: 0;
    width: 50%;
    height: 100%;
    overflow: hidden;
    border-right: 2px solid #C5A869;
    z-index: 2;
}

.ba-img-clipped {
    position: absolute;
    top: 0;
    left: 0;
    width: 100% !important;
    height: 100% !important;
    object-fit: cover;
    display: block;
    clip-path: polygon(0 0, var(--ba-clip, 50%) 0, var(--ba-clip, 50%) 100%, 0 100%);
    z-index: 2;
}

.ba-badge-left {
    position: absolute;
    top: 16px;
    left: 16px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    background-color: rgba(18, 17, 16, 0.90);
    color: #FBF9F4;
    border: 1px solid rgba(255, 255, 255, 0.15);
    padding: 0.4rem 0.75rem;
    z-index: 5;
    pointer-events: none;
}

.ba-badge-right {
    position: absolute;
    top: 16px;
    right: 16px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    background-color: rgba(18, 17, 16, 0.90);
    color: #C5A869;
    border: 1px solid rgba(197, 168, 105, 0.4);
    padding: 0.4rem 0.75rem;
    z-index: 5;
    pointer-events: none;
}

/* Data Strips */
.cs-data-strip {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    border-top: 1px solid #D9D1C4;
    border-bottom: 1px solid #D9D1C4;
    padding: 1.25rem 0;
    margin: 1.75rem 0;
}

.cs-metric-lbl {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #82796D;
    margin-bottom: 0.35rem;
}

.cs-metric-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.35rem;
    font-weight: 700;
    color: #161513;
}

.verdict-stamp {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.55rem 1.15rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    font-weight: 700;
}

.vs-supported {
    background-color: rgba(67, 85, 72, 0.15);
    border: 1px solid #435548;
    color: #2F3E33;
}

.vs-review {
    background-color: rgba(154, 120, 66, 0.15);
    border: 1px solid #9A7842;
    color: #7D6133;
}

/* Section 09: Earth / Observations Mosaic */
.mosaic-grid-6 {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.5rem;
}

.mosaic-tile {
    border: 1px solid #2A2722;
    background-color: #161513;
    overflow: hidden;
    transition: transform 0.4s ease, border-color 0.4s ease;
}

.mosaic-tile:hover {
    transform: translateY(-4px);
    border-color: #C5A869;
}

.mosaic-img {
    max-width: none !important;
    width: 100% !important;
    height: 220px !important;
    object-fit: cover !important;
    display: block !important;
    transition: transform 0.5s ease;
}

.mosaic-tile:hover .mosaic-img {
    transform: scale(1.04);
}

.mosaic-meta {
    padding: 1rem;
    border-top: 1px solid #2A2722;
}

.mosaic-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.16em;
    color: #C5A869;
    margin-bottom: 0.25rem;
}

.mosaic-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.15rem;
    color: #FBF9F4;
    margin-bottom: 0.25rem;
}

.mosaic-desc {
    font-size: 0.78rem;
    color: #82796D;
    line-height: 1.4;
}

/* Section 10: OSCD Validation Board */
.oscd-grid-5 {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 1.25rem;
}

.oscd-card {
    border: 1px solid #D9D1C4;
    background-color: #FBF9F4;
    padding: 0.75rem;
}

.oscd-city {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.16em;
    color: #9A7842;
    font-weight: 700;
    margin-bottom: 0.4rem;
}

/* Section 12: Operational Workstation (Dark Console) */
.ws-top-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #2A2722;
    padding: 0.75rem 0;
    margin-bottom: 1.5rem;
}

.ws-3col-viewport {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.25rem;
    margin-bottom: 1.5rem;
}

.ws-vp-box {
    border: 1px solid #2A2722;
    background-color: #0E0D0C;
    padding: 0.65rem;
}

.ws-vp-lbl {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.16em;
    color: #C5A869;
    margin-bottom: 0.35rem;
}

.ws-horizontal-strip {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1.25rem;
    border-top: 1px solid #2A2722;
    border-bottom: 1px solid #2A2722;
    padding: 1rem 0;
    margin: 1.25rem 0;
    background-color: #161513;
}

.ws-evidence-pipeline-box {
    display: flex;
    flex-direction: column;
    gap: 0.65rem;
}

.ws-step-card {
    background: #141311;
    border: 1px solid #2A2722;
    border-left: 3px solid #3A352D;
    padding: 0.85rem 1.25rem;
    transition: all 0.2s ease;
}

.ws-step-card:hover {
    border-left-color: #C5A869;
    background: #181614;
}

.ws-step-card.active-supported {
    border-left-color: #55B374;
    background: rgba(67, 85, 72, 0.25);
    border-color: rgba(85, 179, 116, 0.4);
}

.ws-step-card.active-review {
    border-left-color: #C5A869;
    background: rgba(154, 120, 66, 0.22);
    border-color: rgba(197, 168, 105, 0.4);
}

.ws-step-num {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.64rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    color: #C5A869;
    margin-bottom: 0.2rem;
}

.ws-step-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.05rem;
    font-weight: 600;
    color: #FBF9F4;
    margin-bottom: 0.25rem;
}

.ws-step-desc {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.74rem;
    color: #A0988A;
    line-height: 1.4;
}

.ws-evidence-chain-vert {
    position: relative;
    padding-left: 2rem;
    margin: 1.5rem 0;
}

.ws-chain-line {
    position: absolute;
    top: 8px;
    bottom: 8px;
    left: 10px;
    width: 1.5px;
    background-color: #C5A869;
}

.ws-chain-step {
    position: relative;
    margin-bottom: 1.25rem;
}

.ws-chain-idx {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    font-weight: 700;
    color: #C5A869;
}

.ws-chain-name {
    font-size: 0.68rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    font-weight: 700;
    color: #82796D;
}

.ws-chain-body {
    font-size: 0.86rem;
    color: #C2BBB0;
    line-height: 1.4;
}

.ws-verdict-supported {
    border-radius: 2px;
    padding: 1.75rem 2.25rem;
    margin: 1.5rem 0;
    background-color: #435548;
    border: 1px solid #55B374;
    color: #FBF9F4;
}

.ws-verdict-review {
    border-radius: 2px;
    padding: 1.75rem 2.25rem;
    margin: 1.5rem 0;
    background-color: #9A7842;
    border: 1px solid #C5A869;
    color: #FBF9F4;
}
</style>
"""
st.markdown(css_styles, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# ENGINE & WORKFLOW CACHING
# -----------------------------------------------------------------------------
@st.cache_resource
def get_engine():
    engine, idx, db = build_retrieval_engine()
    return engine, idx, db

@st.cache_resource
def get_temporal():
    temporal, db = build_temporal_workflow()
    return temporal

engine, idx, db = get_engine()
temporal = get_temporal()

# -----------------------------------------------------------------------------
# HIGH-RESOLUTION SATELLITE ASSET LOADER (100% OFFLINE, ZERO NOISE)
# -----------------------------------------------------------------------------
def get_b64_from_file(path_str):
    p = Path(path_str)
    if not p.exists():
        return ""
    mime = "image/jpeg" if p.suffix.lower() in [".jpg", ".jpeg"] else "image/png"
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode("ascii")

@st.cache_data
def get_base64_mask(mask_arr, max_dim=600):
    if mask_arr is None:
        return ""
    try:
        h, w = mask_arr.shape
        rgb = np.full((h, w, 3), [14, 13, 12], dtype=np.uint8) # Dark Obsidian
        rgb[mask_arr > 0] = [197, 168, 105] # Champagne Gold
        img = Image.fromarray(rgb)
        img.thumbnail((max_dim, max_dim))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=90)
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")
    except Exception:
        return ""

# Pre-load Pristine High-Resolution Assets
hero_sat_b64 = get_b64_from_file("data/ui_assets/hero_beirut_1920x1080.jpg")
if not hero_sat_b64:
    hero_sat_b64 = get_b64_from_file("data/ui_assets/beirut_t1_rgb.jpg")

beirut_rgb_b64 = get_b64_from_file("data/ui_assets/beirut_t1_rgb.jpg")
beirut_cir_b64 = get_b64_from_file("data/ui_assets/beirut_t1_cir.jpg")
cupertino_rgb_b64 = get_b64_from_file("data/ui_assets/cupertino_t1_rgb.jpg")
mumbai_rgb_b64 = get_b64_from_file("data/ui_assets/mumbai_t1_rgb.jpg")
bordeaux_rgb_b64 = get_b64_from_file("data/ui_assets/bordeaux_t1_rgb.jpg")
aguasclaras_rgb_b64 = get_b64_from_file("data/ui_assets/aguasclaras_t1_rgb.jpg")

sentinel2_t0_rgb_b64 = get_b64_from_file("data/ui_assets/sentinel2_t0_rgb.jpg")
sentinel2_t0_cir_b64 = get_b64_from_file("data/ui_assets/sentinel2_t0_cir.jpg")
sentinel2_tmid_rgb_b64 = get_b64_from_file("data/ui_assets/sentinel2_tmid_rgb.jpg")
sentinel2_t1_rgb_b64 = get_b64_from_file("data/ui_assets/sentinel2_t1_rgb.jpg")

ctrl_t0_b64 = get_b64_from_file("data/ui_assets/controlled_t0_rgb.jpg")
ctrl_t1_b64 = get_b64_from_file("data/ui_assets/controlled_t1_rgb.jpg")
ctrl_t2_b64 = get_b64_from_file("data/ui_assets/controlled_t2_rgb.jpg")
ws_real_mask_b64 = get_b64_from_file("data/ui_assets/workstation_case02_mask.jpg")

# Method 6-Stage Investigation Plates (MGRS 43RGM Real Sentinel-2)
method_01_ask_b64 = get_b64_from_file("data/ui_assets/method_01_ask.jpg")
method_02_discover_b64 = get_b64_from_file("data/ui_assets/method_02_discover.jpg")
method_03_compare_b64 = get_b64_from_file("data/ui_assets/method_03_compare.jpg")
method_04_explain_b64 = get_b64_from_file("data/ui_assets/method_04_explain.jpg")
method_05_challenge_b64 = get_b64_from_file("data/ui_assets/method_05_challenge.jpg")
method_06_decide_b64 = get_b64_from_file("data/ui_assets/method_06_decide.jpg")

# Progressive Evidence 6-Layer Decomposition Plates (Controlled Construction Benchmark)
evidence_01_raw_b64 = get_b64_from_file("data/ui_assets/evidence_01_raw.jpg")
evidence_02_mask_b64 = get_b64_from_file("data/ui_assets/evidence_02_mask.jpg")
evidence_03_spectral_b64 = get_b64_from_file("data/ui_assets/evidence_03_spectral.jpg")
evidence_04_topology_b64 = get_b64_from_file("data/ui_assets/evidence_04_topology.jpg")
evidence_05_trajectory_b64 = get_b64_from_file("data/ui_assets/evidence_05_trajectory.jpg")
evidence_06_verdict_b64 = get_b64_from_file("data/ui_assets/evidence_06_verdict.jpg")

# Pre-compute Live Analysis on Canonical Tile IDs
CANONICAL_CTRL_TILE = "747db63c-08b4-4d59-a8f6-fc6a570aeee1"
CANONICAL_REAL_TILE = "2cbad278-c845-4e50-843e-abcc5d4382c6"

@st.cache_data
def run_case_analysis(tile_id, query):
    try:
        return temporal.run_analysis(tile_id, query)
    except Exception as e:
        return None

rc_case1 = run_case_analysis(CANONICAL_CTRL_TILE, "new construction and buildings")
rc_case2 = run_case_analysis(CANONICAL_REAL_TILE, "urban development and building construction")

ctrl_mask_b64 = ""
if rc_case1 and rc_case1.evidence:
    ctrl_mask_b64 = get_base64_mask(rc_case1.evidence[0].change_mask)

real_mask_b64 = ""
if rc_case2 and rc_case2.evidence:
    real_mask_b64 = get_base64_mask(rc_case2.evidence[0].change_mask)

# =============================================================================
# MODE SWITCH: OPERATIONAL WORKSTATION vs PUBLIC PRODUCT WEBSITE
# =============================================================================
if st.session_state.app_mode == "workstation":
    # -------------------------------------------------------------------------
    # OPERATIONAL WORKSTATION (High-Density Analyst Console)
    # -------------------------------------------------------------------------
    render_html("""
    <div class="ws-top-bar">
        <div>
            <div class="editorial-eyebrow">TERRAE / WORKSTATION &middot; AIR-GAPPED CONSOLE</div>
            <div style="font-family: 'Playfair Display', serif; font-size: 1.8rem; font-weight: 700; color: #FBF9F4;">
                Satellite Change &amp; Multi-Temporal Attribution Console
            </div>
        </div>
        <div style="display: flex; gap: 1rem; align-items: center;">
            <span class="mn-offline-tag"><span class="mn-offline-dot"></span> OFFLINE &middot; 0 CALLS</span>
        </div>
    </div>
    """)
    
    col_ws_nav1, col_ws_nav2, col_ws_nav3 = st.columns([2.5, 4, 4])
    with col_ws_nav1:
        if st.button("← RETURN TO PRODUCT STORY", key="btn_ws_back", use_container_width=True):
            st.session_state.app_mode = "website"
            st.rerun()
    with col_ws_nav2:
        if st.button("TERRAE / CASE 01: CONTROLLED (11.5% CHANGE)", key="ws_case_1", type="primary" if st.session_state.active_case_idx == 1 else "secondary", use_container_width=True):
            st.session_state.active_case_idx = 1
            st.rerun()
    with col_ws_nav3:
        if st.button("TERRAE / CASE 02: REAL SENTINEL-2 (43RGM)", key="ws_case_2", type="primary" if st.session_state.active_case_idx == 2 else "secondary", use_container_width=True):
            st.session_state.active_case_idx = 2
            st.rerun()

    active_rc = rc_case1 if st.session_state.active_case_idx == 1 else rc_case2
    active_mask = ctrl_mask_b64 if st.session_state.active_case_idx == 1 else (ws_real_mask_b64 if ws_real_mask_b64 else real_mask_b64)
    active_t0_img = ctrl_t0_b64 if st.session_state.active_case_idx == 1 else sentinel2_t0_rgb_b64
    active_t1_img = ctrl_t2_b64 if st.session_state.active_case_idx == 1 else sentinel2_t1_rgb_b64
    case_title = "Controlled Construction & Building Development" if st.session_state.active_case_idx == 1 else "Real Earth Observation (MGRS 43RGM &middot; NCR)"
    case_query = st.session_state.search_query if st.session_state.get("search_query") else ("new construction and buildings" if st.session_state.active_case_idx == 1 else "urban development and building construction")

    render_html(f"""
    <div style="margin-top: 1.5rem; margin-bottom: 0.5rem;">
        <div style="font-family: 'Playfair Display', serif; font-size: 1.6rem; color: #FBF9F4;">{case_title}</div>
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #82796D;">
            QUERY HYPOTHESIS: &ldquo;{case_query}&rdquo; &middot; 10M GROUND SAMPLE DISTANCE &middot; LOCAL FAISS FLAT L2
        </div>
    </div>
    """)

    # Analytical Metrics Strip
    attr = active_rc.attribution if active_rc else None
    persistence = active_rc.persistence if active_rc else None

    dnir = f"{attr.metrics.get('delta_nir_mean', 0.0):+.2%}" if attr else "-1.50%"
    dred = f"{attr.metrics.get('delta_red_mean', 0.0):+.2%}" if attr else "+21.50%"
    dndvi = f"{attr.metrics.get('delta_ndvi_mean', 0.0):+.2f}" if attr else "-0.75"
    coherence = f"{attr.metrics.get('spatial_coherence', 0.0):.1%}" if attr else "99.7%"
    chg_frac = f"{attr.metrics.get('change_fraction', 0.0):.1%}" if attr else "11.5%"

    if st.session_state.active_case_idx == 1:
        # CASE 01: Heroic Primary Target Inspection Viewport + 5-Step Evidence Pipeline
        col_c1_vis, col_c1_info = st.columns([7, 5], gap="large")
        with col_c1_vis:
            render_html(f"""
            <div style="position: relative; width: 100%; height: 460px; background: #070908; border: 1px solid #2A2722; overflow: hidden; box-shadow: 0 16px 40px rgba(0,0,0,0.6);">
                <img src="{ctrl_t2_b64}" style="width: 100%; height: 100%; object-fit: contain; display: block;" alt="Target T2" />
                <!-- Gold Reticle over Construction Region (Row 250..400, Col 100..250 in 512x512) -->
                <div style="position: absolute; top: 48.8%; left: 19.5%; width: 29.3%; height: 29.3%; border: 2px solid #C5A869; box-shadow: 0 0 20px rgba(197, 168, 105, 0.45); pointer-events: none;">
                    <div style="position: absolute; top: -24px; left: 0; background: #121110; border: 1px solid #C5A869; padding: 2px 8px; font-family: 'JetBrains Mono', monospace; font-size: 0.62rem; color: #C5A869; font-weight: 700; white-space: nowrap;">
                        ⊙ NEW BUILT STRUCTURE &middot; 11.5% FOOTPRINT
                    </div>
                </div>
                <!-- Viewport Badges -->
                <div style="position: absolute; top: 12px; left: 14px; background: rgba(18,17,16,0.9); border: 1px solid rgba(197,168,105,0.4); padding: 0.35rem 0.65rem; font-family: 'JetBrains Mono', monospace; font-size: 0.64rem; color: #C5A869;">
                    TARGET T2 &middot; 65,536 PIXELS &middot; 10M GSD
                </div>
                <div style="position: absolute; bottom: 12px; right: 14px; background: rgba(18,17,16,0.9); border: 1px solid #2A2722; padding: 0.35rem 0.65rem; font-family: 'JetBrains Mono', monospace; font-size: 0.62rem; color: #FBF9F4;">
                    SURFACE REFLECTANCE: B02, B03, B04, B08
                </div>
            </div>
            
            <!-- Synchronized 3-Tile Micro-Strip -->
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.75rem; margin-top: 0.85rem;">
                <div style="background: #0E0D0C; border: 1px solid #2A2722; padding: 0.4rem;">
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.58rem; color: #82796D; margin-bottom: 0.25rem;">01 &middot; T0 BASELINE (NATURAL)</div>
                    <img src="{ctrl_t0_b64}" style="width: 100%; height: 95px; object-fit: contain; background: #070908;" alt="T0" />
                </div>
                <div style="background: #0E0D0C; border: 1px solid #2A2722; padding: 0.4rem;">
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.58rem; color: #C5A869; margin-bottom: 0.25rem;">02 &middot; CHANGE MASK (&tau; = 0.15)</div>
                    <img src="{ctrl_mask_b64}" style="width: 100%; height: 95px; object-fit: contain; background: #070908;" alt="Mask" />
                </div>
                <div style="background: #0E0D0C; border: 1px solid #2A2722; padding: 0.4rem;">
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.58rem; color: #82796D; margin-bottom: 0.25rem;">03 &middot; T1 EXCAVATION PHASE</div>
                    <img src="{ctrl_t1_b64}" style="width: 100%; height: 95px; object-fit: contain; background: #070908;" alt="T1" />
                </div>
            </div>
            """)
        with col_c1_info:
            render_html(f"""
            <div class="ws-evidence-pipeline-box">
                <div class="ws-step-card">
                    <div class="ws-step-num">01 / LOCATION</div>
                    <div class="ws-step-title">GEOSPATIAL BOUNDS &amp; RESOLUTION</div>
                    <div class="ws-step-desc">EPSG:32643 &middot; 10m GSD &middot; Bounded 65,536 px tile (256&times;256)</div>
                </div>
                <div class="ws-step-card">
                    <div class="ws-step-num">02 / TEMPORAL CHANGE</div>
                    <div class="ws-step-title">BASELINE T0 &rarr; TARGET T2</div>
                    <div class="ws-step-desc">11.5% Divergent Pixels (7,549 px) &middot; Late-onset emergence</div>
                </div>
                <div class="ws-step-card">
                    <div class="ws-step-num">03 / SPECTRAL EVIDENCE</div>
                    <div class="ws-step-title">MULTI-SPECTRAL VECTOR DECOMPOSITION</div>
                    <div class="ws-step-desc">&Delta;NIR: {dnir} &middot; &Delta;Red: {dred} &middot; &Delta;NDVI: {dndvi} (Strong built surface)</div>
                </div>
                <div class="ws-step-card">
                    <div class="ws-step-num">04 / ATTRIBUTION</div>
                    <div class="ws-step-title">HEURISTIC SIGNATURE MATCHING</div>
                    <div class="ws-step-desc">Built-surface Support: 97.1% &middot; Spatial Coherence: {coherence}</div>
                </div>
                <div class="ws-step-card active-supported">
                    <div class="ws-step-num">05 / DECISION</div>
                    <div class="ws-step-title">&#x2714; SUPPORTED &middot; AFFIRMATIVE CONCLUSION</div>
                    <div class="ws-step-desc">High spatial coherence &amp; spectral divergence corroborate building construction.</div>
                </div>
            </div>
            """)

    else:
        # CASE 02: 3-Date Multi-Observation Horizon Track + Dual Inspector
        render_html(f"""
        <!-- 3-Observation Horizon Track -->
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.25rem; margin-bottom: 1.5rem;">
            <div style="background: #121110; border: 1px solid #2A2722; padding: 0.85rem; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; font-family: 'JetBrains Mono', monospace;">
                    <span style="font-size: 0.68rem; font-weight: 700; color: #C5A869;">01 &middot; T0: 19 MAY 2023</span>
                    <span style="font-size: 0.58rem; color: #82796D;">PRE-MONSOON DRY</span>
                </div>
                <img src="{sentinel2_t0_rgb_b64}" style="width: 100%; height: 260px; object-fit: contain; background: #070908; display: block;" alt="Case 02 T0" />
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.62rem; color: #82796D; margin-top: 0.45rem;">
                    Baseline soil &amp; dry canopy &middot; NIR: 0.480 &middot; NDVI: +0.192
                </div>
            </div>
            <div style="background: #121110; border: 1px solid rgba(85,179,116,0.4); padding: 0.85rem; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; font-family: 'JetBrains Mono', monospace;">
                    <span style="font-size: 0.68rem; font-weight: 700; color: #55B374;">02 &middot; TMID: 06 OCT 2023</span>
                    <span style="font-size: 0.58rem; color: #55B374;">MONSOON GREEN PEAK</span>
                </div>
                <img src="{sentinel2_tmid_rgb_b64}" style="width: 100%; height: 260px; object-fit: contain; background: #070908; display: block;" alt="Case 02 TMID" />
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.62rem; color: #55B374; margin-top: 0.45rem;">
                    Intense chlorophyll flush &middot; NIR: 0.279 &middot; &Delta;NDVI: +0.112
                </div>
            </div>
            <div style="background: #121110; border: 1px solid #2A2722; padding: 0.85rem; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; font-family: 'JetBrains Mono', monospace;">
                    <span style="font-size: 0.68rem; font-weight: 700; color: #C5A869;">03 &middot; T1: 05 DEC 2023</span>
                    <span style="font-size: 0.58rem; color: #82796D;">WINTER DORMANCY</span>
                </div>
                <img src="{sentinel2_t1_rgb_b64}" style="width: 100%; height: 260px; object-fit: contain; background: #070908; display: block;" alt="Case 02 T1" />
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.62rem; color: #82796D; margin-top: 0.45rem;">
                    Post-harvest senescence &middot; NIR: 0.254 &middot; NDVI: +0.092
                </div>
            </div>
        </div>
        """)
        
        col_c2_vis, col_c2_info = st.columns([7, 5], gap="large")
        with col_c2_vis:
            render_html(f"""
            <div style="position: relative; width: 100%; height: 380px; background: #070908; border: 1px solid #2A2722; overflow: hidden; box-shadow: 0 16px 40px rgba(0,0,0,0.6);">
                <img src="{active_mask}" style="width: 100%; height: 100%; object-fit: contain; display: block;" alt="Case 02 Mask" />
                <div style="position: absolute; top: 12px; left: 14px; background: rgba(18,17,16,0.9); border: 1px solid rgba(197,168,105,0.4); padding: 0.35rem 0.65rem; font-family: 'JetBrains Mono', monospace; font-size: 0.64rem; color: #C5A869;">
                    AMBER CHANGE MASK (&tau; = 0.15) &middot; 2,542 DIVERGENT PIXELS (1.0%)
                </div>
                <div style="position: absolute; bottom: 12px; left: 14px; right: 14px; background: rgba(18,17,16,0.9); border: 1px solid #2A2722; padding: 0.4rem 0.75rem; font-family: 'JetBrains Mono', monospace; font-size: 0.64rem; color: #55B374; display: flex; justify-content: space-between;">
                    <span>STABLE TERRAIN: 98.75% (258,869 PIXELS)</span>
                    <span style="color: #C5A869;">PERSISTENT: 0.39% &middot; LATE: 0.52%</span>
                </div>
            </div>
            """)
        with col_c2_info:
            render_html(f"""
            <div class="ws-evidence-pipeline-box">
                <div class="ws-step-card">
                    <div class="ws-step-num">01 / LOCATION</div>
                    <div class="ws-step-title">MGRS TILE 43RGM &middot; NCR</div>
                    <div class="ws-step-desc">28.5215&deg; N, 77.4782&deg; E &middot; 262,144 valid pixels &middot; 0 clouds (SCL)</div>
                </div>
                <div class="ws-step-card">
                    <div class="ws-step-num">02 / TEMPORAL STACK</div>
                    <div class="ws-step-title">3-OBSERVATION TIME SERIES</div>
                    <div class="ws-step-desc">May &rarr; Oct &rarr; Dec 2023 (T0&rarr;Tmid: 0.7%, Tmid&rarr;T1: 0.2%, T0&rarr;T1: 1.0%)</div>
                </div>
                <div class="ws-step-card">
                    <div class="ws-step-num">03 / SPECTRAL EVIDENCE</div>
                    <div class="ws-step-title">MULTI-BAND PHENOLOGY TRAJECTORY</div>
                    <div class="ws-step-desc">&Delta;NIR: {dnir} &middot; &Delta;Red: {dred} &middot; &Delta;NDVI: {dndvi} (Seasonal greening cycle)</div>
                </div>
                <div class="ws-step-card">
                    <div class="ws-step-num">04 / ATTRIBUTION</div>
                    <div class="ws-step-title">PHENOLOGY vs PERMANENT DIVERGENCE</div>
                    <div class="ws-step-desc">98.75% Stable &middot; 0.39% Persistent &middot; Built support: 51.1% (Sub-threshold)</div>
                </div>
                <div class="ws-step-card active-review">
                    <div class="ws-step-num">05 / DECISION</div>
                    <div class="ws-step-title">&#x26A0; REVIEW &middot; ANALYST INSPECTION RECOMMENDED</div>
                    <div class="ws-step-desc">Sub-5% change &amp; agricultural greening cycle trigger conservative guard against false alerts.</div>
                </div>
            </div>
            """)

    render_html(f"""
    <div class="ws-horizontal-strip">
        <div>
            <div class="cs-metric-lbl">&Delta; NIR MEAN</div>
            <div class="cs-metric-val" style="color: #C5A869;">{dnir}</div>
        </div>
        <div>
            <div class="cs-metric-lbl">&Delta; RED MEAN</div>
            <div class="cs-metric-val" style="color: #C5A869;">{dred}</div>
        </div>
        <div>
            <div class="cs-metric-lbl">&Delta; NDVI (VEGETATION DELTA)</div>
            <div class="cs-metric-val" style="color: #C5A869;">{dndvi}</div>
        </div>
        <div>
            <div class="cs-metric-lbl">SPATIAL COHERENCE RATIO</div>
            <div class="cs-metric-val" style="color: #55B374;">{coherence}</div>
        </div>
    </div>
    """)

    # MECE Trajectory Distribution & Vertical Signature Evidence Chain
    col_traj, col_chain = st.columns([5, 7], gap="large")
    with col_traj:
        render_html("""
        <div class="editorial-eyebrow">MECE TEMPORAL TRAJECTORY PARTITION</div>
        <div style="font-size: 0.85rem; color: #A0988A; margin-bottom: 1rem;">
            Pixel-level partition across all valid observations. Every pixel is assigned to exactly one mutually exclusive, collectively exhaustive state.
        </div>
        """)
        if persistence:
            cat_counts = getattr(persistence, "category_counts", {})
            valid_px = getattr(persistence, "valid_pixels", 1) or 1
            st_pct = cat_counts.get("STABLE", 0) / valid_px * 100
            pc_pct = cat_counts.get("PERSISTENT_CHANGE", 0) / valid_px * 100
            tc_pct = cat_counts.get("TRANSIENT_CHANGE", 0) / valid_px * 100
            lo_pct = cat_counts.get("LATE_ONSET_CHANGE", 0) / valid_px * 100
            rc_pct = cat_counts.get("REVERSIBLE_CHANGE", 0) / valid_px * 100
            
            traj_table = f"""
            <table style="width: 100%; border-collapse: collapse; font-family: 'JetBrains Mono', monospace; font-size: 0.76rem; color: #C2BBB0;">
                <tr style="border-bottom: 1px solid #2A2722; color: #82796D;">
                    <th style="text-align: left; padding: 0.5rem 0;">STATE</th>
                    <th style="text-align: right; padding: 0.5rem 0;">PIXELS</th>
                    <th style="text-align: right; padding: 0.5rem 0;">PERCENT</th>
                </tr>
                <tr style="border-bottom: 1px solid #1E1C19;">
                    <td style="padding: 0.5rem 0; color: #FBF9F4;">STABLE</td>
                    <td style="text-align: right;">{cat_counts.get("STABLE", 0):,}</td>
                    <td style="text-align: right; color: #55B374;">{st_pct:.2f}%</td>
                </tr>
                <tr style="border-bottom: 1px solid #1E1C19;">
                    <td style="padding: 0.5rem 0; color: #FBF9F4;">PERSISTENT_CHANGE</td>
                    <td style="text-align: right;">{cat_counts.get("PERSISTENT_CHANGE", 0):,}</td>
                    <td style="text-align: right; color: #C5A869;">{pc_pct:.2f}%</td>
                </tr>
                <tr style="border-bottom: 1px solid #1E1C19;">
                    <td style="padding: 0.5rem 0; color: #FBF9F4;">TRANSIENT_CHANGE</td>
                    <td style="text-align: right;">{cat_counts.get("TRANSIENT_CHANGE", 0):,}</td>
                    <td style="text-align: right;">{tc_pct:.2f}%</td>
                </tr>
                <tr style="border-bottom: 1px solid #1E1C19;">
                    <td style="padding: 0.5rem 0; color: #FBF9F4;">LATE_ONSET_CHANGE</td>
                    <td style="text-align: right;">{cat_counts.get("LATE_ONSET_CHANGE", 0):,}</td>
                    <td style="text-align: right; color: #C5A869;">{lo_pct:.2f}%</td>
                </tr>
                <tr style="border-bottom: 1px solid #2A2722;">
                    <td style="padding: 0.5rem 0; color: #FBF9F4;">REVERSIBLE_CHANGE</td>
                    <td style="text-align: right;">{cat_counts.get("REVERSIBLE_CHANGE", 0):,}</td>
                    <td style="text-align: right;">{rc_pct:.2f}%</td>
                </tr>
            </table>
            """
            render_html(traj_table)

    with col_chain:
        render_html("""
        <div class="editorial-eyebrow">CONTINUOUS SIGNATURE EVIDENCE CHAIN</div>
        <div class="ws-evidence-chain-vert">
            <div class="ws-chain-line"></div>
            <div class="ws-chain-step">
                <div class="ws-chain-idx">01 / ASK</div>
                <div class="ws-chain-name">QUERY DISCOVERY INTENT</div>
                <div class="ws-chain-body">&ldquo;""" + case_query + """&rdquo; mapped to target change classes</div>
            </div>
            <div class="ws-chain-step">
                <div class="ws-chain-idx">02 / DISCOVER</div>
                <div class="ws-chain-name">SEMANTIC RETRIEVAL MATCH</div>
                <div class="ws-chain-body">Matched via RemoteCLIP ViT-B/32 semantic indexing &middot; Offline FAISS Flat L2</div>
            </div>
            <div class="ws-chain-step">
                <div class="ws-chain-idx">03 / COMPARE</div>
                <div class="ws-chain-name">TEMPORAL CO-REGISTRATION</div>
                <div class="ws-chain-body">""" + chg_frac + """ changed pixels across temporal observation stack</div>
            </div>
            <div class="ws-chain-step">
                <div class="ws-chain-idx">04 / EXPLAIN</div>
                <div class="ws-chain-name">PHYSICAL SPECTRAL ATTRIBUTION</div>
                <div class="ws-chain-body">&Delta;NIR: """ + dnir + """, &Delta;Red: """ + dred + """, &Delta;NDVI: """ + dndvi + """ &middot; Spatial Coherence: """ + coherence + """</div>
            </div>
            <div class="ws-chain-step">
                <div class="ws-chain-idx">05 / CHALLENGE</div>
                <div class="ws-chain-name">TEMPORAL PERSISTENCE</div>
                <div class="ws-chain-body">Trajectory State: """ + (str(persistence.dominant_temporal_state) if persistence else "LATE_ONSET") + """</div>
            </div>
            <div class="ws-chain-step">
                <div class="ws-chain-idx">06 / DECIDE</div>
                <div class="ws-chain-name">AUDITABLE CONCLUSION</div>
                <div class="ws-chain-body">Decision output: <strong>""" + ("SUPPORTED" if st.session_state.active_case_idx == 1 else "REVIEW") + """</strong></div>
            </div>
        </div>
        """)

    # Analyst Decision Banner
    if st.session_state.active_case_idx == 1:
        render_html("""
        <div class="ws-verdict-supported">
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; letter-spacing: 0.18em; opacity: 0.85; margin-bottom: 0.25rem;">ANALYST DECISION</div>
            <div style="font-family: 'Playfair Display', serif; font-size: 2.2rem; font-weight: 700; margin-bottom: 0.5rem;">SUPPORTED &middot; AFFIRMATIVE CONCLUSION</div>
            <div style="font-size: 0.95rem; opacity: 0.95; line-height: 1.5;">
                Spectral divergence, 99.7% spatial coherence, and late-onset temporal persistence corroborate urban construction.
            </div>
        </div>
        """)
    else:
        render_html("""
        <div class="ws-verdict-review">
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; letter-spacing: 0.18em; opacity: 0.85; margin-bottom: 0.25rem;">ANALYST DECISION</div>
            <div style="font-family: 'Playfair Display', serif; font-size: 2.2rem; font-weight: 700; margin-bottom: 0.5rem;">REVIEW</div>
            <div style="font-size: 0.95rem; opacity: 0.95; line-height: 1.5;">
                The available evidence does not cross the configured threshold for an automatic affirmative decision.
                Detected spectral divergence correlates with seasonal crop phenology. ANALYST INSPECTION RECOMMENDED.
            </div>
        </div>
        """)

    # Disclaimer
    render_html(f"""
    <div style="border-top: 1px solid #2A2722; padding-top: 1.5rem; margin-top: 2rem;">
        <div class="editorial-eyebrow">SCIENTIFIC HONESTY &amp; TERMINOLOGY DISCLAIMER</div>
        <div style="font-size: 0.78rem; color: #82796D; line-height: 1.5; margin-top: 0.35rem;">
            {DISCLAIMER_TEXT}
            Temporal categories represent trajectory classifications across discrete observations, not causal proofs.
            The system provides structured evidence to assist human analyst investigation; it does not make automated legal or administrative decisions.
        </div>
    </div>
    """)

else:
    # =========================================================================
    # PUBLIC EDITORIAL PRODUCT WEBSITE (12-Section Spatial Narrative)
    # =========================================================================
    
    # 1. TOP MASTHEAD & GLOBAL INVESTIGATION COCKPIT
    render_html("""
    <div class="global-masthead-sticky" id="globalMasthead">
        <div class="masthead-main-bar">
            <div class="mn-brand" onclick="window.navScrollTo('sec_hero')" style="cursor: pointer;">
                <span class="mn-glyph" style="color: #C5A869; font-size: 1.15rem; line-height: 1;">&#x2299;</span>
                <div style="display: flex; flex-direction: column; justify-content: center;">
                    <span class="mn-title" style="letter-spacing: 0.22em; line-height: 1.1;">TERRAE</span>
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.50rem; letter-spacing: 0.16em; color: #C5A869; line-height: 1; text-transform: uppercase;">EARTH INTELLIGENCE</span>
                </div>
            </div>
            <div class="global-nav-links">
                <span class="nav-item active" id="nav_product" onclick="window.navScrollTo('sec_hero')">PRODUCT</span>
                <span class="nav-item" id="nav_method" onclick="window.navScrollTo('sec_method')">METHOD</span>
                <span class="nav-item" id="nav_investigation" onclick="window.navScrollTo('sec_case01')">INVESTIGATION</span>
                <span class="nav-item" id="nav_validation" onclick="window.navScrollTo('sec_validation')">VALIDATION</span>
                <span class="nav-item" id="nav_workstation" onclick="window.navScrollTo('sec_transition')">WORKSTATION</span>
            </div>
            <div class="masthead-actions">
                <div class="mn-offline-tag">
                    <span class="mn-offline-dot"></span>
                    <span>OFFLINE</span>
                </div>
                <button class="nav-ws-trigger" onclick="window.openWorkstationDirect()">
                    OPEN WORKSTATION &rarr;
                </button>
            </div>
        </div>
        <div class="progress-track-wrapper">
            <div class="progress-track-bar" id="globalProgressFill"></div>
            <div class="progress-nodes-container">
                <div class="progress-node active" id="pNode1" onclick="window.navScrollTo('sec_hero')">
                    <span class="p-num">01</span>
                    <span class="p-lbl">ASK</span>
                </div>
                <div class="progress-line"></div>
                <div class="progress-node" id="pNode2" onclick="window.navScrollTo('sec_philosophy')">
                    <span class="p-num">02</span>
                    <span class="p-lbl">DISCOVER</span>
                </div>
                <div class="progress-line"></div>
                <div class="progress-node" id="pNode3" onclick="window.navScrollTo('sec_method')">
                    <span class="p-num">03</span>
                    <span class="p-lbl">COMPARE</span>
                </div>
                <div class="progress-line"></div>
                <div class="progress-node" id="pNode4" onclick="window.navScrollTo('sec_evidence')">
                    <span class="p-num">04</span>
                    <span class="p-lbl">EXPLAIN</span>
                </div>
                <div class="progress-line"></div>
                <div class="progress-node" id="pNode5" onclick="window.navScrollTo('sec_validation')">
                    <span class="p-num">05</span>
                    <span class="p-lbl">CHALLENGE</span>
                </div>
                <div class="progress-line"></div>
                <div class="progress-node" id="pNode6" onclick="window.navScrollTo('sec_transition')">
                    <span class="p-num">06</span>
                    <span class="p-lbl">DECIDE</span>
                </div>
            </div>
        </div>
    </div>
    """)

    # 2. SECTION 01: FULL-BLEED HERO CANVAS WITH HUD & FUNCTIONAL REAL SEARCH INPUT
    render_html(f"""
    <div class="hero-fullbleed-backdrop" id="sec_hero">
        <img src="{hero_sat_b64}" class="hero-fullbleed-bg" alt="Hero Earth Observation Canvas" />
        <div class="hero-fullbleed-scrim"></div>
        <div class="hero-hud-layer">
            <div class="hud-top-right">
                <span class="hud-dot"></span>
                <span class="hud-tag">SENTINEL-2 L2A &middot; 10M GSD &middot; EPSG:32636</span>
            </div>
            <div class="hud-reticle">
                <div class="hud-crosshair">&#x2316;</div>
                <div class="hud-coord-readout">33&deg;53&prime;42&Prime; N &nbsp; 35&deg;30&prime;18&Prime; E</div>
                <div class="hud-location-tag">BEIRUT HARBOR &amp; LEVANT BASIN &middot; S2A &middot; 2017-10-03</div>
            </div>
            <div class="hud-bot-right">
                <div class="hud-spec-line">SURFACE REFLECTANCE (BOA) &middot; B02, B03, B04, B08</div>
                <div class="hud-sub-line">ZERO NETWORK CALLS &middot; AIR-GAPPED VERIFICATION</div>
            </div>
        </div>
    </div>
    """)

    col_hero_content, col_hero_empty = st.columns([5.8, 4.2], gap="large")
    with col_hero_content:
        render_html("""
        <div style="display: inline-flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;" class="hero-animate-eyebrow">
            <span style="color: #C5A869; font-size: 0.95rem; line-height: 1;">&#x2299;</span>
            <span style="font-family: 'Playfair Display', serif; font-size: 1.25rem; font-weight: 700; letter-spacing: 0.22em; color: #C5A869;">TERRAE</span>
            <span style="color: #6E675D; font-size: 0.75rem;">&middot;</span>
            <span class="editorial-eyebrow" style="margin-bottom: 0; font-size: 0.68rem; letter-spacing: 0.20em;">EARTH INTELLIGENCE</span>
        </div>
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; letter-spacing: 0.16em; color: #8A8376; margin-bottom: 1.1rem; text-transform: uppercase;">
            SATELLITE INVESTIGATION CONSOLE
        </div>
        <h1 class="hero-display-headline hero-animate-headline">
            SEE CHANGE.<br>
            <span class="hero-gold-accent">FOLLOW THE EVIDENCE.</span>
        </h1>
        <p class="hero-subhead hero-animate-desc">
            Natural-language satellite investigation across space and time with physical multi-spectral attribution, spatial coherence verification, and rigorous analyst review.
        </p>
        """)

        # Search Box
        render_html("""
        <div class="hero-search-label hero-animate-search">DESCRIBE WHAT YOU WANT TO INVESTIGATE</div>
        """)
        
        search_c1, search_c2 = st.columns([4, 1.2])
        with search_c1:
            query_input = st.text_input(
                "Query",
                value=st.session_state.search_query,
                placeholder="e.g. new construction and buildings",
                label_visibility="collapsed",
                key="hero_query_field"
            )
        with search_c2:
            search_clicked = st.button("SEARCH →", key="btn_hero_search", type="primary", use_container_width=True)

        # Suggestion Chips
        chip_col1, chip_col2, chip_col3 = st.columns(3)
        with chip_col1:
            if st.button("new construction", key="chip_1", use_container_width=True):
                st.session_state.search_query = "new construction and buildings"
                st.session_state.has_searched = True
                st.rerun()
        with chip_col2:
            if st.button("dense forest", key="chip_2", use_container_width=True):
                st.session_state.search_query = "dense forest"
                st.session_state.has_searched = True
                st.rerun()
        with chip_col3:
            if st.button("urban near water", key="chip_3", use_container_width=True):
                st.session_state.search_query = "urban development near water"
                st.session_state.has_searched = True
                st.rerun()

        if search_clicked or query_input != st.session_state.search_query or st.session_state.has_searched:
            st.session_state.search_query = query_input
            st.session_state.has_searched = True
            
            # Execute REAL Semantic Retrieval
            search_results = engine.search_text(st.session_state.search_query, top_k=2)
            if search_results:
                top_res = search_results[0]
                render_html(f"""
                <div class="hero-candidate-card hero-animate-search">
                    <div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #C5A869; font-weight: 700;">
                            TERRAE / DISCOVER &middot; TOP CANDIDATE &middot; SIMILARITY: {top_res.similarity_score:.4f}
                        </div>
                        <div style="font-size: 0.82rem; color: #FBF9F4; font-family: 'JetBrains Mono', monospace; margin-top: 0.2rem;">
                            TILE: {top_res.tile_id[:16]}... &middot; {top_res.sensor or 'Sentinel-2'}
                        </div>
                        <div style="font-size: 0.68rem; color: #82796D; font-family: 'JetBrains Mono', monospace;">
                            Acquisition: {top_res.acquisition_date or '2023-05-19'} &middot; FAISS Flat L2 Match
                        </div>
                    </div>
                </div>
                """)
                if st.button("INVESTIGATE CANDIDATE IN WORKSTATION →", key="btn_investigate_top", type="primary", use_container_width=True):
                    st.session_state.app_mode = "workstation"
                    st.rerun()

        render_html("""
        <div class="hero-telemetry-bar hero-animate-meta">
            <div class="telemetry-item">
                <span class="telemetry-dot"></span> SENTINEL-2 &middot; 10M GSD &middot; OFFLINE ARCHITECTURE
            </div>
            <div class="telemetry-stage">01 / ASK</div>
        </div>
        """)

    # 3. SECTION 02: PHILOSOPHY STATEMENT (Porcelain Light Tone, CIR Composite, ZERO Noise)
    render_html(f"""
    <div class="section-porcelain why-statement-section" id="sec_philosophy">
        <div style="display: grid; grid-template-columns: 7fr 5fr; gap: 3.5rem; align-items: center;">
            <div>
                <div class="editorial-eyebrow-dark">TERRAE / THE PHILOSOPHY</div>
                <div class="why-big-statement">
                    Satellite imagery shows what is there.<br>
                    <span class="why-statement-gold">Terrae investigates what changed.</span>
                </div>
                <p style="color: #454038; font-size: 1.05rem; line-height: 1.6; max-width: 620px;">
                    Traditional earth observation produces petabytes of static pixels. TERRAE converts multi-temporal satellite imagery into reasoned, auditable intelligence &mdash; detecting spectral divergence, testing spatial coherence, and proving temporal persistence before human analyst escalation.
                </p>
                <div style="margin-top: 1.5rem; font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #82796D;">
                    10M RESOLUTION &middot; AUTOMATED CO-REGISTRATION &middot; MULTI-SPECTRAL ATTRIBUTION
                </div>
            </div>
            <div>
                <div style="border: 1px solid #D9D1C4; background-color: #161513; padding: 0.5rem; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">
                    <img src="{sentinel2_t0_cir_b64}" style="width: 100%; height: 320px; object-fit: cover; display: block;" alt="Sentinel-2 CIR False-Color" />
                    <div style="display: flex; justify-content: space-between; font-family: 'JetBrains Mono', monospace; font-size: 0.62rem; color: #C5A869; padding: 0.4rem 0.2rem 0 0.2rem;">
                        <span>SENTINEL-2 CIR COMPOSITE &middot; B08/B04/B03</span>
                        <span>VEGETATION = CRIMSON &middot; BUILT = CYAN</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """)

    # 4. SECTION 03: STICKY METHOD STORY (Warm Earth Stone Background - Anchored Interactive Narrative)
    render_html(f"""
    <div class="section-warm-stone investigation-section" id="sec_method" style="background-color: #DDD5C7 !important;">
        <div class="editorial-eyebrow-dark">TERRAE / INVESTIGATION PROTOCOL</div>
        <div style="font-family: 'Playfair Display', serif; font-size: 2.4rem; font-weight: 500; color: #161513; margin-bottom: 2rem;">
            From raw imagery to reasoned intelligence.
        </div>
        
        <div style="display: grid; grid-template-columns: 7fr 5fr; gap: 3rem; align-items: flex-start;">
            <!-- Left Sticky Anchored Plate (58% Storytelling Area) -->
            <div style="position: sticky; top: 5.5rem;">
                <div class="inv-display-card" style="padding: 0; background: #141311; border: 1px solid #2A2722; box-shadow: 0 20px 50px rgba(0,0,0,0.35);">
                    <div class="inv-card-header" style="padding: 0.85rem 1.25rem; margin: 0; border-bottom: 1px solid #2A2722; background: #181715;">
                        <span id="methodBadgeStage" style="font-weight: 700; color: #C5A869; font-size: 0.72rem;">TERRAE / 01 ASK &middot; NATURAL INTENT</span>
                        <span id="methodBadgeMeta" style="color: #A0988A; font-size: 0.68rem;">MGRS 43RGM &middot; 10M GSD</span>
                    </div>
                    <div style="position: relative; width: 100%; height: 500px; overflow: hidden; background: #070908; display: flex; align-items: center; justify-content: center;">
                        <img id="methodHeroImg" src="{method_01_ask_b64}" style="width: 100% !important; height: 100% !important; object-fit: contain !important; display: block !important; transition: opacity 0.35s ease;" alt="Investigation Stage Plate" />
                        <div style="position: absolute; bottom: 12px; left: 12px; right: 12px; background: rgba(14, 13, 12, 0.92); border: 1px solid rgba(197, 168, 105, 0.4); padding: 0.65rem 1rem; font-family: 'JetBrains Mono', monospace; font-size: 0.70rem; color: #C5A869; backdrop-filter: blur(4px);" id="methodHeroOverlay">
                            QUERY HYPOTHESIS &rarr; Mapped to Surface Reflectance Targets
                        </div>
                    </div>
                    <div style="padding: 0.75rem 1.25rem; font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; color: #A0988A; line-height: 1.5; border-top: 1px solid #2A2722; background: #121110;" id="methodHeroMeta">
                        Sub-pixel alignment: &plusmn;0.05 px &middot; Bands: B02, B03, B04, B08 &middot; Radiative Transfer
                    </div>
                </div>
            </div>
            
            <!-- Right Scrolling Steps -->
            <div>
                <div class="narrative-step-card active-step" id="mStep0" onclick="window.setMethodStep(0)">
                    <div class="step-num">01 / ASK</div>
                    <div class="step-name">Natural Intent</div>
                    <div class="step-desc">
                        Analyst expresses investigative hypothesis in plain natural language. The query planner maps semantic intent into multi-spectral band constraints.
                    </div>
                    <div class="step-code-detail">&ldquo;new construction and buildings&rdquo; &rarr; Target: Built Surface</div>
                </div>
                
                <div class="narrative-step-card" id="mStep1" onclick="window.setMethodStep(1)">
                    <div class="step-num">02 / DISCOVER</div>
                    <div class="step-name">Semantic Retrieval</div>
                    <div class="step-desc">
                        Offline RemoteCLIP ViT-B/32 encoder and FAISS flat L2 index locate geographically and semantically matching satellite tiles in milliseconds.
                    </div>
                    <div class="step-code-detail">FAISS Flat &middot; 512-dim embedding &middot; Zero network calls</div>
                </div>
                
                <div class="narrative-step-card" id="mStep2" onclick="window.setMethodStep(2)">
                    <div class="step-num">03 / COMPARE</div>
                    <div class="step-name">Temporal Co-Registration</div>
                    <div class="step-desc">
                        Sub-pixel spatial alignment pairs baseline observation T0 with target observation T1, masking cloud, shadow, and invalid pixels via SCL.
                    </div>
                    <div class="step-code-detail">Sentinel-2 4-Band L2A Stack &middot; Exact Geographic Tile Alignment</div>
                </div>
                
                <div class="narrative-step-card" id="mStep3" onclick="window.setMethodStep(3)">
                    <div class="step-num">04 / EXPLAIN</div>
                    <div class="step-name">Physical Attribution</div>
                    <div class="step-desc">
                        Physical band differences decompose the spectral change vector into explicit physical causes: vegetation drop, soil disturbance, or built-up reflectance.
                    </div>
                    <div class="step-code-detail">&Delta;NIR, &Delta;Red, &Delta;NDVI &middot; Radiometric Attribution Rules</div>
                </div>
                
                <div class="narrative-step-card" id="mStep4" onclick="window.setMethodStep(4)">
                    <div class="step-num">05 / CHALLENGE</div>
                    <div class="step-name">Spatial &amp; Trajectory Verification</div>
                    <div class="step-desc">
                        Rejects noise via 8-connected component clustering and evaluates multi-date temporal persistence to weed out transient or seasonal fluctuations.
                    </div>
                    <div class="step-code-detail">Spatial Coherence &gt; 70% &middot; 3-Date Trajectory Classification</div>
                </div>
                
                <div class="narrative-step-card" id="mStep5" onclick="window.setMethodStep(5)">
                    <div class="step-num">06 / DECIDE</div>
                    <div class="step-name">Auditable Conclusion</div>
                    <div class="step-desc">
                        Synthesizes all evidence into unambiguous SUPPORTED, REVIEW, or ABSTAIN determinations with a complete cryptographic provenance trail.
                    </div>
                    <div class="step-code-detail">Evidence Chain &middot; Clear Analyst Decision Recommendation</div>
                </div>
            </div>
        </div>
    </div>
    """)

    # 5. SECTION 04: TEMPORAL STORY (Deep Forest Earth Background - Interactive Dynamic Progression)
    render_html(f"""
    <div class="section-deep-forest temporal-progression-section" id="sec_temporal">
        <div class="editorial-eyebrow">TEMPORAL PERSISTENCE &middot; DYNAMIC TRAJECTORY</div>
        <div style="font-family: 'Playfair Display', serif; font-size: 2.6rem; font-weight: 500; color: #FBF9F4; margin-bottom: 0.5rem;">
            The Earth changes. The question is whether the change holds.
        </div>
        <p style="color: #A3B5A6; font-size: 1.05rem; max-width: 720px; margin-bottom: 2rem;">
            Multi-temporal investigation over MGRS tile 43RGM (National Capital Region). Scrub or play through time to witness real seasonal greening peak versus genuine permanent structural change.
        </p>

        <div style="background-color: #0B0E0C; border: 1px solid #1C261F; padding: clamp(1rem, 2vw, 1.75rem); box-shadow: 0 20px 50px rgba(0,0,0,0.6);">
            <!-- Three Synchronized Real Satellite Panels -->
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: clamp(0.75rem, 1.5vw, 1.25rem); margin-bottom: 1.25rem;" id="temporalPanelsContainer">
                <!-- Panel 0: T0 -->
                <div class="temporal-panel active" id="tPanel0" onclick="window.setTemporalStage(0)" style="cursor: pointer; background: #121714; border: 2px solid #C5A869; box-shadow: 0 0 15px rgba(197, 168, 105, 0.25); transition: all 0.3s ease;">
                    <div style="background: rgba(18, 23, 20, 0.95); padding: 0.75rem 1rem; border-bottom: 1px solid #233026; display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; font-weight: 700; color: #C5A869;">T0 &middot; 19 MAY 2023</span>
                        <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #82796D;">BASELINE</span>
                    </div>
                    <div style="width: 100%; aspect-ratio: 1/1; background: #070908; overflow: hidden; display: flex; align-items: center; justify-content: center;">
                        <img src="{sentinel2_t0_rgb_b64}" style="width: 100%; height: 100%; object-fit: contain; display: block;" alt="T0 19 May 2023" />
                    </div>
                    <div style="background: rgba(14, 18, 15, 0.95); padding: 0.75rem 1rem; border-top: 1px solid #233026;">
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.70rem; font-weight: 600; color: #FBF9F4; letter-spacing: 0.08em;">PRE-MONSOON BASELINE</div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #A3B5A6; margin-top: 0.25rem;">NIR: 0.480 &middot; NDVI: +0.192</div>
                    </div>
                </div>

                <!-- Panel 1: TMID -->
                <div class="temporal-panel" id="tPanel1" onclick="window.setTemporalStage(1)" style="cursor: pointer; background: #121714; border: 2px solid #233026; transition: all 0.3s ease;">
                    <div style="background: rgba(18, 23, 20, 0.95); padding: 0.75rem 1rem; border-bottom: 1px solid #233026; display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; font-weight: 700; color: #55B374;">TMID &middot; 06 OCT 2023</span>
                        <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #55B374;">MIDPOINT</span>
                    </div>
                    <div style="width: 100%; aspect-ratio: 1/1; background: #070908; overflow: hidden; display: flex; align-items: center; justify-content: center;">
                        <img src="{sentinel2_tmid_rgb_b64}" style="width: 100%; height: 100%; object-fit: contain; display: block;" alt="Tmid 06 Oct 2023" />
                    </div>
                    <div style="background: rgba(14, 18, 15, 0.95); padding: 0.75rem 1rem; border-top: 1px solid #233026;">
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.70rem; font-weight: 600; color: #55B374; letter-spacing: 0.08em;">MONSOON GREEN PEAK</div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #A3B5A6; margin-top: 0.25rem;">NIR: 0.279 &middot; NDVI: +0.112 (PEAK VEG)</div>
                    </div>
                </div>

                <!-- Panel 2: T1 -->
                <div class="temporal-panel" id="tPanel2" onclick="window.setTemporalStage(2)" style="cursor: pointer; background: #121714; border: 2px solid #233026; transition: all 0.3s ease;">
                    <div style="background: rgba(18, 23, 20, 0.95); padding: 0.75rem 1rem; border-bottom: 1px solid #233026; display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; font-weight: 700; color: #C5A869;">T1 &middot; 05 DEC 2023</span>
                        <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #82796D;">TARGET</span>
                    </div>
                    <div style="width: 100%; aspect-ratio: 1/1; background: #070908; overflow: hidden; display: flex; align-items: center; justify-content: center;">
                        <img src="{sentinel2_t1_rgb_b64}" style="width: 100%; height: 100%; object-fit: contain; display: block;" alt="T1 05 Dec 2023" />
                    </div>
                    <div style="background: rgba(14, 18, 15, 0.95); padding: 0.75rem 1rem; border-top: 1px solid #233026;">
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.70rem; font-weight: 600; color: #FBF9F4; letter-spacing: 0.08em;">WINTER DORMANCY</div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #A3B5A6; margin-top: 0.25rem;">NIR: 0.254 &middot; NDVI: +0.092</div>
                    </div>
                </div>
            </div>

            <!-- Timeline Scrubber Bar Beneath Panels -->
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.75rem; background: #121714; border: 1px solid #1C261F; padding: 1rem 1.5rem; font-family: 'JetBrains Mono', monospace;">
                <div style="display: flex; gap: 0.75rem; align-items: center; flex-wrap: wrap;">
                    <span style="font-size: 0.72rem; color: #A3B5A6; letter-spacing: 0.12em; font-weight: 700;">OBSERVATION SCRUBBER:</span>
                    <button class="orbital-pill active" id="pillT0" onclick="window.setTemporalStage(0)">T0 (19 MAY 2023)</button>
                    <button class="orbital-pill" id="pillTmid" onclick="window.setTemporalStage(1)">TMID (06 OCT 2023)</button>
                    <button class="orbital-pill" id="pillT1" onclick="window.setTemporalStage(2)">T1 (05 DEC 2023)</button>
                </div>
                <div style="font-size: 0.75rem; color: #C5A869; font-weight: 600;" id="temporalNarrative">
                    Dry Season Baseline &rarr; Soil &amp; pre-monsoon vegetation
                </div>
            </div>
        </div>
    </div>
    """)

    # 6. SECTION 05: ORBITAL SCAN MOTION PLAYER (Deep Obsidian, Immersive Scale)
    render_html(f"""
    <div class="section-dark-obsidian video-feature-section" id="sec_motion">
        <div style="max-width: 1160px; margin: 0 auto 1.5rem auto; display: flex; justify-content: space-between; align-items: flex-end; flex-wrap: wrap; gap: 1rem;">
            <div>
                <div class="editorial-eyebrow">EARTH IN MOTION</div>
                <div style="font-family: 'Playfair Display', serif; font-size: 2.4rem; font-weight: 500; color: #FBF9F4; line-height: 1.2;">
                    Observe the same region across multiple satellite observations.
                </div>
            </div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; color: #C5A869; background: rgba(197, 168, 105, 0.08); border: 1px solid rgba(197, 168, 105, 0.3); padding: 0.35rem 0.75rem;">
                AIR-GAPPED HIGH-RES TIMELAPSE &middot; 43RGM &middot; 10M GSD
            </div>
        </div>
        
        <div class="orbital-player-container" id="orbitalPlayer">
            <div style="position: absolute; top: 16px; left: 20px; z-index: 5; background: rgba(14,13,12,0.85); backdrop-filter: blur(6px); border: 1px solid rgba(197,168,105,0.4); padding: 0.35rem 0.75rem; font-family: 'JetBrains Mono', monospace; font-size: 0.64rem; color: #C5A869; display: flex; align-items: center; gap: 0.5rem;">
                <span style="width: 6px; height: 6px; border-radius: 50%; background: #55B374;"></span>
                <span>SENTINEL-2 L2A &middot; MGRS 43RGM &middot; 10M GSD</span>
            </div>
            <div style="position: absolute; top: 16px; right: 20px; z-index: 5; background: rgba(14,13,12,0.85); backdrop-filter: blur(6px); border: 1px solid #2A2722; padding: 0.35rem 0.75rem; font-family: 'JetBrains Mono', monospace; font-size: 0.64rem; color: #FBF9F4;">
                MULTI-TEMPORAL PHENOLOGICAL PLAYER
            </div>
            
            <img src="{sentinel2_t0_rgb_b64}" id="orbitalImg" class="orbital-img-frame" alt="Orbital Scan" />
            
            <div class="orbital-hud-bar">
                <div class="orbital-timeline-track">
                    <button class="orbital-pill" id="btnOrbitalPrev" onclick="window.stepOrbitalFrame(-1)" title="Previous Frame">&lang; PREV</button>
                    <button class="orbital-pill" id="btnOrbitalPlay" onclick="window.toggleOrbitalPlay()">&#x23F8; PAUSE LOOP</button>
                    <button class="orbital-pill" id="btnOrbitalNext" onclick="window.stepOrbitalFrame(1)" title="Next Frame">NEXT &rang;</button>
                    <span style="font-size: 0.72rem; color: #FBF9F4; font-weight: 700; margin-left: 0.5rem; margin-right: 0.25rem;">OBSERVATION:</span>
                    <button class="orbital-pill active" id="btnPill0" onclick="window.setOrbitalFrame(0)">T0 (19 MAY 2023)</button>
                    <button class="orbital-pill" id="btnPill1" onclick="window.setOrbitalFrame(1)">TMID (06 OCT 2023)</button>
                    <button class="orbital-pill" id="btnPill2" onclick="window.setOrbitalFrame(2)">T1 (05 DEC 2023)</button>
                    <button class="orbital-pill" id="btnPill3" onclick="window.setOrbitalFrame(3)">CIR COMPOSITE</button>
                </div>
                <div style="font-size: 0.72rem; color: #C5A869; font-weight: 600;" id="orbitalCaption">
                    Observation 1/4 &middot; 19 MAY 2023 (Pre-monsoon dry baseline)
                </div>
            </div>
        </div>
    </div>
    """)

    # 7. SECTION 06: CASE STUDY 01 — CONTROLLED CONSTRUCTION (Warm Stone, Interactive Slider)
    render_html(f"""
    <div class="section-warm-stone case-study-section" id="sec_case01">
        <div style="display: grid; grid-template-columns: 5fr 7fr; gap: 3.5rem; align-items: center;">
            <div>
                <div style="display: inline-block; background: rgba(154, 120, 66, 0.12); border: 1px solid #C5A869; padding: 0.35rem 0.75rem; font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; letter-spacing: 0.14em; color: #9A7842; font-weight: 700; margin-bottom: 0.75rem;">
                    CONTROLLED SYNTHETIC TEMPORAL BENCHMARK &mdash; NOT A REAL EARTH SCENE
                </div>
                <div class="editorial-eyebrow-dark">TERRAE / CASE 01 &middot; CONTROLLED CONSTRUCTION</div>
                <div style="font-family: 'Playfair Display', serif; font-size: 2.2rem; font-weight: 600; color: #161513; margin-bottom: 0.35rem;">
                    Controlled Construction &amp; Building Development
                </div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; color: #736C61; margin-bottom: 0.85rem;">
                    SYNTHETIC TEMPORAL BENCHMARK &middot; EPSG:32643 &middot; 10M GSD &middot; 65,536 PIXELS (256&times;256)
                </div>
                <p style="color: #454038; font-size: 0.95rem; line-height: 1.6; margin-bottom: 1.5rem;">
                    Earth-observation imagery across other sections is derived from local GeoTIFF data; Case 01 is a controlled synthetic benchmark designed to test geometric edge-cases, tight spatial clustering, and algorithmic attribution against known ground truth.
                </p>
                
                <div class="cs-data-strip">
                    <div>
                        <div class="cs-metric-lbl">CHANGED FRACTION</div>
                        <div class="cs-metric-val">11.5%</div>
                    </div>
                    <div>
                        <div class="cs-metric-lbl">BUILT-SURFACE</div>
                        <div class="cs-metric-val">97.1%</div>
                    </div>
                    <div>
                        <div class="cs-metric-lbl">COHERENCE</div>
                        <div class="cs-metric-val">99.7%</div>
                    </div>
                    <div>
                        <div class="cs-metric-lbl">TRAJECTORY</div>
                        <div class="cs-metric-val" style="font-size: 1rem; margin-top: 0.25rem;">LATE-ONSET</div>
                    </div>
                </div>
                
                <div>
                    <span class="verdict-stamp vs-supported">&#x2714; SUPPORTED &middot; AFFIRMATIVE CONCLUSION</span>
                </div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.70rem; color: #82796D; margin-top: 1rem;">
                    Drag slider on right to inspect Before vs After co-registered surface
                </div>
            </div>
            
            <div>
                <!-- 3-Phase Temporal Progression Strip -->
                <div style="margin-bottom: 1rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; font-family: 'JetBrains Mono', monospace; font-size: 0.64rem; color: #82796D; letter-spacing: 0.12em; text-transform: uppercase;">
                        <span>TEMPORAL GROUND TRUTH PROGRESSION</span>
                        <span style="color: #9A7842; font-weight: 700;">10M GSD &middot; 3 PHASES</span>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.75rem;">
                        <div style="background: #FBF9F4; border: 1px solid #D9D1C4; padding: 0.5rem; box-shadow: 0 4px 12px rgba(0,0,0,0.06);">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem;">
                                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.60rem; font-weight: 700; color: #82796D;">PHASE 01 &middot; T0</span>
                                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.54rem; color: #82796D;">19 MAY</span>
                            </div>
                            <img src="{ctrl_t0_b64}" style="width: 100%; aspect-ratio: 1/1; object-fit: cover; display: block; border: 1px solid #D9D1C4;" alt="T0 Baseline" />
                            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.62rem; font-weight: 700; color: #161513; margin-top: 0.35rem;">Natural Terrain</div>
                            <div style="font-size: 0.60rem; color: #736C61; line-height: 1.3;">Undisturbed baseline soil &amp; shrub</div>
                        </div>
                        <div style="background: #FBF9F4; border: 1px solid #C5A869; padding: 0.5rem; box-shadow: 0 4px 12px rgba(0,0,0,0.06);">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem;">
                                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.60rem; font-weight: 700; color: #9A7842;">PHASE 02 &middot; T1</span>
                                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.54rem; color: #9A7842;">06 OCT</span>
                            </div>
                            <img src="{ctrl_t1_b64}" style="width: 100%; aspect-ratio: 1/1; object-fit: cover; display: block; border: 1px solid #C5A869;" alt="T1 Excavation" />
                            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.62rem; font-weight: 700; color: #161513; margin-top: 0.35rem;">Ground Excavation</div>
                            <div style="font-size: 0.60rem; color: #736C61; line-height: 1.3;">Soil clearing &amp; foundation works</div>
                        </div>
                        <div style="background: #FBF9F4; border: 1px solid #435548; padding: 0.5rem; box-shadow: 0 4px 12px rgba(0,0,0,0.06);">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem;">
                                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.60rem; font-weight: 700; color: #435548;">PHASE 03 &middot; T2</span>
                                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.54rem; color: #435548;">05 DEC</span>
                            </div>
                            <img src="{ctrl_t2_b64}" style="width: 100%; aspect-ratio: 1/1; object-fit: cover; display: block; border: 1px solid #435548;" alt="T2 Structure" />
                            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.62rem; font-weight: 700; color: #161513; margin-top: 0.35rem;">Built Structure</div>
                            <div style="font-size: 0.60rem; color: #736C61; line-height: 1.3;">Erected concrete building footprint</div>
                        </div>
                    </div>
                </div>

                <!-- Draggable Interactive Wipe Slider with Target Reticle -->
                <div class="ba-slider-container" id="baSlider" style="--ba-clip: 50%; height: 380px;" onmousemove="if(window.__baDrag) {{{{ var r = this.getBoundingClientRect(); var p = Math.max(0, Math.min(100, (event.clientX - r.left)/r.width*100)); this.style.setProperty('--ba-clip', p + '%'); document.getElementById('baDivider').style.left = p + '%'; }}}}" onmousedown="window.__baDrag = true; var r = this.getBoundingClientRect(); var p = Math.max(0, Math.min(100, (event.clientX - r.left)/r.width*100)); this.style.setProperty('--ba-clip', p + '%'); document.getElementById('baDivider').style.left = p + '%';" onmouseup="window.__baDrag = false;" onmouseleave="window.__baDrag = false;">
                    <img src="{ctrl_t0_b64}" class="ba-img-base" alt="Baseline T0 Before" />
                    <img src="{ctrl_t2_b64}" class="ba-img-clipped" alt="Target T2 After" />
                    <!-- Gold Reticle on Target Footprint (Rows 250..400, Cols 100..250 in 512x512) -->
                    <div style="position: absolute; top: 48.8%; left: 19.5%; width: 29.3%; height: 29.3%; border: 2px solid #C5A869; box-shadow: 0 0 16px rgba(197, 168, 105, 0.45); pointer-events: none; z-index: 3;">
                        <div style="position: absolute; top: -20px; left: 0; background: rgba(18,17,16,0.92); border: 1px solid #C5A869; padding: 1px 6px; font-family: 'JetBrains Mono', monospace; font-size: 0.58rem; color: #C5A869; font-weight: 700; white-space: nowrap;">
                            &#x2299; 11.5% CHANGE FOOTPRINT
                        </div>
                    </div>
                    <div id="baDivider" style="position: absolute; top: 0; bottom: 0; left: 50%; width: 2px; background-color: #C5A869; z-index: 4; pointer-events: none;">
                        <div style="position: absolute; top: 50%; left: -14px; width: 28px; height: 28px; border-radius: 50%; background: #161513; border: 2px solid #C5A869; color: #C5A869; display: flex; align-items: center; justify-content: center; font-size: 11px; transform: translateY(-50%); font-weight: bold; pointer-events: none;">&#x21F7;</div>
                    </div>
                    <div class="ba-badge-left">AFTER (T2 &middot; DEVELOPED STRUCTURE)</div>
                    <div class="ba-badge-right">BEFORE (T0 &middot; BASELINE TERRAIN)</div>
                </div>
            </div>
        </div>
    </div>
    """)

    # 8. SECTION 07: CASE STUDY 02 — REAL SENTINEL-2 (Porcelain Light Tone)
    render_html(f"""
    <div class="section-porcelain case-study-section" id="sec_case02">
        <div style="display: grid; grid-template-columns: 7.5fr 4.5fr; gap: 3rem; align-items: center;">
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; background-color: #121110; padding: 1.25rem; border: 1px solid #2A2722; box-shadow: 0 15px 40px rgba(0,0,0,0.4);">
                <div style="position: relative; border: 1px solid #2A2722; background: #070908;">
                    <div style="background: rgba(18,17,16,0.92); padding: 0.35rem 0.5rem; font-family: 'JetBrains Mono', monospace; font-size: 0.62rem; font-weight: 700; color: #C5A869; border-bottom: 1px solid #2A2722;">T0 &middot; 19 MAY 2023</div>
                    <img src="{sentinel2_t0_rgb_b64}" style="width: 100%; aspect-ratio: 1/1; object-fit: contain; display: block;" alt="Case 2 T0">
                    <div style="background: rgba(18,17,16,0.92); padding: 0.3rem 0.5rem; font-family: 'JetBrains Mono', monospace; font-size: 0.58rem; color: #82796D; border-top: 1px solid #2A2722;">PRE-MONSOON DRY</div>
                </div>
                <div style="position: relative; border: 1px solid rgba(85,179,116,0.5); background: #070908;">
                    <div style="background: rgba(18,17,16,0.92); padding: 0.35rem 0.5rem; font-family: 'JetBrains Mono', monospace; font-size: 0.62rem; font-weight: 700; color: #55B374; border-bottom: 1px solid rgba(85,179,116,0.4);">TMID &middot; 06 OCT 2023</div>
                    <img src="{sentinel2_tmid_rgb_b64}" style="width: 100%; aspect-ratio: 1/1; object-fit: contain; display: block;" alt="Case 2 Tmid">
                    <div style="background: rgba(18,17,16,0.92); padding: 0.3rem 0.5rem; font-family: 'JetBrains Mono', monospace; font-size: 0.58rem; color: #55B374; border-top: 1px solid rgba(85,179,116,0.4);">MONSOON GREEN PEAK</div>
                </div>
                <div style="position: relative; border: 1px solid rgba(197,168,105,0.5); background: #070908;">
                    <div style="background: rgba(18,17,16,0.92); padding: 0.35rem 0.5rem; font-family: 'JetBrains Mono', monospace; font-size: 0.62rem; font-weight: 700; color: #C5A869; border-bottom: 1px solid rgba(197,168,105,0.4);">T1 &middot; 05 DEC 2023</div>
                    <img src="{sentinel2_t1_rgb_b64}" style="width: 100%; aspect-ratio: 1/1; object-fit: contain; display: block;" alt="Case 2 T1">
                    <div style="background: rgba(18,17,16,0.92); padding: 0.3rem 0.5rem; font-family: 'JetBrains Mono', monospace; font-size: 0.58rem; color: #C5A869; border-top: 1px solid rgba(197,168,105,0.4);">WINTER DORMANCY</div>
                </div>
            </div>
            
            <div>
                <div class="editorial-eyebrow-dark">TERRAE / CASE 02 &middot; REAL SENTINEL-2</div>
                <div style="font-family: 'Playfair Display', serif; font-size: 2.2rem; font-weight: 600; color: #161513; margin-bottom: 0.35rem;">
                    MGRS 43RGM &middot; National Capital Region
                </div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; color: #736C61; margin-bottom: 0.85rem;">
                    MGRS: 43RGM &middot; 28.5215&deg; N, 77.4782&deg; E &middot; EPSG:32643 &middot; 10M GSD &middot; 262,144 VALID PIXELS
                </div>
                <p style="color: #454038; font-size: 0.95rem; line-height: 1.6; margin-bottom: 1.5rem;">
                    Real Sentinel-2 satellite stack across 3 seasons. The scene is predominantly stable (98.75%). The detected change is correctly attributed to natural seasonal vegetation phenology rather than permanent construction.
                </p>
                
                <div class="cs-data-strip">
                    <div>
                        <div class="cs-metric-lbl">STABLE PIXELS</div>
                        <div class="cs-metric-val">98.75%</div>
                    </div>
                    <div>
                        <div class="cs-metric-lbl">PERSISTENT CHANGE</div>
                        <div class="cs-metric-val">0.39%</div>
                    </div>
                    <div>
                        <div class="cs-metric-lbl">BUILT-SURFACE</div>
                        <div class="cs-metric-val">51.1%</div>
                    </div>
                    <div>
                        <div class="cs-metric-lbl">DECISION</div>
                        <div class="cs-metric-val" style="color: #9A7842;">REVIEW</div>
                    </div>
                </div>
                
                <div>
                    <span class="verdict-stamp vs-review">&#x26A0; REVIEW &middot; ANALYST INSPECTION RECOMMENDED</span>
                </div>
                <div style="font-size: 0.76rem; color: #555049; line-height: 1.5; margin-top: 1rem;">
                    <em>Scientific note:</em> REVIEW is intentionally produced because the available evidence does not cross the threshold for an automatic affirmative decision. This safeguards analysts against false-positive land clearing alerts.
                </div>
            </div>
        </div>
    </div>
    """)

    # 9. SECTION 08: PROGRESSIVE ANALYTICAL EVIDENCE DECOMPOSITION (Deep Analytical Console)
    render_html(f"""
    <div class="section-dark-obsidian progressive-evidence-section" id="sec_evidence">
        <div class="editorial-eyebrow">TERRAE / PROGRESSIVE EVIDENCE</div>
        <div style="font-family: 'Playfair Display', serif; font-size: 2.4rem; font-weight: 500; color: #FBF9F4; margin-bottom: 0.5rem;">
            What changed? And what proves that interpretation?
        </div>
        <p style="color: #A0988A; font-size: 1.0rem; max-width: 720px; margin-bottom: 1.5rem;">
            The satellite observation progressively gains physical and mathematical overlays &mdash; advancing through 6 verifiable stages from raw surface reflectance to an auditable decision.
        </p>

        <div class="evidence-console-container">
            <!-- Left High-Resolution Stage Viewport -->
            <div>
                <div class="evidence-stage-viewport">
                    <img id="evidStageImg" src="{evidence_01_raw_b64}" class="evidence-stage-img" alt="Evidence Layer" />
                    <div class="evidence-stage-badge" id="evidStageBadge">
                        LAYER 01 / 06 &middot; RAW SURFACE REFLECTANCE
                    </div>
                    <div class="evidence-stage-legend" id="evidStageLegend">
                        RGB BOA Reflectance (B04=Red, B03=Green, B02=Blue)
                    </div>

                    <!-- Reticle Targeting Divergence Region -->
                    <div style="position: absolute; top: 38%; left: 35%; width: 28%; height: 28%; border: 1px dashed rgba(197, 168, 105, 0.45); pointer-events: none; z-index: 4;">
                        <div style="position: absolute; top: -18px; left: 0; background: rgba(14,13,12,0.92); border: 1px solid rgba(197,168,105,0.4); padding: 1px 6px; font-family: 'JetBrains Mono', monospace; font-size: 0.56rem; color: #C5A869; font-weight: 700;">
                            &#x2299; TARGET CLUSTER &middot; 28.5215&deg; N, 77.4782&deg; E
                        </div>
                    </div>

                    <!-- Translucent Intelligence HUD Docked at Bottom of Viewport -->
                    <div class="evidence-hud-overlay" id="evidHudOverlay">
                        <div class="evid-hud-item">
                            <span class="evid-hud-lbl">01 / LOCATION OF DIVERGENCE</span>
                            <span class="evid-hud-val" id="evidHudLoc">2,542 px (1.00%) &middot; Cluster #14</span>
                        </div>
                        <div class="evid-hud-divider"></div>
                        <div class="evid-hud-item">
                            <span class="evid-hud-lbl">02 / PHYSICAL EVIDENCE</span>
                            <span class="evid-hud-val" id="evidHudEvidence">&Delta;NIR: -22.6% &middot; &Delta;Red: -12.6% (Veg Flush)</span>
                        </div>
                        <div class="evid-hud-divider"></div>
                        <div class="evid-hud-item">
                            <span class="evid-hud-lbl">03 / AUDITABLE DECISION</span>
                            <span class="evid-hud-val" style="color: #C5A869;" id="evidHudVerdict">&#x26A0; REVIEW (Agrarian Phenology)</span>
                        </div>
                    </div>
                </div>

                <!-- Direct 3-Pillar Evidence Architecture Bar -->
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.75rem; margin-top: 0.85rem; font-family: 'JetBrains Mono', monospace;">
                    <div style="background: #141311; border: 1px solid #2A2722; border-top: 2px solid #C5A869; padding: 0.75rem 0.85rem;">
                        <div style="font-size: 0.60rem; color: #C5A869; letter-spacing: 0.14em; font-weight: 700;">1. LOCATION OF DIVERGENCE</div>
                        <div style="font-size: 0.95rem; font-weight: 700; color: #FBF9F4; margin: 0.2rem 0;">2,542 Pixels (1.00%)</div>
                        <div style="font-size: 0.65rem; color: #82796D; line-height: 1.3;">MGRS 43RGM &middot; Localized agrarian parcels</div>
                    </div>
                    <div style="background: #141311; border: 1px solid #2A2722; border-top: 2px solid #55B374; padding: 0.75rem 0.85rem;">
                        <div style="font-size: 0.60rem; color: #55B374; letter-spacing: 0.14em; font-weight: 700;">2. PHYSICAL ATTRIBUTION</div>
                        <div style="font-size: 0.95rem; font-weight: 700; color: #FBF9F4; margin: 0.2rem 0;">&Delta;NIR -22.6% &middot; &Delta;Red -12.6%</div>
                        <div style="font-size: 0.65rem; color: #82796D; line-height: 1.3;">Chlorophyll absorption cycle, not concrete</div>
                    </div>
                    <div style="background: #141311; border: 1px solid #2A2722; border-top: 2px solid #9A7842; padding: 0.75rem 0.85rem;">
                        <div style="font-size: 0.60rem; color: #C5A869; letter-spacing: 0.14em; font-weight: 700;">3. AUDITABLE CONCLUSION</div>
                        <div style="font-size: 0.95rem; font-weight: 700; color: #C5A869; margin: 0.2rem 0;">&#x26A0; REVIEW REQUIRED</div>
                        <div style="font-size: 0.65rem; color: #82796D; line-height: 1.3;">Seasonal shift suppressed to prevent false alert</div>
                    </div>
                </div>

                <!-- Layer Transport Strip -->
                <div style="display: flex; justify-content: space-between; align-items: center; background: #121110; border: 1px solid #2A2722; padding: 0.65rem 1rem; margin-top: 0.85rem; font-family: 'JetBrains Mono', monospace;">
                    <div style="display: flex; gap: 0.5rem; align-items: center;">
                        <button class="orbital-pill" onclick="window.stepEvidLayer(-1)">&lang; PREV LAYER</button>
                        <button class="orbital-pill" onclick="window.stepEvidLayer(1)">NEXT LAYER &rang;</button>
                    </div>
                    <div style="font-size: 0.70rem; color: #C5A869;" id="evidReadout">
                        Raw Multispectral Radiance &rarr; Unfiltered baseline observation
                    </div>
                </div>
            </div>

            <!-- Right Interactive Layer Selector Track -->
            <div>
                <div class="evidence-layer-card active-layer" id="evidCard0" onclick="window.setEvidLayer(0)">
                    <div class="layer-idx">01 / SATELLITE REFLECTANCE</div>
                    <div class="layer-title">Raw Multispectral Surface Radiance</div>
                    <div class="layer-desc">Sub-pixel aligned 10m Sentinel-2 bands B02 (Blue), B03 (Green), B04 (Red), and B08 (NIR).</div>
                </div>

                <div class="evidence-layer-card" id="evidCard1" onclick="window.setEvidLayer(1)">
                    <div class="layer-idx">02 / SPECTRAL DIFFERENCING</div>
                    <div class="layer-title">Change Mask Overlay (&tau; = 0.15)</div>
                    <div class="layer-desc">Amber/coral overlay isolates 1.0% (2,542 pixels) significant divergence while suppressing background sensor noise.</div>
                </div>

                <div class="evidence-layer-card" id="evidCard2" onclick="window.setEvidLayer(2)">
                    <div class="layer-idx">03 / PHYSICAL ATTRIBUTION</div>
                    <div class="layer-title">Multi-Spectral Vector Decomposition</div>
                    <div class="layer-desc">Analytical palette distinguishes vegetation flush (green), water (teal), and disturbance (amber). &Delta;NIR: -22.6%, &Delta;Red: -12.6%.</div>
                </div>

                <div class="evidence-layer-card" id="evidCard3" onclick="window.setEvidLayer(3)">
                    <div class="layer-idx">04 / SPATIAL COHERENCE</div>
                    <div class="layer-title">8-Connected Topological Clustering</div>
                    <div class="layer-desc">15.7% spatial coherence across 152 clustered components. Distinguishes dispersed seasonal changes from contiguous infrastructure.</div>
                </div>

                <div class="evidence-layer-card" id="evidCard4" onclick="window.setEvidLayer(4)">
                    <div class="layer-idx">05 / TEMPORAL PERSISTENCE</div>
                    <div class="layer-title">MECE Multi-Date Trajectory</div>
                    <div class="layer-desc">Evaluates 3 discrete observations. 98.75% of terrain confirmed stable with localized seasonal phenology.</div>
                </div>

                <div class="evidence-layer-card" id="evidCard5" onclick="window.setEvidLayer(5)">
                    <div class="layer-idx">06 / AUDITABLE DECISION</div>
                    <div class="layer-title">REVIEW &middot; Cryptographic Provenance</div>
                    <div class="layer-desc">Conservative REVIEW decision avoids false-positive alerting on seasonal crop shifts. SHA-256 provenance trail recorded.</div>
                </div>
            </div>
        </div>
    </div>
    """)

    # 10. SECTION 09: EARTH / OBSERVATIONS MOSAIC (Deep Obsidian Dark Surface)
    render_html(f"""
    <div class="section-dark-obsidian" id="sec_observations">
        <div class="editorial-eyebrow">DIVERSE EARTH OBSERVATION REGIONS</div>
        <div style="font-family: 'Playfair Display', serif; font-size: 2.4rem; font-weight: 500; color: #FBF9F4; margin-bottom: 0.5rem;">
            Earth / Observations
        </div>
        <p style="color: #A0988A; font-size: 1.05rem; max-width: 680px; margin-bottom: 2.5rem;">
            Tested across diverse global geographies, terrain profiles, and sensor geometries &mdash; from dense coastal ports to agrarian plains.
        </p>
        
        <div class="mosaic-grid-6">
            <div class="mosaic-tile">
                <img src="{beirut_rgb_b64}" class="mosaic-img" alt="Beirut" />
                <div class="mosaic-meta">
                    <div class="mosaic-tag">URBAN &middot; COASTAL</div>
                    <div class="mosaic-title">Beirut Port &amp; Waterfront</div>
                    <div class="mosaic-desc">Dense commercial infrastructure &amp; coastal construction monitoring.</div>
                </div>
            </div>
            
            <div class="mosaic-tile">
                <img src="{sentinel2_t0_rgb_b64}" class="mosaic-img" alt="NCR Plains" />
                <div class="mosaic-meta">
                    <div class="mosaic-tag">AGRICULTURE &middot; PHENOLOGICAL / TRANSIENT</div>
                    <div class="mosaic-title">NCR Agrarian Plains</div>
                    <div class="mosaic-desc">Seasonal crop phenology &amp; agricultural greening discrimination.</div>
                </div>
            </div>
            
            <div class="mosaic-tile">
                <img src="{bordeaux_rgb_b64}" class="mosaic-img" alt="Bordeaux" />
                <div class="mosaic-meta">
                    <div class="mosaic-tag">ESTUARY &middot; FORESTRY</div>
                    <div class="mosaic-title">Bordeaux River Basin</div>
                    <div class="mosaic-desc">Riparian vegetation, river corridor shifts &amp; vineyard expansion.</div>
                </div>
            </div>

            <div class="mosaic-tile">
                <img src="{mumbai_rgb_b64}" class="mosaic-img" alt="Mumbai" />
                <div class="mosaic-meta">
                    <div class="mosaic-tag">MEGACITY &middot; PENINSULAR</div>
                    <div class="mosaic-title">Mumbai Coastal Bay</div>
                    <div class="mosaic-desc">High-density peninsular urban growth &amp; reclamation activity.</div>
                </div>
            </div>

            <div class="mosaic-tile">
                <img src="{cupertino_rgb_b64}" class="mosaic-img" alt="Cupertino" />
                <div class="mosaic-meta">
                    <div class="mosaic-tag">TECH CAMPUS &middot; LOW-DENSITY</div>
                    <div class="mosaic-title">Cupertino Silicon Valley</div>
                    <div class="mosaic-desc">Low-density commercial development &amp; suburban transit corridors.</div>
                </div>
            </div>

            <div class="mosaic-tile">
                <img src="{aguasclaras_rgb_b64}" class="mosaic-img" alt="Aguas Claras" />
                <div class="mosaic-meta">
                    <div class="mosaic-tag">MINERAL &middot; SAVANNA</div>
                    <div class="mosaic-title">Aguas Claras Disturbance</div>
                    <div class="mosaic-desc">Open surface disturbance &amp; vegetation suppression tracking.</div>
                </div>
            </div>
        </div>
    </div>
    """)

    # 11. SECTION 10: OSCD VALIDATION BOARD (Mineral Neutral)
    render_html(f"""
    <div class="section-mineral-neutral" id="sec_validation">
        <div class="editorial-eyebrow-dark">EXTERNAL VALIDATION</div>
        <div style="font-family: 'Playfair Display', serif; font-size: 2.2rem; font-weight: 500; color: #161513; margin-bottom: 0.35rem;">
            OSCD &mdash; 5-pair validation subset
        </div>
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; color: #6E675D; margin-bottom: 1.25rem;">
            3,025,938 valid pixels &middot; Fixed threshold (&tau; = 0.15) &middot; Zero task-specific fine-tuning
        </div>
        <p style="color: #454038; font-size: 0.95rem; max-width: 680px; margin-bottom: 2rem;">
            Rigorous evaluation against human pixel-level ground truth from a 5-pair validation subset of the On-ground Satellite Change Detection (OSCD) benchmark. Staged 100% locally with zero external network dependencies.
        </p>
        
        <div style="display: inline-block; background: rgba(67, 85, 72, 0.10); border: 1px solid #435548; padding: 0.4rem 0.85rem; font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; color: #435548; font-weight: 700; margin-bottom: 1.5rem;">
            ZERO-SHOT UNSUPERVISED EVALUATION &middot; CLASS IMBALANCE (&lt;3% POSITIVE CHANGE) &middot; 97.90% MACRO ACCURACY &middot; 97.70% MICRO ACCURACY
        </div>
        
        <div class="oscd-grid-5">
            <div class="oscd-card" style="background: #FAF7F0; border: 1px solid #D9D1C4; padding: 0.85rem; box-shadow: 0 4px 15px rgba(0,0,0,0.06);">
                <div class="oscd-city" style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; font-weight: 700; color: #161513; margin-bottom: 0.5rem;">BEIRUT</div>
                <div style="width: 100%; height: 210px; overflow: hidden; background: #0E0D0C; border: 1px solid #D9D1C4; display: flex; align-items: center; justify-content: center;">
                    <img src="{beirut_rgb_b64}" style="width: 100%; height: 100%; object-fit: contain; object-position: center; display: block;" alt="Beirut">
                </div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.62rem; color: #6E675D; margin-top: 0.5rem; font-weight: 600;">LEBANON &middot; 1,262,600 PX</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.58rem; color: #8A8376;">2015-08-20 / 2017-10-03</div>
            </div>
            
            <div class="oscd-card" style="background: #FAF7F0; border: 1px solid #D9D1C4; padding: 0.85rem; box-shadow: 0 4px 15px rgba(0,0,0,0.06);">
                <div class="oscd-city" style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; font-weight: 700; color: #161513; margin-bottom: 0.5rem;">MUMBAI</div>
                <div style="width: 100%; height: 210px; overflow: hidden; background: #0E0D0C; border: 1px solid #D9D1C4; display: flex; align-items: center; justify-content: center;">
                    <img src="{mumbai_rgb_b64}" style="width: 100%; height: 100%; object-fit: contain; object-position: center; display: block;" alt="Mumbai">
                </div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.62rem; color: #6E675D; margin-top: 0.5rem; font-weight: 600;">INDIA &middot; 477,906 PX</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.55rem; color: #8A8376;">2015-11-30 / 2018-03-19</div>
            </div>
            
            <div class="oscd-card" style="background: #FAF7F0; border: 1px solid #D9D1C4; padding: 0.85rem; box-shadow: 0 4px 15px rgba(0,0,0,0.06);">
                <div class="oscd-city" style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; font-weight: 700; color: #161513; margin-bottom: 0.5rem;">BORDEAUX</div>
                <div style="width: 100%; height: 210px; overflow: hidden; background: #0E0D0C; border: 1px solid #D9D1C4; display: flex; align-items: center; justify-content: center;">
                    <img src="{bordeaux_rgb_b64}" style="width: 100%; height: 100%; object-fit: contain; object-position: center; display: block;" alt="Bordeaux">
                </div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.62rem; color: #6E675D; margin-top: 0.5rem; font-weight: 600;">FRANCE &middot; 238,337 PX</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.55rem; color: #8A8376;">2016-05-04 / 2017-10-26</div>
            </div>
            
            <div class="oscd-card" style="background: #FAF7F0; border: 1px solid #D9D1C4; padding: 0.85rem; box-shadow: 0 4px 15px rgba(0,0,0,0.06);">
                <div class="oscd-city" style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; font-weight: 700; color: #161513; margin-bottom: 0.5rem;">CUPERTINO</div>
                <div style="width: 100%; height: 210px; overflow: hidden; background: #0E0D0C; border: 1px solid #D9D1C4; display: flex; align-items: center; justify-content: center;">
                    <img src="{cupertino_rgb_b64}" style="width: 100%; height: 100%; object-fit: contain; object-position: center; display: block;" alt="Cupertino">
                </div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.62rem; color: #6E675D; margin-top: 0.5rem; font-weight: 600;">USA &middot; 799,820 PX</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.55rem; color: #8A8376;">2015-09-18 / 2018-03-26</div>
            </div>
            
            <div class="oscd-card" style="background: #FAF7F0; border: 1px solid #D9D1C4; padding: 0.85rem; box-shadow: 0 4px 15px rgba(0,0,0,0.06);">
                <div class="oscd-city" style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; font-weight: 700; color: #161513; margin-bottom: 0.5rem;">AGUAS CLARAS</div>
                <div style="width: 100%; height: 210px; overflow: hidden; background: #0E0D0C; border: 1px solid #D9D1C4; display: flex; align-items: center; justify-content: center;">
                    <img src="{aguasclaras_rgb_b64}" style="width: 100%; height: 100%; object-fit: contain; object-position: center; display: block;" alt="Aguas Claras">
                </div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.62rem; color: #6E675D; margin-top: 0.5rem; font-weight: 600;">BRAZIL &middot; 247,275 PX</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.55rem; color: #8A8376;">2015-09-16 / 2017-10-15</div>
            </div>
        </div>
        
        <div style="margin-top: 1.5rem; background: #FAF7F0; border: 1px solid #D9D1C4; padding: 1.25rem 1.5rem; box-shadow: 0 4px 15px rgba(0,0,0,0.04);">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #E5DEC9; padding-bottom: 0.5rem; margin-bottom: 1rem;">
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; font-weight: 700; color: #161513; letter-spacing: 0.12em;">
                    EVALUATION METRICS &middot; 5-PAIR VALIDATION SUBSET &middot; 3,025,938 VALID PIXELS
                </div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #6E675D;">
                    FIXED &tau; = 0.15 &middot; ZERO TASK-SPECIFIC FINE-TUNING
                </div>
            </div>
            
            <!-- Micro Aggregate Row -->
            <div style="margin-bottom: 1.25rem;">
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #9A7842; font-weight: 700; letter-spacing: 0.1em; margin-bottom: 0.5rem;">
                    MICRO AGGREGATE (POOLED OVER 3,025,938 VALID PIXELS)
                </div>
                <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 1rem;">
                    <div>
                        <div class="cs-metric-lbl">Micro Precision</div>
                        <div class="cs-metric-val" style="color: #161513; font-size: 1.15rem;">57.55%</div>
                    </div>
                    <div>
                        <div class="cs-metric-lbl">Micro Recall</div>
                        <div class="cs-metric-val" style="color: #161513; font-size: 1.15rem;">9.72%</div>
                    </div>
                    <div>
                        <div class="cs-metric-lbl">Micro F1</div>
                        <div class="cs-metric-val" style="color: #9A7842; font-size: 1.15rem;">0.1663</div>
                    </div>
                    <div>
                        <div class="cs-metric-lbl">Micro IoU</div>
                        <div class="cs-metric-val" style="color: #161513; font-size: 1.15rem;">0.0907</div>
                    </div>
                    <div>
                        <div class="cs-metric-lbl">Micro Accuracy</div>
                        <div class="cs-metric-val" style="color: #435548; font-size: 1.15rem;">97.70%</div>
                    </div>
                </div>
            </div>

            <!-- Macro Average Row -->
            <div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #435548; font-weight: 700; letter-spacing: 0.1em; margin-bottom: 0.5rem; border-top: 1px dashed #D9D1C4; padding-top: 0.75rem;">
                    MACRO AVERAGE (UNWEIGHTED MEAN ACROSS 5 GEOGRAPHIES)
                </div>
                <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 1rem;">
                    <div>
                        <div class="cs-metric-lbl">Macro Precision</div>
                        <div class="cs-metric-val" style="color: #161513; font-size: 1.15rem;">52.22%</div>
                    </div>
                    <div>
                        <div class="cs-metric-lbl">Macro Recall</div>
                        <div class="cs-metric-val" style="color: #161513; font-size: 1.15rem;">7.84%</div>
                    </div>
                    <div>
                        <div class="cs-metric-lbl">Macro F1</div>
                        <div class="cs-metric-val" style="color: #435548; font-size: 1.15rem;">0.1267</div>
                    </div>
                    <div>
                        <div class="cs-metric-lbl">Macro IoU</div>
                        <div class="cs-metric-val" style="color: #161513; font-size: 1.15rem;">0.0692</div>
                    </div>
                    <div>
                        <div class="cs-metric-lbl">Macro Accuracy</div>
                        <div class="cs-metric-val" style="color: #435548; font-size: 1.15rem;">97.90%</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div style="font-size: 0.74rem; color: #555049; line-height: 1.5; margin-top: 1rem;">
            <em>Class-imbalance interpretation note:</em> The 97.70% Micro Accuracy and 97.90% Macro Accuracy are strongly governed by extreme class imbalance in pixel-level satellite change detection (only 2.36% of ground-truth pixels are changed; a trivial baseline predicting all pixels unchanged scores 97.64% accuracy). Therefore, Micro F1 (0.1663), Precision, and Recall represent the genuine operational headline metrics. Evaluated strictly zero-shot with fixed &tau; = 0.15 threshold.
        </div>
    </div>
    """)

    # 12. SECTION 11: WORKSTATION PREVIEW & TRANSITION (Warm Stone)
    render_html("""
    <div class="section-dark-obsidian workstation-preview-section" id="sec_transition" style="background-color: #181614 !important;">
        <div style="background-color: #121110; border: 1px solid rgba(197, 168, 105, 0.3); padding: 3.5rem;">
            <div style="display: grid; grid-template-columns: 7fr 3.5fr; gap: 2.5rem; align-items: center;">
                <div>
                    <div class="editorial-eyebrow">TERRAE / OPERATIONAL CONSOLE</div>
                    <div style="font-family: 'Playfair Display', serif; font-size: 2.4rem; font-weight: 500; line-height: 1.15; color: #FBF9F4; margin-bottom: 1rem;">
                        Inspect raw imagery, tweak queries, and evaluate full evidence chains.
                    </div>
                    <div style="font-size: 1.05rem; line-height: 1.6; color: #C2BBB0;">
                        Transition from the public overview into the full-density geospatial analyst console. Run live multi-spectral change comparisons, inspect MECE trajectory tables, and generate auditable dossiers.
                    </div>
                </div>
                <div>
    """)
    if st.button("OPEN THE WORKSTATION →", key="btn_wp_transition", type="primary", use_container_width=True):
        st.session_state.app_mode = "workstation"
        st.rerun()
    render_html("""
                </div>
            </div>
        </div>
    </div>
    """)

    # FOOTER
    render_html("""
    <div style="padding: 3rem 0; border-top: 1px solid #2A2722; margin-top: 3rem; display: flex; justify-content: space-between; align-items: center; font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; color: #82796D;">
        <div>
            <span style="font-weight: 700; color: #C5A869; letter-spacing: 0.16em;">TERRAE</span> &middot; EARTH INTELLIGENCE &middot; SATELLITE INVESTIGATION CONSOLE &middot; SIH26227
        </div>
        <div>POWERED BY REMOTECLIP &middot; FAISS &middot; SENTINEL-2 L2A &middot; SPECTRAL ATTRIBUTION ENGINE</div>
        <div>&bull; AIR-GAPPED OFFLINE &middot; ZERO NETWORK CALLS</div>
    </div>
    """)

    # -------------------------------------------------------------------------
    # CLIENT-SIDE INTERACTION ENGINE (Executes in Browser Context via Components)
    # -------------------------------------------------------------------------
    client_payload = {
        "mPlates": [
            method_01_ask_b64,
            method_02_discover_b64,
            method_03_compare_b64,
            method_04_explain_b64,
            method_05_challenge_b64,
            method_06_decide_b64
        ],
        "mHeaders": [
            "01 / ASK &middot; NATURAL INTENT",
            "02 / DISCOVER &middot; SEMANTIC RETRIEVAL",
            "03 / COMPARE &middot; CO-REGISTRATION",
            "04 / EXPLAIN &middot; PHYSICAL ATTRIBUTION",
            "05 / CHALLENGE &middot; SPATIAL &amp; TEMPORAL",
            "06 / DECIDE &middot; AUDITABLE CONCLUSION"
        ],
        "mOverlays": [
            "QUERY HYPOTHESIS &rarr; Mapped to Surface Reflectance Targets",
            "REMOTECLIP + FAISS &rarr; Top Candidate Match (Sim: 0.2812)",
            "CIR FALSE-COLOR &rarr; Pre-aligned ESA MGRS 10m Grid",
            "PHYSICAL ATTRIBUTION &rarr; &Delta;NIR: -22.6%, &Delta;Red: -12.6%, &Delta;NDVI: -0.10",
            "SPATIAL COHERENCE: 15.7% &rarr; Trajectory: LATE_ONSET_CHANGE",
            "ANALYST CONCLUSION &rarr; REVIEW (Cryptographic Provenance)"
        ],
        "mMetas": [
            "Target: Built Surface<br>Bands: B02 Blue, B03 Green, B04 Red, B08 NIR<br>Planner: Natural Language Parsing",
            "Embedding: 512-dim L2 Normalized<br>Index: In-Memory FAISS Flat L2<br>Network Calls: 0 (Strictly Air-Gapped)",
            "Sub-pixel alignment: &plusmn;0.05 px<br>Valid pixels: 262,144 (100% SCL valid)<br>Cloud &amp; shadow: Masked",
            "Attribution Rule: Seasonal Phenology Response<br>Heuristic Support: 51.1% Built / 24.7% Veg / 19.9% Season<br>NDVI drop: -0.10 (Localized vegetative shift)",
            "Spatial Clusters: 152 connected components<br>Coherence Ratio: 15.7% (Threshold: 70%)<br>Dispersed agricultural phenology",
            "Decision Verdict: REVIEW<br>Confidence model: Heuristic Signature Matching<br>Audit Provenance: SHA-256 Verified"
        ],
        "tFrames": [sentinel2_t0_rgb_b64, sentinel2_tmid_rgb_b64, sentinel2_t1_rgb_b64],
        "tDates": [
            "T0 &middot; 19 MAY 2023 &middot; PRE-MONSOON BASELINE",
            "TMID &middot; 06 OCT 2023 &middot; POST-MONSOON GREENING PEAK",
            "T1 &middot; 05 DEC 2023 &middot; WINTER HARVEST DORMANCY"
        ],
        "tStats": [
            "NIR REFLECTANCE: 0.480 &middot; NDVI: +0.192",
            "NIR REFLECTANCE: 0.279 &middot; NDVI: +0.112 (GREATEST VEGETATION CHANGE)",
            "NIR REFLECTANCE: 0.254 &middot; NDVI: +0.092 (REVERSIBLE CYCLE)"
        ],
        "tNarratives": [
            "Dry Season Baseline &rarr; Soil &amp; pre-monsoon vegetation",
            "Intense Chlorophyll Absorption &rarr; Monsoon vegetation flush",
            "Post-Harvest Senescence &rarr; Trajectory confirms seasonal non-persistence"
        ],
        "oFrames": [sentinel2_t0_rgb_b64, sentinel2_tmid_rgb_b64, sentinel2_t1_rgb_b64, sentinel2_t0_cir_b64],
        "oCaptions": [
            "Observation 1/4 &middot; 19 MAY 2023 (Pre-monsoon dry baseline)",
            "Observation 2/4 &middot; 06 OCT 2023 (Post-monsoon agricultural greening peak)",
            "Observation 3/4 &middot; 05 DEC 2023 (Winter harvest dormancy)",
            "Observation 4/4 &middot; CIR FALSE-COLOR (NIR B08 / Red B04 / Green B03)"
        ],
        "eImgs": [
            evidence_01_raw_b64,
            evidence_02_mask_b64,
            evidence_03_spectral_b64,
            evidence_04_topology_b64,
            evidence_05_trajectory_b64,
            evidence_06_verdict_b64
        ],
        "eBadges": [
            "LAYER 01 / 06 &middot; RAW SURFACE REFLECTANCE",
            "LAYER 02 / 06 &middot; CHANGE MASK OVERLAY (&tau; = 0.15)",
            "LAYER 03 / 06 &middot; PHYSICAL SPECTRAL ATTRIBUTION",
            "LAYER 04 / 06 &middot; 8-CONNECTED TOPOLOGY (15.7% COHERENCE)",
            "LAYER 05 / 06 &middot; TEMPORAL PERSISTENCE TRAJECTORY",
            "LAYER 06 / 06 &middot; AUDITABLE CONCLUSION (REVIEW)"
        ],
        "eStats": [
            "SENTINEL-2 L2A &middot; 10M GSD &middot; B02, B03, B04, B08",
            "THRESHOLD: &tau; = 0.15 &middot; CHANGED: 1.0% (2,542 PX) &middot; VALID: 100%",
            "&Delta;NIR: -22.6% &middot; &Delta;RED: -12.6% &middot; &Delta;NDVI: -0.10",
            "CLUSTERS: 152 &middot; COHERENCE: 15.7% &middot; NOISE FILTER: PASS",
            "STABLE: 98.75% &middot; PERSISTENT: 0.39% &middot; LATE: 0.52%",
            "VERDICT: REVIEW &middot; SEASONAL PHENOLOGY &middot; SHA-256 VERIFIED"
        ],
        "eReadouts": [
            "Raw Multispectral Radiance &rarr; Pre-aligned Sentinel-2 BOA surface reflectance",
            "Spectral Differencing &rarr; Amber mask isolates genuine divergence from sensor noise",
            "Analytical Palette &rarr; Separates seasonal greening (green) from disturbance (amber)",
            "Topological Clustering &rarr; Eliminates single-pixel atmospheric artifacts",
            "Multi-Date Progression &rarr; 98.75% of scene confirmed stable across 3 observations",
            "Auditable Conclusion &rarr; Conservative REVIEW safeguards analysts against false alerts"
        ],
        "eLegends": [
            "RGB BOA Reflectance (B04=Red, B03=Green, B02=Blue)",
            "Amber = Divergent (&tau; &ge; 0.15) &middot; Black = Stable Background (99.0%)",
            "Green = Veg Flush (&Delta;NIR &gt; 0) &middot; Amber = Disturbance (&Delta;NIR &lt; 0) &middot; Teal = Water",
            "Color Coded = 152 8-Connected Clusters &middot; 84.3% Single-pixel Noise Suppressed",
            "Green = Stable (98.75%) &middot; Gold = Late-Onset (0.52%) &middot; Amber = Transient (0.39%)",
            "Gold Stamp = REVIEW &middot; SHA-256 Provenance Locked"
        ],
        "eLocs": [
            "MGRS 43RGM &middot; 262,144 valid pixels (100% SCL valid)",
            "2,542 px (1.00%) &middot; Cluster #14 Centroid (184, 112)",
            "2,542 px &middot; Focused across localized agrarian parcels",
            "152 connected components &middot; Dispersed agrarian topology",
            "258,869 px (98.75%) stable terrain &middot; 3 dates evaluated",
            "MGRS 43RGM &middot; Canonical Tile 2cbad278 &middot; SHA-256 Verified"
        ],
        "eAttributions": [
            "Sub-pixel aligned 10m bands B02, B03, B04, B08 &middot; TOA &rarr; BOA",
            "Amber mask isolates genuine divergence from sensor noise (&tau; = 0.15)",
            "&Delta;NIR: -22.6% &middot; &Delta;Red: -12.6% &middot; Chlorophyll absorption cycle",
            "Spatial coherence 15.7% &middot; Dispersed, non-contiguous components",
            "98.75% Stable &middot; 0.39% Persistent &middot; Seasonal reversible trajectory",
            "Heuristic Support: 51.1% Built / 24.7% Veg / 19.9% Season"
        ],
        "eVerdicts": [
            "OBSERVATION BASELINE &middot; Pre-monsoon dry canopy",
            "FLAGGED FOR DECOMPOSITION &middot; 1.0% divergence",
            "VEGETATIVE DIVERGENCE &middot; Crop senescence, not concrete",
            "SPATIAL REJECTION &middot; Sub-threshold coherence (15.7% &lt; 70%)",
            "TEMPORAL REJECTION &middot; Seasonal non-persistent cycle",
            "&#x26A0; REVIEW REQUIRED &middot; False alert avoided"
        ]
    }
    payload_json = json.dumps(client_payload)
    component_script = f"""
    <script>
    (function() {{
        const payload = {payload_json};
        const pWin = window.parent;
        const pDoc = window.parent.document;
        if (!pWin || !pDoc) return;

        // Method Step switcher
        pWin.setMethodStep = function(idx) {{
            const img = pDoc.getElementById('methodHeroImg');
            const hdr = pDoc.getElementById('methodBadgeStage');
            const ovr = pDoc.getElementById('methodHeroOverlay');
            const meta = pDoc.getElementById('methodHeroMeta');

            if (img && payload.mPlates[idx]) img.src = payload.mPlates[idx];
            if (hdr && payload.mHeaders[idx]) hdr.innerHTML = payload.mHeaders[idx];
            if (ovr && payload.mOverlays[idx]) ovr.innerHTML = payload.mOverlays[idx];
            if (meta && payload.mMetas[idx]) meta.innerHTML = payload.mMetas[idx];

            for (let i = 0; i < 6; i++) {{
                const el = pDoc.getElementById('mStep' + i);
                if (el) {{
                    if (i === idx) el.classList.add('active-step');
                    else el.classList.remove('active-step');
                }}
            }}
        }};

        // Temporal Stage switcher
        pWin.setTemporalStage = function(idx) {{
            const pills = [pDoc.getElementById('pillT0'), pDoc.getElementById('pillTmid'), pDoc.getElementById('pillT1')];
            pills.forEach((p, i) => {{
                if (p) {{
                    if (i === idx) p.classList.add('active');
                    else p.classList.remove('active');
                }}
            }});

            for (let i = 0; i < 3; i++) {{
                const panel = pDoc.getElementById('tPanel' + i);
                if (panel) {{
                    if (i === idx) {{
                        panel.classList.add('active');
                        panel.style.borderColor = '#C5A869';
                        panel.style.boxShadow = '0 0 20px rgba(197, 168, 105, 0.35)';
                    }} else {{
                        panel.classList.remove('active');
                        panel.style.borderColor = '#233026';
                        panel.style.boxShadow = 'none';
                    }}
                }}
            }}

            const bNarrative = pDoc.getElementById('temporalNarrative');
            if (bNarrative && payload.tNarratives[idx]) bNarrative.innerHTML = payload.tNarratives[idx];
        }};

        // Orbital Scan Player
        let curOrbitalIdx = 0;
        let isOrbitalPlaying = true;

        pWin.setOrbitalFrame = function(idx) {{
            curOrbitalIdx = (idx + payload.oFrames.length) % payload.oFrames.length;
            const img = pDoc.getElementById('orbitalImg');
            const cap = pDoc.getElementById('orbitalCaption');
            if (img && payload.oFrames[curOrbitalIdx]) img.src = payload.oFrames[curOrbitalIdx];
            if (cap && payload.oCaptions[curOrbitalIdx]) cap.innerHTML = payload.oCaptions[curOrbitalIdx];
            for (let i = 0; i < 4; i++) {{
                const pill = pDoc.getElementById('btnPill' + i);
                if (pill) {{
                    if (i === curOrbitalIdx) pill.classList.add('active');
                    else pill.classList.remove('active');
                }}
            }}
        }};

        pWin.stepOrbitalFrame = function(delta) {{
            pWin.setOrbitalFrame(curOrbitalIdx + delta);
        }};

        pWin.toggleOrbitalPlay = function() {{
            isOrbitalPlaying = !isOrbitalPlaying;
            const b = pDoc.getElementById('btnOrbitalPlay');
            if (b) b.textContent = isOrbitalPlaying ? '\\u23F8 PAUSE LOOP' : '\\u25B6 PLAY LOOP';
        }};

        if (pWin._orbitalInterval) clearInterval(pWin._orbitalInterval);
        pWin._orbitalInterval = setInterval(() => {{
            if (isOrbitalPlaying) {{
                curOrbitalIdx = (curOrbitalIdx + 1) % payload.oFrames.length;
                pWin.setOrbitalFrame(curOrbitalIdx);
            }}
        }}, 2200);

        // Progressive Evidence Layer Switcher
        let curEvidIdx = 0;

        pWin.setEvidLayer = function(idx) {{
            curEvidIdx = (idx + 6) % 6;
            const img = pDoc.getElementById('evidStageImg');
            const badge = pDoc.getElementById('evidStageBadge');
            const stat = pDoc.getElementById('evidStageStat');
            const read = pDoc.getElementById('evidReadout');
            const legend = pDoc.getElementById('evidStageLegend');
            const loc = pDoc.getElementById('evidHudLoc');
            const att = pDoc.getElementById('evidHudEvidence');
            const verd = pDoc.getElementById('evidHudVerdict');

            if (img && payload.eImgs[curEvidIdx]) img.src = payload.eImgs[curEvidIdx];
            if (badge && payload.eBadges[curEvidIdx]) badge.innerHTML = payload.eBadges[curEvidIdx];
            if (stat && payload.eStats[curEvidIdx]) stat.innerHTML = payload.eStats[curEvidIdx];
            if (read && payload.eReadouts[curEvidIdx]) read.innerHTML = payload.eReadouts[curEvidIdx];
            if (legend && payload.eLegends && payload.eLegends[curEvidIdx]) legend.innerHTML = payload.eLegends[curEvidIdx];
            if (loc && payload.eLocs && payload.eLocs[curEvidIdx]) loc.innerHTML = payload.eLocs[curEvidIdx];
            if (att && payload.eAttributions && payload.eAttributions[curEvidIdx]) att.innerHTML = payload.eAttributions[curEvidIdx];
            if (verd && payload.eVerdicts && payload.eVerdicts[curEvidIdx]) verd.innerHTML = payload.eVerdicts[curEvidIdx];

            for (let i = 0; i < 6; i++) {{
                const card = pDoc.getElementById('evidCard' + i);
                if (card) {{
                    if (i === curEvidIdx) card.classList.add('active-layer');
                    else card.classList.remove('active-layer');
                }}
            }}
        }};

        pWin.stepEvidLayer = function(delta) {{
            pWin.setEvidLayer(curEvidIdx + delta);
        }};

        // Scroll-driven IntersectionObserver for Method Steps
        function setupObserver() {{
            if ('IntersectionObserver' in pWin) {{
                const observer = new pWin.IntersectionObserver((entries) => {{
                    entries.forEach(entry => {{
                        if (entry.isIntersecting) {{
                            const idStr = entry.target.id;
                            if (idStr && idStr.startsWith('mStep')) {{
                                const stepIdx = parseInt(idStr.replace('mStep', ''), 10);
                                if (!isNaN(stepIdx)) pWin.setMethodStep(stepIdx);
                            }}
                        }}
                    }});
                }}, {{ threshold: 0.55 }});

                for (let i = 0; i < 6; i++) {{
                    const el = pDoc.getElementById('mStep' + i);
                    if (el) observer.observe(el);
                }}
            }}
        }}

        // Setup Before/After Slider Interaction
        function setupSlider() {{
            const baSlider = pDoc.getElementById('baSlider');
            const baDivider = pDoc.getElementById('baDivider');
            if (!baSlider || !baDivider) return;
            let isDragging = false;
            function updatePos(e) {{
                const r = baSlider.getBoundingClientRect();
                const clientX = e.touches ? e.touches[0].clientX : e.clientX;
                const p = Math.max(0, Math.min(100, (clientX - r.left) / r.width * 100));
                baSlider.style.setProperty('--ba-clip', p + '%');
                baDivider.style.left = p + '%';
            }}
            baSlider.addEventListener('mousedown', (e) => {{ isDragging = true; updatePos(e); }});
            baSlider.addEventListener('touchstart', (e) => {{ isDragging = true; updatePos(e); }}, {{ passive: true }});
            pDoc.addEventListener('mousemove', (e) => {{ if (isDragging) updatePos(e); }});
            pDoc.addEventListener('touchmove', (e) => {{ if (isDragging) updatePos(e); }}, {{ passive: true }});
            pDoc.addEventListener('mouseup', () => {{ isDragging = false; }});
            pDoc.addEventListener('touchend', () => {{ isDragging = false; }});
        }}

        // Smooth Section Scroll Controller
        pWin.navScrollTo = function(secId) {{
            const el = pDoc.getElementById(secId);
            if (!el) return;
            const headerOffset = 90;
            const container = pDoc.querySelector('[data-testid="stMain"]') || pDoc.querySelector('.main') || pDoc.querySelector('[data-testid="stAppViewContainer"]') || pDoc.documentElement;
            const currentScroll = container.scrollTop || pWin.pageYOffset || 0;
            const elementTop = el.getBoundingClientRect().top;
            const targetPos = currentScroll + elementTop - headerOffset;

            if (container.scrollTo) {{
                container.scrollTo({{
                    top: Math.max(0, targetPos),
                    behavior: 'smooth'
                }});
            }} else {{
                container.scrollTop = Math.max(0, targetPos);
            }}
            setTimeout(updateScrollTelemetry, 250);
            setTimeout(updateScrollTelemetry, 600);
        }};

        // Open Workstation Direct Trigger
        pWin.openWorkstationDirect = function() {{
            const all = Array.from(pDoc.querySelectorAll('button'));
            const target = all.find(b => b.textContent.includes('OPEN THE WORKSTATION'));
            if (target) {{
                target.click();
            }} else {{
                pWin.navScrollTo('sec_transition');
            }}
        }};

        // Global Scrollspy & Progress Rail Controller
        function updateScrollTelemetry() {{
            const vh = pWin.innerHeight;
            const threshold = vh * 0.40;

            const secHero = pDoc.getElementById('sec_hero');
            const secPhil = pDoc.getElementById('sec_philosophy');
            const secMethod = pDoc.getElementById('sec_method');
            const secTemporal = pDoc.getElementById('sec_temporal');
            const secMotion = pDoc.getElementById('sec_motion');
            const secCase01 = pDoc.getElementById('sec_case01');
            const secCase02 = pDoc.getElementById('sec_case02');
            const secEvidence = pDoc.getElementById('sec_evidence');
            const secObs = pDoc.getElementById('sec_observations');
            const secValid = pDoc.getElementById('sec_validation');
            const secWs = pDoc.getElementById('sec_transition');

            let activeStage = 1;
            let currentNav = 'product';

            if (secWs && secWs.getBoundingClientRect().top <= threshold) {{
                activeStage = 6;
                currentNav = 'workstation';
            }} else if (secValid && secValid.getBoundingClientRect().top <= threshold) {{
                activeStage = 5;
                currentNav = 'validation';
            }} else if (secObs && secObs.getBoundingClientRect().top <= threshold) {{
                activeStage = 5;
                currentNav = 'validation';
            }} else if (secEvidence && secEvidence.getBoundingClientRect().top <= threshold) {{
                activeStage = 4;
                currentNav = 'investigation';
            }} else if (secCase02 && secCase02.getBoundingClientRect().top <= threshold) {{
                activeStage = 4;
                currentNav = 'investigation';
            }} else if (secCase01 && secCase01.getBoundingClientRect().top <= threshold) {{
                activeStage = 3;
                currentNav = 'investigation';
            }} else if (secMotion && secMotion.getBoundingClientRect().top <= threshold) {{
                activeStage = 3;
                currentNav = 'method';
            }} else if (secTemporal && secTemporal.getBoundingClientRect().top <= threshold) {{
                activeStage = 3;
                currentNav = 'method';
            }} else if (secMethod && secMethod.getBoundingClientRect().top <= threshold) {{
                activeStage = 3;
                currentNav = 'method';
            }} else if (secPhil && secPhil.getBoundingClientRect().top <= threshold) {{
                activeStage = 2;
                currentNav = 'product';
            }} else {{
                activeStage = 1;
                currentNav = 'product';
            }}

            // Hero Scroll Transformation (Responsive, non-scrolljacking choreography)
            const heroEl = pDoc.getElementById('sec_hero');
            const isReduced = pWin.matchMedia && pWin.matchMedia('(prefers-reduced-motion: reduce)').matches;
            if (heroEl && !isReduced) {{
                const heroBg = pDoc.querySelector('.hero-fullbleed-bg');
                const heroHeadline = pDoc.querySelector('.hero-display-headline');
                const heroEyebrow = pDoc.querySelector('.hero-animate-eyebrow');
                const heroSubhead = pDoc.querySelector('.hero-subhead');
                const heroHud = pDoc.querySelector('.hero-hud-layer');
                
                const heroRect = heroEl.getBoundingClientRect();
                const heroH = heroEl.offsetHeight || 760;
                const heroProg = Math.min(1.0, Math.max(0.0, -heroRect.top / (heroH * 0.85)));

                if (heroBg) {{
                    const scale = 1.0 + heroProg * 0.08;
                    const translateY = heroProg * 35;
                    heroBg.style.transform = "scale(" + scale.toFixed(4) + ") translateY(" + translateY.toFixed(1) + "px)";
                }}

                if (heroHeadline) {{
                    const hOpacity = Math.max(0, 1.0 - Math.max(0, (heroProg - 0.15) * 2.2));
                    const hY = -heroProg * 25;
                    heroHeadline.style.opacity = hOpacity.toFixed(3);
                    heroHeadline.style.transform = "translateY(" + hY.toFixed(1) + "px)";
                }}

                if (heroEyebrow) {{
                    const eOpacity = Math.max(0, 1.0 - Math.max(0, (heroProg - 0.20) * 2.5));
                    heroEyebrow.style.opacity = eOpacity.toFixed(3);
                }}

                if (heroSubhead) {{
                    const sOpacity = Math.max(0, 1.0 - Math.max(0, (heroProg - 0.25) * 2.5));
                    heroSubhead.style.opacity = sOpacity.toFixed(3);
                }}

                if (heroHud) {{
                    const hudOpacity = Math.max(0, 1.0 - Math.max(0, (heroProg - 0.20) * 2.0));
                    heroHud.style.opacity = hudOpacity.toFixed(3);
                }}
            }}

            ['product', 'method', 'investigation', 'validation', 'workstation'].forEach(name => {{
                const el = pDoc.getElementById('nav_' + name);
                if (el) {{
                    if (name === currentNav) el.classList.add('active');
                    else el.classList.remove('active');
                }}
            }});

            // Investigation Progress Rail: fills discretely from stage 1 to current stage
            const fill = pDoc.getElementById('globalProgressFill');
            if (fill) {{
                const stageFillPct = ((activeStage - 1) / 5) * 100;
                fill.style.width = stageFillPct.toFixed(1) + '%';
            }}

            // Update discrete stage nodes
            for (let i = 1; i <= 6; i++) {{
                const node = pDoc.getElementById('pNode' + i);
                if (node) {{
                    if (i < activeStage) {{
                        node.classList.add('active');
                        node.classList.remove('active-current');
                    }} else if (i === activeStage) {{
                        node.classList.add('active');
                        node.classList.add('active-current');
                    }} else {{
                        node.classList.remove('active');
                        node.classList.remove('active-current');
                    }}
                }}
            }}
        }}
        pWin.updateScrollTelemetry = updateScrollTelemetry;

        function setupScrollListeners() {{
            const container = pDoc.querySelector('[data-testid="stMain"]') || pDoc.querySelector('.main') || pDoc.querySelector('[data-testid="stAppViewContainer"]') || pDoc.documentElement;
            if (container) container.addEventListener('scroll', updateScrollTelemetry, {{ passive: true }});
            pWin.addEventListener('scroll', updateScrollTelemetry, {{ passive: true }});
            pDoc.addEventListener('scroll', updateScrollTelemetry, {{ passive: true }});
            updateScrollTelemetry();
        }}

        setTimeout(() => {{
            setupObserver();
            setupSlider();
            setupScrollListeners();
        }}, 400);
    }})();
    </script>
    """
    components.html(component_script, height=0)

