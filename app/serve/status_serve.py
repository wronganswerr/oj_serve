import os
import asyncio
import datetime
import shutil

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
from app.database_rep import user_rep
from app.common.enums.mongo_enum import MongoTable
from app.schemas.common_schemas import ListResponse

from app.actors.judge_process import process_judge_message

logger = get_logger(__name__)



async def get_user_info(user_id:int, user_rating:int, user_name:str)->dict:
    
    key = f'get_user_status|last_time|{user_id}'
    info_in_memory = await memroy_manger.similar_redis_query_key(key)
    if info_in_memory is not None:
        if info_in_memory["time"] + datetime.timedelta(hours=1) > datetime.datetime.now():
            return info_in_memory["content"]
    
    res = await mongodb_manger.select_doc(MongoTable.USER_STATUS.value,
                                          select_query={
                                              "user_id":user_id
                                          },
                                          sort_query={
                                              "id":-1
                                          })
    
    ac_problem_dict = dict() # problem: first_ac_time

    for stat in res:
        if stat["verdict"] == "OK":
            problem_key = f'{stat["problem"]["contestId"]}{ ["index"]}'
            if problem_key not in ac_problem_dict:
                ac_problem_dict[problem_key] = datetime.datetime.fromtimestamp(stat["creationTimeSeconds"])
            else:
                # 寻找最早的ac记录
                ac_problem_dict[problem_key] = min(datetime.datetime.fromtimestamp(stat["creationTimeSeconds"]), ac_problem_dict[problem_key])
    
    today_ac_num = 0
    this_week_ac_num = 0
    accumulate_ac_num = 0
    
    now = datetime.datetime.now()
    today = now.replace(hour=0,minute=0,second=0)

    weekday = today.weekday()
    days_to_monday = weekday
    monday = today - datetime.timedelta(days=days_to_monday)
    
    for problem_key, ac_time in ac_problem_dict.items():
        if ac_time >= monday:
            this_week_ac_num += 1
            if ac_time >= today:
                today_ac_num += 1
        accumulate_ac_num += 1
    
    user_info = {
        "user_name": user_name,
        "rating": user_rating,
        "solve_problem_today": today_ac_num,
        "solve_problem_this_week": this_week_ac_num,
        "solve_problem_total": accumulate_ac_num
    }

    await memroy_manger.similar_redis_set_key_value(key,{
        "time": now,
        "content": user_info
    })

    return user_info

    

async def user_rank_info()->ListResponse:
    user_list = await user_rep.get_have_cf_name_user_id()
    user_info_list = []
    for user in user_list:
        user_info_list.append(await get_user_info(user.user_id, user.codeforcesrating, user.name))
    
    return ListResponse(
        size= len(user_info_list),
        content= user_info_list
    )