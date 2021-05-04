from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from pydantic.dataclasses import dataclass

@dataclass
class Birth:
    year: int
    month: int
    day: int

class UserSchema(BaseModel):
    # 어떻게 유저데이터가 MongoDB에 저장할것인지 알려주는 규칙? 개념
    # ...은 이 필드가 필수임을 나타낸다. None으로 바꿔도 무방
    fullname: str = Field(...)
    email: EmailStr = Field(None)
    gender: str = Field(...)
    birth: Birth = Field(...)
    # gt(greater than)와 lt(less than)는 값이 1~9까지 세팅. 즉, 0, 10, 11 값은 에러 송출
    height: int = Field(...)
    weitht: int = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "fullname": "John Doe",
                "email": "jdoe@dankook.ac.kr",
                "gender": "male",
                "birth": {'year': 1994, 'month': 2, 'day': 16},
                "height": "171",
                "weitht": "75",
            }
        }


class UpdateUserModel(BaseModel):
    fullname: Optional[str]
    email: Optional[EmailStr]
    gender: Optional[str]
    birth: Optional[Birth]
    height: Optional[int]
    weitht: Optional[int]

    class Config:
        schema_extra = {
            "example": {
                "fullname": "Heeji Kim",
                "email": "jdoe@dankook.ac.kr",
                "gender": "female",
                "birth": {'year': 1997, 'month': 2, 'day': 22},
                "height": "160",
                "weitht": "54",
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