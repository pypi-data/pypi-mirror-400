"""Software Engineering domain primitives.

These primitives represent common operations needed for software engineering tasks,
based on patterns identified in successful bug fixes and feature implementations.
"""

from __future__ import annotations

from cognitive_core.core.types import CodeConcept


class SWEPrimitiveLoader:
    """Load software engineering primitives.

    Provides a set of fundamental operations for working with codebases,
    including file operations, code search, and git operations.

    Example:
        ```python
        loader = SWEPrimitiveLoader()
        primitives = loader.load()
        read = primitives["swe_read_file"]
        ```
    """

    def load(self) -> dict[str, CodeConcept]:
        """Load all SWE primitives.

        Returns:
            Dict mapping primitive ID to CodeConcept.
        """
        return {
            "swe_read_file": CodeConcept(
                id="swe_read_file",
                name="read_file",
                description="Read the contents of a file from the codebase",
                code="""def read_file(path: str) -> str:
    '''Read file contents at the given path.'''
    with open(path, 'r') as f:
        return f.read()""",
                signature="(path: str) -> str",
                examples=[
                    ("'src/main.py'", "contents of main.py"),
                    ("'README.md'", "contents of README"),
                ],
                source="primitive",
            ),
            "swe_write_file": CodeConcept(
                id="swe_write_file",
                name="write_file",
                description="Write contents to a file in the codebase",
                code="""def write_file(path: str, content: str) -> None:
    '''Write content to file at the given path.'''
    with open(path, 'w') as f:
        f.write(content)""",
                signature="(path: str, content: str) -> None",
                examples=[
                    ("'output.txt', 'hello'", "creates file with 'hello'"),
                ],
                source="primitive",
            ),
            "swe_search_codebase": CodeConcept(
                id="swe_search_codebase",
                name="search_codebase",
                description="Search for a pattern across all files in the codebase using regex or text matching",
                code="""def search_codebase(pattern: str, path: str = '.', regex: bool = False) -> list[SearchResult]:
    '''Search for pattern in all files under path.'''
    # Returns list of (file, line_number, line_content) matches
    ...""",
                signature="(pattern: str, path: str = '.', regex: bool = False) -> list[SearchResult]",
                examples=[
                    ("'def process'", "list of function definitions containing 'process'"),
                    ("'TODO:', regex=False", "list of TODO comments"),
                ],
                source="primitive",
            ),
            "swe_find_definition": CodeConcept(
                id="swe_find_definition",
                name="find_definition",
                description="Find the definition of a symbol (function, class, variable) in the codebase",
                code="""def find_definition(symbol: str, language: str | None = None) -> Definition | None:
    '''Find where a symbol is defined.'''
    # Uses language-specific parsing when language is specified
    ...""",
                signature="(symbol: str, language: str | None = None) -> Definition | None",
                examples=[
                    ("'UserService'", "Definition(file='services/user.py', line=15)"),
                    ("'process_data'", "Definition(file='utils.py', line=42)"),
                ],
                source="primitive",
            ),
            "swe_find_references": CodeConcept(
                id="swe_find_references",
                name="find_references",
                description="Find all references to a symbol throughout the codebase",
                code="""def find_references(symbol: str) -> list[Reference]:
    '''Find all places where symbol is used.'''
    ...""",
                signature="(symbol: str) -> list[Reference]",
                examples=[
                    ("'UserService'", "list of files/lines where UserService is referenced"),
                ],
                source="primitive",
            ),
            "swe_run_tests": CodeConcept(
                id="swe_run_tests",
                name="run_tests",
                description="Run test suite or specific tests and return results",
                code="""def run_tests(test_path: str | None = None, verbose: bool = False) -> TestResult:
    '''Run tests and return pass/fail results.'''
    # Supports pytest, unittest, jest, etc.
    ...""",
                signature="(test_path: str | None = None, verbose: bool = False) -> TestResult",
                examples=[
                    ("None", "run all tests"),
                    ("'tests/test_user.py'", "run specific test file"),
                ],
                source="primitive",
            ),
            "swe_apply_patch": CodeConcept(
                id="swe_apply_patch",
                name="apply_patch",
                description="Apply a unified diff patch to modify files",
                code="""def apply_patch(patch: str, dry_run: bool = False) -> PatchResult:
    '''Apply a unified diff patch to the codebase.'''
    ...""",
                signature="(patch: str, dry_run: bool = False) -> PatchResult",
                examples=[
                    ("unified diff string", "applies changes to files"),
                ],
                source="primitive",
            ),
            "swe_git_diff": CodeConcept(
                id="swe_git_diff",
                name="git_diff",
                description="Get the git diff showing current changes or changes between commits",
                code="""def git_diff(ref1: str | None = None, ref2: str | None = None) -> str:
    '''Get git diff output.'''
    # If no refs: diff of working tree vs HEAD
    # If one ref: diff of working tree vs ref
    # If two refs: diff between refs
    ...""",
                signature="(ref1: str | None = None, ref2: str | None = None) -> str",
                examples=[
                    ("None, None", "current uncommitted changes"),
                    ("'main', 'feature'", "diff between branches"),
                ],
                source="primitive",
            ),
            "swe_edit_file": CodeConcept(
                id="swe_edit_file",
                name="edit_file",
                description="Make targeted edits to a file by replacing specific text",
                code="""def edit_file(path: str, old_text: str, new_text: str) -> bool:
    '''Replace old_text with new_text in file.'''
    content = read_file(path)
    if old_text not in content:
        return False
    new_content = content.replace(old_text, new_text, 1)
    write_file(path, new_content)
    return True""",
                signature="(path: str, old_text: str, new_text: str) -> bool",
                examples=[
                    ("'main.py', 'old_func()', 'new_func()'", "True if replacement made"),
                ],
                source="primitive",
            ),
            "swe_list_files": CodeConcept(
                id="swe_list_files",
                name="list_files",
                description="List files in a directory matching a pattern",
                code="""def list_files(path: str = '.', pattern: str = '*') -> list[str]:
    '''List files matching pattern under path.'''
    import glob
    return glob.glob(f'{path}/{pattern}', recursive=True)""",
                signature="(path: str = '.', pattern: str = '*') -> list[str]",
                examples=[
                    ("'.', '**/*.py'", "all Python files"),
                    ("'src', '*.ts'", "TypeScript files in src/"),
                ],
                source="primitive",
            ),
        }
