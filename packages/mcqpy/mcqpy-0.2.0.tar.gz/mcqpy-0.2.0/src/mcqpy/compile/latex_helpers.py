from pylatex.base_classes import Environment
from pylatex.package import Package
from pylatex.utils import NoEscape


class Form(Environment):
    """Form environment from hyperref."""

    _latex_name = "Form"

    packages = [Package("hyperref")]
    escape = False
    content_separator = " "


def radio_option(quiz_index: int, q_slug: str, q_qid: str, i: int, checked=False) -> NoEscape:
    return multi_checkbox(
        quiz_index=quiz_index,
        q_slug=q_slug,
        q_qid=q_qid,
        i=i,
        checked=checked,
    )


def multi_checkbox(quiz_index: int, q_slug: str, q_qid: str, i: int, checked=False) -> NoEscape:
    command = NoEscape(
        r"\raisebox{0pt}[0pt][0pt]{\CheckBox"
        + f"[name=Q{quiz_index}-opt={i}-slug={q_slug}-qid={q_qid},"
        + r"width=1em,"
        + r"height=1em,"
        + r"bordercolor=0 0 0,"
        + r"backgroundcolor=1 1 1,"
        + (r"checked=true," if checked else "")
        + r"]{{}}"
        + "}"
    )
    return command

def code_block(code: str, language: str = "python") -> NoEscape:
    latex_block = rf"""\begin{{minted}}
    [
    frame=lines,
    framesep=2mm,
    baselinestretch=1.2,
    fontsize=\footnotesize,
    linenos
    ]
    {{{language}}}
{code}\end{{minted}}
"""
    return NoEscape(latex_block)