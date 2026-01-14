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
import os

from io import BytesIO
from urllib.parse import unquote

from ..client import NedrugClient
from ..utils import (
    _NEDRUG_EXCEL_URL_,
    GEMINI_COLUMNS,
    decode_euc_kr,
    get_filename,
)

from .excel import ExcelParser

logger = logging.getLogger(__name__)

class DownloadParser:

    page_size = 10000
    medicine_list_file = "medicine_list_nedrug.csv"

    def __init__(self, client: NedrugClient, local_path: str = "./data"):
        self._client = client
        self._excel_parser = ExcelParser(client)

        self._local_path = local_path
        self._excel_filename = None
        self._excel_data = None

    def fetch(self):
        page_num = 0
        total_medicines = []
        while True:
            filename, content, medicines = self.download(page_num)

            if len(medicines) == 0:
                break

            total_medicines.extend(medicines)
            page_num += 1

        print('total_medicines', total_medicines)
        self._save_to_csv(self.medicine_list_file, total_medicines)
        os.remove(self.medicine_list_file)
    
    def download(self, page_num):

        payload = {
            "ExcelRowdata": f"{(page_num * self.page_size)}",
            "excelSearchCnt": self.page_size,
            "page": 1,
            "sort": "",
            "sortOrder": "",
            "searchYn": "",
            "searchDivision": "detail",
            "itemName": "",
            "itemEngName": "",
            "entpName": "",
            "entpEngName": "",
            "ingrName1": "",
            "ingrName2": "",
            "ingrName3": "",
            "ingrEngName": "",
            "itemSeq": "",
            "stdrCodeName": "",
            "atcCodeName": "",
            "indutyClassCode": "",
            "sClassNo": "",
            "narcoticKindCode": "",
            "cancelCode": "",
            "etcOtcCode": "",
            "makeMaterialGb": "",
            "searchConEe": "AND",
            "eeDocData": "",
            "searchConUd": "AND",
            "udDocData": "",
            "searchConNb": "AND",
            "nbDocData": "",
            "startPermitDate": "",
            "endPermitDate": ""
        }

        url = _NEDRUG_EXCEL_URL_
        
        response = self._client._post(url, body=payload, timeout=60)
        logger.info('response', response, type(response))

        headers = response.headers
        print('headers', headers)
        logger.info('headers', headers)
        #print('response.body', response.content)

        # 한글 파일명 변환
        filename = get_filename(headers)

        if not filename:
            return None, None, []

        # 1. URL 디코딩
        decoded_filename = unquote(filename)
        logger.info('Decoded filename', decoded_filename)
        logger.info('response.body', response.content)

        data = self._excel_parser.parse_excel_stream(response.content)
        logger.info('data', data, type(data))
        if len(data) <= 1:
            return None, None, []
        
        path = response.url.split('/')[-1]
        #path = decoded_filename if decoded_filename else path
        file_suffix = ((page_num + 1) * self.page_size) \
            if len(data) >= (self.page_size + 1) else \
            (page_num * self.page_size + (len(data) - 1))
        filename = decoded_filename.replace(".xls", f"_{file_suffix}.xls") if decoded_filename else path
        print('Excel file', filename)

        """ """
        # 로컬에 저장
        if not os.path.exists(self._local_path):
            os.makedirs(self._local_path)
        
        path = os.path.join(self._local_path, filename)
        with open(path, 'wb') as f:
            f.write(response.content)
        """ """

        #keys = ('name', 'age', 'city')
        keys = tuple(GEMINI_COLUMNS.keys())
        #print('keys', keys, type(keys))
        medicines = []
        for item in data:
            if isinstance(item, tuple) and \
                self._exist_string_in_tuple(item, "품목기준코드"):
                continue
            #print('item', item)
            medicine = dict(zip(keys, item))
            medicines.append(medicine)
        
        return filename, response.content, medicines
    
    def _parse_params(self, query_string):

        # "?" 제거 후 파싱
        parsed_params = parse_qs(query_string.lstrip("?"))

        # 값이 리스트로 반환되므로 단일 값만 있는 경우 리스트에서 추출
        parsed_params = {k: v[0] if len(v) == 1 else v for k, v in parsed_params.items()}

        print(parsed_params)
        return parsed_params
    
    def _convert_table_to_csv(self, table):
        rows = []
        for row in table.find_all("tr"):
            cells = [cell.get_text(strip=True) for cell in row.find_all(["th", "td"])]
            rows.append(cells)

        return rows
    
    def _extract_ul(self, text):
        """
        HTML에서 <li> 태그의 텍스트를 추출하여 개행하여 반환하는 함수
        :param html: HTML 문자열
        :return: 개행된 문자열
        """
        soup = BeautifulSoup(text, "html.parser")
        li_texts = [unicodedata.normalize('NFKC', li.get_text(strip=True)) for li in soup.find_all("li")]
        return "\n".join(map(str, li_texts))
        
    def _exist_string_in_tuple(self, items, string):
        """
        튜플 내에 특정 문자열이 포함된 요소가 있는지 확인합니다.

        Args:
            my_tuple: 확인할 튜플 (문자열로 구성된 튜플).
            search_string: 찾을 문자열.

        Returns:
            True: 튜플 내에 search_string을 포함하는 요소가 하나 이상 있는 경우.
            False: 그렇지 않은 경우.
        """
        for item in items:
            if item and string in item:
                return True
        return False
    
    def _save_to_csv(self, file_path, data):
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["id","name"])
            index = 1
            for row in data:
                writer.writerow([index, row.get("product_name")])
                index += 1