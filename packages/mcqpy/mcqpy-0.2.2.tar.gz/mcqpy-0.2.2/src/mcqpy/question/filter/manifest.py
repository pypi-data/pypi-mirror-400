from mcqpy.question import Question
from mcqpy.question.filter import BaseFilter
from mcqpy.compile.manifest import Manifest


class ManifestFilter(BaseFilter):
    def __init__(
        self,
        manifest: Manifest | None = None,
        manifest_path: str | None = None,
        exclude: bool = True,
    ):
        """
        Filter questions based on a manifest file.

        Args:
            manifest (Manifest | None): An instance of Manifest. If provided, it will be used directly.
            manifest_path (str | None): Path to the manifest file. Used if `manifest` is None.
            exclude (bool): If True, questions in the manifest are excluded.
        """

        if manifest is not None:
            self.manifest = manifest
        elif manifest_path is not None:
            self.manifest = Manifest.load_from_file(manifest_path)
        else:
            raise ValueError("Either manifest or manifest_path must be provided.")

        self.exclude = exclude

    def apply(self, questions: list[Question]) -> list[Question]:
        filtered_questions = []
        manifest_qids = {item.qid for item in self.manifest.items}

        for question in questions:
            if question.qid in manifest_qids:
                if not self.exclude:
                    filtered_questions.append(question)
            else:
                if self.exclude:
                    filtered_questions.append(question)

        return filtered_questions
