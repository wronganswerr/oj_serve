from app.command.database import database
from sqlalchemy import select, update, insert, delete, and_, or_, func, text, union_all
from app.command.models.users import User
from app.command.core.logger import get_logger

logger = get_logger(__name__)



async def get_user_info(user_id:int):
    try:
        query = select(User).where(
            User.user_id == user_id
        )
        await database.fetch_one(query)
    except Exception as e:
        logger.error(f"Unexpect error: {e}")

async def add_new_user(new_user:User):
    try:
        query = insert(User).values(
            new_user.to_dict()
        )
        await database.execute(query)
        return True
    except Exception as e:
        logger.error(f"Unexpect error: {e}")
        return False
    
