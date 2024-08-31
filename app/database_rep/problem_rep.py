from app.common.database import database
from sqlalchemy import select, update, insert, delete, and_, or_, func, text, union_all
from app.common.models.users import Status
from app.common.core.logger import get_logger

logger = get_logger(__name__)
async def get_user_problem_status(user_id:int):
    try:
        query = select(Status.problem_id).where(
            Status.user_id == user_id,
            Status.verdict_id == 0,
        ).group_by(Status.problem_id)
        return await database.fetch_all(query)
    except Exception as e:
        logger.error(f'Unexpected error: {e}')
        return None