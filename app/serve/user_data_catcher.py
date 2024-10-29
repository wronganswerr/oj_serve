import asyncio
import json
from app.common.database import database


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

    async def request(self, url)->CfResponse:
        response = await AsyncHttpClient().request('GET',url=url,response_type="json")
        response = CfResponse(**response)
        if response.status == ExecuteState.FAILED.value:
            logger.error(f'request get FAILED')
            return None
        else:
            return response

    async def api_cf_get_user_info(self, user_cf_name_list: str) -> CfResponse:
        url = codeforce_api["user_info"].format(UserNameList= user_cf_name_list)
        res = await self.request(url)
        return res
    

    async def api_cf_get_user_status(self, user_cf_name:str) -> CfResponse:
        # 一次查询一千条
        # 定义一个 basemodel 构造返回的值
        # 直接入 mongo 库
        url = codeforce_api["user_status"].format(UserName= user_cf_name)
        begin = 1
        step = 1000
        while True:
            url = codeforce_api["user_status"].format(UserName= user_cf_name,begin_submission_id=begin,end_submission_id=begin+step-1)
            res = await self.request(url)
            if res is not None:
                if res.status == ExecuteState.OK.value:
                    if len(res.result) ==0:
                        break
                    else:

                        pass

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
            
            # codeforcessloved = await self.api_cf_get_user_status(user["codeforcesname"]) 

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
        # print(in_data)
        name_str = ""

        cf_name_index = dict()

        for index,info in enumerate(in_data):
            cf_name_index[info["codeforcesname"]] = index
        
        for user in in_data:
            name_str += user["codeforcesname"] + ';'
        # print(name_str)
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

    await database.connect()

    catcher = UserDataCatcherCodeforces()
    await catcher.get_user_cf_info()
    await catcher.update_info_into_db()
    
    await database.disconnect()


if __name__ == "__main__":
    # python -m app.serve.user_data_catcher
    asyncio.run(main())
