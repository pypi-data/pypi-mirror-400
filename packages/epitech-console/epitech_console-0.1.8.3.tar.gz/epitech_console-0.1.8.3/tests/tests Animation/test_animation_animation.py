import pytest


from epitech_console.Text import Text
from epitech_console.Animation import Animation
from epitech_console import init, quit


init()


def test_animation_initialization_with_list(
    ) -> None:
    frames = ["A", "B", "C"]
    anim = Animation(frames)
    assert anim.animation == frames
    assert anim.step == 0
    assert anim.render().replace("\033[0m", "") == "A"


def test_animation_initialization_with_string(
    ) -> None:
    anim = Animation("X\\Y\\Z")
    assert anim.animation == ["X", "Y", "Z"]
    assert anim.render().replace("\033[0m", "") == "X"


def test_animation_add(
    ) -> None:
    anim1 = Animation(["A", "B", "C"])
    anim2 = Animation("X\\Y\\Z")
    anim3 = anim1 + anim2
    assert anim3.animation == ["A", "B", "C", "X", "Y", "Z"]


def test_animation_add_text(
    ) -> None:
    anim1 = Animation(["A", "B", "C"])
    text = Text("D")
    anim2 = anim1 + text
    assert anim2.animation == ["A", "B", "C", "D"]


def test_animation_update_basic(
    ) -> None:
    anim = Animation(["A", "B", "C"])
    assert anim.render().replace("\033[0m", "") == "A"
    anim.update()
    assert anim.render().replace("\033[0m", "") == "B"
    anim.update()
    assert anim.render().replace("\033[0m", "") == "C"


def test_animation_update_call(
    ) -> None:
    anim = Animation(["A", "B", "C"])
    assert anim.render().replace("\033[0m", "") == "A"
    anim()
    assert anim.render().replace("\033[0m", "") == "B"
    anim()
    assert anim.render().replace("\033[0m", "") == "C"


def test_animation_update_auto_reset_enabled(
    ) -> None:
    anim = Animation(["A", "B"])
    anim.update()  # index 1
    anim.update()  # auto-reset to 0
    assert anim.render().replace("\033[0m", "") == "A"


def test_animation_update_auto_reset_disabled(
    ) -> None:
    anim = Animation(["A", "B"])
    anim.update(auto_reset=False)
    anim.update(auto_reset=False)
    # Stays on last frame
    assert anim.render().replace("\033[0m", "") == "B"


def test_animation_render(
    ) -> None:
    anim = Animation(["A"])
    output = anim.render().replace("\033[0m", "")
    assert isinstance(output, str)
    assert output == "A"


def test_animation_render_delete_flag(
    ) -> None:
    anim = Animation(["A"])
    output = anim.render(delete=True).replace("\033[0m", "")
    assert isinstance(output, str)
    assert output == "A\x1b[1A\x1b[0G"


def test_animation_render_color_int(
    ) -> None:
    anim = Animation(["A"])
    output = anim.render(color=1).replace("\033[0m", "")
    assert isinstance(output, str)
    assert output == "\033[1mA"


def test_animation_repr(
    ) -> None:
    anim = Animation(["A"])
    assert repr(anim) == "Animation(['A'])"


def test_animation_length(
    ) -> None:
    anim = Animation(["A", "B", "C"])
    assert len(anim) == 3


quit(delete_log=True)
