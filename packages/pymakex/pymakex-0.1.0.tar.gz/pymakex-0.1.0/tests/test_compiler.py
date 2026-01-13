import pytest
from pycompiler import Compiler


def test_compiler_init():
    compiler = Compiler("test code")
    assert compiler.source_code == "test code"


def test_compiler_tokenize():
    compiler = Compiler("test code")
    with pytest.raises(ValueError):
        empty_compiler = Compiler()
        empty_compiler.tokenize()


def test_compiler_compile():
    compiler = Compiler("test code")
    result = compiler.compile()
    assert result == "Compiled successfully"


def test_compiler_execute():
    compiler = Compiler("test code")
    result = compiler.execute()
    assert "Executing" in result
