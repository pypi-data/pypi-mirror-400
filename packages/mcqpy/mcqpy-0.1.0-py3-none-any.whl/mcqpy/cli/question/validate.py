import rich_click as click


from mcqpy.cli.question.main import question_group


@question_group.command(name="validate", help="Validate question files")
@click.argument("paths", type=click.Path(exists=True), nargs=-1)
def validate_command(paths):
    from mcqpy.question import Question
    from rich.console import Console
    from rich.pretty import Pretty

    console = Console()

    for path in paths:
        try:
            question = Question.load_yaml(path)
            console.print(f"[bold green]Valid question file:[/bold green] {path}")
        except Exception as e:
            console.print(f"[bold red]Error loading question from {path}:[/bold red]")
            console.print(e)

        console.print()
            