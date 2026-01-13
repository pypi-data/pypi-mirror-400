from functools import wraps
from fastapi import HTTPException
import magic

DEFAULT_ALLOWED_MIME_TYPES = (
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "application/pdf",
    "application/msword",
    "application/x-ole-storage",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "text/plain",
    "text/csv",
    "audio/mpeg",
    "audio/wav",
    "audio/mp3",
)


def get_mime_type(fileobj) -> str:
    """
    Detects the real MIME type of a file based on its content (magic bytes),
    not the client-provided extension or Content-Type header.
    """
    try:
        fileobj.seek(0)
        sample = fileobj.read(2048)
        fileobj.seek(0)
        m = magic.Magic(mime=True)
        mime = m.from_buffer(sample)
        return mime or "application/octet-stream"
    except Exception:
        return "application/octet-stream"


def validate_file_type(fileobj, allowed_mimes=None):
    """
    Validates the uploaded file’s real MIME type against the allowed list.
    """
    allowed_mimes = allowed_mimes or DEFAULT_ALLOWED_MIME_TYPES
    mime = get_mime_type(fileobj)
    if mime not in allowed_mimes:
        raise ValueError(f"نوع فایل مجاز نیست: {mime}")
    return mime


def is_upload_file(obj):
    return (
        hasattr(obj, "file") and
        hasattr(obj, "filename") and
        callable(getattr(obj.file, "read", None)) and
        callable(getattr(obj.file, "seek", None))
    )


def validate_upload_file(allowed_mimes=None):
    allowed_mimes = allowed_mimes or DEFAULT_ALLOWED_MIME_TYPES

    def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                for value in list(args) + list(kwargs.values()):
                    if is_upload_file(value):
                        try:
                            validate_file_type(value.file, allowed_mimes)
                        except ValueError as e:
                            raise HTTPException(status_code=400, detail=str(e))
                    elif isinstance(value, list):
                        for f in value:
                            if is_upload_file(f):
                                try:
                                    validate_file_type(f.file, allowed_mimes)
                                except ValueError as e:
                                    raise HTTPException(status_code=400, detail=str(e))
                return await func(*args, **kwargs)
            return wrapper
    return decorator
