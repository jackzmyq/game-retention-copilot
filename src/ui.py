from html import escape
from src.config import ROOT


def css():
    return "<style>"+(ROOT/"src/theme.css").read_text(encoding="utf-8")+"</style>"


def banner(label,title,detail):
    return (f'<div class="decision-banner"><div class="decision-label">{escape(label)}</div>'
            f'<div><div class="decision-title">{escape(title)}</div>'
            f'<div class="decision-detail">{escape(detail)}</div></div></div>')


def note(text):
    return f'<div class="note-box">{escape(text)}</div>'
