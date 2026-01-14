from __future__ import annotations

import pytest
from concurrent.futures import ThreadPoolExecutor

from plugins import GeneratorPlugin, RefinerPlugin, PluginRegistry


class EchoGenerator(GeneratorPlugin):
    def __init__(self) -> None:
        super().__init__("echo")
        self.initialized = False
        self.cleaned = False

    def init(self, config=None) -> None:
        self.initialized = True

    def process(self, data):
        return data

    def cleanup(self) -> None:
        self.cleaned = True


class UpperRefiner(RefinerPlugin):
    def __init__(self) -> None:
        super().__init__("upper")
        self.initialized = False
        self.cleaned = False

    def init(self, config=None) -> None:
        self.initialized = True

    def process(self, data):
        return str(data).upper()

    def cleanup(self) -> None:
        self.cleaned = True


def test_generator_registration_and_lifecycle():
    reg = PluginRegistry()
    plugin = EchoGenerator()
    reg.register(plugin)
    plugin.init()
    assert reg.get_generator("echo").process("hi") == "hi"
    reg.unregister("echo")
    assert plugin.cleaned


def test_refiner_registration_and_lifecycle():
    reg = PluginRegistry()
    plugin = UpperRefiner()
    reg.register(plugin)
    plugin.init()
    assert reg.get_refiner("upper").process("hi") == "HI"
    reg.unregister("upper")
    assert plugin.cleaned


def test_duplicate_registration_raises():
    reg = PluginRegistry()
    reg.register(EchoGenerator())
    with pytest.raises(ValueError):
        reg.register(EchoGenerator())


def test_concurrent_register_and_unregister():
    reg = PluginRegistry()

    def do_register():
        plugin = EchoGenerator()
        reg.register(plugin)
        return plugin

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(do_register) for _ in range(10)]

    successes = []
    errors = 0
    for fut in futures:
        try:
            successes.append(fut.result())
        except ValueError:
            errors += 1

    assert len(successes) == 1
    assert errors == 9
    plugin = successes[0]
    assert reg.get_generator("echo") is plugin

    def do_unregister():
        reg.unregister("echo")

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(do_unregister) for _ in range(10)]
    for fut in futures:
        fut.result()

    assert "echo" not in reg.generators
    assert plugin.cleaned
