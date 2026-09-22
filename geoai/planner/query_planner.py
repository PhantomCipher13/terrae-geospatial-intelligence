"""
geoai/planner/query_planner.py
Maps a text query to an AnalysisPlan — decides which pipeline stages are needed.
No model inference happens here. Pure intent classification via keyword matching.
This is a minimal rule-based implementation for Phase 3.
Future: replace with a small local classifier or semantic intent model.
"""
from __future__ import annotations
import re
from geoai.core.result import AnalysisPlan

# Intent keywords — order matters (more specific first)
_CHANGE_KEYWORDS = {
    "construction","demolish","clearance","deforestation","build",
    "change","changed","expansion","flood","burned","fire","water",
    "grew","shrank","appear","disappear","before","after","temporal",
    "increase","decrease","new","removed","development",
}
_RETRIEVAL_KEYWORDS = {
    "find","search","show","locate","similar","like","where",
    "image","scene","area","region","look for","retrieve",
}


def plan_query(
    query_text: str | None = None,
    query_image_path: str | None = None,
    top_k: int = 10,
) -> AnalysisPlan:
    """
    Determine which pipeline stages are required for this query.
    Does NOT run any inference — pure rule-based planning.

    Expensive stages (registration, learned change) are only activated
    when the query explicitly requires temporal/change analysis.
    """
    plan = AnalysisPlan(
        query_text=query_text,
        query_image_path=query_image_path,
        top_k=top_k,
    )

    if query_text is None and query_image_path is None:
        plan.intent = "empty"
        plan.requires_retrieval = False
        plan.notes.append("No query provided.")
        return plan

    # Image-only query → image-to-image retrieval (semantic only)
    if query_text is None:
        plan.intent = "image_retrieval"
        plan.requires_retrieval = True
        plan.notes.append("Image query: semantic retrieval only.")
        return plan

    text_lower = query_text.lower()
    tokens = set(re.findall(r"\b\w+\b", text_lower))

    change_hits = tokens & _CHANGE_KEYWORDS
    retrieval_hits = tokens & _RETRIEVAL_KEYWORDS

    if change_hits:
        plan.intent = "change_detection"
        plan.requires_retrieval = True
        plan.requires_temporal_selection = True
        plan.requires_quality_gate = True
        plan.requires_registration = True
        plan.requires_spectral_analysis = True
        plan.requires_temporal_persistence = True
        plan.notes.append(f"Change intent detected (keywords: {change_hits}). Full temporal pipeline required.")
        # Learned change model is expensive — only activate if explicitly temporal
        if any(k in tokens for k in {"construction","deforestation","clearance","flood","burned"}):
            plan.requires_learned_change = True
            plan.notes.append("High-specificity change keyword: learned change model activated.")
    else:
        plan.intent = "semantic_retrieval"
        plan.requires_retrieval = True
        plan.notes.append("Retrieval intent. Temporal/change stages skipped.")

    return plan
