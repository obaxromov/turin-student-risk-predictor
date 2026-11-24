"""Guard workspace surfaces, navigation and reduced transparency."""
from pathlib import Path

CSS = (Path(__file__).resolve().parents[1] / "web/style.css").read_text(encoding="utf8")


def test_workspace_respects_display_preferences():
    assert ".card,.stat-card{background:var(--surface);" in CSS
    assert "@media(prefers-reduced-transparency:reduce)" in CSS
    assert ".topbar .tabs{background:var(--surface);backdrop-filter:none;" in CSS
    assert "@media (prefers-reduced-motion:reduce)" in CSS


def test_mobile_navigation_eases_access_to_all_teacher_destinations():
    assert "grid-template-columns:repeat(6,minmax(0,1fr))" in CSS
    assert "min-height:54px" in CSS
    assert "env(safe-area-inset-bottom,0px)" in CSS
