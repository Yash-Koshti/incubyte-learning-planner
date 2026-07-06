import os
import sys

from temporalio.testing import ActivityEnvironment

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from activities import greet


async def test_greet_returns_greeting():
    env = ActivityEnvironment()
    result = await env.run(greet, "Yash")
    assert result == "Hello, Yash! From a Temporal activity."


async def test_greet_includes_name():
    env = ActivityEnvironment()
    result = await env.run(greet, "Temporal")
    assert "Temporal" in result
