import subprocess
import tempfile
from pathlib import Path
from typing import Tuple
from dataclasses import dataclass

@dataclass
class LaTeXCheckResult:
    command: str
    is_available: bool
    version: str

def check_latex_command(command: str) -> LaTeXCheckResult:
    """Check if a LaTeX command is available in the system PATH.
    
    Args:
        command: The command name to check (e.g., 'pdflatex', 'latexmk')
        
    Returns:
        LaTeXCheckResult: Result of the command check.
    """
    try:
        output = subprocess.check_output(
            [command, '--version'],
            timeout=5
        )
        version = output.decode().split('\n')[0]
        return LaTeXCheckResult(command, True, version)
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return LaTeXCheckResult(command, False, "N/A")
    
def check_latex_compilation() -> Tuple[bool, str]:
    from pylatex import Document
    from mcqpy.compile.preamble import add_preamble

    document = Document()
    add_preamble(document)
    document.append("This is a test document to check LaTeX installation.")
    with tempfile.TemporaryDirectory() as tmpdirname:
        tmp_path = Path(tmpdirname)
        tex_file = tmp_path / "test"

        try:
            document.generate_pdf(filepath=tex_file, clean=True, silent=True)
            pdf_file = tex_file.with_suffix('.pdf')
            if not pdf_file.exists():
                return False, "PDF file was not generated."

        except Exception as e:
            return False, str(e)
        
        return True, ""
        
def check_latex_installation() -> Tuple[bool, dict]:
    """Comprehensive check of LaTeX installation.
    
    Args:
        verbose: If True, return detailed information about each check
        
    Returns:
        Tuple[bool, dict]: (all_checks_passed, details_dict)
    """
    results = {
        'pdflatex': None,
        'latexmk': None,
        'compilation_test': False,
        'error_message': None
    }
    
    # Tier 1: Check for required commands
    results['pdflatex'] = check_latex_command('pdflatex')
    results['latexmk'] = check_latex_command('latexmk')

    if not (results['pdflatex'].is_available and results['latexmk'].is_available):
        results['error_message'] = "Required LaTeX (pdflatex & latexmk) commands are missing."
        return False, results
    
    # Tier 2: Test actual compilation
    success, error_msg = check_latex_compilation()
    results['compilation_test'] = success
    
    if not success:
        results['error_message'] = error_msg
        return False, results
    
    return True, results