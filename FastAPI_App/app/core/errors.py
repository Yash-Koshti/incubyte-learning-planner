from fastapi import Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    def __init__(self, code: str, message: str, status_code: int) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code


class DocumentNotFoundError(AppError):
    def __init__(self, document_id: object) -> None:
        super().__init__(
            code="DOCUMENT_NOT_FOUND",
            message=f"Document {document_id} does not exist",
            status_code=404,
        )


class JobNotFoundError(AppError):
    def __init__(self, job_id: object) -> None:
        super().__init__(
            code="JOB_NOT_FOUND",
            message=f"Job {job_id} does not exist",
            status_code=404,
        )


class JobNotCompletedError(AppError):
    def __init__(self, job_id: object, current_status: str) -> None:
        super().__init__(
            code="JOB_NOT_COMPLETED",
            message=f"Job {job_id} is not completed yet (status: {current_status})",
            status_code=409,
        )


class UnsupportedFileTypeError(AppError):
    def __init__(self, suffix: str) -> None:
        super().__init__(
            code="UNSUPPORTED_FILE_TYPE",
            message=f"File type '{suffix}' is not supported",
            status_code=422,
        )


class UnsupportedOperationError(AppError):
    def __init__(self, invalid: set) -> None:
        super().__init__(
            code="UNSUPPORTED_OPERATION",
            message=f"Unsupported operations: {invalid}",
            status_code=422,
        )


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message}},
    )


class InvalidTitleError(AppError):
    def __init__(self) -> None:
        super().__init__(
            code="INVALID_TITLE",
            message="Title cannot be empty",
            status_code=422,
        )
