

from textwrap import dedent
from IPython.display import Code, display, Markdown

def format_snippet(code_str: str) -> str:
    """Dedent and return a code string."""
    return dedent(code_str).strip() + "\n"

def display_snippet(code_str: str, language='python'):
    """
    In a Jupyter/Colab cell: pretty-print the code using IPython.display.Code
    If not in a notebook, it just prints.
    """
    try:
        display(Code(data=code_str, language=language))
    except Exception:
        print(code_str)

def save_snippet(code_str: str, path: str):
    """Save the snippet to a .py file"""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(code_str)
    return path
