import asyncio
import json
import datetime
import os
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
from app.common.models.mongo_problem import ProblemMG,Example

from app.database_rep import user_rep
from app.database_rep import problem_rep

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from bs4 import Tag

from app.common.unity.unity import get_hash_id


logger = get_logger(__name__)


codeforce_api = {
    "contest_list": "https://codeforces.com/api/contest.list", # 获取比赛
    
    "user_rating": "https://codeforces.com/api/user.rating?handle={UserName}", # 获取用户 rating 变化列表

    "user_info" : "https://codeforces.com/api/user.info?handles={UserNameList}&checkHistoricHandles=true",

    "user_status": "https://codeforces.com/api/user.status?handle={UserName}&from={begin_submission_id}&count={end_submission_id}", # 获取用户的提交,

    "problem_list": "https://codeforces.com/api/problemset.problems",

    "problem_detailed_info": "https://codeforces.com/problemset/problem/{ContestId}/{Index}",

}


headers_list = [
    {
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"
    }
]

def get_x_ele(gen,index) -> str:
    while index:
        text = next(gen)
        index-=1
    return text

ignore_id_class_list = ['MathJax_Preview','MathJax','MJX_Assistive_MathML',
                        'MJX-TeXAtom-ORD','math','mrow','mn',
                        'input-output-copier']
ignore_name_list = ['nobr','math','mn','mo','mi']

