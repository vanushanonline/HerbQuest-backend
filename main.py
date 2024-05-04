from fastapi import FastAPI, HTTPException,UploadFile,BackgroundTasks
from database import (
    get_user_collection, User,
    store_image_metadata, update_processing_time, 
    store_plant_data
)
from fastapi.middleware.cors import CORSMiddleware
from datetime import  timedelta, datetime
from jwt import create_access_token,JWTMiddleware
from logger import log
import bcrypt
from session import create_session, get_session
import cv2
import numpy as np
from model import model

app = FastAPI(docs_url="/")

# CORS settings
origins = [
    "http://localhost:3000",  # Add other origins as needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows specified origins to make requests
    allow_credentials=True,  # Allows cookies to be submitted across domains
    allow_methods=["*"],  # Allows all methods (GET, POST, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)
app.add_middleware(JWTMiddleware)

store_plant_data()

@app.post("/process")
async def process(file: UploadFile, background_tasks: BackgroundTasks):
    userID= None
    try:
       
        userID = get_session()

        file_size = file.size  # This gets the size of the file in bytes
        file.file.seek(0)
        
        contents = await file.read()
        nparr = np.fromstring(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        upload_timestamp = datetime.utcnow()
        file_type = file.content_type

        image_id = store_image_metadata(upload_timestamp, None, file_size, file_type,userID)

        start_time = datetime.now()

        result = model(img)
        
        end_time = datetime.now()
        processing_time = end_time - start_time
        
        def update_db():
            update_processing_time(image_id, processing_time)
        background_tasks.add_task(update_db)

        
        if result:
            response = {"status": 0,"message": f'Leaf identified as {result['name']}' , "data":result}
        else: 
            response = {"status": 1,"message": "Unable to identify the leaf"}
        return response

    except Exception as e:
        if hasattr(e,'detail'):
            error_message = f"Unexpected error: {str(e.detail)}"
        else:
            error_message = f"Unexpected error: {str(e)}"
        log(error_message)
        raise HTTPException(status_code=500, detail=error_message)  # Internal Server Error

@app.get("/token")
async def generate_token():
    token_data = {"sub": 'jwt_token'} 
    access_token = create_access_token(
        data=token_data,
        expires_delta=timedelta(minutes=60)  
    )
    return {"access_token": access_token, "token_type": "bearer"}
    
@app.post("/login")
async def login(user: User):
    user_collection = get_user_collection()
    found_user = user_collection.find_one({"email": user.email})
    
    if not found_user or not bcrypt.checkpw(user.password.encode('utf-8'), found_user['password'].encode('utf-8')):
        return {"status": 1, "message": "Invalid login credentials supplied"}
   
    access_token_expires = timedelta(minutes=5)
    access_token = create_access_token( data={"sub": user.email}, expires_delta=access_token_expires )
    await create_session(user.email)

    return {"status": 0,"message": "Login success" ,"access_token": access_token, "token_type": "bearer"}

@app.post("/register")
async def register(user: User):
    user_collection = get_user_collection()
    if user_collection.find_one({"email": user.email}):
        return {"status":1,"message": "Email already registered"}
    
    # Hash the password
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    user_dict = user.dict()
    user_dict['password'] = hashed_password.decode('utf-8')  # Store the hashed password as a string

    user_collection.insert_one(user_dict)
    return {"status":0, "message": "User registered successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)