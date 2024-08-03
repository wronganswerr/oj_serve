from app.command.database import database
from sqlalchemy import select, update, insert, delete, and_, or_, func, text, union_all
from app.command.models.users import User
from app.command.core.logger import get_logger

from app.command.memroy_manger import memroy_manger

logger = get_logger(__name__)



async def get_user_info(user_id:int):
    try:
        query = select(User).where(
            User.user_id == user_id
        )
        return await database.fetch_one(query)
    except Exception as e:
        logger.error(f"Unexpect error: {e}")

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
        return False
    

async def get_user_id_by_token(token:str):
    user_info = await memroy_manger.get_user_info_memory(token)
    if user_info:
        return user_info.user_id
    else:
        return None
