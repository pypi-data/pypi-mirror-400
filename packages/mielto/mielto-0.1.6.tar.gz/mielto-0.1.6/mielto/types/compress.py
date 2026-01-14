"""Compress type definitions."""

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class CompressRequest(BaseModel):
    """Request schema for text compression."""

    content: Union[str, List[Dict[str, Any]]] = Field(..., description="Content to compress")
    strategy: Optional[str] = Field("ai_compress", description="Compression strategy")
    include_metadata: Optional[bool] = Field(False, description="Include metadata in compression")
    webhook_url: Optional[str] = Field(None, description="Webhook URL for async results")


class CompressResponse(BaseModel):
    """Response schema for text compression."""

    status: str = Field(..., description="Status of the compression")
    content: Optional[str] = Field(None, description="Compressed content")
    compression_time: Optional[float] = Field(None, description="Time taken for compression")
    original_length: Optional[int] = Field(None, description="Original content length")
    compressed_length: Optional[int] = Field(None, description="Compressed content length")
    message: Optional[str] = Field(None, description="Optional message")
