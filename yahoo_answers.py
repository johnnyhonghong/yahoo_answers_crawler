import time
import json
import random
import requests
from pprint import pprint
from typing import Dict


class YahooAnswersSpider():
    """Yahoo知識+ 爬蟲"""
    def __init__(self) -> None:
        self.api_url = 'https://tw.answers.yahoo.com/_reservice_/'
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36',
            'content-type': 'application/json'
        }

    def request_put(self, payload: Dict) -> Dict:
        """送出 PUT 請求

        :param payload: 傳遞參數資料
        :return data: requests 回應資料
        """
        response = requests.put(self.api_url, data=json.dumps(payload), headers=self.headers)
        if response.status_code != requests.codes.ok:
            print(f'網頁載入發生問題：{payload}')
            return None
        data = response.json()
        if data['error']:
            print(f'回傳資料發生錯誤：{data["payload"]}')
        return data["payload"]

    def get_question_list(self, is_popular=False, category_id="0", offset="", count=15) -> Dict:
        """取得問題列表(文章列表)資料

        :param is_popular: 是否取得熱門問題，否則取得最新問題
        :param category_id: 分類
        :param offset: 偏移值(字串)
        :param count: 數量
        :return data: 回應資料
        """
        reservice_name = "FETCH_ANSWER_STREAMS_END"
        reservice_start = "FETCH_ANSWER_STREAMS_START"
        if is_popular:
            reservice_name = "FETCH_DISCOVER_STREAMS_END"
            reservice_start = "FETCH_DISCOVER_STREAMS_START"

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

    def get_question(self, qid: str) -> Dict:
        """取得問題(文章)資料

        :param qid: 問題 ID
        :return data: 回應資料
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

    def get_answer_list(self, qid: str, start=1, count=15) -> Dict:
        """取得解答(留言)資料

        :param qid: 文章 ID
        :param start: 解答抓取起始值(偏移值)
        :param count: 數量
        :return data: 回應資料
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


if __name__ == "__main__":
    yahoo_answers_spider = YahooAnswersSpider()

    data = yahoo_answers_spider.get_question_list(is_popular=False, category_id='2115500139')
    print(data)
    # with open(f'yahoo_answers.json', 'w', encoding='utf-8') as f:
    #     f.write(json.dumps(data))
    # for question in data['questions']:
    #     print(question['title'][:20])

    # data = yahoo_answers_spider.get_question('20210310121058AAxKYlh')
    # print(data)

    # data = yahoo_answers_spider.get_answer_list('20210310121058AAxKYlh', start=1)
    # print(data)