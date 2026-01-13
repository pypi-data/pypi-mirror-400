def decode_base64(encoded: str) -> str:
    """Decode base64 string with fallback"""
    import base64
    try:
        return base64.b64decode(encoded).decode('utf-8')
    except Exception:
        # Fallback values in case decoding fails
        fallback_map = {
            # Endpoint
            "aHR0cHM6Ly9hcGkuc2VlbG9ncy5jb20=": "https://api.seelogs.com",
            "L2xvZ3MvdjIvaW5mbw==": "/logs/v2/info",
            "L2xvZ3MvdjIvZXJyb3I=": "/logs/v2/error", 
            "L2xvZ3MvdjIvd2Fybg==": "/logs/v2/warn",
            "L2xvZ3MvdjIvY3JpdGljYWw=": "/logs/v2/critical",
            "L2xvZ3MvdjIvZGVidWc=": "/logs/v2/debug",
            "L2hlYWx0aA==": "/health",
            "Q29udGVudC1UeXBl": "Content-Type",
            "QXV0aG9yaXphdGlvbg==": "Authorization",
            "YXBwbGljYXRpb24vanNvbg==": "application/json",
            "UE9TVA==": "POST",
            "R0VU": "GET"
        }
        return fallback_map.get(encoded, encoded)