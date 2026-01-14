import rich_click as click
from mcqpy.cli.main import main
from mcqpy.cli.config import QuizConfig

from pathlib import Path


@main.command(name="init", help="Initialize a new quiz project")
@click.argument("name", type=str, help="The name of the quiz project")
@click.option(
    "-f",
    "--file-name",
    type=str,
    default="quiz.pdf",
    help="Name of the output PDF file",
    show_default=True,
)
@click.option(
    "-mqd",
    "--make-questions-directory",
    is_flag=True,
    help="Create a questions directory",
    default=True,
)
@click.option(
    "-o",
    "--output-directory",
    type=str,
    default="output",
    help="Directory for output files",
    show_default=True,
)
@click.option(
    "-s",
    "--submission-directory",
    type=str,
    default="submissions",
    help="Directory for student submissions",
    show_default=True,
)
def init_command(
    name: str,
    file_name: str,
    make_questions_directory: bool,
    output_directory: str,
    submission_directory: str,
):
    # Create project directory
    project_path = Path(name)
    project_path.mkdir(parents=True, exist_ok=False)
    print(f"Initialized quiz project at: {project_path}")

    # Create questions directory if flag is set
    if make_questions_directory:
        questions_dir = project_path / "questions"
        questions_dir.mkdir(parents=True, exist_ok=False)
        print(f"Created questions directory at: {questions_dir}")

    submission_directory_path = project_path / submission_directory
    submission_directory_path.mkdir(parents=True, exist_ok=False)

    # Create example config.yaml
    config_file = project_path / "config.yaml"
    config = QuizConfig(
        questions_paths=["questions"],
        file_name=file_name,
        output_directory=output_directory,
        submission_directory=submission_directory,
    )
    config_file.write_text(config.yaml_dump())
    print(f"Created config file at: {config_file}")

    # Output directory
    output_dir = project_path / output_directory
    output_dir.mkdir(parents=True, exist_ok=False)
    print(f"Created output directory at: {output_dir}")
