import rich_click as click
from mcqpy.cli.main import main

@main.group(name="question")
def question_group() -> None:
    """
    Commands related to question management.
    """
    return None # pragma: no cover
