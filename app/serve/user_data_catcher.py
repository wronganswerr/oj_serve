import asyncio
import json
import datetime
from app.common.database import database
from app.common.mongodb import mongodb_manger
from app.common.enums.mongo_enum import MongoTable

from app.common.unity.http_client import AsyncHttpClient
from app.schemas.data_catcher_schemas import CfResponse
from app.common.enums.common_enum import ExecuteState
from app.common.core.logger import get_logger

from app.database_rep import user_rep
logger = get_logger(__name__)


codeforce_api = {
    "contest_list": "https://codeforces.com/api/contest.list", # 获取比赛
    
    "user_rating": "https://codeforces.com/api/user.rating?handle={UserName}", # 获取用户 rating 变化列表

    "user_info" : "https://codeforces.com/api/user.info?handles={UserNameList}&checkHistoricHandles=true",

    "user_status": "https://codeforces.com/api/user.status?handle={UserName}&from={begin_submission_id}&count={end_submission_id}" # 获取用户的提交,
}


class UserDataCatcherCodeforces:
    def __init__(self):
        self.data_path = './runtime/catcher_data'
        self.mongo_db = None
        self.httpclient = AsyncHttpClient()

    async def request(self, url)->CfResponse:
        response = await self.httpclient.request('GET',url=url,response_type="json")
        if response is None:
            raise RuntimeError('http request error')
        
        response = CfResponse(**response)
        if response.status == ExecuteState.FAILED.name:
            logger.error(f'request get FAILED')
            return None
        else:
            return response

    async def api_cf_get_user_info(self, user_cf_name_list: str) -> CfResponse:
        url = codeforce_api["user_info"].format(UserNameList= user_cf_name_list)
        res = await self.request(url)
        return res
    

    async def api_cf_get_user_status(self, user_id:int, user_cf_name:str) -> CfResponse:
        # 一次查询一千条
        # 直接入 mongo 库
        url = codeforce_api["user_status"]
        begin = 1
        step = 1000
        
        select_query = {
            "user_id": user_id
        }
        filter_query = {"id": 1}
        sort_query = {"id": -1}
        
        last_user_status_id = await mongodb_manger.select_doc(MongoTable.USER_STATUS.value, select_query, filter_query, sort_query, 1)
        
        if len(last_user_status_id)==0:
            last_user_status_id = -1
        else:
            last_user_status_id = last_user_status_id[0]["id"]
        print(user_cf_name, 'last_user_status_id', last_user_status_id)

        while True:
            url = codeforce_api["user_status"].format(UserName= user_cf_name,
                                                      begin_submission_id= begin,
                                                      end_submission_id= begin + step - 1)
            res = await self.request(url)
            if res is not None:
                if res.status == ExecuteState.OK.name:
                    if len(res.result) == 0:
                        break
                    else:
                        need_insert_list = []
                        for user_statu in res.result:
                            if user_statu["id"] > last_user_status_id:
                                user_statu["user_id"] = user_id
                                need_insert_list.append(user_statu)
                            else:
                                break
                        if len(need_insert_list) == 0:
                            break 
                        await mongodb_manger.insert_doc(MongoTable.USER_STATUS.value, need_insert_list)
                        print(user_cf_name, 'insert', len(need_insert_list))
                        begin += step
                else:
                    break
            else:
                break

            await asyncio.sleep(1)

    async def api_cf_get_contest_list(self) -> CfResponse:
        url = codeforce_api["contest_list"]
        res = await self.request(url)
        return res
    
    
    async def update_info_into_db(self):
        with open(f'{self.data_path}/test.1.json','r') as f:
            user_data = json.load(f)
        
        for user in user_data:
            if "user_id" not in user or True:
                res = await user_rep.get_user_id_with_user_name(user["WAOJ"])
                if res is not None:
                    user["user_id"] = res.user_id
                else:
                    continue

            await self.api_cf_get_user_status(user["user_id"], user["codeforcesname"]) 

            if "user_id" in user:
                res = await user_rep.update_user_info(user["user_id"],{
                    "codeforcesrating": user["codeforcesrating"],
                    "codeforcesname": user["codeforcesname"]
                })
            

        with open(f'{self.data_path}/test.1.json','w') as f:
            json.dump(user_data, f, ensure_ascii=False, indent=2)


    async def get_user_cf_info(self):
        with open(f'{self.data_path}/test.in.json','r') as f:
                in_data = json.load(f)

        name_str = ""

        cf_name_index = dict()

        for index,info in enumerate(in_data):
            cf_name_index[info["codeforcesname"]] = index
        
        for user in in_data:
            name_str += user["codeforcesname"] + ';'
        
        res = await self.api_cf_get_user_info(name_str)
        if res.status == 'OK':
            with open(f'{self.data_path}/test.json','w') as f:
                json.dump(res.model_dump(exclude_none=True), f, ensure_ascii=False, indent=2)
            
            for user_info in res.result:
                if user_info["handle"] in cf_name_index:
                    if "rating" in user_info:
                        in_data[cf_name_index[user_info["handle"]]]["codeforcesrating"] = user_info["rating"]
                    else:
                        in_data[cf_name_index[user_info["handle"]]]["codeforcesrating"] = 0
                else:
                    in_data[cf_name_index[user_info["handle"]]]["codeforcesrating"] = 0
            with open(f'{self.data_path}/test.1.json','w') as f:
                json.dump(in_data, f, ensure_ascii=False, indent=2)
    


async def main():
    now = datetime.datetime.now()
    try:
        await database.connect()

        catcher = UserDataCatcherCodeforces()

        await mongodb_manger.get_mongodb_connection()

        await catcher.get_user_cf_info()
        await catcher.update_info_into_db()

        # await catcher.api_cf_get_user_status(0,'wronganswerrr')

        await database.disconnect()

        with open(f'{catcher.data_path}/log.out','a') as f:
            f.write(f'data_catcher;success;{now};;\n')

    except Exception as e:
        with open(f'{catcher.data_path}/log.out','a') as f:
            f.write(f'data_catcher;error;{now};{e};\n')

if __name__ == "__main__":
    # python -m app.serve.user_data_catcher
    asyncio.run(main())
