from django.http import StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from core.pacs.pacs_integrations import RESPONSE_STRIP
from rest_framework.decorators import permission_classes, authentication_classes, api_view

from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.pacs.pacs_integrations import pacs_client

ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"]
CHUNK_SIZE = 64 * 1024

@csrf_exempt
@api_view(ALLOWED_METHODS)  # This makes it a DRF function-based view
@authentication_classes([JWTAuthentication])  # Explicitly use JWT authentication
@permission_classes([IsAuthenticated])  # Enforce authentication
def pacs_proxy(request, path):
    print(request.user)
    # Reconstruct headers from Django's META
    incoming_headers = {}
    for key, value in request.META.items():
        if key.startswith("HTTP_"):
            header_name = key[5:].replace("_", "-").title()
            incoming_headers[header_name] = value
        elif key in ("CONTENT_TYPE", "CONTENT_LENGTH") and value:
            header_name = key.replace("_", "-").title()
            incoming_headers[header_name] = value

    # Forward
    print(incoming_headers)
    upstream = pacs_client.proxy(
        method=request.method,
        path=path,
        query_string=request.META.get("QUERY_STRING", ""),
        headers=incoming_headers,
        body=request.body if request.method in ("POST", "PUT", "PATCH") else None,
    )

    # Stream the response back to the client
    response = StreamingHttpResponse(
        streaming_content=upstream.iter_content(chunk_size=CHUNK_SIZE),
        status=upstream.status_code,
    )

    # Pass through useful headers
    for header, value in upstream.headers.items():
        if header.lower() not in RESPONSE_STRIP:
            response[header] = value

    return response