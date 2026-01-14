import rich_click as click


from mcqpy.cli.question.main import question_group

def _render_question(name, question):
    from pylatex import Document
    from mcqpy.compile.latex_questions import build_question

    document = Document(
        documentclass="article",
        geometry_options={
            "paper": "a4paper",
            "includeheadfoot": True,
            "left": "2cm",
            "right": "3cm",
            "top": "2.5cm",
            "bottom": "2.5cm",
        },
    )

    build_question(document, question, quiz_index=0)
    document.generate_pdf(f"{name}", clean_tex=True)

    return name



@question_group.command(name="render", help="Render a question as PDF. Useful to check LaTeX formatting.")
@click.argument("path", type=click.Path(exists=True))
def render_command(path):
    from mcqpy.question import Question
    from rich.console import Console
    import subprocess
    from pathlib import Path

    console = Console()
    try:
        question = Question.load_yaml(path)
    except Exception as e:
        console.print(f"[bold red]Error loading question from {path}:[/bold red]")
        console.print(e)
        return 
    
    name = Path(path).stem

    try:
       _render_question(name, question)
    except subprocess.CalledProcessError as e:
        console.print(f"[bold red]Invalid latex for question {path}[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Error generating question PDF for {path}:[/bold red]")
        console.print(e)
    else:
        console.print(f"[bold green]Generated question PDF at: {name}.pdf[/bold green]")



