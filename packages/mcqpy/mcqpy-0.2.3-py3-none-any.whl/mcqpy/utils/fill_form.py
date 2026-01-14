import numpy as np
from pypdf import PdfReader, PdfWriter


def get_student_name():
    first_names = [
        "Mikkel",
        "Sofie",
        "Frederik",
        "Emma",
        "William",
        "Ida",
        "Noah",
        "Anna",
        "Lucas",
        "Clara",
        "Oscar",
        "Laura",
        "Oliver",
        "Mathilde",
        "Alfred",
        "Katrine",
        "Emil",
    ]
    last_names = [
        "Jensen",
        "Nielsen",
        "Hansen",
        "Pedersen",
        "Andersen",
        "Christensen",
        "Larsen",
        "Sørensen",
        "Rasmussen",
        "Jørgensen",
        "Madsen",
        "Kristensen",
        "Olsen",
        "Johansen",
        "Poulsen",
        "Thomsen",
    ]

    return f"{np.random.choice(first_names)} {np.random.choice(last_names)}"


def fill_pdf_form(quiz_path, out_path, index=0, manifest=None, correct_only=False):
    reader = PdfReader(quiz_path)
    writer = PdfWriter(fileobj=reader)

    fields = reader.get_fields()
    keys = list(fields.keys())
    qid_name_dict = {}
    for key in keys:
        qid_idx = key.find("qid")
        if qid_idx != -1:
            qid = key[qid_idx + 4 :]

            if qid not in qid_name_dict:
                qid_name_dict[qid] = [key]
            else:
                qid_name_dict[qid].append(key)

    update_dict = {}
    for qid, names in qid_name_dict.items():
        if manifest:
            question = manifest.get_item_by_qid(qid)
            correct_choice = np.argwhere(question.correct_onehot).flatten()[0]

            if correct_only:
                name_to_fill = names[correct_choice]
            else:
                correct_prob = (
                    (1 / question.point_value) if question.point_value > 1 else 0.5
                )
                other_prob = (1 - correct_prob) / (len(question.correct_onehot) - 1)
                probs = [other_prob] * len(question.correct_onehot)
                probs[correct_choice] = correct_prob
                name_to_fill = np.random.choice(names, p=probs)

        update_dict[name_to_fill] = "/Yes"

    update_dict.update(
        {"studentname": f"{get_student_name()}", "studentid": f"TID{index}"}
    )

    writer.update_page_form_field_values(None, update_dict)

    with open(out_path / f"{quiz_path.stem}_autofill_{index}.pdf", "wb") as output_pdf:
        writer.write(output_pdf)
