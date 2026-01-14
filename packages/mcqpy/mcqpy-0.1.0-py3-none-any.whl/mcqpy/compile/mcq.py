from pathlib import Path

from pylatex import (
    Command,
    Document,
    Foot,
    Head,
    PageStyle,
    Section,
)
from pylatex.utils import NoEscape
from pylatex.base_classes import Environment

from mcqpy.compile import FrontMatterOptions, HeaderFooterOptions
from mcqpy.compile.latex_helpers import Form
from mcqpy.compile.latex_questions import build_question
from mcqpy.compile.manifest import Manifest, ManifestItem
from mcqpy.compile.preamble import add_preamble
from mcqpy.question import Question

class SamePage(Environment):
    """SamePage environment to keep content on the same page."""

    _latex_name = "samepage"


class MultipleChoiceQuiz(Document):
    def __init__(
        self,
        file: Path | str | None = None,
        questions: list[Question] | None = None,
        front_matter: FrontMatterOptions | None = None,
        header_footer: HeaderFooterOptions | None = None,
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
        self._questions = questions or []
        self.front_matter = front_matter or FrontMatterOptions()
        self.header_footer = header_footer or HeaderFooterOptions()
        self.file = Path(file) if file is not None else Path("default_quiz.pdf")

    def get_questions(self) -> list[Question]:
        return self._questions

    ############################################################################
    # Build the document
    ############################################################################

    def build(self, generate_pdf: bool = False, **kwargs):
        # Front matter
        add_preamble(self)
        self._build_front_matter()
        self._build_header()

        # Questions:
        questions = self.get_questions()
        manifest_items = self._build_questions(questions)

        if generate_pdf:
            default_kwargs = {"clean_tex": True}
            default_kwargs.update(kwargs)
            self.generate_pdf(self.file.with_suffix(""), **default_kwargs)
            self._build_manifest(manifest_items)
            print(f"Generated quiz PDF at: {self.file}")

    def _build_header(self):
        # Check if any header/footer option is not None
        if not any(value is not None for value in self.header_footer.__dict__.values()):
            return  # No header/footer to build

        header = PageStyle("header")

        for position, content in [
            ("L", self.header_footer.header_left),
            ("C", self.header_footer.header_center),
            ("R", self.header_footer.header_right),
        ]:
            if content is not None:
                with header.create(Head(position)):
                    header.append(NoEscape(content))

        for position, content in [
            ("L", self.header_footer.footer_left),
            ("C", self.header_footer.footer_center),
            ("R", self.header_footer.footer_right),
        ]:
            if content is not None:
                with header.create(Foot(position)):
                    header.append(NoEscape(content))

        self.preamble.append(header)
        self.change_document_style("header")

    def get_manifest_path(self) -> Path:
        return self.file.with_name(self.file.stem + "_manifest").with_suffix(".json")

    def _build_manifest(self, manifest_items: list[ManifestItem]):
        manifest = Manifest(items=manifest_items)
        manifest_path = self.get_manifest_path()
        manifest.save_to_file(manifest_path)
        print(f"Generated manifest file at: {manifest_path}")

    def _build_front_matter(self):

        if self.front_matter.title is not None:
            self.preamble.append(Command("title", self.front_matter.title))
        else:
            self.preamble.append(Command("title", " "))

        if self.front_matter.author is not None:
            self.preamble.append(Command("author", self.front_matter.author))        
        else:
            self.preamble.append(Command("author", " "))

        if self.front_matter.date is not None:
            if isinstance(self.front_matter.date, str):
                self.preamble.append(Command("date", NoEscape(self.front_matter.date)))
            elif self.front_matter.date is True:
                self.preamble.append(Command("date", NoEscape(r"\today")))

        self.append(NoEscape(r"\maketitle"))

        if self.front_matter.id_fields:
            self._build_id_fields()

        if self.front_matter.exam_information is not None:
            with self.create(Section("Exam Information", numbering=False)):
                self.append(NoEscape(self.front_matter.exam_information))

    def _build_id_fields(self):

        field_options = "width=0.7\\textwidth, bordercolor=0 0 0, backgroundcolor=1 1 1"
        with self.create(Section("Student Information", numbering=False)):
            self.append(
                NoEscape(
                    r"Please fill in your name and student ID below, this is \underline{important}! \\"
                )
            )
            # A little vspace
            self.append(NoEscape(r"\\[5pt]"))
            with self.create(Form()):
                raw_field = NoEscape(
                    r"\TextField[name=student_name, "
                    + field_options
                    + r"]{\textbf{Name}:}"
                )
                self.append(raw_field)
                self.append(NoEscape(r"\\[10pt]"))  # add some vertical space
                raw_field = NoEscape(
                    r"\TextField[name=student_id, " + field_options + r"]{\textbf{ID}:}"
                )
                self.append(raw_field)

    def _build_questions(self, questions: list[Question]):
        manifest_items = []
        for quiz_index, question in enumerate(questions):
            self._build_question(question, quiz_index)
            manifest_items.append(
                ManifestItem.from_question(question, permutation=question.permutation)
            )

        return manifest_items

    def _build_question(self, question: Question, quiz_index: int):
        self.append(Command("pagebreak"))

        build_question(self, question, quiz_index)