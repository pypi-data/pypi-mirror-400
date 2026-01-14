from dataclasses import dataclass

@dataclass
class ParsedQuestion:
    qid: str
    slug: str
    answers: list[int]
    onehot: list[int]


@dataclass
class ParsedSet:
    student_id: str
    student_name: str
    questions: list[ParsedQuestion]
    file: str | None = None


@dataclass
class GradedQuestion:
    qid: str
    slug: str
    student_answers: list[int]
    correct_answers: list[int]
    max_point_value: int
    point_value: int = 0

@dataclass
class GradedSet:
    student_id: str
    student_name: str
    graded_questions: list[GradedQuestion]
    points: int = 0
    max_points: int = 0
