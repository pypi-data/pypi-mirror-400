import numpy as np
from mcqpy.question import Question
from mcqpy.question.filter import BaseFilter


class StratifiedFilter(BaseFilter):
    def __init__(
        self,
        number_of_questions: int,
        filters: list[BaseFilter] | None = None,
        proportions: list[float] | None = None,
        filter_configs: list[dict] | None = None,
    ):
        if filters is None:
            if filter_configs is None:
                raise ValueError("Either filters or filter_configs must be provided.")
            filters = self._make_filters(filter_configs)
        
        if proportions is None:
            proportions = [1.0 / len(filters)] * len(filters)
        
        if len(filters) != len(proportions):
            raise ValueError("Length of filters and proportions must match.")
        else: # Normalize        
            total = sum(proportions)
            proportions = [p / total for p in proportions]

        self.filters = filters
        self.proportions = proportions
        self.number_of_questions = number_of_questions

    def apply(self, questions: list[Question]) -> list[Question]:
        selected_questions = []
        total_questions = self.number_of_questions
        
        for filt, prop in zip(self.filters, self.proportions):
            num_to_select = int(total_questions * prop)
            filtered = filt.apply(questions)
            np.random.shuffle(filtered)
            selected_questions.extend(filtered[:num_to_select])
        
        return selected_questions
    
    def _make_filters(self, filter_configs: list[dict]) -> list[BaseFilter]:
        from mcqpy.question.filter import FilterFactory
        return [FilterFactory.from_config(cfg) for cfg in filter_configs]
