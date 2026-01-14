# mcqpy 

[![codecov](https://codecov.io/github/au-mbg/mcqpy/graph/badge.svg?token=JIXBIKWVOQ)](https://codecov.io/github/au-mbg/mcqpy)

Generate and grade interactive multiple-choice quiz PDF documents. 
Rendered documents with 

- LaTeX formatting - including for math/equations.
- Include figures from files or from links.
- Code snippets with highlighted code. 
- Headers and footers. 

Easily grade hundreds of quizzes with grades exported to `.xlsx` or `.csv` while 
obtaining question-level statistics.

## Example

The simplest way to use `mcqpy` is through the command line interface (CLI). A project 
can be initialized like so
```
mcqpy init <PROJECT_NAME>
```
Which will create a directory `<PROJECT_NAME>` containing the following: 

- `config.yaml`: Overall configuration of the project, including author, document name, header, footer and preface options. 
- `questions/`: A directory where the project expects question `.yaml` files to be located. 
- `output/`: Where the built documents will be put. 
- `submissions/`: A directory where submitted quizzes should be put for grading. 

For a quiz to be interesting it needs questions, the template structure of a question 
can be created using 
```
mcqpy question init <QUESTION_PATH>
```
where `<QUESTION_PATH>` could be `questions/q1.yaml`. Once the desired number of questions have been 
written the quiz can be compiled using 
```
mcqpy build 
```
Which produces a number of files in the `output/` directory the important ones being 

- `<NAME>.pdf`: The quiz document
- `<NAME>_solution.pdf`: A human readable solution key to all questions contained in the quiz. 
- `<NAME>_manifest.json`: Quiz key used by `mcqpy` to grade quizzes. 

The `<NMAE>.pdf` document can be distributed to quiz takers through any means and once 
returned and placed in the `submissions/` directory be graded by the program. 
A number of test submissions can be created using
```
mcqpy test-autofill -n 50 
```
Which here generates 50 randomly filled quizzes. To grade run 
```
mcqpy grade -a 
```
Which will produce the files `<NAME>_grades.xlsx` containing the grades of all submissions and `analysis/<NAME>_analysis.pdf` containing statistics about overall point distributions as well as question level statistics. 

## Installation

`mcqpy` requires Python, a small number of Python packages and a working LaTeX installation. 

### Installing `mcqpy` in a venv.

If you have a working Python installation we recommend installing `mcqpy` in a suitable virtual environment (venv) using `pip`

```
pip install git+https://github.com/au-mbg/mcqpy.git
```

### Installing Python & `mcqpy`. 

If you do not have a suitable Python version, `uv` can be recommended for installing and managing Python, see [Installing uv](https://docs.astral.sh/uv/getting-started/installation/). With uv installed you can create a venv with `mcqpy` using
```
uv venv
source .venv/bin/activate  # On Mac/Linux
uv pip install git+https://github.com/au-mbg/mcqpy.git
```

### Install LaTeX 

You will also need a working LaTeX installation, once `mcqpy` is installed you can check for that using 

```
mcqpy check-latex
```
Which will output the versions of `pdflatex` and `latexmk` if they are installed, if not you should install an OS 
appropriate LaTeX distribution for example from one of these sources: 

- **macOS**: [MacTeX](https://www.tug.org/mactex/)
- **Windows**: [TeX Live](https://www.tug.org/texlive/) or [MiKTeX](https://miktex.org/)
- **Linux**: TeX Live (usually available through your package manager, e.g., `sudo apt install texlive-full` on Ubuntu/Debian)




