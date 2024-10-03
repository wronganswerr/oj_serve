import os
import asyncio
import datetime

from bson import ObjectId
from app.common.core.config import config
from app.common.enums.common_enum import ExecuteState, JudgeLanguage
from app.common.models.users import User
from app.common.memroy_manger import memroy_manger
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import HTTPException, Depends
from app.exceptions import MCException
from app.common.enums.mongo_enum import MongoTable
from app.common.core.logger import get_logger
from app.common.enums.user_enum import UserRole
from app.common.mongodb import mongodb_manger
from app.common.models.mongo_problem import ProblemMG, Example
from app.common.unity.unity import get_hash_id
from app.database_rep import problem_rep 
from app.schemas.problem_schemas import ProblemResponse, RequestProblem, AddRequest, AddResponse, ExecuteResponse, JudgeMessage
from app.actors.judge_process import process_judge_message

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
    
    filter_query = {'hash_id':1, 'problemtitle':1}

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
    
    if user_role_name != UserRole.SUPERMAN:
        logger.warning(f'{user_id} try del problem {problem_id} but not super_man')
        # raise HTTPException(status_code=500, detail="Internal Server Error")
        return ExecuteResponse(state= ExecuteState.FAILED.value,
                               message= f'{user_id} try del problem {problem_id} but not super_man')  
    
    query = {'_id': ObjectId(problem_id)}

    result = await mongodb_manger.del_doc(MongoTable.PROBLEM.value, query)
    
    result_message = f"Deleted count: {result.deleted_count}, Acknowledged: {result.acknowledged}"

    return  ExecuteResponse(state= ExecuteState.OK.value,
                            message= result_message) 

async def write_problem_data(input_path,output_path,data:Example):
    try:
        with open(input_path,'w') as f:
            f.write(data.input.replace('\r', ''))
        with open(output_path,'w') as f:
            f.write(data.output.replace('\r', ''))
        return True,Example(
            input= input_path,
            output= output_path
        )
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
        logger.info(f'created hash_id {new_problem.hash_id}')
        tasks_list = []
        logger.info(f"problem data: {new_problem.data}")
        for index,_ in enumerate(new_problem.data):
            last_input_path = config.PROBLEM_DATA_PATH + '/' +  new_problem.hash_id + '/' + str(index) + '.in'
            last_output_path = config.PROBLEM_DATA_PATH + '/' + new_problem.hash_id + '/' + str(index) + '.out'
            os.makedirs(os.path.dirname(last_input_path), exist_ok=True)
            os.makedirs(os.path.dirname(last_output_path), exist_ok=True)
            tasks_list.append(asyncio.create_task(write_problem_data(last_input_path,last_output_path,_)))
        
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

        res = await mongodb_manger.insert_doc(MongoTable.PROBLEM.value, [new_problem.dict()])
        if res == None:
            res = ExecuteResponse(
                state= ExecuteState.FAILED.value,
                message= ExecuteState.FAILED.name
            )
        else:
            res = ExecuteResponse(
                state= ExecuteState.OK.value,
                message= ExecuteState.OK.name
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

async def add_problem(new_problem_data: AddRequest, role):
    user_role =  UserRole(role)
    if user_role != UserRole.SUPERMAN:
        return ExecuteResponse(
            state=ExecuteState.FAILED.value,
            message="no permission"
        )
    
    new_problem = ProblemMG(
        problemtitle= new_problem_data.problem_title,
        timelimit= new_problem_data.time_limit,
        memorylimit= new_problem_data.memory_limit,
        problemmain= new_problem_data.problem_main,
        inputdescribe= new_problem_data.input_describe,
        outputdescribe= new_problem_data.output_describe,
        is_hide= new_problem_data.is_hide,
        example= new_problem_data.example,
        data= new_problem_data.data,
        hash_id=""
    )

    return await insert_problem(new_problem)

async def get_problem_detile(problem_id:str):

    filter_query = {'memorylimit': 1, 'timelimit': 1, 'problemtitle': 1,
                    'problemmain': 1, 'inputdescribe':1, 'outputdescribe': 1,
                    'example':1}
    select_query = {'_id': ObjectId(problem_id)}

    result = await mongodb_manger.select_doc(MongoTable.PROBLEM.value, select_query, filter_query)
    if len(result) <= 0:
        logger.error(f'id {problem_id} not exit')
        raise ValueError('id not exit')
    
    problem = result[0]
    
    # logger.info(f'get problem id list: {result}')

    return ProblemMG(**problem)


async def submit_problem(problem_id:int, user_id:int, code:str, language:str):
    try:
        try:
            language = JudgeLanguage(language)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return ExecuteResponse(state=0, message="language not been supported")
        
        judge_message = JudgeMessage(
            user_id= user_id,
            problem_id= problem_id,
            code=code,
            created_at= datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            online_oj_choose='waoj',
            language= language,
            search_id= '114514'
        )
        serialized_value = judge_message.model_dump_json(exclude_none=True, exclude_unset=True, by_alias=True)
        # python -m app.client.judge_test
        send_tasks = []
        send_tasks.append(
                        asyncio.to_thread(
                            lambda: process_judge_message.send(serialized_value)
                        )
                    )
        result= await asyncio.gather(*send_tasks)
        logger.info(f'success send message: {result}')
        return ExecuteResponse(state=1, message="IN QUEUE")
    except Exception as e:
        logger.error(f'Unexpected error: {e}')
        raise e
    
