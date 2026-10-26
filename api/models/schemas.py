from pydantic import BaseModel, HttpUrl, Field


class RecoveryRequest(BaseModel):
    url: HttpUrl
    failed_locator: str = Field(
        ...,
        min_length=1,
        description="The locator that failed in the browser"
    )


class RecoveryResponse(BaseModel):
    success: bool
    message: str
    old_locator: str
    new_locator: str | None = None
    browser_validation: dict | None = None