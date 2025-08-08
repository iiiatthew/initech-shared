import json
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse

from app import crud
from app.api import deps
from app.schemas.activity import ActivityCreate


class APIActivityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Only track API calls
        if not request.url.path.startswith('/api/'):
            return await call_next(request)

        # Get token from request if present
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token_value = auth_header.split(' ')[1]
            # Get db session
            db = next(deps.get_db())
            try:
                db_token = crud.token.get_by_token(db, token=token_value)
                if db_token:
                    token = db_token
            finally:
                db.close()

        # If no valid token, just proceed without tracking
        if not token:
            return await call_next(request)

        # Capture request data
        request_body = None
        if request.method in ['POST', 'PUT', 'PATCH']:
            body = await request.body()
            if body:
                try:
                    request_body = json.dumps(json.loads(body))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    request_body = body.decode('utf-8', errors='replace')
            # Need to recreate the request with the body we read
            request._body = body

        # Process the request
        response = await call_next(request)

        # Capture response data
        response_body = None
        response_status = response.status_code

        # Capture response body for JSON responses
        if hasattr(response, 'body'):
            try:
                if response.headers.get('content-type', '').startswith('application/json'):
                    response_body = response.body.decode('utf-8')
                elif len(response.body) < 1000:  # Only capture small non-JSON responses
                    response_body = response.body.decode('utf-8', errors='replace')[:500]
            except Exception:
                response_body = None
        elif isinstance(response, StreamingResponse):
            # For streaming responses, we can't easily capture the body
            response_body = '[Streaming Response]'

        # Log the activity
        db = next(deps.get_db())
        try:
            activity = ActivityCreate(
                endpoint=f'{request.method} {request.url.path}',
                request=request_body,
                response=response_body,
                status_code=response_status,
                token_id=token.id,
            )
            crud.activity.create(db, obj_in=activity)
        finally:
            db.close()

        return response
