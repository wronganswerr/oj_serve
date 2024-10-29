from app.common.database import database
from sqlalchemy import select, update, insert, delete, and_, or_, func, text, union_all, join,values
from app.common.models.users import User, Status
from app.common.core.logger import get_logger
from sqlalchemy.orm import aliased
from app.common.memroy_manger import memroy_manger

logger = get_logger(__name__)



async def get_user_info(user_id:int, phone_number: str= None):
    try:
        if phone_number is None:
            query = select(User).where(
                User.user_id == user_id,
            )
        else:
            query = select(User).where(
                or_(
                    User.user_id == user_id,
                    User.phone_number == phone_number
                )
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

# async def update_user_info(user_id, values:dict):
#     try:
#         query = update(User).where(
#             User.user_id == user_id
#         ).values(values)
#         await database.execute(query)
#         return True
#     except Exception as e:
#         logger.error(f'Unexpect error: {e}')
#         raise e
    
async def get_user_by_phone_number(phone_number:str):
    try:
        query = select(User).where(
            User.phone_number == phone_number
        )
        return await database.fetch_one(query)
    except Exception as e:
        logger.error(f'Unexpected error: {e}')
        raise e
    
async def get_user_status(_self, user_id, limit_l, limit_r) -> list[Status]:
    try:
        logger.info(f'{limit_l} {limit_r}')
        # user_alias = aliased(User)
        base_query = select(Status, User.name).select_from(
            join(Status, User, Status.user_id == User.user_id)
        )

        if _self:
            query = base_query.where(
                Status.user_id == user_id,
            ).order_by(Status.when.desc()).limit(limit_r-limit_l+1).offset(limit_l-1)
        else:
            query = base_query.order_by(Status.when.desc()).limit(limit_r-limit_l+1).offset(limit_l-1)
        
        data = await database.fetch_all(query)
        logger.debug(f'sql: {query}, res: {data}')
        return data

    except Exception as e:
        logger.error(f'Unexpected error: {e}', exc_info=True)
        raise e

async def get_user_status_total_number(_self, user_id) -> int:
    try:
        if _self:
            query = f"SELECT COUNT(*) FROM status WHERE user_id = {user_id}"
        else:
            query = "SELECT COUNT(*) FROM status"
        
        data = await database.fetch_one(query)
        logger.debug(f'sql: {query}, res: {data}')
        
        return data[0]

    except Exception as e:
        logger.error(f'Unexpected error: {e}', exc_info=True)
        raise e

async def get_user_id_with_user_name(user_name:str)->User:
    try:
        query = select(User.user_id).where(
            User.name == user_name
        )
        result = await database.fetch_one(query)
        logger.debug(f'sql: {query}, res: {result}')
        return result
    
    except Exception as e:
        logger.error(f'Unexpected error: {e}', exc_info=True)
        raise e

async def update_user_info(user_id: int, value:dict):
    try:
        query = update(User).where(
            User.user_id == user_id
        ).values(
            **value
        )
        res = await database.execute(query)
        logger.debug(f'sql: {query}, res: {res}')

    except Exception as e:
        logger.error(f'Unexpected error: {e}', exc_info=True)
        raise e