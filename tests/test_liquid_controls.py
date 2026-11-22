"""V7 custom control regression: no CDN, preserve native input state and role routing."""
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]

def test_enhancements_are_loaded_after_application():
    html=(BASE/'web/index.html').read_text()
    assert html.index('src="/app.js"')<html.index('src="/pages.js"')<html.index('src="/controls.js"')
    assert 'http' not in html.split('src="/controls.js"')[0].split('src=')[-1]

def test_accessible_custom_controls_keep_native_values():
    js=(BASE/'web/controls.js').read_text()
    assert "el.dispatchEvent(new Event('change',{bubbles:true}))" in js
    assert "role','combobox'" in js
    assert "role','listbox'" in js
    assert "aria-expanded" in js
    assert "aria-hidden" in js
    assert "el.files=dt.files" in js
    assert "innerHTML" not in js

def test_glass_and_lms_course_visuals():
    css=(BASE/'web/style.css').read_text()
    pages=(BASE/'web/pages.js').read_text()
    for key in ['.liquid-trigger','.liquid-dropdown','.liquid-upload','.badge','.cohort-chart .bar-f','.tierbar i']:
        assert key in css
    assert 'function courseLook(name)' in pages
    assert 'data-course-type' in pages
