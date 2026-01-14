import numpy as np
from mcqpy.question import Question
from mcqpy.question.filter import BaseFilter, CompositeFilter
from dataclasses import dataclass
from pathlib import Path
from typing import Literal


@dataclass(frozen=True)
class BankItem:
    question: Question
    path: Path


class QuestionBank:
    def __init__(self, items: list[BankItem], seed: int | None = None):
        self._items = items
        self._by_slug = {it.question.slug: it for it in items}
        self._by_qid = {it.question.qid: it for it in items}
        self._rng = np.random.default_rng(seed=seed)
        self._filters = []

    @classmethod
    def from_questions(cls, questions: list[Question], **kwargs):
        items = [BankItem(question=q, path=None) for q in questions]
        return cls(items=items, **kwargs)

    @classmethod
    def from_directories(cls, directories: list[str], glob_pattern="*.yaml", **kwargs):
        items = []
        qids, slugs = set(), set()
        for directory in directories:
            p = Path(directory)
            for file_path in p.glob(glob_pattern):
                question = Question.load_yaml(file_path)

                if question.slug in slugs:
                    raise ValueError(
                        f"Duplicate slug found: {question.slug} - {file_path}"
                    )

                slugs.add(question.slug)
                qids.add(question.qid)
                items.append(BankItem(question, file_path))

        return cls(items=items, **kwargs)

    def get_by_slug(self, slug: str) -> Question:
        if slug not in self._by_slug:
            raise KeyError(f"Slug {slug} not found in question bank")
        return self._by_slug[slug].question

    def get_by_qid(self, qid: str) -> Question:
        if qid not in self._by_qid:
            raise KeyError(f"QID {qid} not found in question bank")
        return self._by_qid[qid].question
    
    def __len__(self) -> int:
        return len(self._items)

    def get_all_questions(self) -> list[Question]:
        return [item.question for item in self._items]

    def add_filter(self, filter: BaseFilter):
        self._filters.append(filter)

    def get_filtered_questions(
        self,
        number_of_questions: int | None = None,
        shuffle: bool = False,
        sorting: Literal['none', 'slug'] = "none",
    ) -> list[Question]:
        if not self._filters:
            questions = self.get_all_questions()
        else:
            comp_filter = CompositeFilter(self._filters)
            questions = comp_filter.apply(self.get_all_questions())

        if shuffle:
            questions = self._rng.permutation(questions).tolist()

        if number_of_questions is not None:
            questions = questions[:number_of_questions]

        if sorting == "slug":
            questions = sorted(questions, key=lambda q: q.slug)
        elif sorting == "none":
            pass  # No sorting

        return questions
