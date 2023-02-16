from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from passlib.context import CryptContext
import mysql.connector as mysql
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

# Password hashing method
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Loading .env
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DATABASE = os.getenv("DB_DATABASE")


# Connecting database
def get_db():
    db = mysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_DATABASE,
    )
    return db


# User model
class User(BaseModel):
    username: str
    password: str


# Sign Up API
@app.post("/signup")
def signup(user: User):
    # Input validation
    if not user.username:
        raise HTTPException(status_code=400, detail={"success": False, "message": "Username is required"})
    if not user.password:
        raise HTTPException(status_code=400, detail={"success": False, "message": "Password is required"})
    # Check username length
    if len(user.username) < 3 or len(user.username) > 32:
        raise HTTPException(status_code=400, detail={"success": False, "message": "Username must be between 3 and 32 characters"})
    # Check password length and detail
    if len(user.password) < 8 or len(user.password) > 32:
        raise HTTPException(status_code=400, detail={"success": False, "message": "Password must be between 8 and 32 characters"})
    if not any(char.isupper() for char in user.password):
        raise HTTPException(status_code=400, detail={"success": False, "message": "Password must contain at least one uppercase letter"})
    if not any(char.islower() for char in user.password):
        raise HTTPException(status_code=400, detail={"success": False, "message": "Password must contain at least one lowercase letter"})
    if not any(char.isdigit() for char in user.password):
        raise HTTPException(status_code=400, detail={"success": False, "message": "Password must contain at least one number"})

    # Check if usernane exist
    db = get_db()
    cursor = db.cursor()
    query = "SELECT * FROM user WHERE username=%s"
    cursor.execute(query, (user.username,))
    result = cursor.fetchone()
    if result is not None:
        raise HTTPException(status_code=400, detail={"success": False, "message": "Username already exists"})
    # Hash password and store in database
    hashed_password = pwd_context.hash(user.password)
    query = "INSERT INTO user (username, password) VALUES (%s, %s)"
    values = (user.username, hashed_password)
    cursor.execute(query, values)
    db.commit()
    return {"success": True, "message": "Account created successfully"}


# Sign In API
@app.post("/signin")
def signin(user: User):
    # Input validation
    if not user.username:
        raise HTTPException(status_code=400, detail={"success": False, "message": "Username is required"})
    if not user.password:
        raise HTTPException(status_code=400, detail={"success": False, "message": "Password is required"})

    # Check if usernane not exist
    db = get_db()
    cursor = db.cursor()
    query = "SELECT * FROM user WHERE username=%s"
    cursor.execute(query, (user.username,))
    result = cursor.fetchone()
    if result is None:
        raise HTTPException(status_code=400, detail={"success": False, "message": "Username does not exist"})
    # Check if password is correct
    if not pwd_context.verify(user.password, result[2]):
        raise HTTPException(status_code=400, detail={"success": False, "message": "Password is incorrect"})
    return {"success": True, "message": "Sign in successfully"}