"""
Standard API response helpers.

All API responses follow this format:
{
    "success": true/false,
    "message": "...",
    "data": {},
    "meta": {},
    "request_id": "req_xxxxx"
}
"""
import uuid

from rest_framework.response import Response


def success_response(data=None, message="OK", meta=None, status=200):
    """Standard success response."""
    return Response({
        "success": True,
        "message": message,
        "data": data or {},
        "meta": meta or {},
        "request_id": f"req_{uuid.uuid4().hex[:12]}",
    }, status=status)


def error_response(message="Error", error_code="ERROR", status=400, data=None):
    """Standard error response."""
    return Response({
        "success": False,
        "message": message,
        "error": {"code": error_code},
        "data": data or {},
        "request_id": f"req_{uuid.uuid4().hex[:12]}",
    }, status=status)


def list_response(data, meta=None, message="OK"):
    """Standard list response with pagination meta."""
    return Response({
        "success": True,
        "message": message,
        "data": data,
        "meta": meta or {},
        "request_id": f"req_{uuid.uuid4().hex[:12]}",
    })
