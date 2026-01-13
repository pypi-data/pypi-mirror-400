"""A tool for running python code in a REPL."""

import ast
import re
import sys
from contextlib import redirect_stdout
from io import StringIO
from typing import Any, Dict, Optional, Type

from langchain_core.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.runnables.config import run_in_executor
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field, model_validator
from eagle.utils.restricted_python_utils import SafePythonCompiler, SafePythonCompilerForbiddenModuleException

# Auxiliary functions

def sanitize_input(query: str) -> str:
    """Sanitize input to the python REPL.

    Remove whitespace, backtick & python (if llm mistakes python console as terminal)

    Args:
        query: The query to sanitize

    Returns:
        str: The sanitized query
    """

    # Removes `, whitespace & python from start
    query = re.sub(r"^(\s|`)*(?i:python)?\s*", "", query)
    # Removes whitespace & ` from end
    query = re.sub(r"(\s|`)*$", "", query)
    return query

def set_def_code(query: str) -> str:
    """Set def code for the python REPL.

    Args:
        query: The query to set def code
    Returns:
        str: The def code query
    """
    def_code = "def myfunction(**kwargs):\n"
    def_code += "\n".join(
        "    " + line if line.strip() else line
        for line in query.splitlines()
    )
    return def_code

def _print_code_error_explanation(code_with_error: str, e: Exception) -> Dict[str, str]:
    # From the exception 'e', use regexp to get the line number after <inline>:
    try:
        if isinstance(e.args[0], str):
            inline_detected = re.findall(r"File \"<inline>\", line (\d+)", e.args[0])
        else:
            inline_detected = ''
    except Exception as b:
        raise b #TODO: Remove this line later, it's just for debugging
    if len(inline_detected) > 0:
        line_number = int(inline_detected[0])
        # get the line of code that raised the error
        line_of_code = code_with_error.split("\n")[line_number - 1]
        # get the error message
        error_message = str(e).split(re.findall(r"File .+, line .*", e.args[0])[-1])[-1]
    else:
        line_of_code = "Could not extract line number from error message. Look at the error message for more details."
        error_message = str(e)
    return f"""
**Code with error:**
```python
{code_with_error}
```
**Line of code that raised the error:**
```python
{line_of_code}
```
**Error message:**
```
{error_message}
```
"""

# Inputs
class PythonInputs(BaseModel):
    """Python inputs."""

    query: str = Field(description="code snippet to run")

# Tools
class SafePythonAstREPLTool(BaseTool):
    """Tool for running python code in a REPL."""

    name: str = "python_repl_ast"
    description: str = (
        "A Python shell. Use this to execute python commands. "
        "Input should be a valid python command. "
        "When using this tool, sometimes output is abbreviated - "
        "make sure it does not look abbreviated before using it in your answer."
    )
    locals: Optional[Dict] = Field(default_factory=dict)
    sanitize_input: bool = True
    args_schema: Type[BaseModel] = PythonInputs
    safe_import_module: Optional[list] = Field(
        default_factory=lambda: ["math", "random", "datetime", "itertools", "functools", "operator", "os", "plotly", "pandas", "numpy"]
    )
    forbidden_modules: Optional[list] = Field(
        default_factory=lambda: [
            'builtins.open',
            'builtins.input',
            'os.system', 
            'os.popen',
            'os.getenv',
            'os.environ.get',
            'subprocess.call',
            'subprocess.Popen',
            'pty.spawn',
            'platform.os.system',
            'imp.load_source',
            # 'imp.os',
            'pip.main'
        ]
    )
    max_for: int = 1000
    exec_timeout: int = 5

    @model_validator(mode="before")
    @classmethod
    def validate_python_version(cls, values: Dict) -> Any:
        """Validate valid python version."""
        if sys.version_info < (3, 9):
            raise ValueError(
                "This tool relies on Python 3.9 or higher "
                "(as it uses new functionality in the `ast` module, "
                f"you have Python version: {sys.version}"
            )
        return values

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        compiler = SafePythonCompiler(
            safe_import_modules=self.safe_import_module,
            forbidden_modules=self.forbidden_modules,
            max_for=self.max_for,
            exec_timeout=self.exec_timeout
        )
        compiler.loc.update(self.locals or {})
        try:
            if self.sanitize_input:
                query = sanitize_input(query)
            
            # def_code = set_def_code(query)
            def_code = query
            compiler.compile(def_code)
            tree = ast.parse(query)
            module = ast.Module(tree.body[:-1], type_ignores=[])
            exec(ast.unparse(module), compiler.restricted_globals, compiler.loc)  # type: ignore
            module_end = ast.Module(tree.body[-1:], type_ignores=[])
            module_end_str = ast.unparse(module_end)  # type: ignore
            io_buffer = StringIO()
            try:
                with redirect_stdout(io_buffer):
                    ret = eval(module_end_str, compiler.restricted_globals, compiler.loc)
                    if ret is None:
                        return io_buffer.getvalue()
                    else:
                        return ret
            except Exception:
                with redirect_stdout(io_buffer):
                    exec(module_end_str, compiler.restricted_globals, compiler.loc)
                return io_buffer.getvalue()
        except SafePythonCompilerForbiddenModuleException as e:
            return str(e)
        except Exception as e:
            return _print_code_error_explanation(def_code, e)

    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> Any:
        """Use the tool asynchronously."""

        return await run_in_executor(None, self._run, query)
