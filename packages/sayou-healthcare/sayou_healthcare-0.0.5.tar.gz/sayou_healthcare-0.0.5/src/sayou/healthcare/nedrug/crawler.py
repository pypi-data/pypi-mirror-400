# Copyright (c) 2025-2026, Sayouzone
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
 
from .client import NedrugClient

from .parsers import (
    DownloadParser,
    ExcelParser,
)

class NedrugCrawler:
    """
    의약품안전나라 > 의약품등 제품정보 검색 > 엑셀다운로드
    
    의약품안전나라 > 의약품등 제품정보 검색:
    https://nedrug.mfds.go.kr/searchDrug
    엑셀다운로드
    https://nedrug.mfds.go.kr/searchDrug/getExcel

    1. Excel 파일 다운로드
    2. GCS에 업로드
    3. Excel 파일에서 약품목록 파싱
    4. BigQuery에 로드
    5. medicine_list.csv에 저장
    """

    def __init__(self):
        self.client = NedrugClient()

        # 파서 초기화
        self._download_parser: DownloadParser = DownloadParser(self.client)
        self._excel_parser: ExcelParser = ExcelParser(self.client)

    def download(self):
        return self._download_parser.fetch()

    def parse(self):
        return self._excel_parser.parse("./data")