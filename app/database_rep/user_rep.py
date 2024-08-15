from app.common.database import database
from sqlalchemy import select, update, insert, delete, and_, or_, func, text, union_all
from app.common.models.users import User
from app.common.core.logger import get_logger

from app.common.memroy_manger import memroy_manger

logger = get_logger(__name__)



async def get_user_info(user_id:int):
    try:
        query = select(User).where(
            User.user_id == user_id
        )
        return await database.fetch_one(query)
    except Exception as e:
        logger.error(f"Unexpect error: {e}")
        raise e

async def add_new_user(new_user:User):
    try:
        query = insert(User).values(
            new_user.to_dict()
        )
        logger.notice(query)
        await database.execute(query)
        return True
    except Exception as e:
        logger.error(f"Unexpect error: {e}")
        raise e
    

async def get_user_id_by_token(token:str):
    user_info = await memroy_manger.get_user_info_memory(token)
    if user_info:
        return user_info.user_id
    else:
        return None

async def update_user_info(user_id, values:dict):
    try:
        query = update(User).where(
            User.user_id == user_id
        ).values(values)
        await database.execute(query)
        return True
    except Exception as e:
        logger.error(f'Unexpect error: {e}')
        raise e