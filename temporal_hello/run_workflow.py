import asyncio
import uuid

from temporalio.client import Client
from workflow import GreetingWorkflow


async def main():
    client = await Client.connect("localhost:7233")
    result = await client.execute_workflow(
        GreetingWorkflow.run,
        "Temporal",
        id=f"greeting-{uuid.uuid4()}",
        task_queue="hello-queue",
    )
    print("Result:", result)


asyncio.run(main())
