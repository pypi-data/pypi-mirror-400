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
 
from .client import HiraClient
from .parsers.download import DownloadParser
from .parsers.excel import ExcelParser
from .parsers.opendata import OpenDataParser

class HiraCrawler:
    """
    건강보험심사평가원 > 약제급여목록표 > 약제정보 > 약제정보 다운로드
    업로드 주기: 1개월

    1. Excel 파일 다운로드
    2. GCS에 업로드
    3. Excel 파일에서 약품목록 파싱
    4. BigQuery에 로드
    5. medicine_list.csv에 저장
    """

    def __init__(self):
        self.client = HiraClient()

        self._download_parser = DownloadParser(self.client)
        self._excel_parser = ExcelParser(self.client)
        self._opendata_parser = OpenDataParser(self.client)
        
    def download(self):
        return self._download_parser.fetch()

    def excel(self):
        return self._excel_parser.fetch()

    def parse(self):
        return self._excel_parser.parse("./data")

    def opendata(self):
        # 압축 해제된 파일 정리하지 않음
        return self._opendata_parser.fetch(is_cleanup_files=False)

    def hospitals(self):
        return self._opendata_parser.hospitals()

    def pharmacies(self):
        return self._opendata_parser.pharmacies()
