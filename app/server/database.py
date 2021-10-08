import motor.motor_asyncio
from bson.objectid import ObjectId
from decouple import config
from datetime import datetime
import time
import pytz

MONGO_DETAILS = config('MONGO_DETAILS') # DB key 데이터를 가지고 온다.

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS) # mongoDB에 key값을 통해 접속

database = client.users    # 해당 클라이언트의 users라는 이름의 mongoDB 데이터베이스에 접속
user_collection = database.get_collection("users_collection") # users 콜렉션 내 users_collection 가지고 온다.
bcm_collection = database.get_collection("bcm_collection") # users 콜렉션 내 bcm_collection 가지고 온다.
physio_collection = database.get_collection("physio_collection") # users 콜렉션 내 physio_collection 가지고 온다.


def bcm_data_helper(bcm) -> dict: # bcm 데이터를 dictionary 형태로 반환.
    return {
        "id": str(bcm["_id"]),
        "userid": str(bcm['userid']),
        "datetime": str(bcm['datetime']),
        "bcmdata": bcm["bcmdata"],
        "gainPD1": bcm["gainPD1"],
        "gainPD2": bcm["gainPD2"],
        "gainPD3": bcm["gainPD3"],
    }

def user_helper(user) -> dict: # user 데이터를 dictionary 형태로 반환.
    return {
        "id": str(user["_id"]),
        "joined": str(user['joined']),
        "userid": user["userid"],
        "hashed_password": user["hashed_password"],
        "fullname": user["fullname"],
        "email": user["email"],
        "gender": user["gender"],
        "age": user["age"],
        "height": user["height"],
        "weight": user["weight"],
    }
def physio_data_helper(physio) -> dict: # phyiso 데이터를 dictionary 형태로 반환.
    return {
        "id": str(physio["_id"]),
        "userid": str(physio['userid']),
        "datetime": str(physio['datetime']),
        "time": physio["time"],
        
        "mua685": physio["mua685"],
        "mua785": physio["mua785"],
        "mua830": physio["mua830"],
        "mua850": physio["mua850"],
        "mua915": physio["mua915"],
        "mua975": physio["mua975"],
        "mus685": physio["mus685"],
        "mus785": physio["mus785"],
        "mus830": physio["mus830"],
        "mus850": physio["mus850"],
        "mus915": physio["mus915"],
        "mus975": physio["mus975"],

        "hbo2": physio["hbo2"],
        "hhb": physio["hhb"],
        "water": physio["water"],
        "fat": physio["fat"],
    }

# 모든 유저의 정보를 조회한다.
async def retrieve_users():
    users = []
    async for user in user_collection.find():
        users.append(user_helper(user))
    return users


# 회원가입한 유저의 정보 데이터를 데이터베이스에 추가한다.
async def add_user(user_data: dict) -> dict:
    s = datetime.now(pytz.timezone("Asia/Seoul")).strftime('%Y-%m-%d %H:%M:%S')
    user_data.update({'joined': s})
    user = await user_collection.insert_one(user_data)
    new_user = await user_collection.find_one({"_id": user.inserted_id})
    return user_helper(new_user)

# 유저의 MDCW로 측정 데이터를 데이터베이스에 추가한다.
async def add_bcm(bcm_data: dict) -> dict:
    s = datetime.now(pytz.timezone("Asia/Seoul")).strftime('%Y-%m-%d %H:%M:%S')
    bcm_data.update({'datetime': s})
    bcm = await bcm_collection.insert_one(bcm_data)
    new_bcm = await bcm_collection.find_one({"_id": bcm.inserted_id})
    return bcm_data_helper(new_bcm)

# 유저의 분석이 완료된 physio 데이터를 데이터베이스에 추가한다.
async def add_physio(physio_data: dict) -> dict:
    s = datetime.now(pytz.timezone("Asia/Seoul")).strftime('%Y-%m-%d %H:%M:%S')
    physio_data.update({'datetime': s})
    temp_physio = await physio_collection.insert_one(physio_data)
    new_physio = await physio_collection.find_one({"_id": temp_physio.inserted_id})
    return new_physio

# 유저의 MDCW로 측정된 데이터를 데이터베이스에 조회한다.
async def retrieve_users_bcm(userid: str) -> dict:
    user_bcm = bcm_collection.find({"userid": userid})
    all_user_bcm = []
    async for doc in user_bcm: 
        all_user_bcm.append(doc)
    if all_user_bcm:
        return bcm_data_helper(all_user_bcm[-1])

# 특정 유저의 분석이 완료된 phsio 데이터를 데이터베이스에 조회한다.
async def retrieve_users_physio(userid: str) -> dict:
    physio_cursor = physio_collection.find({"userid": userid}).sort("id", 1)
    all_user_physio = []
    async for doc in physio_cursor: 
        all_user_physio.append(doc)
    if all_user_physio:
        return physio_data_helper(all_user_physio[-1])
    
# 유저가 입력한 아이디와 비밀번호가 연결된 데이터베이스에서 일치하는지 확인한다.
async def retrieve_user(id: str) -> dict:
    user = await user_collection.find_one({"_id": ObjectId(id)})
    if user:
        return user_helper(user)

async def check_auth(user_data:dict)->dict:
    cursor = await user_collection.find_one({'userid': user_data['userid']})
    if user_data['hashed_password'] == cursor['hashed_password']:
        return True
    return False

# 유저데이터를 연결된 데이터베이스에서 수정한다.
async def update_user(id: str, data: dict):
    # Return false if an empty request body is sent.
    if len(data) < 1:
        return False
    user = await user_collection.find_one({"_id": ObjectId(id)})
    if user:
        updated_user = await user_collection.update_one(
            {"_id": ObjectId(id)}, {"$set": data}
        )
        if updated_user:
            return True
        return False


# 유저데이터를 연결된 데이터베이스에서 삭제한다.
async def delete_user(id: str):
    user = await user_collection.find_one({"_id": ObjectId(id)})
    if user:
        await user_collection.delete_one({"_id": ObjectId(id)})
        return True
