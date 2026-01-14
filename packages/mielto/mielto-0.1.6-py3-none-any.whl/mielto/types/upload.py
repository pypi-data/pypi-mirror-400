"""Upload type definitions."""

from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, computed_field


class FileUpload(BaseModel):
    """Schema for file upload."""

    file: str = Field(..., description="Base64 encoded file content")
    label: str = Field(..., description="Filename/label for the file")
    mimetype: Optional[str] = Field(None, description="File MIME type")


class UploadRequest(BaseModel):
    """Request schema for uploading content."""

    collection_id: str = Field(..., description="ID of the collection to upload to")
    content_type: str = Field(default="file", description="Type of content - 'file', 'url', or 'text'")
    files: Optional[List[FileUpload]] = Field(None, description="List of files to upload (base64 encoded)")
    content: Optional[str] = Field(None, description="Direct text content to upload")
    urls: Optional[List[str]] = Field(None, description="List of URLs to download and upload")
    label: Optional[str] = Field(None, description="Custom label for the content")
    description: Optional[str] = Field(None, description="Description of the content")
    user_id: Optional[str] = Field(None, description="User ID for the upload")
    crawl: Optional[bool] = Field(False, description="Whether to crawl linked content from URLs")
    ingest: Optional[bool] = Field(True, description="Whether to ingest content into vector database")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata to attach")
    reader: Optional[Union[str, Dict[str, str]]] = Field(None, description="Reader configuration")


class ContentResult(BaseModel):
    """Individual content upload result."""

    id: Optional[str] = Field(None, description="Unique identifier for the content")
    name: str = Field(..., description="Name of the content")
    description: Optional[str] = Field(None, description="Description of the content")
    content: Optional[str] = Field(None, description="The actual text content")
    content_type: str = Field(..., description="Type of content (text, document, image, etc.)")
    type: Optional[str] = Field(None, description="Original file type/mimetype")
    size: Optional[int] = Field(None, description="Size of the content in bytes")
    url: Optional[str] = Field(None, description="Original URL if uploaded from URL")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    error: Optional[str] = Field(None, description="Error message if upload failed")


class UploadResponse(BaseModel):
    """
    Response schema for upload.
        Status values:
            - "success": All uploads succeeded
            - "failed": All uploads failed
            - "partial_success": Some succeeded, some failed
    """

    status: Literal["success", "failed", "partial_success"] = Field(
        ..., description="Overall status of the upload operation"
    )
    contents: List[ContentResult] = Field(
        default_factory=list, description="List of content results (both successful and failed)"
    )

    @computed_field
    @property
    def total_uploads(self) -> int:
        """Total number of uploads attempted."""
        return len(self.contents)

    @computed_field
    @property
    def successful_uploads(self) -> int:
        """Number of successful uploads."""
        return sum(1 for c in self.contents if not c.error)

    @computed_field
    @property
    def failed_uploads(self) -> int:
        """Number of failed uploads."""
        return sum(1 for c in self.contents if c.error)

    @computed_field
    @property
    def errors(self) -> List[ContentResult]:
        """List of failed uploads with error details."""
        return [c for c in self.contents if c.error]

    @computed_field
    @property
    def successful(self) -> List[ContentResult]:
        """List of successful uploads."""
        return [c for c in self.contents if not c.error]

    def is_success(self) -> bool:
        """Check if all uploads succeeded."""
        return self.status == "success"

    def has_failures(self) -> bool:
        """Check if any uploads failed."""
        return self.status in ["failed", "partial_success"]
