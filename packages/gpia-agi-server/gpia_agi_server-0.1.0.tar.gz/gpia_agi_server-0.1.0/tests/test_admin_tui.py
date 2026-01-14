import pytest


def run_main(monkeypatch, inputs, route, check_ceo):
    import admin_tui

    idx = 0
    printed = []

    class DummyConsole:
        def input(self, prompt):
            nonlocal idx
            if idx >= len(inputs):
                raise EOFError
            line = inputs[idx]
            idx += 1
            return line

        def print(self, msg):
            printed.append(msg)

    monkeypatch.setattr(admin_tui, "Console", DummyConsole)
    monkeypatch.setattr(
        admin_tui,
        "load_texts",
        lambda lang: {"prompt": ">", "policy": "policy", "unknown_command": "unknown"},
    )

    admin_tui.main(route=route, check_ceo=check_ceo)
    return printed


def test_chat_and_unknown(monkeypatch):
    calls = []

    def route(src, agent, msg):
        calls.append((src, agent, msg))

    printed = run_main(
        monkeypatch,
        ["chat bob::hi", "foobar"],
        route,
        lambda msg: "ok",
    )

    assert calls == [("admin", "bob", "hi")]
    assert printed == ["unknown"]


@pytest.mark.parametrize(
    "command, called, expected_print",
    [
        ("check CEO::hi", True, ["policy: verdict"]),
        ("check Bob::hi", False, []),
    ],
)
def test_check_ceo(monkeypatch, command, called, expected_print):
    check_calls = []

    def check(msg):
        check_calls.append(msg)
        return "verdict"

    printed = run_main(monkeypatch, [command], lambda *a: None, check)

    assert (len(check_calls) == 1) is called
    assert printed == expected_print
