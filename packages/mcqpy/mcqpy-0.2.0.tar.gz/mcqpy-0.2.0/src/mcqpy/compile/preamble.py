
from pylatex.package import Package
from pylatex.utils import NoEscape


def add_preamble(document):
    document.preamble.append(Package("caption"))
    document.preamble.append(Package("xcolor", options=["dvipsnames"]))
    document.preamble.append(Package("minted"))
    document.preamble.append(Package("textpos"))
    document.preamble.append(Package("tikz"))


    document.preamble.append(NoEscape(r"\usemintedstyle{vs}"))
    document.preamble.append(NoEscape(r"\captionsetup[figure]{labelformat=empty}"))
