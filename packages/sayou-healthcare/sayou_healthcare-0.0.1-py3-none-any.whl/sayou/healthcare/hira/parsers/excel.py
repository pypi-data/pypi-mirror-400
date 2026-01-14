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
import os
import openpyxl

from io import BytesIO

from ..client import HiraClient
from ..utils import (
    _DOWNLOAD_BASE_URL_,
    decode_euc_kr,
    get_filename,
)

logger = logging.getLogger(__name__)

class ExcelParser:

    def __init__(self, client: HiraClient, local_path: str = "./data"):
        self._client = client

        self._local_path = local_path

    def parse_excel_file(self, file_path):
        """
        엑셀 파일을 파싱하여 데이터를 리스트 형식으로 반환하는 함수
        :param file_path: 엑셀 파일 경로
        :return: 파싱된 데이터 (리스트 형태)
        """

        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active  # 첫 번째 시트 선택
    
        excel_data = self._parse_excel_sheet(sheet)
    
        workbook.close()
        return excel_data

    def parse_excel_stream(self, file_stream):
        """
        엑셀 파일 스트림을 파싱하여 데이터를 리스트 형식으로 반환하는 함수
        :param file_stream: 엑셀 파일의 바이트 스트림
        :return: 파싱된 데이터 (리스트 형태)
        """
        workbook = openpyxl.load_workbook(BytesIO(file_stream))
        sheet = workbook.active  # 첫 번째 시트 선택

        excel_data = self._parse_excel_sheet(sheet)

        workbook.close()
    
        return excel_data

    def save_to_csv(self, file_path):
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["id","name"])

            index = 1
            for row in self._excel_data:
                if isinstance(row, tuple) and \
                    self._exist_string_in_tuple(row, "연번"):
                    continue

                writer.writerow([index, row[5]])
                index += 1
    
    def _parse_excel_sheet(self, sheet):
        data = []
        for row in sheet.iter_rows(values_only=True):
            data.append(row)
       
        return data

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
            if item and isinstance(item, str) and string in item:
                return True
        return False