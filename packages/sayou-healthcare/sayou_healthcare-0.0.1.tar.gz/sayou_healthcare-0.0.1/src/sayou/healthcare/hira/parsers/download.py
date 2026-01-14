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
 
import logging
import pandas as pd

from lxml import html
from urllib.parse import parse_qs, quote, unquote

from ..client import HiraClient
from ..utils import (
    _START_URL_,
    decode_euc_kr,
    get_filename,
)
from .excel import ExcelParser

logger = logging.getLogger(__name__)

class DownloadParser:

    def __init__(self, client: HiraClient):
        self._client = client

        self._excel_parser = ExcelParser(client)

    def fetch(self):
        url = _START_URL_
        response = self._client._get(url)

        page = html.fromstring(response.content)
        table_rows = page.xpath('//div[@class="tb-type01"]/table/tbody/tr')

        download_url = None
        rows = []
        for row in table_rows:
            td_texts = [td.text_content().strip() for td in row.xpath(".//td")]
            link = row.xpath('.//td[@class="col-tit"]/a/@href')
            file_type = row.xpath('.//td[@class="col-file"]/i/@title')

            brd_blt_no = None
            if len(link) > 0:
                parsed_params = self._parse_params(link[0])
                brd_blt_no = parsed_params.get("brdBltNo")

            td_texts.insert(2, brd_blt_no)
            td_texts[len(td_texts)-1] = (file_type[0] if len(file_type) else None)

            td_classes = row.xpath('.//td/@class')
            td_classes.insert(2, "brdBltNo")

            rows.append(td_texts)

        if len(rows) == 0:
            return None, []

        latest_rows = max(rows, key=lambda x: x[4])
        brd_blt_no = latest_rows[2]

        filename, data = self.download(brd_blt_no)
        return filename, data

    def download(self, brd_blt_no):
        url = _DOWNLOAD_BASE_URL_
        params = {
            "apndNo": 1,
            "apndBrdBltNo": brd_blt_no,
            "apndBrdTyNo": 1,
            "apndBltNo": 59
        }
        response = self._client._get(url, params=params)
        headers = response.headers

        self._excel_filename = get_filename(headers)

        path = os.path.join(self._local_path, self._excel_filename)
        with open(path, "wb") as file:
            file.write(response.content)

        excel_data = self._excel_parser.parse_excel_stream(response.content)

        return self._excel_filename, excel_data

    def _parse_params(self, query_string):

        # "?" 제거 후 파싱
        parsed_params = parse_qs(query_string.lstrip("?"))

        # 값이 리스트로 반환되므로 단일 값만 있는 경우 리스트에서 추출
        parsed_params = {k: v[0] if len(v) == 1 else v for k, v in parsed_params.items()}

        print(parsed_params)
        return parsed_params
