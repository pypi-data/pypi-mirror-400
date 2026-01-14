import contextlib
import io
from pathlib import Path

import rich_click as click
from rich.progress import track

from mcqpy.cli.config import QuizConfig
from mcqpy.cli.main import main
from mcqpy.compile.manifest import Manifest
from mcqpy.utils.fill_form import fill_pdf_form


@main.command(
    name="test-autofill",
    help="Make answered versions of quiz to test mcqpy functionality",
)
@click.option(
    "-c",
    "--config",
    type=click.Path(exists=True, path_type=Path),
    default="config.yaml",
    help="Path to the config file",
    show_default=True,
)
@click.option(
    "-n",
    "--num-forms",
    type=int,
    default=10,
    help="Number of filled forms to generate",
    show_default=True,
)
@click.option('--correct', is_flag=True, help="Fill forms with correct answers")
def autofill_command(config, num_forms, correct):
    print(correct)
    # Directories & files
    config = QuizConfig.read_yaml(config)
    file_path = Path(config.output_directory) / config.file_name
    output_dir = Path(config.submission_directory)
    output_dir.mkdir(parents=True, exist_ok=True)
    file_name = Path(config.file_name).stem
    manifest_path = Path(config.output_directory) / f"{file_name}_manifest.json"
    manifest = Manifest.load_from_file(manifest_path)

    # In the autofill_command function
    for i in track(range(num_forms), description="Generating filled forms..."):
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        with (
            contextlib.redirect_stdout(stdout_capture),
            contextlib.redirect_stderr(stderr_capture),
        ):
            fill_pdf_form(file_path, out_path=output_dir, index=i, manifest=manifest, correct_only=correct)

    click.echo(f"Generated {num_forms} filled forms based on {file_path}")
