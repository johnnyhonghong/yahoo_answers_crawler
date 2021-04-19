import time
import json
import random
import requests
from pprint import pprint
from typing import Dict
from urllib.request import urlopen
from bs4 import BeautifulSoup
import os
import json
this_file_path = os.path.realpath(__file__)
this_file_path = this_file_path.replace('\\','/')
p_dir = '/'.join(this_file_path.split('/')[:-1])
class YahooAnswersSpider():
    """Yahoo知識+ 爬蟲"""
    def __init__(self):
        self.api_url = 'https://tw.answers.yahoo.com/_reservice_/'
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36',
            'content-type': 'application/json'
        }

    def request_put(self, payload: Dict) -> dict:
        """
        PUT request
        Args:
            payload: 傳遞參數資料(json)
        """
        response = requests.put(self.api_url, data=json.dumps(payload), headers=self.headers)
        if response.status_code != requests.codes.ok:
            print(f'Load error： {payload}')
            return None
        data = response.json()
        if data['error']:
            print(f'return error: {data["payload"]}')
        return data['payload']

    def get_question_list(self, is_popular=False, category_id="", offset="", count=20) -> dict:
        """取得問題列表(文章列表)資料
        Args:
            is_popular: 探索或解答 
            category_id: QA 種類
            offset: 偏移值(ajax load)
            count: 回傳 QA 數量
            data: 回傳 QA 列表
        """
        
        if not is_popular: # 解答
            reservice_name = "FETCH_ANSWER_STREAMS_END"
            reservice_start = "FETCH_ANSWER_STREAMS_START"
            
        elif is_popular: # 探索
            reservice_name = "FETCH_DISCOVER_STREAMS_END"
            reservice_start = "FETCH_DISCOVER_STREAMS_START"
            
        # payload config
        payload = {
            "type": "CALL_RESERVICE",
            "payload": {
                "categoryId": category_id,
                "lang": "zh-Hant-TW",
                "count": count,
                "offset": offset
            },
            "reservice": {
                "name": reservice_name,
                "start": reservice_start,
                "state": "CREATED"
            }
        }
        return self.request_put(payload)

    def get_question(self, qid: str) -> dict:
        """
        Args:
            qid: question ID
        """
        payload = {
            "type": "CALL_RESERVICE",
            "payload": {
                "qid": qid
            },
            "reservice": {
                "name": "FETCH_QUESTION_END",
                "start": "FETCH_QUESTION_START",
                "state": "CREATED"
            },
            "kvPayload": {
                "key": qid,
                "kvActionPrefix": "KV/question/"
            }
        }
        return self.request_put(payload)

    def get_answer_list(self, qid: str, start=1, count=10) -> dict:
        """
        取得解答(留言)資料
        Args:
            qid: question ID
            start: 解答抓取起始值(偏移值)
            count: 數量
            data: 回應資料
        """
        payload = {
            "type": "CALL_RESERVICE",
            "payload": {
                "qid": qid,
                "count": count,
                "start": start,
                "lang": "zh-Hant-TW",
                "sortType": "NEWEST"  # RATING:評分 NEWEST:最新 OLDEST:最舊
            },
            "reservice": {
                "name": "FETCH_QUESTION_ANSWERS_END",
                "start": "FETCH_QUESTION_ANSWERS_START",
                "state": "CREATED"
            },
            "kvPayload": {
                "key": qid,
                "kvActionPrefix": "KV/questionAnswers/"
            }
        }
        return self.request_put(payload)
    def get_extra_question_list(self, qid: str) -> dict:
        """取得問題列表(文章列表)資料
        Args:
            is_popular: 探索或解答 
            category_id: QA 種類
            offset: 偏移值(ajax load)
            count: 回傳 QA 數量
            data: 回傳 QA 列表
        """
        # payload config
        payload = {
            "type": "CALL_RESERVICE",
            "payload": {
                "lang": "zh-Hant-TW",
                "qid": qid
            },
            "reservice": {
                "name": "FETCH_EXTRA_QUESTION_LIST_END",
                "start": "FETCH_EXTRA_QUESTION_LIST_START",
                "state": "CREATED"
            }
        }
        return self.request_put(payload)
