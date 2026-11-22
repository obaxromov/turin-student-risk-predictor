"""Guard against the former V6/V7 thick-stroke and stacked-gloss regression."""
from pathlib import Path
CSS=(Path(__file__).resolve().parents[1]/"web/style.css").read_text()

def test_there_is_only_one_material_control_definition():
    assert "/* V8 — one coherent material system" in CSS
    assert "/* V7 — material" not in CSS
    assert "border:1px solid rgba(131,173,255,.68)" not in CSS
    assert "box-shadow:inset 0 1.5px 1px var(--liquid-inner)" not in CSS

def test_panels_have_no_decorative_outline_or_overlay():
    assert "border:none;" in CSS and "background:var(--panel-quiet)" in CSS
    assert ".card::before,.stat-card::before {content:none;display:none;}" in CSS
    assert "--panel-quiet:rgba(29,40,59,.88)" in CSS

def test_controls_support_reduced_motion_and_transparency():
    assert "--pointer-x" in CSS
    assert "@media(prefers-reduced-motion:reduce)" in CSS
    assert "@media(prefers-reduced-transparency:reduce)" in CSS
