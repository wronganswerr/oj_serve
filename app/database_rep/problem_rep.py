from app.common.database import database
from sqlalchemy import select, update, insert, delete, and_, or_, func, text, union_all
from app.common.models.users import Status

from app.common.models.problem import CFProblem

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
    
async def block_insert_codeforce_problem(problem_list:list[CFProblem]):
    try:
        step = 1000
        begin = 0
        while begin < len(problem_list):
            query = insert(CFProblem).values(
                [
                    tmp.to_dict() for tmp in problem_list[begin:begin+step]
                ]
            )
            
            await database.execute(query)
            begin += step
    except Exception as e:
        logger.error(f'Unexpected error: {e}')
        return None
    
async def update_id_for_codeforce_problem(contest_id, index, _id):
    try:
        query = update(CFProblem).where(
            CFProblem.contest_id == contest_id,
            CFProblem.contest_index == index
        ).values(
            {"id_in_mongodb":_id}
        )
        return await database.execute(query)
    except Exception as e:
        logger.error(f'Unexpected error: {e}')
        return None

async def get_less_date_problem_codeforce(number:int)->list[CFProblem]:
    try:
        query = select(CFProblem).where(
            CFProblem.id_in_mongodb == None
        ).order_by(CFProblem.id.asc()).limit(number)
        return await database.fetch_all(query)
    except Exception as e:
        logger.error(f'Unexpected error: {e}')
        return None
        