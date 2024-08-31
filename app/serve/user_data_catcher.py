import asyncio

from app.common.unity.http_client import AsyncHttpClient
from app.schemas.data_catcher_schemas import CfResponse
from app.common.enums.common_enum import ExecuteState
from app.common.core.logger import get_logger

logger = get_logger(__name__)


codeforce_api = {
    "contest_list": "https://codeforces.com/api/contest.list", # 获取比赛
    
    "user_rating": "https://codeforces.com/api/user.rating?handle={UserName}", # 获取用户 rating 变化列表

    "user_info" : "https://codeforces.com/api/user.info?handles={UserNameList}&checkHistoricHandles=true",

    "user_status": "https://codeforces.com/api/user.status?handle={UserName}&from={begin_submission_id}&count={end_submission_id}" # 获取用户的提交,
}


class UserDataCatcherCodeforces:
    
    async def request(self, url):
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
    

    async def api_cf_get_contest_list(self) -> CfResponse:
        url = codeforce_api["contest_list"]
        res = await self.request(url)
        return res

async def main():
    catcher = UserDataCatcherCodeforces()
    res = await catcher.api_cf_get_contest_list()
    print(res.status)
    print(res.result[0])
    res = await catcher.api_cf_get_user_info('wronganswerr')
    print(res.status)
    print(res.result)

if __name__ == "__main__":
    # python -m app.serve.user_data_catcher
    asyncio.run(main())
