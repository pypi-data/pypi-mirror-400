from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from annotated_types import doc
from pylatex import (
    Command,
    Document,
    Enumerate,
    Figure,
    Foot,
    Head,
    LongTable,
    MultiColumn,
    NewPage,
    NoEscape,
    Package,
    PageStyle,
    Section,
    SubFigure,
)
from rich.console import Console
from rich.progress import track

from mcqpy.grade.utils import GradedQuestion, GradedSet
from mcqpy.question import Question, QuestionBank


def get_grade_dataframe(graded_sets: list[GradedSet]) -> pd.DataFrame:
    records = []
    for graded_set in graded_sets:
        record = {
            "student_id": graded_set.student_id,
            "student_name": graded_set.student_name,
            "total_points": graded_set.points,
            "max_points": graded_set.max_points,
        }

        for index, graded_question in enumerate(graded_set.graded_questions):
            record[f"Q{index + 1}_points"] = graded_question.point_value

        records.append(record)

    df = pd.DataFrame.from_records(records)
    df.sort_values(by="student_name", inplace=True)
    return df


def question_analysis(
    graded_questions: list[GradedQuestion], out_directory: str | Path = None
):
    fig, axes = plt.subplots(1, 2, figsize=(10, 5), layout="constrained")

    fig.suptitle(f"Question Analysis: {graded_questions[0].slug}")

    # Answer distribution:
    all_onehots = np.vstack([q.student_answers for q in graded_questions])
    answer_sums = all_onehots.sum(axis=0)
    answer_labels = [f"{chr(i + 65)}" for i in range(all_onehots.shape[1])]

    correct_answers = graded_questions[0].correct_answers

    colors = [
        "green" if correct_answers[i] == 1 else "red"
        for i in range(len(correct_answers))
    ]

    ax = axes[0]
    ax.bar(answer_labels, answer_sums, color=colors, alpha=0.7, edgecolor="black")
    ax.set_xlabel("Answer Options")
    ax.set_ylabel("Number of Selections")
    ax.set_title("Distribution of Selected Answers")

    # Score distribution:
    scores = [q.point_value for q in graded_questions]
    ax = axes[1]
    ax.hist(
        scores,
        bins=np.arange(-0.5, max(scores) + 1.5, 1),
        color="blue",
        alpha=0.7,
        edgecolor="black",
    )
    ax.set_xticks(np.arange(0, max(scores) + 1, 1))
    ax.set_xlabel("Points Awarded")
    ax.set_ylabel("Number of Students")
    ax.set_title("Distribution of Points Awarded")

    # Save figure
    name = f"{graded_questions[0].slug}.pdf"
    output_path = Path(out_directory) / name

    plt.savefig(output_path) if out_directory else None
    plt.close(fig)

    return name


def make_quiz_analysis(graded_sets: list[GradedSet], output_dir: str | Path):
    point_distribution = np.array([gs.points for gs in graded_sets])
    max_points = graded_sets[0].max_points

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(
        point_distribution,
        bins=np.arange(-0.5, max_points + 1.5, 1),
        color="blue",
        alpha=0.7,
        edgecolor="black",
    )

    ax.axvline(max_points, color="red", linestyle="dashed", linewidth=1)

    ax.set_xlabel("Total Points")
    ax.set_ylabel("Number of Students")
    ax.set_title("Distribution of Total Points")

    name = "quiz_overall_analysis.pdf"
    output_path = output_dir / name

    plt.savefig(output_path)
    plt.close()
    return name


class QuizAnalysis(Document):
    def __init__(
        self,
        graded_sets: list[GradedSet],
        question_bank: QuestionBank,
        output_dir: str | Path = None,
        console: Console = None,
    ):
        super().__init__(
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
        self.graded_sets = graded_sets
        self.output_dir = Path(output_dir)
        self.figure_directory = self.output_dir / "figures"
        self.figure_directory.mkdir(parents=True, exist_ok=True)
        self.console = console or Console()
        self.question_bank = question_bank

    def build(self):
        # Added TOC
        self.preamble.append(Package("xcolor", options=["dvipsnames"]))
        self.preamble.append(Command("title", "Quiz Analysis Report"))
        self.preamble.append(Command("author", "MCQPy"))
        self.preamble.append(Command("date", NoEscape(r"\today")))
        self.append(NoEscape(r"\maketitle"))
        self.append(NoEscape(r"\tableofcontents"))
        self.append(NewPage())

        self.console.log("Building quiz analysis...")
        self.build_quiz_analysis()
        self.console.log("Building question analysis...")
        self.build_question_analyses()
        self.console.log("Building grade table...")
        self.build_grade_table()

        self.console.log("Generating PDF...")
        self.generate_pdf(self.output_dir / "quiz_analysis", clean_tex=True)
        self.console.log("Finished generating PDF.")

    def build_quiz_analysis(self):
        name = make_quiz_analysis(self.graded_sets, self.figure_directory)
        with self.create(Section("Overall Quiz Analysis")):
            with self.create(Figure(position="h!")) as fig:
                fig.add_image((Path("figures") / name).as_posix(), width="400px")
                fig.add_caption("Distribution of Total Points Scored in the Quiz")

            self.append(NewPage())

    def build_question_analyses(self):
        num_questions = len(self.graded_sets[0].graded_questions)
        for q_index in track(
            range(num_questions), description="Generating question analyses"
        ):
            with self.create(Section(f"Question {q_index + 1} Analysis")):
                graded_questions = [
                    gs.graded_questions[q_index] for gs in self.graded_sets
                ]
                fig_name = question_analysis(
                    graded_questions, out_directory=self.figure_directory
                )

                question = self.question_bank.get_by_qid(graded_questions[0].qid)

                self.append(NoEscape(question.text))

                with self.create(
                    Enumerate(enumeration_symbol=r"(\alph*)", options={})
                ) as enum:
                    for choice in question.choices:
                        enum.add_item(NoEscape(choice))

                with self.create(Figure(position="h!")) as fig:
                    fig.add_image(
                        (Path("figures") / fig_name).as_posix(), width="400px"
                    )
                    fig.add_caption(
                        f"Analysis for Question {q_index + 1}: {graded_questions[0].slug}"
                    )

                self.append(NewPage())

    def build_grade_table(self):
        df = get_grade_dataframe(self.graded_sets)

        with self.create(Section("Grade Summary Table")):
            with self.create(LongTable("l l l")) as data_table:
                data_table.add_hline()
                data_table.add_row(["ID", "Name", "Points"])
                data_table.add_hline()
                data_table.end_table_header()
                data_table.add_hline()
                data_table.add_row(
                    (MultiColumn(3, align="r", data="Continued on Next Page"),)
                )
                data_table.add_hline()
                data_table.end_table_footer()
                data_table.add_hline()
                data_table.add_row(
                    (MultiColumn(3, align="r", data="Not Continued on Next Page"),)
                )
                data_table.add_hline()
                data_table.end_table_last_footer()

                for row in df.itertuples(index=False):
                    data_table.add_row(
                        [row.student_id, row.student_name, f"{row.total_points}"]
                    )
