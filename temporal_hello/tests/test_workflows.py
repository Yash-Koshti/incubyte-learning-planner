import os
import sys
import uuid

import pytest
from temporalio import activity
from temporalio.client import WorkflowFailureError
from temporalio.exceptions import ActivityError, ApplicationError
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

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


async def test_workflow_fails_when_activity_raises():
    @activity.defn(name="greet")
    async def greet_failing(name: str) -> str:
        raise ApplicationError(
            "Service unavailable",
            type="ServiceUnavailable",
            non_retryable=True,  # fails immediately, no retries
        )

    async with await WorkflowEnvironment.start_time_skipping() as env:
        async with Worker(
            env.client,
            task_queue="test-queue",
            workflows=[GreetingWorkflow],
            activities=[greet_failing],
        ):
            with pytest.raises(WorkflowFailureError) as exc_info:
                await env.client.execute_workflow(
                    GreetingWorkflow.run,
                    "Yash",
                    id=f"test-{uuid.uuid4()}",
                    task_queue="test-queue",
                )
            assert isinstance(exc_info.value.cause, ActivityError)


async def test_workflow_fails_after_exhausting_retries():
    attempt_count = 0

    @activity.defn(name="greet")
    async def greet_always_fails(name: str) -> str:
        nonlocal attempt_count
        attempt_count += 1
        raise ApplicationError("Always fails")

    async with await WorkflowEnvironment.start_time_skipping() as env:
        async with Worker(
            env.client,
            task_queue="test-queue",
            workflows=[GreetingWorkflow],
            activities=[greet_always_fails],
        ):
            with pytest.raises(WorkflowFailureError):
                await env.client.execute_workflow(
                    GreetingWorkflow.run,
                    "Yash",
                    id=f"test-{uuid.uuid4()}",
                    task_queue="test-queue",
                )
            # default retry policy retries — attempt_count > 1
            assert attempt_count > 1
