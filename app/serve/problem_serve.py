import os
import asyncio

from app.common.core.config import config
from app.schemas.problem_schemas import ProblemResponse, ExecuteResponse
from app.common.enums.common_enum import ExecuteState
from app.schemas.problem_schemas import ProblemResponse, RequestProblem, AddRequest, AddResponse
from app.common.models.users import User
from app.common.memroy_manger import memroy_manger
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import HTTPException, Depends
from app.common.exceptions import MCException
from app.common.enums.mongo_enum import MongoTable
from app.common.core.logger import get_logger
from app.common.enums.user_enum import UserRole
from app.common.mongodb import mongodb_manger
from app.common.models.mongo_problem import ProblemMG
from app.common.unity.unity import get_hash_id
from app.database_rep import problem_rep 

logger = get_logger(__name__)


def select_response(result):
    if result is None:
        result = []
    logger.info(result)
    response = ProblemResponse(
        size= len(result) or 0,
        content=result
    )
    return response

# 查
async def get_all_problem(user_role:int):
    try:
        user_role_name = UserRole(user_role)
    except Exception as e:
        raise e

    select_query = {}
    if user_role_name != UserRole.SUPERMAN:
        select_query['is_hide'] = False
    
    filter_query = {'hash_id':1, }

    result = await mongodb_manger.select_doc(MongoTable.PROBLEM.value, select_query, filter_query)
    
    logger.info(f'get problem id list: {result}')
    return select_response(result)

async def get_problem_specific_info(user_id:int,user_role:int,problem_id:str):
    try:
        user_role_name = UserRole(user_role)
    except Exception as e:
        raise e
    
    select_query = {
        '_id': problem_id
    }
    if user_role_name == UserRole.COMMON_USER:
        select_query['is_hide'] = False
    
    result =  await mongodb_manger.select_doc(MongoTable.PROBLEM.value, select_query)
    logger.info(f'user_id {user_id} query {problem_id} result {result}')
    return select_response(result)


async def del_problem(user_id:int, user_role:int, problem_id:str):
    # 进行权限校验，非超级用户不执行
    try:
        user_role_name = UserRole(user_role)
    except Exception as e:
        raise e
    
    if user_role_name != UserRole.SUPER_MAN:
        logger.warning(f'{user_id} try del problem {problem_id} but not super_man')
        # raise HTTPException(status_code=500, detail="Internal Server Error")
        return f'{user_id} try del problem {problem_id} but not super_man'
    
    query = {'_id':problem_id}

    result = await mongodb_manger.del_doc(query)

    return {'state':'ok','message':result}

async def write_problem_data(input_path,output_path,data:dict):
    try:
        with open(input_path,'w') as f:
            f.write(data['input'].replace('\r', ''))
        with open(output_path,'w') as f:
            f.write(data['output'].replace('\r', ''))
        return True,{
            'input_path': input_path,
            'output_path':output_path
        }
    except Exception as e:
        logger.error(f'Unexepected error: {e}')
        return False, None

async def insert_problem(new_problem:ProblemMG):
    """
    1. 属性入库
    2. 测试的数据，解包，写本地文件
    """
    try:
        logger.info(f'PROBLEM PATH IS {config.PROBLEM_DATA_PATH}')
        new_problem.hash_id = get_hash_id(new_problem.problemtitle)
        
        tasks_list = []
        
        for index,_ in enumerate(new_problem.data):
            last_input_path = config.PROBLEM_DATA_PATH + '/' +  new_problem.hash_id + '/' + str(index) + '.in'
            last_output_path = config.PROBLEM_DATA_PATH + '/' + new_problem.hash_id + '/' + str(index) + '.out'
            os.makedirs(os.path.dirname(last_input_path), exist_ok=True)
            os.makedirs(os.path.dirname(last_output_path), exist_ok=True)
            tasks_list.append(asyncio.create_task(write_problem_data(last_input_path,last_input_path,_)))
        
        # 清空数据
        new_problem.data = []
        # 写入失败的索引
        fail_list = []
        
        write_results = await asyncio.gather(*tasks_list)
        
        for index,(result, path_dict) in enumerate(write_results):
            if result:
                new_problem.data.append(path_dict)
            else:
                fail_list.append(index)
            pass

        res = await mongodb_manger.insert_doc(MongoTable.PROBLEM.value, [ProblemMG.model_dump_json()])
        if res == None:
            message = f'fail insert problem in mongodb'
            res = ExecuteResponse(
                state= ExecuteState.FAIL.value,
                message= message
            )
        else:
            message = f'success message: {res}'
            res = ExecuteResponse(
                state= ExecuteState.OK.value,
                message= message
            )
        
        return res
    
    except Exception as e:
        logger.error(f'Unexpected error: {e}')
        raise e

async def update_problem(new_problem:ProblemMG):
    """
    修改（hold）
    """
    
    pass

async def get_user_problem_status(user_id:int):
    data = await problem_rep.get_user_problem_status(user_id)
    if data == None or len(data) == 0:
        data = []
    
    return ProblemResponse(
        size=len(data),
        content=[x.problem_id for x in data]
    )

async def add_problem(new_problem: AddRequest, role):
    user_role =  UserRole(role)
    if user_role != UserRole.SUPERMAN:
        return AddResponse(
            code= 0,
            problem_id= ""
        )
    pass