class UserDataCatcherCodeforces:
    def __init__(self):
        self.data_path = './runtime/catcher_data'
        self.problem_html_dir = 'problem_html'
        self.mongo_db = None
        self.httpclient = AsyncHttpClient()
        self.user:list[User] = []
    
    def human_like_delay(self):
        time.sleep(random.uniform(1, 3))

    def simulate_human_behavior(self,driver):
        actions = ActionChains(driver)
        # 模拟鼠标移动到某个位置
        actions.move_by_offset(random.randint(0, 100), random.randint(0, 100)).perform()
        self.human_like_delay()
        # 模拟点击
        actions.click().perform()
        self.human_like_delay()

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

    async def request_text(self, url)->CfResponse:
        response = await self.httpclient.request('GET',url=url,response_type="text",headers=
                                                 {
                                                     
                                                 })
        if response is None:
            raise RuntimeError('http request error')
        
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
                            if "verdict" not in user_statu:
                                # 还未有结果的记录 当次更新失效
                                need_insert_list.clear()
                                break
                            if user_statu["id"] > last_user_status_id:
                                user_statu["user_id"] = user_id
                                need_insert_list.append(user_statu)
                            else:
                                break
                        if len(need_insert_list) == 0:
                            break 
                        if len(need_insert_list) > 0:
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
        for user in self.user:
            await self.api_cf_get_user_status(user.user_id, user.codeforcesname)
            print(user.codeforcesname, user.codeforcesrating)
            res = await user_rep.update_user_info(user.user_id,{
                    "codeforcesrating": user.codeforcesrating,
                })
            


    async def get_user_cf_info(self):
        # with open(f'{self.data_path}/test.in.json','r') as f:
        #         in_data = json.load(f)

        name_str = ""

        cf_name_index:dict[str, int] = dict()

        for index, user in enumerate(self.user):
            cf_name_index[user.codeforcesname] = index
            name_str += user.codeforcesname + ';'

        res = await self.api_cf_get_user_info(name_str)

        if res.status == 'OK':
            
            for user_info in res.result:
                if user_info["handle"] in cf_name_index:
                    if "rating" in user_info:
                        self.user[cf_name_index[user_info["handle"]]].codeforcesrating = user_info["rating"]
                    else:
                        self.user[cf_name_index[user_info["handle"]]].codeforcesrating = 0
                else:
                    self.user[cf_name_index[user_info["handle"]]].codeforcesrating = 0
        else:
            raise ValueError('http error')   
    
    async def get_user_info(self):
        self.user = await user_rep.get_all_user_cf_name()

    async def get_problem_list(self):
        response = await self.request(codeforce_api["problem_list"])
        problem_model_list = []
        for p_index, problem in enumerate(response.result["problems"]):
            problem["contest_id"] = problem["contestId"]
            problem["contest_index"] = problem["index"]
            statistics = response.result["problemStatistics"][p_index]
            solved_count = statistics["solvedCount"]
            del problem["contestId"]
            del problem["index"]
            problem["solved_count"] = solved_count
            problem_model_list.append(
                CFProblem.from_dict(problem)
            )
        # print(f'need insert {len(problem_model_list)} problem')
        await problem_rep.block_insert_codeforce_problem(problem_model_list)

    async def get_problem_detailed_info(self, contest_id, index):
        try:

            html_path = os.path.join(self.data_path,self.problem_html_dir)
            os.makedirs(html_path, exist_ok=True) 

            url=codeforce_api["problem_detailed_info"].format(ContestId=contest_id, Index=index)

            # 创建 Service 对象
            service = Service(executable_path='/root/chromedriver-linux64/chromedriver')
            # 创建 ChromeOptions 对象
            options = Options()
            options.add_argument('--headless')  # 设置无头模式
            options.add_argument('--no-sandbox')  # 关键选项，禁用沙盒模式
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--remote-debugging-port=9222')
            options.add_argument('--disable-gpu')  # 如果你的系统没有 GPU
            options.add_argument('--disable-software-rasterizer')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-background-networking')
            options.add_argument('--disable-background-timer-throttling')
            options.add_argument('--disable-client-side-phishing-detection')
            options.add_argument('--disable-default-apps')
            options.add_argument('--disable-hang-monitor')
            options.add_argument('--disable-popup-blocking')
            options.add_argument('--disable-prompt-on-repost')
            options.add_argument('--disable-sync')
            options.add_argument('--disable-translate')
            options.add_argument('--metrics-recording-only')
            options.add_argument('--safebrowsing-disable-auto-update')
            options.add_argument('--enable-automation')
            options.add_argument('--disable-browser-side-navigation')
            options.add_argument('--disable-infobars')
            options.add_argument("--window-size=1920,1050")
            options.add_argument("--disable-blink-features=AutomationControlled")

            options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            driver = webdriver.Chrome(options=options, service=service)
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                get: () => false
                })
            """
            })

            # 打开指定的 URL
            driver.get(url)
            self.simulate_human_behavior(driver)
            
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "problem-statement"))
            )

            fail_path = os.path.join(html_path, f'{contest_id}_{index}.html')
            with open(fail_path, 'w') as f:
                f.write(driver.page_source)
            return True
        except TimeoutException:
            try:
                logger.warning('being prove human')
                fail_path = os.path.join(html_path, f'{contest_id}_{index}.html')
                with open(fail_path, 'w') as f:
                    f.write(driver.page_source)
                time.sleep(2)
                selenium_element = driver.find_element(By.ID, 'cf-chl-widget-kzdv0_response')
                selenium_element.click()
                element = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "problem-statement"))
                )
                fail_path = os.path.join(html_path, f'{contest_id}_{index}.html')
                with open(fail_path, 'w') as f:
                    f.write(driver.page_source)
                return True
            except:
                return False
        except Exception as e:
            logger.error(f'yxn error: {e}',exc_info=True)
            fail_path = os.path.join(html_path, f'{contest_id}_{index}.html')
            with open(fail_path, 'w') as f:
                f.write(driver.page_source)
            return False
        finally:
            # 关闭浏览器
            driver.save_screenshot(os.path.join(self.data_path,self.problem_html_dir,f'{contest_id}_{index}.png'))
            driver.quit()
    
    async def dfs(self, tag:Tag, is_strip=True):
        tmp_list = []
        if tag.name == 'br':
            tmp_list.append('\n')
        for tag_c in tag.children:
            if isinstance(tag_c,Tag):
                if tag_c.get('class',['0'])[0] not in ignore_id_class_list and tag_c.name not in ignore_name_list:
                    tmp_list += await self.dfs(tag_c, is_strip&(tag.name!='code'))
                    if tag_c.name in ['p','div']:
                        tmp_list.append('\n')
            elif isinstance(tag_c,str):
                tag_id = tag.get('id',None)
                if is_strip:
                    text = tag_c.strip()
                else:
                    text = tag_c
                if tag.name == 'p':
                    text = text.replace('\n',' ')
                text_del_space = ""
                if is_strip:
                    for index in range(len(text)):
                        if text[index] == ' ':
                            if text[index+1] != ' ':
                                text_del_space += text[index]
                        else:
                            text_del_space += text[index]
                    text = text_del_space

                if tag_id is not None:
                    if tag_id.startswith('MathJax-Element'):
                        text = f'${text}$'
                if len(text)>0:
                    tmp_list.append(text)
        if tag.name == 'code':
            tmp_list = ['```\n'] + tmp_list + ['```\n']
        return tmp_list

    async def analysis_problem_html(self, contest_id, index, offline_path: bool = False):
        try:
            if not offline_path:
                html_path = os.path.join(self.data_path,self.problem_html_dir)
                fail_path = os.path.join(html_path, f'{contest_id}_{index}.html')
            else:
                fail_path = os.path.join(self.data_path,'off_line_data','problem_html',f'{contest_id}_{index}.html')
                if not os.path.exists(fail_path):
                    logger.warning(f'{fail_path} not find maybe pdf')
                    return 
            soup = BeautifulSoup(open(fail_path, 'r', encoding='utf-8'), 'html.parser')
            soup = soup.find('div', class_='problem-statement')


            divs = soup.find('div', class_='title')
            # problem_info.problemtitle = next(divs.stripped_strings) #返回的生成器
            text_generator = divs.stripped_strings
            problem_title = get_x_ele(text_generator,1)

            divs = soup.find('div',class_ = 'time-limit')
            text_generator = divs.stripped_strings
            time_limit = float(get_x_ele(text_generator,2).split(' ')[0])

            divs = soup.find('div',class_ = 'memory-limit')
            text_generator = divs.stripped_strings
            memory_limit = int(get_x_ele(text_generator,2).split(' ')[0])

            all_div = list(soup.children)

            problem_div:Tag = all_div[1]
            input_div: Tag = all_div[2]
            output_div: Tag = all_div[3]
            sample_div: Tag = all_div[4]

            note_div: Tag = None
            if len(all_div) >= 6:
                note_div = all_div[5]

            problem_main_list = await self.dfs(problem_div)
            input_des_list = await self.dfs(input_div)
            output_des_list = await self.dfs(output_div)
            sample_des_list = await self.dfs(sample_div)
            
            if note_div is not None:
                note_list = await self.dfs(note_div)
            else:
                note_list = []
            
            problem_main_str = ""
            for i_str in problem_main_list:
                problem_main_str += i_str + " "

            input_des_str = ""
            for i_str in input_des_list[1:]:
                input_des_str += i_str + " "

            output_des_str = ""
            for i_str in output_des_list[1:]:
                output_des_str += i_str + " "

            note_des_str = ""
            for i_str in note_list[1:]:
                note_des_str += i_str + " "

            example_list = []
            str_tmp = ""
            for index,i_str in enumerate(sample_des_list):
                if i_str == 'Example' or i_str == 'Examples':
                    str_tmp = ""
                    example_list.append({})
                elif i_str == 'Input':
                    # print(str_tmp)
                    if len(str_tmp) > 0:
                        example_list[-1]["output"] = str_tmp
                        example_list.append({})
                    str_tmp = ""
                    
                elif i_str == 'Output':
                    example_list[-1]["input"] = str_tmp
                    str_tmp = ""
                else:
                    if i_str == '\n':
                        if str_tmp == "" or str_tmp[-1:] == "\n":
                            pass
                        else:
                            str_tmp += i_str
                    else:
                        str_tmp += i_str
                if index+1 == len(sample_des_list):
                    example_list[-1]["output"] = str_tmp
            
            problem = ProblemMG(
                problemtitle=problem_title,
                timelimit= time_limit,
                memorylimit=memory_limit,
                problemmain=problem_main_str,
                inputdescribe=input_des_str,
                outputdescribe=output_des_str,
                example = [Example(**tmp) for tmp in example_list],
                oj_from="codeforces",
                hash_id=get_hash_id(problem_title),
                note=note_des_str
            )
            return problem
        except Exception as e:
            logger.error(f'Unexpected error: {e}')
            return None
        
    async def insert_new_problem(self, contest_id,index,problem:ProblemMG):
        res = await mongodb_manger.insert_doc(MongoTable.PROBLEM.value,[problem.model_dump()])
        logger.info(f'sucessful insert id {res.inserted_ids}')
        _id = str(res.inserted_ids[0])
        
        await problem_rep.update_id_for_codeforce_problem(contest_id,index,_id)

        
async def main():
    now = datetime.datetime.now()
    try:
        await database.connect()

        catcher = UserDataCatcherCodeforces()

        await mongodb_manger.get_mongodb_connection()

        # await catcher.get_problem_list()

        await catcher.get_user_info()
        await catcher.get_user_cf_info()
        await catcher.update_info_into_db()

        # await catcher.api_cf_get_user_status(0,'wronganswerrr')

        await database.disconnect()

        # with open(f'{catcher.data_path}/log.out','a') as f:
        #     f.write(f'data_catcher;success;{now};;\n')

    except Exception as e:
        logger.error(f'yxn error: {e}',exc_info=True)
        # with open(f'{catcher.data_path}/log.out','a') as f:
        #     f.write(f'data_catcher;error;{now};{e};\n')

if __name__ == "__main__":
    # python -m app.serve.user_data_catcher
    asyncio.run(main())
