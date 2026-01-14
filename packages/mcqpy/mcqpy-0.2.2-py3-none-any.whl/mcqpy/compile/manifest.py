from pydantic import BaseModel, ConfigDict, Field

from mcqpy.question import Question, compute_question_sha256


class ManifestItem(BaseModel):
    model_config = ConfigDict(
        frozen=True
    )  # make instances immutable (optional but helpful)
    qid: str
    slug: str
    non_permuted_correct_answers: list[int] = Field(
        ...,
        min_length=1,
        description="Indices of correct answers in `choices`, 0-based",
    )
    permutation: list[int] = Field(
        None,
        description="If provided, specifies a permutation of the choices to present",
    )

    permuted_correct_answers: list[int] | None = Field(
        ...,
        min_length=1,
        description="Indices of correct answers in the permuted choices, 0-based",
    )

    correct_onehot: list[int] = Field(
        ...,
        min_length=1,
        description="One-hot encoding of correct answers in the permuted choices",
    )

    sha256: str | None = Field(..., description="SHA256 hash of the question blob")
    point_value: int | None = Field(..., description="Point value of the question")

    @classmethod
    def from_question(
        cls, question: Question, permutation: list[int] | None
    ) -> "ManifestItem":
        if permutation is None:
            permutation = question.permutation

        sha256 = compute_question_sha256(question)

        # Compute the one-hot encoding of the correct answers
        n_choices = len(question.choices)
        correct_onehot = [0] * n_choices
        for i in question.correct_answers:
            permuted_index = permutation.index(i)
            correct_onehot[permuted_index] = 1

        return cls(
            qid=question.qid,
            slug=question.slug,
            non_permuted_correct_answers=question.correct_answers,
            permutation=permutation,
            permuted_correct_answers=[
                permutation.index(i) for i in question.correct_answers
            ],
            sha256=sha256,
            correct_onehot=correct_onehot,
            point_value=question.point_value,
        )


class Manifest(BaseModel):
    items: list[ManifestItem]

    def save_to_file(self, path):
        with open(path, "w") as f:
            f.write(self.model_dump_json(indent=2))

    def load_from_file(path):
        with open(path, "r") as f:
            data = f.read()
        return Manifest.model_validate_json(data)
    
    def get_item_by_qid(self, qid: str) -> ManifestItem | None:
        for item in self.items:
            if item.qid == qid:
                return item
        else:
            raise ValueError(f"Item with qid {qid} not found in manifest")
