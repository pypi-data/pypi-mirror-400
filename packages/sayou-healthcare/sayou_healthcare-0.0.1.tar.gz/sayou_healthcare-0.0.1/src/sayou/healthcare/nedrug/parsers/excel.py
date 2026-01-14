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
import openpyxl
import pandas as pd

from io import BytesIO

from ..client import NedrugClient
from ..utils import (
    get_filename
)

logger = logging.getLogger(__name__)

class ExcelParser:

    def __init__(self, client: NedrugClient):
        self._client = client

    def parse_excel_file(self, file_path):
        """
        엑셀 파일을 파싱하여 데이터를 리스트 형식으로 반환하는 함수
        :param file_path: 엑셀 파일 경로
        :return: 파싱된 데이터 (리스트 형태)
        """

        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active  # 첫 번째 시트 선택
    
        data = self._parse_excel_sheet(sheet)
    
        workbook.close()
        return data
    
    def parse_excel_stream(self, file_stream):
        """
        엑셀 파일 스트림을 파싱하여 데이터를 리스트 형식으로 반환하는 함수
        :param file_stream: 엑셀 파일의 바이트 스트림
        :return: 파싱된 데이터 (리스트 형태)
        """
        workbook = openpyxl.load_workbook(BytesIO(file_stream))
        sheet = workbook.active  # 첫 번째 시트 선택

        data = self._parse_excel_sheet(sheet)

        workbook.close()
    
        return data
    
    def _parse_excel_sheet(self, sheet):
        data = []
        for row in sheet.iter_rows(values_only=True):
            data.append(row)
       
        return data