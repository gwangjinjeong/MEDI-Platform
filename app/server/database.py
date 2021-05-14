import motor.motor_asyncio
from bson.objectid import ObjectId
from decouple import config
from datetime import datetime
import time
import pytz

MONGO_DETAILS = config('MONGO_DETAILS')

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

database = client.users
# bcm_database = client.bcm
user_collection = database.get_collection("users_collection")
bcm_collection = database.get_collection("bcm_collection")

#

# helpers
def bcm_data_helper(bcm) -> dict:
    return {
        "id": str(bcm["_id"]),
        "userid": str(bcm['userid']),
        "datetime": str(bcm['datetime']),
        "bcmdata": bcm["bcmdata"],
    }

def user_helper(user) -> dict:
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
# Retrieve all users present in the database
async def retrieve_users():
    users = []
    async for user in user_collection.find():
        users.append(user_helper(user))
    return users


# Add a new user into to the database
async def add_user(user_data: dict) -> dict:
    s = datetime.now(pytz.timezone("Asia/Seoul")).strftime('%Y-%m-%d %H:%M:%S')
    user_data.update({'joined': s})
    user = await user_collection.insert_one(user_data)
    new_user = await user_collection.find_one({"_id": user.inserted_id})
    return user_helper(new_user)

# Add BCM data for each users
async def add_bcm(bcm_data: dict) -> dict:
    print(bcm_data)
    s = datetime.now(pytz.timezone("Asia/Seoul")).strftime('%Y-%m-%d %H:%M:%S')
    bcm_data.update({'datetime': s})
    bcm = await bcm_collection.insert_one(bcm_data)
    print('2')
    new_bcm = await bcm_collection.find_one({"_id": bcm.inserted_id})
    print('3')
    return bcm_data_helper(new_bcm)

# Retrieve a user with a matching ID
async def retrieve_user(id: str) -> dict:
    user = await user_collection.find_one({"_id": ObjectId(id)})
    if user:
        return user_helper(user)

async def check_auth(user_data:dict)->dict:
    # cursor = user_collection.find({'userid': user_data['userid']}).sort('userid')
    cursor = await user_collection.find_one({'userid': user_data['userid']})
    # for document in await cursor.to_list(length=100):
    #     print(document)
    if user_data['hashed_password'] == cursor['hashed_password']:
        return True
    return False


# async def duplicate_check(userid: str)->dict:
#     print(userid)
#     user = await user_collection.find_one({"userid": ObjectId(userid)})
#     if user:
#         return True
#     return False

# Update a user with a matching ID
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


# Delete a user from the database
async def delete_user(id: str):
    user = await user_collection.find_one({"_id": ObjectId(id)})
    if user:
        await user_collection.delete_one({"_id": ObjectId(id)})
        return True
