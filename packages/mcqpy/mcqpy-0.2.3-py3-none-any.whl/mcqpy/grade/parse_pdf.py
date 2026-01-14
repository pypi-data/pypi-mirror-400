from pathlib import Path

from pypdf import PdfReader

from mcqpy.grade.utils import ParsedQuestion, ParsedSet


class MCQPDFParser:
    def parse_pdf(self, student_answer: str | Path) -> str:
        reader = PdfReader(student_answer)

        split_by_id = self._split_by_id(reader.get_fields())
        student_name, student_id = self._find_student_info(reader.get_fields())
        parsed_questions = self._parse_questions(split_by_id)

        # Make ParsedQuestion objects
        parsed_set = ParsedSet(
            student_id=student_id,
            student_name=student_name,
            questions=parsed_questions,
            file=str(student_answer),
        )

        return parsed_set

    def _split_by_id(self, fields):
        split_by_id = {}
        for name, field in fields.items():
            # Find the id in the field name
            qid_start = name.find("qid")
            if qid_start == -1:
                continue  # Not a question field, hopefully.

            qid = name[qid_start + 4 :]  # +4 to skip 'qid='

            if qid not in split_by_id:
                split_by_id[qid] = [(name, field)]
            else:
                split_by_id[qid].append((name, field))
        return split_by_id

    def _find_student_info(self, fields):
        student_name = None
        student_id = None
        for name, field in fields.items():
            if name == "studentname":
                student_name = field.get("/V")
            elif name == "studentid":
                student_id = field.get("/V")

        return student_name, student_id

    def _parse_questions(self, split_by_id):
        parsed = []
        for qid, entries in split_by_id.items():
            slug = None
            answers = []
            onehot = []
            for name, field in entries:
                # Find the slug in the field name
                slug_start = name.find("slug")
                if slug_start != -1:
                    slug = name[slug_start + 5 :]  # +5 to skip 'slug='

                # Find the answer index in the field name
                opt_start = name.find("opt")
                if opt_start != -1:
                    opt_str = name[opt_start + 4 :].split("-")[0]  # +4 to skip 'opt='
                    opt_index = int(opt_str)
                    if field.get("/V") == "/Yes":
                        answers.append(opt_index)
                        onehot.append(1)
                    else:
                        onehot.append(0)

            parsed.append(
                ParsedQuestion(qid=qid, slug=slug, answers=answers, onehot=onehot)
            )

        return parsed
