import asyncio

from activities import greet
from temporalio.client import Client
from temporalio.worker import Worker
from workflow import GreetingWorkflow


async def main():
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue="hello-queue",
        workflows=[GreetingWorkflow],
        activities=[greet],
    )
    print("Worker started, waiting for tasks...")
    await worker.run()


asyncio.run(main())
