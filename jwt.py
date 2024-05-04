from jose import  jwt
from datetime import datetime, timedelta
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.responses import Response

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_jwt(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload['exp'] < datetime.utcnow().timestamp():
            return False
        return True
    except Exception as e:
        return False

class JWTMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Log all headers for debugging

        path_whitelist = ["/token",'/favicon.ico','/openapi.json','/']
        if not any([request.url.path == p for p in path_whitelist] ) and request.method != "OPTIONS" :
            authorization: str = request.headers.get('Authorization')
            if not authorization:
                return JSONResponse(status_code=403, content={"message": "Authorization header missing"})

            parts = authorization.split()
            if parts[0].lower() != "bearer" or len(parts) != 2:
                return JSONResponse(status_code=403, content={"message": "Invalid Authorization header format"})

            token = parts[1]
            if not verify_jwt(token):
                return JSONResponse(status_code=403, content={"message": "Invalid or expired token"})

        return await call_next(request)