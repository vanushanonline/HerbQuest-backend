
from fastapi_sessions.backends.implementations import InMemoryBackend
from pydantic import BaseModel

class SessionData(BaseModel): 
    email: str

backend = InMemoryBackend[str, SessionData]()

async def create_session(email):
    if 'user' in backend.data:
        await backend.delete('user')
    await backend.create('user', SessionData(email=email))

def get_session():
    return backend.data['user'].email if 'user' in  backend.data else "Login"