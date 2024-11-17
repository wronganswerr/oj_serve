import asyncio
import json
import datetime
import time
import random

from app.common.database import database
from app.common.mongodb import mongodb_manger
from app.common.enums.mongo_enum import MongoTable

from app.common.unity.http_client import AsyncHttpClient
from app.schemas.data_catcher_schemas import CfResponse
from app.common.enums.common_enum import ExecuteState
from app.common.core.logger import get_logger
from app.common.models.users import User
from app.common.models.problem import CFProblem

from app.database_rep import user_rep
from app.database_rep import problem_rep
from app.serve.user_data_catcher import UserDataCatcherCodeforces
logger = get_logger(__name__)



async def main():
    now = datetime.datetime.now()
    try:
        await database.connect()

        catcher = UserDataCatcherCodeforces()


        await mongodb_manger.get_mongodb_connection()
        # await catcher.get_problem_list()
        need_prcess_problems = await problem_rep.get_less_date_problem_codeforce(1)
        for ned_problem in need_prcess_problems:
            # logger.error(f'claw html failed task stop!!! {ned_problem.contest_id} {ned_problem.contest_index}')
            # break
            logger.info(f'begin procee {ned_problem.contest_id} {ned_problem.contest_index}')
            try:
                if not await catcher.get_problem_detailed_info(ned_problem.contest_id,ned_problem.contest_index):
                    logger.error(f'claw html failed task stop!!! {ned_problem.contest_id} {ned_problem.contest_index}')
                    break
                probelm = await catcher.analysis_problem_html(ned_problem.contest_id,ned_problem.contest_index)
                await catcher.insert_new_problem(ned_problem.contest_id,ned_problem.contest_index,probelm)
                logger.info(f'problem {ned_problem.contest_id} {ned_problem.contest_index} success processed')
                time.sleep(random.randint(1,5))

            except Exception as e:
                logger.error(f'Unexpected error: {e}')
        await database.disconnect()


    except Exception as e:
        logger.error(f'yxn error: {e}',exc_info=True)
        print(e)
        # with open(f'{catcher.data_path}/log.out','a') as f:
        #     f.write(f'data_catcher;error;{now};{e};\n')

if __name__ == "__main__":
    # python -m app.client.user_data_catcher
    # nohup python -m app.client.user_data_catcher >> 1.out  2>&1 &
    asyncio.run(main())
