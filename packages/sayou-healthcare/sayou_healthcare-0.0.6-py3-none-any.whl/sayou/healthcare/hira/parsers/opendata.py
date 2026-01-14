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

"""
공공데이터 파싱 모듈

HIRA 공공데이터 포털에서 병원/약국 데이터를 다운로드하고 파싱합니다.
"""

import csv
import io
import logging
import os
import re
import zipfile

from io import BytesIO
from lxml import html
from pathlib import Path
from typing import Optional
from urllib.parse import unquote

from ..client import HiraClient
from ..models import (
    DownloadFile,
    ExcelData,
    FileType,
    Hospital,
    OpenDataResult,
    Pharmacy,
)
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

logger = logging.getLogger(__name__)


class OpenDataParser:
    """공공데이터 파싱 클래스"""

    HOSPITAL_FILE_PREFIX = "1.병원정보서비스"
    PHARMACY_FILE_PREFIX = "2.약국정보서비스"
    DEST_DIR = "opendata_hira_data"

    def __init__(self, client: HiraClient, local_path: str = "./data"):
        """
        OpenDataParser 초기화
        
        Args:
            client: HiraClient 인스턴스
            local_path: 로컬 저장 경로
        """
        self._client = client
        self._local_path = local_path
        self._excel_parser = ExcelParser(client, local_path)

        self._hospital_data = None
        self._pharmacy_data = None

    def fetch(self, is_cleanup_files: bool = True) -> Optional[OpenDataResult]:
        """
        공공데이터 다운로드 및 파싱
        
        Args:
            is_cleanup_files: 압축 해제된 파일 정리 여부
        
        Returns:
            OpenDataResult: 파싱 결과 (실패 시 None)
        """
        # ZIP 파일 다운로드
        download_file = self._download_latest_file()
        if download_file is None:
            return None

        # ZIP 파일 압축 해제
        extracted_files = self._extract_zip(download_file.content, self.DEST_DIR)
        logger.info(f"압축 해제 완료: {len(extracted_files)}개 파일")

        # 병원 데이터 파싱
        self._hospital_data = self._parse_service_file(
            extracted_files,
            self.HOSPITAL_FILE_PREFIX,
        )

        # 약국 데이터 파싱
        self._pharmacy_data = self._parse_service_file(
            extracted_files,
            self.PHARMACY_FILE_PREFIX,
        )

        # 임시 파일 정리
        if is_cleanup_files:
            self._cleanup_extracted_files(extracted_files, self.DEST_DIR)

        return OpenDataResult(
            download_file=download_file,
            hospital_data=self._hospital_data,
            pharmacy_data=self._pharmacy_data,
            extracted_files=extracted_files,
        )

    def hospitals(self):
        if self._hospital_data:
            return self._hospital_data

        self.fetch()
        return self._hospital_data

    def pharmacies(self):
        if self._pharmacy_data:
            return self._pharmacy_data

        self.fetch()
        return self._pharmacy_data

    def get_hospitals(
        self,
        result: OpenDataResult,
        columns: Optional[dict] = None,
    ) -> list[Hospital]:
        """
        OpenDataResult에서 Hospital 객체 리스트 추출
        
        Args:
            result: OpenDataResult 객체
            columns: 컬럼 매핑 (기본: HOSPITAL_COLUMNS)
            
        Returns:
            Hospital 리스트
        """
        if not result.has_hospital_data:
            return []

        columns = columns or HOSPITAL_COLUMNS
        hospitals = []
        
        for idx, row in enumerate(result.hospital_data.get_data_rows(), start=1):
            if self._is_header_row(row, "암호화요양기호"):
                continue
            hospital = Hospital.from_tuple(row, columns, idx)
            hospitals.append(hospital)

        return hospitals

    def get_pharmacies(
        self,
        result: OpenDataResult,
        columns: Optional[dict] = None,
    ) -> list[Pharmacy]:
        """
        OpenDataResult에서 Pharmacy 객체 리스트 추출
        
        Args:
            result: OpenDataResult 객체
            columns: 컬럼 매핑 (기본: PHARMACY_COLUMNS)
            
        Returns:
            Pharmacy 리스트
        """
        if not result.has_pharmacy_data:
            return []

        columns = columns or PHARMACY_COLUMNS
        pharmacies = []
        
        for idx, row in enumerate(result.pharmacy_data.get_data_rows(), start=1):
            if self._is_header_row(row, "암호화요양기호"):
                continue
            pharmacy = Pharmacy.from_tuple(row, columns, idx)
            pharmacies.append(pharmacy)

        return pharmacies

    def save_hospitals_to_csv(
        self,
        hospitals: list[Hospital],
        file_path: str,
        encoding: str = "utf-8-sig",
    ) -> None:
        """
        Hospital 리스트를 CSV로 저장
        
        Args:
            hospitals: Hospital 리스트
            file_path: 저장할 파일 경로
            encoding: 파일 인코딩
        """
        with open(file_path, "w", newline="", encoding=encoding) as file:
            writer = csv.writer(file)
            writer.writerow(["id", "name", "address"])
            
            for hospital in hospitals:
                writer.writerow([hospital.id, hospital.name, hospital.address])

    def save_pharmacies_to_csv(
        self,
        pharmacies: list[Pharmacy],
        file_path: str,
        encoding: str = "utf-8-sig",
    ) -> None:
        """
        Pharmacy 리스트를 CSV로 저장
        
        Args:
            pharmacies: Pharmacy 리스트
            file_path: 저장할 파일 경로
            encoding: 파일 인코딩
        """
        with open(file_path, "w", newline="", encoding=encoding) as file:
            writer = csv.writer(file)
            writer.writerow(["id", "name", "address"])
            
            for pharmacy in pharmacies:
                writer.writerow([pharmacy.id, pharmacy.name, pharmacy.address])

    def _download_latest_file(self) -> Optional[DownloadFile]:
        """
        최신 파일 다운로드
        
        Returns:
            DownloadFile: 다운로드된 파일 정보 (실패 시 None)
        """
        download_code = self._get_latest_download_code()
        if download_code is None:
            logger.error("다운로드 코드를 찾을 수 없습니다.")
            return None

        return self._download_file(download_code)

    def _get_latest_download_code(self) -> Optional[str]:
        """
        최신 다운로드 코드 조회
        
        Returns:
            다운로드 코드 (실패 시 None)
        """
        url = _OPENDATA_START_URL_
        
        try:
            response = self._client._get(url)
            page = html.fromstring(response.content)

            li_rows = page.xpath('//dl[@class="fileList ml00"]/dd/ul/li/a/@href')
            onclicks = [re.search(r"fn_fileDown\('(.+?)'\)", row) for row in li_rows]
            onclicks = [match.group(1) for match in onclicks if match]

            if not onclicks:
                return None

            onclicks.sort(reverse=True)
            return onclicks[0]
        except Exception as e:
            logger.error(f"다운로드 코드 조회 실패: {e}")
            return None

    def _download_file(self, download_code: str) -> Optional[DownloadFile]:
        """
        파일 다운로드
        
        Args:
            download_code: 다운로드 코드
            
        Returns:
            DownloadFile: 다운로드된 파일 정보 (실패 시 None)
        """
        url = _OPENDATA_DOWNLOAD_URL_
        payload = {
            "customValue": download_code,
            "d00": "UlpEQXhER1J2ZDI1c2IyRmtVbVZ4ZFdWemRBdGtNVEFNWHd0a01qVU1MM05vWVhKbFpDOWtZWFJoTDNWd2JHOWhaRVpwYkdWekwyWnBiR1V2T0RrNU56WXhPVVl0T0VJNFJpMURSRFU0TFRkQ05qa3RNVUZEUlRKR09UaEVOa0V5TG5wcGNBdGtNallNN0tDRTZyV3RJT3V6a2V5ZG1PeWJrQ0Ryc0k4ZzdKVzk2cld0SU8yWWhPMlpxU0F5TURJMExqRXlMbnBwY0F0a01EY01ORGN4UVVaRVF6RXRORGRCTXkxRVFUSTJMVE16UlRjdFJrUkdNMFJFTWtFd1FqTkRDdz09",
        }

        try:
            response = self._client._post(url, body=payload)
            headers = response.headers

            filename = get_filename(headers)
            logger.info(f"다운로드 완료: {filename}")

            return DownloadFile(
                filename=unquote(filename),
                content=response.content,
                file_type=FileType.ZIP,
            )
        except Exception as e:
            logger.error(f"파일 다운로드 실패: {e}")
            return None

    def _extract_zip(self, data: bytes, dest_dir: str) -> list[str]:
        """
        ZIP 파일 압축 해제
        
        Args:
            data: ZIP 파일 바이트 데이터
            dest_dir: 압축 해제 대상 디렉토리
            
        Returns:
            압축 해제된 파일명 리스트
        """
        os.makedirs(dest_dir, exist_ok=True)
        extracted_files = []

        with zipfile.ZipFile(io.BytesIO(data), "r") as zip_ref:
            for fileinfo in zip_ref.namelist():
                extracted_path = Path(zip_ref.extract(fileinfo, dest_dir))

                # 한글 파일명 디코딩 (cp437 -> euc-kr)
                decoded_name = fileinfo.encode("cp437").decode("euc-kr", "ignore")
                final_path = os.path.join(dest_dir, decoded_name)
                
                extracted_path.rename(final_path)
                extracted_files.append(decoded_name)
                logger.debug(f"압축 해제: {decoded_name}")

        return extracted_files

    def _save_zip_contents(
        self,
        data: bytes,
        dest_dir: Optional[str] = None,
        overwrite: bool = False,
    ) -> list[str]:
        """
        ZIP 파일 내용을 로컬에 저장
        
        Args:
            data: ZIP 파일 바이트 데이터
            dest_dir: 저장할 디렉토리 경로 (기본: self._local_path)
            overwrite: 기존 파일 덮어쓰기 여부
            
        Returns:
            저장된 파일 경로 리스트
        """
        dest_dir = dest_dir or self._local_path
        os.makedirs(dest_dir, exist_ok=True)
        saved_files = []

        with zipfile.ZipFile(io.BytesIO(data), "r") as zip_ref:
            for fileinfo in zip_ref.namelist():
                # 한글 파일명 디코딩 (cp437 -> euc-kr)
                decoded_name = fileinfo.encode("cp437").decode("euc-kr", "ignore")
                final_path = os.path.join(dest_dir, decoded_name)
                
                # 기존 파일 존재 시 처리
                if os.path.exists(final_path) and not overwrite:
                    logger.warning(f"파일이 이미 존재합니다 (건너뜀): {final_path}")
                    continue
                
                # 디렉토리인 경우 생성만
                if fileinfo.endswith("/"):
                    os.makedirs(final_path, exist_ok=True)
                    continue
                
                # 파일 저장
                with zip_ref.open(fileinfo) as src, open(final_path, "wb") as dst:
                    dst.write(src.read())
                
                saved_files.append(final_path)
                logger.info(f"파일 저장: {final_path}")

        return saved_files

    def _parse_service_file(
        self,
        extracted_files: list[str],
        file_prefix: str,
    ) -> Optional[ExcelData]:
        """
        서비스 엑셀 파일 파싱
        
        Args:
            extracted_files: 압축 해제된 파일 리스트
            file_prefix: 파일명 접두사
            
        Returns:
            ExcelData: 파싱된 데이터 (파일이 없으면 None)
        """
        matching_files = [f for f in extracted_files if file_prefix in f]
        
        if not matching_files:
            logger.warning(f"'{file_prefix}' 파일을 찾을 수 없습니다.")
            return None

        file_path = os.path.join(self.DEST_DIR, matching_files[0])
        logger.info(f"파싱 중: {matching_files[0]}")

        return self._excel_parser.parse_excel_file(file_path)

    def _cleanup_extracted_files(self, files: list[str], directory: str) -> None:
        """
        압축 해제된 파일 정리
        
        Args:
            files: 파일명 리스트
            directory: 디렉토리 경로
        """
        for file in files:
            file_path = os.path.join(directory, file)
            try:
                os.remove(file_path)
                logger.debug(f"파일 삭제: {file_path}")
            except OSError as e:
                logger.warning(f"파일 삭제 실패: {file_path} - {e}")

    def _is_header_row(self, row: tuple, keyword: str) -> bool:
        """
        헤더 행인지 확인
        
        Args:
            row: 확인할 행
            keyword: 헤더 식별 키워드
            
        Returns:
            True: 헤더 행인 경우
        """
        for item in row:
            if item and isinstance(item, str) and keyword in item:
                return True
        return False
