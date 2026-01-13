import pytest


from epitech_console.System import Config
from epitech_console import init, quit


init()



def test_config_exist_returns_false(
    ) -> None:
    assert not Config.exist("tests")


def test_config_create_and_dont_exist(
    ) -> None:
    data = {
        "SECTION1": {"key11": "value11", "key12": "value12"},
        "SECTION2": {"key21": True, "key22": False},
        "SECTION3": {"key31": -100, "key32": 0, "key33": 100},
        "SECTION4": {"key41": -0.5, "key42": 0, "key43": 0.5}
    }
    Config("tests", data)

    assert Config.exist("tests")


def test_config_create_and_exist(
    ) -> None:
    Config("tests")

    assert Config.exist("tests")


def test_config_read(
    ) -> None:
    result = Config("tests")
    assert result.get("SECTION1", "key11") == "value11"
    assert result.get("SECTION1", "key12") == "value12"
    assert result.get_bool("SECTION2", "key21") == True
    assert result.get_bool("SECTION2", "key22") == False
    assert result.get_int("SECTION3", "key31") == -100
    assert result.get_int("SECTION3", "key32") == 0
    assert result.get_int("SECTION3", "key33") == 100
    assert result.get_float("SECTION4", "key41") == -0.5
    assert result.get_float("SECTION4", "key42") == 0
    assert result.get_float("SECTION4", "key43") == 0.5


def test_config_delete_cached(
    ) -> None:
    config = Config("tests")
    assert config.delete(True)
    assert config.config
    assert not Config.exist("tests")


def test_config_repr(
    ) -> None:
    config = Config("tests")

    assert repr(config) == "Config(\"tests/\", ?, \"config.ini\")"


def test_config_delete_not_cached(
    ) -> None:
    config = Config("tests")
    assert config.delete()
    assert not config.config
    assert not Config.exist("tests")


def test_config_delete_not_exist(
    ) -> None:
    assert not Config.exist("tests")


quit(delete_log=True)