def get_category_path(category = "") -> str:
    try:
        if category != "":
            category = f"?sid={category}"
        
        url = f"https://tw.answers.yahoo.com/dir/index{category}"
        html = urlopen(url).read()
        soup = BeautifulSoup(html, 'lxml')
        category_path = soup.findAll(class_ = "CategoryBoard__paths___g8qpm")
        path = []
        if category_path:
            for line in category_path[0].findAll("li"):
                path.append(line.text)
            path_str = '/'.join(path)
        else:
            print("CategoryBoard__paths___g8qpm not found")
    except:
        print("some errors")
        path_str = "some errors"
    return path_str
def get_all_qid(is_popular:bool, category_id: str) -> list:
    offset = ""
    can_load_more = True
    qid_list = []
    while can_load_more:
        # get reservice data
        data = yahoo_answers_spider.get_question_list(is_popular=is_popular,
                                                      category_id=category_id,
                                                      offset=offset)
        # get offset
        offset = data['offset']
        if is_popular:
            prefix = "explore"
        elif not is_popular:
            prefix = "answer"
        print(f"\rnumber of {prefix} qid: {len(qid_list)},{offset}",end="")
        # get canLoadMore
        can_load_more = data['canLoadMore']
        # get qid
        for question in data['questions']:
            qid_list.append(question['qid'])
        time.sleep(2)
    print("")
    return qid_list
if __name__ == "__main__":
    
    dir_path = ""
    yahoo_answers_spider = YahooAnswersSpider()
    category_id_list = []
    # read sid.txt
    with open("./sid.txt", 'r') as txt_file:
        for line in txt_file.readlines():
            category_id_list.append(line.replace("\n",""))
    print(category_id_list)
    # 依照sid，先掃qid，再進入qid
    for category_id in category_id_list:
        
        # get category path
        path_str = get_category_path(category = category_id)
        print(f"path: {path_str}")
        print(f"sid: {category_id}")
        # mkdir
        path_list = path_str.split("/")
        level_dir = ""
        for path_dir in path_list:
            level_dir = f"{level_dir}/{path_dir}"
            dist_dir = f"{p_dir}{level_dir}"
            if not os.path.isdir(dist_dir):
                os.mkdir(dist_dir)
        # get all qid
        explore_qid_list = get_all_qid(is_popular=True, category_id=category_id)
        answer_qid_list = get_all_qid(is_popular=False, category_id=category_id)
        union_qid_set = set(explore_qid_list) | set(answer_qid_list)
        print(f"union qid length: {len(union_qid_set)}")
        # qid parameter init
        
        for question_id in union_qid_set:
            print(f"\rqid: {question_id}",end="")
            question_dir = f"{dist_dir}/{question_id}"
            if not os.path.isdir(question_dir):
                os.mkdir(question_dir)
            question_data = yahoo_answers_spider.get_question(question_id)
            # question json dump
            with open(f"{question_dir}/question.json", 'w') as json_file:
                json.dump(question_data, json_file)
            # answer process
            answer_count = 0
            start = 1
            count = 5
            while True:
                answer_data = yahoo_answers_spider.get_answer_list(question_id,
                                                                   start=start,
                                                                   count=count)
                answer_length = len(answer_data['answers'])
                if answer_length > 0:
                    answer_count += 1
                    # answer json dump
                    with open(f"{question_dir}/answer_{answer_count}.json", 'w') as json_file:
                        json.dump(answer_data, json_file)
                else:
                    break
                start += count
                # get extra question
                """
                question_data = yahoo_answers_spider.get_extra_question_list("20210418115252AAO7dbn")
                """
                time.sleep(2)
        print("")
        
    
        # qid reservice
        #pass
         
    