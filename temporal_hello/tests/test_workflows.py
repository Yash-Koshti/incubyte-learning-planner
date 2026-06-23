import os
import sys
import uuid

from temporalio import activity
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from activities import greet
from workflow import GreetingWorkflow


async def test_greeting_workflow_returns_result():
    async with await WorkflowEnvironment.start_time_skipping() as env:
        async with Worker(
            env.client,
            task_queue="test-queue",
            workflows=[GreetingWorkflow],
            activities=[greet],
        ):
            result = await env.client.execute_workflow(
                GreetingWorkflow.run,
                "Yash",
                id=f"test-{uuid.uuid4()}",
                task_queue="test-queue",
            )
            assert result == "Hello, Yash! From a Temporal activity."


async def test_greeting_workflow_uses_provided_name():
    async with await WorkflowEnvironment.start_time_skipping() as env:
        async with Worker(
            env.client,
            task_queue="test-queue",
            workflows=[GreetingWorkflow],
            activities=[greet],
        ):
            result = await env.client.execute_workflow(
                GreetingWorkflow.run,
                "Temporal",
                id=f"test-{uuid.uuid4()}",
                task_queue="test-queue",
            )
            assert "Temporal" in result


async def test_greeting_workflow_with_mocked_activity():
    @activity.defn(name="greet")  # same name as the real activity
    async def greet_mocked(name: str) -> str:
        return f"Mocked greeting for {name}"

    async with await WorkflowEnvironment.start_time_skipping() as env:
        async with Worker(
            env.client,
            task_queue="test-queue",
            workflows=[GreetingWorkflow],
            activities=[greet_mocked],  # register the mock, not the real one
        ):
            result = await env.client.execute_workflow(
                GreetingWorkflow.run,
                "Yash",
                id=f"test-{uuid.uuid4()}",
                task_queue="test-queue",
            )
            assert result == "Mocked greeting for Yash"


async def test_greeting_workflow_tracks_mock_calls():
    call_log = []

    @activity.defn(name="greet")
    async def greet_mocked(name: str) -> str:
        call_log.append(name)
        return f"Hi {name}"

    async with await WorkflowEnvironment.start_time_skipping() as env:
        async with Worker(
            env.client,
            task_queue="test-queue",
            workflows=[GreetingWorkflow],
            activities=[greet_mocked],
        ):
            await env.client.execute_workflow(
                GreetingWorkflow.run,
                "Yash",
                id=f"test-{uuid.uuid4()}",
                task_queue="test-queue",
            )
            assert call_log == ["Yash"]
