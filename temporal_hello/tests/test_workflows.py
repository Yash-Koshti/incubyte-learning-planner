import os
import sys
import uuid

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
