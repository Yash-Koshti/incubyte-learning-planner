from dataclasses import dataclass
from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy
from temporalio.exceptions import ActivityError

with workflow.unsafe.imports_passed_through():
    from app.temporal.activities import (
        ExtractKeywordsInput,
        ExtractTextInput,
        GenerateSummaryInput,
        MarkJobInput,
        StoreResultsInput,
        extract_keywords,
        extract_text,
        generate_summary,
        mark_job_failed,
        mark_job_running,
        store_results,
    )


@dataclass
class ProcessDocumentInput:
    job_id: str
    document_id: str
    operations: list[str]


DEFAULT_RETRY = RetryPolicy(
    maximum_attempts=3,
    initial_interval=timedelta(seconds=1),
    backoff_coefficient=2.0,
)

SHORT_TIMEOUT = timedelta(seconds=10)


@workflow.defn
class DocumentProcessingWorkflow:
    @workflow.run
    async def run(self, input: ProcessDocumentInput) -> None:
        await workflow.execute_activity(
            mark_job_running,
            MarkJobInput(job_id=input.job_id),
            start_to_close_timeout=SHORT_TIMEOUT,
            retry_policy=DEFAULT_RETRY,
        )

        try:
            extracted_text = ""
            summary = ""
            keywords: list[str] = []

            if "extract_text" in input.operations:
                result = await workflow.execute_activity(
                    extract_text,
                    ExtractTextInput(document_id=input.document_id),
                    start_to_close_timeout=SHORT_TIMEOUT,
                    retry_policy=DEFAULT_RETRY,
                )
                extracted_text = result.text

            if "generate_summary" in input.operations:
                text_to_summarize = extracted_text or f"Document {input.document_id}"
                result = await workflow.execute_activity(
                    generate_summary,
                    GenerateSummaryInput(text=text_to_summarize),
                    start_to_close_timeout=SHORT_TIMEOUT,
                    retry_policy=DEFAULT_RETRY,
                )
                summary = result.summary

            if "extract_keywords" in input.operations:
                text_for_keywords = extracted_text or f"Document {input.document_id}"
                result = await workflow.execute_activity(
                    extract_keywords,
                    ExtractKeywordsInput(text=text_for_keywords),
                    start_to_close_timeout=SHORT_TIMEOUT,
                    retry_policy=DEFAULT_RETRY,
                )
                keywords = result.keywords

            await workflow.execute_activity(
                store_results,
                StoreResultsInput(
                    job_id=input.job_id,
                    extracted_text=extracted_text,
                    summary=summary,
                    keywords=keywords,
                ),
                start_to_close_timeout=SHORT_TIMEOUT,
                retry_policy=DEFAULT_RETRY,
            )

        except ActivityError:
            await workflow.execute_activity(
                mark_job_failed,
                MarkJobInput(job_id=input.job_id),
                start_to_close_timeout=SHORT_TIMEOUT,
                retry_policy=DEFAULT_RETRY,
            )
            raise
