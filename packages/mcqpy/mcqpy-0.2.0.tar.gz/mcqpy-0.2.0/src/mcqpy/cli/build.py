import rich_click as click
import numpy as np
from mcqpy.cli.main import main
from mcqpy.cli.config import QuizConfig, SelectionConfig
from pathlib import Path
from mcqpy.question.filter import FilterFactory

from mcqpy.compile import MultipleChoiceQuiz
from mcqpy.question import QuestionBank
from mcqpy.compile.manifest import Manifest

from rich.pretty import Pretty
from rich.console import Console


def build_solution(questions, manifest, output_path: Path):
    from mcqpy.compile.solution_pdf import SolutionPDF
    solution_pdf = SolutionPDF(file=output_path, questions=questions, manifest=manifest)
    solution_pdf.build(generate_pdf=True)


def _select_questions(question_bank: QuestionBank, selection_config: SelectionConfig):
    ## Setup filters:
    if selection_config.filters:
        filter_objs = []
        for filter_name, filter_params in selection_config.filters.items():
            filter_config = {"type": filter_name, **filter_params}
            filter_obj = FilterFactory.from_config(filter_config)
            filter_objs.append(filter_obj)
            question_bank.add_filter(filter_obj)

    ## Apply filters and select questions
    questions = question_bank.get_filtered_questions(
        number_of_questions=selection_config.number_of_questions,
        shuffle=selection_config.shuffle,
        sorting=selection_config.sort_type,
    )
    return questions


@main.command(name="build", help="Build the quiz PDF from question files")
@click.option(
    "-c",
    "--config",
    type=click.Path(exists=True, path_type=Path),
    default="config.yaml",
    help="Path to the config file",
    show_default=True,
)
def build_command(config):
    config = QuizConfig.read_yaml(config)
    question_bank = QuestionBank.from_directories(config.questions_paths, seed=config.selection.seed)
    questions = _select_questions(question_bank, config.selection)

    console = Console()
    console.print("[bold green]Quiz Configuration:[/bold green]")
    console.print(Pretty(config))
    console.print(f"[bold green]Total questions in bank:[/bold green] {len(question_bank)}")
    console.print(f"[bold green]Selected questions:[/bold green] {len(questions)}")

    ## Paths:
    root = Path(config.root_directory)
    output_dir = root / config.output_directory
    file_path = output_dir / config.file_name
    submission_dir = (
        root / config.submission_directory if config.submission_directory else None
    )

    for path in [root, output_dir, submission_dir]:
        if path and not path.exists():
            path.mkdir(parents=True, exist_ok=True) # pragma: no cover

    mcq = MultipleChoiceQuiz(
        file=file_path,
        questions=questions,
        front_matter=config.front_matter,
        header_footer=config.header,
    )

    mcq.build(generate_pdf=True)

    # Build solution PDF
    manifest_path = mcq.get_manifest_path()
    manifest = Manifest.load_from_file(manifest_path)
    solution_output_path = (
        output_dir / f"{config.file_name.replace('.pdf', '')}_solution.pdf"
    )
    build_solution(questions, manifest, solution_output_path)
