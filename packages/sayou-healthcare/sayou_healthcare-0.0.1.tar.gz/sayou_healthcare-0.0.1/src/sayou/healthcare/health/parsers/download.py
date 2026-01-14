# Copyright (c) 2025, Sayouzone
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import csv
import logging
import pandas as pd
import time

from lxml import html
from urllib.parse import parse_qs, quote

from ..client import HealthClient
from ..utils import (
    _HEALTH_START_URL_,
    _HEALTH_BASE_URL_,
    _HEALTH_DOWNLOAD_URL_,
    KOREAN_INITIALS,
    decode_euc_kr,
    get_filename,
)

logger = logging.getLogger(__name__)

class DownloadParser:

    page_size = 1000
    wait_time = 10
    medicine_list_file = "medicine_list_health.csv"

    def __init__(self, client: HealthClient):
        self._client = client

    def fetch(self):

        initial_num = 1
        page_num = 1
        total_rows = []
        while True:
            # 초성 "ㄱ"을 URL 인코딩한 값 "%E3%84%B1" 전환
            print('initial_num', initial_num, len(KOREAN_INITIALS))
            print('page_num', page_num)
            encoded_string = quote(KOREAN_INITIALS[initial_num - 1], encoding='utf-8')
            rows = self.parse(page_num, encoded_string)

            if len(rows) == 0 and initial_num >= len(KOREAN_INITIALS):
                print(total_rows)
                print('Total', len(total_rows))
                self._save_to_csv(self.medicine_list_file, total_rows)
                return
            
            total_rows.extend(rows)
         
            if len(rows) > 0:
                page_num += 1
            elif len(KOREAN_INITIALS) >= initial_num:
                initial_num += 1
                page_num = 1
            
            time.sleep(self.wait_time)

    def parse(self, page_num, initial):
        url = _HEALTH_BASE_URL_

        payload = {
            "req_page": page_num,
            "listup": self.page_size,
            "search_drugnm_initial": initial,
            "inner_search_word": "",
            "origin_cnt": "",
            "inner_search_flag": "",
            "inner_match_value": "",
            "input_drug_nm": "",
            "input_upsoNm": "",
            "cbx_sunbcnt": "0",
            "cbx_class": "0",
            "anchor_dosage_route_hidden": "",
            "mfds_cd": "",
            "mfds_cdword": "",
            "input_hiraingdcd": "",
            "search_sunb1": "",
            "search_sunb2": "",
            "search_sunb3": "",
            "sunb_equals1": "",
            "sunb_equals2": "",
            "sunb_equals3": "",
            "sunb_where1": "and",
            "sunb_where2": "and",
            "search_effect": "",
            "cbx_bohtype": "",
            "search_bohcode": "",
            "anchor_form_info_hidden": "",
            "cbx_narcotic": "",
            "atccode_val": "",
            "atccode_name": "",
            "kpic_atc_nm_opener": "",
            "kpic_atc_nm": "",
            "cbx_bio": "",
            "icode": "",
            "ori_search_word": "",
            "search_flag": "",
            "movefrom": "drug",
            "viewmode": "",
            "more": ""
        }

        payload = f"req_page={page_num}&listup={self.page_size}" \
            f"&search_drugnm_initial={initial}" \
            "&inner_search_word=&origin_cnt=&inner_search_flag=" \
            "&inner_match_value=&input_drug_nm=&input_upsoNm=&cbx_sunbcnt=0" \
            "&cbx_class=0&anchor_dosage_route_hidden=&mfds_cd=&mfds_cdword=" \
            "&input_hiraingdcd=&search_sunb1=&search_sunb2=&search_sunb3=" \
            "&sunb_equals1=&sunb_equals2=&sunb_equals3=&sunb_where1=and" \
            "&sunb_where2=and&search_effect=&cbx_bohtype=&search_bohcode=" \
            "&anchor_form_info_hidden=&cbx_narcotic=&atccode_val=&atccode_name=" \
            "&kpic_atc_nm_opener=&kpic_atc_nm=&cbx_bio=&icode=&ori_search_word=" \
            "&search_flag=&movefrom=drug&viewmode=&more="
        #print('headers', self.headers)
        print('payload', payload)
        
        response = self._client._post(url, body=payload, timeout=60)
        print('response', response, type(response))
        #print('response.content', response.content, type(response.content))

        #page = BeautifulSoup(response.content, "html.parser")
        #print('page', page, type(page))
        page = html.fromstring(response.content)

        #
        #articles = [article.text_content().strip() for article in page.xpath('//article[@id="resultMoreTable"]//h3[@class="subtitle"]//span[@class="count"]')]
        #print('articles', articles)
        #articles = page.xpath('//article[@id="resultMoreTable"]')
        #for article in articles:
        #    print(etree.tostring(article, pretty_print=True).decode('utf-8'))

        table_rows = page.xpath('//table[@id="tbl_pro"]//tr')  # 테이블의 모든 행(tr) 선택

        rows = []
        columns = ["name", "code", "ingredient", "effect", "company", "category",
                   "form", "expert", "insurance", "bioequiv", "image"]
        for row in table_rows:
            #print('row', row)
            #print(etree.tostring(row, pretty_print=True).decode('utf-8'))
            #cells = row.xpath('.//th | .//td')  # 헤더(th) 및 데이터(td) 선택

            #texts = row.xpath(".//tr/th/text()")
            th_texts = [th.text_content().strip() for th in row.xpath('.//th')]
            #if len(texts) > 0 or len(th_texts) > 0:
            if len(th_texts) > 0:
                #print(texts)
                #print(th_texts)
                continue

            td_texts = [td.text_content().strip() for td in row.xpath(".//td")]
            img_src = row.xpath('.//td[@class="img"]/img/@src')
            onclick_values = [re.search(r"show_idfypop\('(.+?)'\)", img.get('onclick', '')) for img in row.xpath('.//td[@class="img"]/img')]
            onclick_values = [match.group(1) for match in onclick_values if match]
            if len(onclick_values) == 0:
                onclick_values = [re.search(r"drug_detailHref\('(.+?)'\)", td.get('onclick', '')) for td in row.xpath('.//td[@class="txtL"]')]
                onclick_values = [match.group(1) for match in onclick_values if match]
            #print("Extracted Texts:", td_texts)
            #print("Image Source:", img_src)
            #print("Onclick Values:", onclick_values)
            medicine_code = onclick_values[0] if len(onclick_values) > 0 else None

            td_texts.pop(0)
            td_texts.insert(1, medicine_code)
            td_texts.insert(len(td_texts), img_src[0] if img_src[0] != '/images/img_empty3.jpg' else None)
            
            #print('code', medicine_code)
            row_data = dict(zip(columns, td_texts))
            rows.append(row_data)

            if page_num == 1 and len(rows) == 1:
                print('rows', rows)
        
        #print(rows)
        return rows

    def _parse_params(self, query_string):

        # "?" 제거 후 파싱
        parsed_params = parse_qs(query_string.lstrip("?"))

        # 값이 리스트로 반환되므로 단일 값만 있는 경우 리스트에서 추출
        parsed_params = {k: v[0] if len(v) == 1 else v for k, v in parsed_params.items()}

        print(parsed_params)
        return parsed_params

    def _save_to_csv(self, file_path, data):
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["id","name"])
            index = 1
            for row in data:
                writer.writerow([index, row.get("name")])
                index += 1
