import requests
from django.conf import settings


# Headers that must not be forwarded between client and upstream (RFC 7230 §6.1)
# plus Authorization (we replace it) and Host (requests sets it from URL).
HOP_BY_HOP = {
    "connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
    "te", "trailers", "transfer-encoding", "upgrade",
    "host", "content-length", "authorization", "cookie",
}

# Headers we don't want to leak back from Orthanc to the browser
RESPONSE_STRIP = {
    "connection", "keep-alive", "transfer-encoding", "upgrade",
    "www-authenticate",   # don't trigger browser Basic Auth dialog
    "server",             # don't reveal "Orthanc" version to the browser
}


class PACSClient:
    """Thin pass-through proxy to Orthanc with server-side auth injection."""

    BASE_URL  = settings.PACS_PRIVATE_URL.rstrip("/")
    USER      = settings.PACS_USER
    PASSWORD  = settings.PACS_PASSWORD
    TIMEOUT   = settings.PACS_TIMEOUT

    def __init__(self):
        # Connection pool, reused across requests
        self.session = requests.Session()
        self.session.auth = (self.USER, self.PASSWORD)

    def proxy(self, method, path, *, query_string=b"", headers=None, body=None):
        """
        Forward a request to Orthanc and return a streaming response object.
        Caller is responsible for streaming the body to the client.
        """
        print("@!#@!#@!#@!")
        url = f"{self.BASE_URL}/{path.lstrip('/')}"
        if query_string:
            url = f"{url}?{query_string.decode('latin-1') if isinstance(query_string, bytes) else query_string}"

        # upstream_headers = {
        #     k: v for k, v in (headers or {}).items()
        #     if k.lower() not in HOP_BY_HOP
        # }
        # print(upstream_headers)
        print(self.session.auth)
        return self.session.request(
            method=method,
            url=url,
            # headers=upstream_headers,
            data=body,
            stream=True,             # don't buffer response body
            timeout=self.TIMEOUT,
            allow_redirects=False,
        )


# Module-level singleton — Session reuses connections across requests
pacs_client = PACSClient()