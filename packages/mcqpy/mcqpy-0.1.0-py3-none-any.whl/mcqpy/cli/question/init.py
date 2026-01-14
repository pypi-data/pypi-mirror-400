import rich_click as click


from mcqpy.cli.question.main import question_group


@question_group.command(name="init", help="Initialize question file.")
@click.argument("path", type=click.Path(exists=False))
def init_command(path):
    from mcqpy.question import Question
    from rich.console import Console
    from rich.pretty import Pretty


    # Get the yaml schema for a question
    schema = Question.get_yaml_template()
    # Write to the specified path
    with open(path, "w", encoding="utf-8") as f:
        f.write(schema)
    




            