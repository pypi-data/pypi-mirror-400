import pytest
from sys import stderr
from time import time


from epitech_console.System import Console
from epitech_console import init, quit


init()



def test_console_print_basic(
    ) -> None:
    assert str(Console.print("hello")) == "hello\033[0m\n"


def test_console_print_multiple_argument(
    ) -> None:
    assert str(Console.print("hello", "world", "!!!")) == "hello world !!!\033[0m\n"


def test_console_print_with_start_end(
    ) -> None:
    assert str(Console.print("world", start=">>> ", end=" !!!\n")) == ">>> world\033[0m !!!\n"


def test_console_print_custom_file(
    ) -> None:
    assert str(Console.print("test", file=stderr)) == "test\033[0m\n"


def test_console_print_cut(
    ) -> None:
    assert ("-" * 100) in str(Console.print(("-" * 100), cut=True))
    result = str(Console.print(("-" * 110), cut=True))
    assert ("-" * 100) in result and "..." in result


def test_console_print_sleep(
    ) -> None:
    start_time = time()
    str(Console.print("hello world", sleep=0.1))
    end_time = time()
    assert 0.1 < (end_time - start_time) < 0.11


def test_console_len(
    ) -> None:
    assert len(Console) == 100


quit(delete_log=True)
