from pathlib import Path

from mcqpy.compile.manifest import Manifest
from mcqpy.grade.utils import GradedQuestion, GradedSet, ParsedSet
from mcqpy.grade.rubric import Rubric
from mcqpy.grade.parse_pdf import MCQPDFParser


class MCQGrader:
    def __init__(self, manifest: Manifest, rubric: Rubric):
        self.manifest = manifest
        self.rubric = rubric
        self.parser = MCQPDFParser()

    ############################################################################
    # Grade the parsed student answers
    ############################################################################

    def grade(self, student_answer: str | Path = None, parsed_set: ParsedSet = None) -> GradedSet:
        if parsed_set is None:
            parsed_set = self.parser.parse_pdf(student_answer)
        graded_set = GradedSet(
            student_id=parsed_set.student_id,
            student_name=parsed_set.student_name,
            graded_questions=[]
        )

        for parsed_question in parsed_set.questions:
            manifest_item = self.manifest.get_item_by_qid(parsed_question.qid)

            # Grade the question
            graded_question = GradedQuestion(
                qid=parsed_question.qid,
                slug=parsed_question.slug,
                student_answers=parsed_question.onehot,
                correct_answers=manifest_item.correct_onehot,
                max_point_value=manifest_item.point_value,
            )

            # Apply rubric to determine point value earned
            graded_question.point_value = self.rubric.score_question(graded_question)            
            graded_set.graded_questions.append(graded_question)


        # Return the graded set
        graded_set.points = sum(q.point_value for q in graded_set.graded_questions)
        graded_set.max_points = sum(q.max_point_value for q in graded_set.graded_questions)
        return graded_set


