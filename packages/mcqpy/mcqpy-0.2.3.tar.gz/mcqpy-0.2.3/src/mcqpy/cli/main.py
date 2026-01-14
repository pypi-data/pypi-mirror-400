import rich_click as click

@click.group(name="mcqpy")
@click.version_option()
def main() -> None:
    """
    Command line interface for mcqpy.
    """
    return None # pragma: no cover

