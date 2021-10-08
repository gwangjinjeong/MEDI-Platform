from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from enum import Enum
from typing import List


class Gender(str, Enum): # Gender에 들어갈수있는 종류 4개 미리 선언
    male = 'male'
    female = 'female'
    other = 'other'
    not_given = 'not_given'

class UserSchema(BaseModel):
    # 앱으로부터 받은 유저데이터가 MongoDB에 저장할것인지 알려주는 스키마
    # ...은 이 필드가 필수임을 나타낸다. None으로 바꿔도 무방
    userid: str = Field(...)
    fullname: str = Field(...)
    email: EmailStr = Field(...)
    gender: Gender = Field(...)
    age: int = Field(...,gt=0,lt=100)   # gt(greater than)와 lt(less than)는 값이 1~9까지 세팅. 즉, 0, 10, 11 값은 에러 송출
    height: int = Field(...)
    weight: int = Field(...)
        
class UserBCM(BaseModel):
    # 앱으로부터 받은 MDCW의 측정데이터가 MongoDB에 저장할것인지 알려주는 스키마
    userid: str = Field(...) # 매치시킬것은 ID로 하자
    bcmdata: str = Field(...)      # bcm은 T를 제외한 값들 64byte인가를 받자.
    gainPD1: float = Field(...) 
    gainPD2: float = Field(...)
    gainPD3: float = Field(...)
    class Config:            # 입력되는 데이터가 어떠한 형식으로 되야하는지에 대한 예시
        schema_extra = {
            "example": {
                "userid": "gwangjin",
                "bcmdata": "T00DF039600F4h399F087B0C6Bh2310058E0730h2530072909C9h083D01EE0005h1E6F0106000D\nT1DBE07380B09h274808060B9Bh2341056F060Fh2493071909B7h0894021B03B1h1E9700F10089\nT1DC207610A0Fh271407FC0C00h22BF059F0673h247D06F90A28h0842020A0386h1E8500E10186\nT1DC407980B47h265907DA0BFDh229A054D0741h2518073009E9h08AC02240142h1E7B00D800E4\nT1DC407B60BB6h25E208130AE0h21EB055C05B9h249B06B80AA1h098603200119h1F8300FA0021\nT1DCB07710B04h272B07F60C15h232405AC06DFh23EA06FB0B0Fh096502640433h1ED201090180\nT1DCC07500BA6h2789081A0BCBh22B305490779h250907650AAEh08BC02990322h1ECA00E400FF\nT1DC1076C0B72h272708120AA7h22AC05BC06B6h249407070A6Eh08FE02120084h1F25010F0195\nT1DC507150AA3h273D08480AD9h21CC057D0742h248706B50AA2h09C0035101B7h1F6800F0017B\n",
                "gainPD1": 10.832,
                "gainPD2": 94.15,
                "gainPD3": 119.391
}
        }
class UserPhysio(BaseModel):
    # 서버내에서 인공지능으로 예측한 결과 분석데이터가 MongoDB에 저장할것인지 알려주는 스키마
    
    time: List[float] = Field(...)
    mua685: List[float] = Field(...)      
    mua785: List[float] = Field(...)   
    mua830: List[float] = Field(...)      
    mua850: List[float] = Field(...)      
    mua915: List[float] = Field(...)      
    mua975: List[float] = Field(...)      
    mus685: List[float] = Field(...)
    mus785: List[float] = Field(...)
    mus830: List[float] = Field(...)
    mus850: List[float] = Field(...)
    mus915: List[float] = Field(...)
    mus975: List[float] = Field(...)        
    hbo2: List[float] = Field(...)
    hhb: List[float] = Field(...)
    fat: List[float] = Field(...)
    water: List[float] = Field(...)
    class Config:  # 입력되는 데이터가 어떠한 형식으로 되야하는지에 대한 예시
        schema_extra = {
            "example": {
                "userid": "gwangjin",
                "time":[1,2],
                "mua685": [8.42641683, 1.22293563],
                "mua785": [7.08869255, 1.62395152],
                "mua830": [7.43068556, 1.67743087],
                "mua850": [6.29488418 ,0.93608081],
                "mua915": [6.90653301, 1.6422445 ],
                "mua975": [6.90653301, 1.6422445 ],      
                "mus685": [6.90653301, 1.6422445 ],
                "mus785": [6.90653301, 1.6422445 ],
                "mus830": [6.90653301, 1.6422445 ],
                "mus850": [6.90653301, 1.6422445 ],
                "mus915": [6.90653301, 1.6422445 ],
                "mus975": [6.90653301, 1.6422445 ],
                "hbo2": [6.90653301, 1.6422445 ],
                "hhb": [6.90653301, 1.6422445 ],
                "fat": [6.90653301 ,1.6422445 ],
                "water": [6.90653301 ,1.6422445 ],
                }
        }
class UserIn(UserSchema):
    # 앱으로부터 받은 유저데이터가 서버내에서 어떻게 처리될지 알려주는 스키마 여기서는 password 필드를 추가해서 보여준다.
    password: str = Field(...)
    class Config:
        schema_extra = {
            "example": {
                "userid": "abc123",
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
    # 앱으로부터 받은 유저데이터가 MongoDB에 저장될때는 hash함수로 암호화되어 hase_password로 저장시킨다.
    hashed_password: str
    class Config:
        schema_extra = {
            "example": {
                "userid": "abc123",
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
    # 앱으로부터 유저데이터 수정을 요청했을때 받는 서버에서 받을 수 있는 형식
    userid: Optional[str]
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
                "userid": "dcf123",
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
    # 앱에서 호출한 결과를 반환해주는 함수 성공적으로 했을때, 아래와 같다.
    return {
        "data": [data],
        "code": 200,
        "message": message,
    }
def ResponseModelForBCM(data, message):
    # 앱에서 호출한 결과를 반환해주는 함수 성공적으로 했을때, 아래와 같다.
    return {
        "data": data,
        "code": 200,
        "message": message,
    }

def ErrorResponseModel(error, code, message):
    # 앱에서 호출한 결과를 반환해주는 함수 실패로 되었을때, 아래와 같다.
    return {"error": error, "code": code, "message": message}