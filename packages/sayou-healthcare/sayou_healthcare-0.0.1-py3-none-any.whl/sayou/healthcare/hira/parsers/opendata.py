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
import io
import os
import re
import zipfile

from io import BytesIO
from lxml import html
from pathlib import Path

from ..client import HiraClient
from ..utils import (
    _OPENDATA_START_URL_,
    _OPENDATA_DOWNLOAD_URL_,
    _OPENDATA_SELECT_URL_,
    HOSPITAL_COLUMNS,
    PHARMACY_COLUMNS,
    decode_euc_kr,
    get_filename,
)

from .excel import ExcelParser

class OpenDataParser:
    def __init__(self, client: HiraClient, local_path: str = "./data"):
        self._client = client
        self._excel_parser = ExcelParser(client)

        self._local_path = local_path
        self._excel_filename = None
        self._hospital_data = None
        self._pharmacy_data = None

    def fetch(self):
        # GCS에 업로드
        #gcs_api = StorageAPI(self.project_id, self.gcs_region, self.bucket_name)

        filename, content = self.parse()

        blob_name = os.path.join(self._local_path, filename)
        #blob = gcs_api.check_data(self.bucket_name, blob_name)
        #gcs_api.upload_data(content, blob_name)

        # 전국 병의원 및 약국 현황 zip 파일 압축해제
        dest_dir = "opendata_hira_data"
        self._unzip_from_data(content, dest_dir)
        list_files = self._list_files(dest_dir)
        for file in list_files:
            #gcs_api.upload_file(os.path.join(dest_dir, file), f"data/{dest_dir}/{file}")
            print('Excel', file)

        # 병원정보서비스 엑셀 파일 파싱 및 BigQuery에 로드, CSV 파일 생성
        file = "1.병원정보서비스"
        items = [item for item in list_files if file in item]
        csv_file_path = "hospital_list.csv"
        if len(items) > 0:
            columns = HOSPITAL_COLUMNS

            # 엑셀 파일 파싱
            self._hospital_data = self._excel_parser.parse_excel_file(os.path.join(dest_dir, items[0]))
            #print('Hospital', data)

        # 약국정보서비스 엑셀 파일 파싱 및 BigQuery에 로드, CSV 파일 생성
        file = "2.약국정보서비스"
        items = [item for item in list_files if file in item]
        csv_file_path = "pharmacy_list.csv"
        if len(items) > 0:
            columns = PHARMACY_COLUMNS

            # 엑셀 파일 파싱
            self._pharmacy_data = self._excel_parser.parse_excel_file(os.path.join(dest_dir, items[0]))
            #print('Pharmacy', data)

        # 압축해제 디렉토리 내부 파일 삭제
        #os.rmdir(dest_dir)
        for file in list_files:
            os.remove(os.path.join(dest_dir, file))

    def parse(self):
        url = _OPENDATA_START_URL_

        response = self._client._get(url)
        print('response', response, type(response))

        headers = response.headers
        print('headers', headers)

        page = html.fromstring(response.content)
        
        li_rows = page.xpath('//dl[@class="fileList ml00"]/dd/ul/li/a/@href')
        onclicks = [re.search(r"fn_fileDown\('(.+?)'\)", row) for row in li_rows]
        onclicks = [match.group(1) for match in onclicks if match]
        print('onclicks', onclicks)

        onclicks.sort(reverse=True)
        download_code = onclicks[0] if len(onclicks) > 0 else None
        print('download_code', download_code)
        #download_code = "295053"

        filename, content = self.download(download_code)
        return filename, content
    
    def download(self, download_code):
        url = _OPENDATA_DOWNLOAD_URL_
        payload = {
            "customValue": download_code,
            "d00": "UlpEQXhER1J2ZDI1c2IyRmtVbVZ4ZFdWemRBdGtNVEFNWHd0a01qVU1MM05vWVhKbFpDOWtZWFJoTDNWd2JHOWhaRVpwYkdWekwyWnBiR1V2T0RrNU56WXhPVVl0T0VJNFJpMURSRFU0TFRkQ05qa3RNVUZEUlRKR09UaEVOa0V5TG5wcGNBdGtNallNN0tDRTZyV3RJT3V6a2V5ZG1PeWJrQ0Ryc0k4ZzdKVzk2cld0SU8yWWhPMlpxU0F5TURJMExqRXlMbnBwY0F0a01EY01ORGN4UVVaRVF6RXRORGRCTXkxRVFUSTJMVE16UlRjdFJrUkdNMFJFTWtFd1FqTkRDdz09"
        }

        response = self._client._post(url, body=payload)
        print('response', response, type(response))

        headers = response.headers
        print('headers', headers, type(headers))

        # 한글 파일명 변환
        filename = get_filename(headers)
        print('Excel filename', filename)

        return filename, response.content

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
    
    def _save_to_csv(self, file_path, columns, data):
        keys = tuple(columns.keys())

        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["id","name","address"])
            index = 1
            for row in data:
                if isinstance(row, tuple) and \
                    self._exist_string_in_tuple(row, "암호화요양기호"):
                    continue
                item = dict(zip(keys, row))
                writer.writerow([index, item.get("medical_institution_name"), item.get("address")])
                index += 1
    
    def _parse_params(self, query_string):

        # "?" 제거 후 파싱
        parsed_params = parse_qs(query_string.lstrip("?"))

        # 값이 리스트로 반환되므로 단일 값만 있는 경우 리스트에서 추출
        parsed_params = {k: v[0] if len(v) == 1 else v for k, v in parsed_params.items()}

        print(parsed_params)
        return parsed_params
    
    def _unzip_from_file(self, file_path, dest_dir):
        zip_ref = zipfile.ZipFile(file_path, 'r') 
        for fileinfo in zip_ref.namelist():
            #print(fileinfo.filename)
            #extracted_path = Path(zip_ref.extract(fileinfo))
            extracted_path = Path(zip_ref.extract(fileinfo, dest_dir))
            #print('extracted_path', extracted_path)
    
            # 파일명이 한글인 경우 cp437로 인코딩되어 있어서 euc-kr로 디코딩
            decoded_path = fileinfo.encode('cp437').decode('euc-kr', 'ignore')
            print('decoded_path', decoded_path)
            extracted_path.rename(os.path.join(dest_dir, decoded_path))
    
    def _unzip_from_data(self, data, dest_dir):
        zip_ref = zipfile.ZipFile(io.BytesIO(data), 'r') 
        for fileinfo in zip_ref.namelist():
            #print(fileinfo.filename)
            #extracted_path = Path(zip_ref.extract(fileinfo))
            extracted_path = Path(zip_ref.extract(fileinfo, dest_dir))
            #print('extracted_path', extracted_path)
    
            # 파일명이 한글인 경우 cp437로 인코딩되어 있어서 euc-kr로 디코딩
            decoded_path = fileinfo.encode('cp437').decode('euc-kr', 'ignore')
            print('decoded_path', decoded_path)
            extracted_path.rename(os.path.join(dest_dir, decoded_path))
    
    def _list_files(self, directory):
        try:
            file_list = os.listdir(directory)
            return file_list
        except FileNotFoundError:
            print(f"Error: Directory '{directory}' not found.")
            return None
        except Exception as e:
            print(f"Error: An error occurred - {e}")
            return None