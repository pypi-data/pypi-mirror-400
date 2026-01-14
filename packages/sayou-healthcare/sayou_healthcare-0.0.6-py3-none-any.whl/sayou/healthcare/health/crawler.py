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
 
from .client import HealthClient
from .parsers.download import DownloadParser

class HealthCrawler:
    """
    약학정보원 > 의약품 상세검색 > 초성별 검색
    급여 + 비급여 약품 포함
    업로드 주기: xxx

    의약품 상세검색 (기본 페이지):
    https://www.health.kr/searchDrug/search_detail.asp
    검색결과 리스트 (검색 결과):
    https://www.health.kr/searchDrug/search_detail.asp
    검색결과 더보기:
    https://www.health.kr/searchDrug/result_more.asp
    의약품 상세정보
    https://www.health.kr/searchDrug/result_drug.asp?drug_cd=2018061800005

    1. 초성 "ㄱ ㄴ ㄷ ㄹ ㅁ ㅂ ㅅ ㅇ ㅈ ㅊ ㅋ ㅌ ㅍ ㅎ"
    2. 페이지 사이즈 : 1000
    3. xpath으로 약품목록 파싱
    4. BigQuery에 로드
    5. medicine_list.csv에 저장
    """

    def __init__(self):
        self.client = HealthClient()

        self._download_parser = DownloadParser(self.client, output_path="./data")
        
    def medicines(self):
        return self._download_parser.fetch_all()
        #return self._download_parser.fetch()