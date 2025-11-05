# src/api/middleware.py

import time
from fastapi import Request, HTTPException, status

# A simple in-memory dictionary to store request timestamps
request_timestamps = {}

def rate_limit(limit: int = 10, per: int = 60):
    """
    A dependency for rate-limiting API endpoints.
    This is the modern FastAPI way to handle rate limiting.
    """
    def dependency(request: Request):
        # Use the user's IP address as a unique key
        key = f"rl_{request.client.host}"
        
        # Get the list of timestamps for this IP, or an empty list if none
        timestamps = request_timestamps.get(key, [])
        
        # Current time
        now = time.time()
        
        # Remove timestamps that are older than our time window ('per')
        in_window_timestamps = [t for t in timestamps if now - t < per]
        
        # If the number of requests in the window is already at the limit, block it
        if len(in_window_timestamps) >= limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many requests. Limit is {limit} per {per} seconds."
            )
        
        # Add the current request's timestamp to the list
        in_window_timestamps.append(now)
        request_timestamps[key] = in_window_timestamps
        
    return dependency