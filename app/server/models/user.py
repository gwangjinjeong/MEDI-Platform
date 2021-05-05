from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from enum import Enum


class Gender(str, Enum):
    male = 'male'
    female = 'female'
    other = 'other'
    not_given = 'not_given'

class UserSchema(BaseModel):
    # 어떻게 유저데이터가 MongoDB에 저장할것인지 알려주는 규칙? 개념
    # ...은 이 필드가 필수임을 나타낸다. None으로 바꿔도 무방
    username: str = Field(...)
    fullname: str = Field(...)
    email: EmailStr = Field(...)
    gender: Gender = Field(...)
    age: int = Field(...,gt=0,lt=100)
    height: int = Field(...)
    weight: int = Field(...)
    # gt(greater than)와 lt(less than)는 값이 1~9까지 세팅. 즉, 0, 10, 11 값은 에러 송출

class UserIn(UserSchema):
    password: str = Field(...)
    class Config:
        schema_extra = {
            "example": {
                "username": "abc123",
                "password": "loveme",
                "fullname": "John Doe",
                "email": "jdoe@dankook.ac.kr",
                "gender": "male",
                "age": 24,
                "height": 171,
                "weight": 75,
            }
        }
class UserOut(UserSchema):
    pass

class UserInDB(UserSchema):
    hashed_password: str
    class Config:
        schema_extra = {
            "example": {
                "username": "abc123",
                "hashed_password": "supersecretloveme",
                "fullname": "John Doe",
                "email": "jdoe@dankook.ac.kr",
                "gender": "male",
                "age": 24,
                "height": 171,
                "weight": 75,
            }
        }
class UpdateUserModel(BaseModel):
    username: Optional[str]
    password: Optional[str]
    fullname: Optional[str]  
    email: Optional[EmailStr]
    gender: Optional[str]
    birth: Optional[int]
    height: Optional[int]
    weitht: Optional[int]

    class Config:
        schema_extra = {
            "example": {
                "username": "dcf123",
                "password": "loveyou",
                "fullname": "John Doe",
                "email": "jdoe@dankook.ac.kr",
                "gender": "male",
                "age": 25,
                "height": 172,
                "weight": 75,
            }
        }


def ResponseModel(data, message):
    return {
        "data": [data],
        "code": 200,
        "message": message,
    }


def ErrorResponseModel(error, code, message):
    return {"error": error, "code": code, "message": message}