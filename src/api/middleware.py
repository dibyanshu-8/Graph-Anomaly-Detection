# src/api/middleware.py

import time
from functools import wraps
from flask import request, abort

# A simple in-memory dictionary to store request timestamps
# In a production system, you'd use something more robust like Redis
request_timestamps = {}

def rate_limit(limit: int = 5, per: int = 60):
    """
    A rate-limiting decorator.

    :param limit: The number of allowed requests.
    :param per: The time window in seconds.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Use the user's IP address as a unique key
            key = f"rl_{request.remote_addr}"
            
            # Get the list of timestamps for this IP, or an empty list if none
            timestamps = request_timestamps.get(key, [])
            
            # Current time
            now = time.time()
            
            # Remove timestamps that are older than our time window ('per')
            # This is a list comprehension that builds a new list
            in_window_timestamps = [t for t in timestamps if now - t < per]
            
            # If the number of requests in the window is already at the limit, block it
            if len(in_window_timestamps) >= limit:
                # 429 is the HTTP status code for "Too Many Requests"
                abort(429)
            
            # Add the current request's timestamp to the list
            in_window_timestamps.append(now)
            request_timestamps[key] = in_window_timestamps
            
            # If we're not rate-limited, run the original function (e.g., the API endpoint)
            return f(*args, **kwargs)
            
        return decorated_function
    return decorator