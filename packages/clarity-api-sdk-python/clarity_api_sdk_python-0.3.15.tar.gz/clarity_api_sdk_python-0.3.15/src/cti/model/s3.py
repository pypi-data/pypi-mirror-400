"""Pydantic models for S3 operations."""

from pydantic import BaseModel


class Part(BaseModel):
    """Pydantic model for a part in a multipart upload.

    Notes:
        'Parts': [
          {
            'ETag': 'string',
            'PartNumber': 123
          },
        ]
    """

    ETag: str
    PartNumber: int


class PartPresignedURL(BaseModel):
    """Pydantic model for a presigned URL for a part in a multipart upload.

    Attributes:
        url: Presigned URL for the part.
    """

    url: str


class MultipartUploadStartResponse(BaseModel):
    """Pydantic model for the response of starting a multipart upload.

    Attributes:
        UploadId: ID for the initiated multipart upload.
        Key: Object key for which the multipart upload was initiated.
    """

    UploadId: str
    Key: str


class CompleteMultipartUploadBody(BaseModel):
    """Pydantic model for the body of a complete multipart upload request.

    Attributes:
        parts: A list of parts to be included in the multipart upload.
    """

    parts: list[Part]
