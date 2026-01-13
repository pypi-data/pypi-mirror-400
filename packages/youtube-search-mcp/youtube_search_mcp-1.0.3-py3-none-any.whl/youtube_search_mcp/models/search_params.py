"""Search parameter models using Pydantic."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SearchParams(BaseModel):
    """Parameters for YouTube video search."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": "python programming tutorial",
                "max_results": 10,
                "sort_by": "relevance",
            }
        }
    )

    query: str = Field(..., min_length=1, max_length=200, description="Search query string")
    max_results: int | None = Field(
        10, ge=1, le=50, description="Maximum number of results to return (1-50)"
    )
    sort_by: Literal["relevance", "upload_date", "view_count", "rating"] | None = Field(
        "relevance", description="Sort order for results"
    )
