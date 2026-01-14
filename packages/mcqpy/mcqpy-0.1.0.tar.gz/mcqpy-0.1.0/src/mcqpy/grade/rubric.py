import numpy as np
from mcqpy.grade.utils import GradedQuestion


class Rubric:

    def __init__(self):
        pass

    def score_question(self, question: GradedQuestion) -> int:
        return NotImplementedError("Subclasses should implement this method.") # pragma: no cover
    

class StrictRubric(Rubric):
    
    def score_question(self, question: GradedQuestion) -> int:
        return (question.student_answers == question.correct_answers) * question.max_point_value