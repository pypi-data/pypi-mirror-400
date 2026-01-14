import pyperclip
from pathlib import Path

def split_document():
    template_path = Path(__file__).parent / "template.py"
    code = template_path.read_text(encoding="utf-8")
    pyperclip.copy(code)
