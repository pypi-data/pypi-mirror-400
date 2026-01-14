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
의약품 데이터 다운로드 파싱 모듈

Nedrug 사이트에서 의약품 데이터를 페이지 단위로 다운로드하고 파싱합니다.
"""

import csv
import logging
import os
import unicodedata

from bs4 import BeautifulSoup
from typing import Optional
from urllib.parse import parse_qs, unquote

from ..client import NedrugClient
from ..models import (
    DownloadFile,
    DownloadResult,
    ExcelData,
    FileType,
    Medicine,
    PageResult,
    SearchParams,
)
from ..utils import (
    _NEDRUG_EXCEL_URL_,
    GEMINI_COLUMNS,
    decode_euc_kr,
    get_filename,
)
from .excel import ExcelParser

logger = logging.getLogger(__name__)


class DownloadParser:
    """의약품 데이터 다운로드 파서"""

    DEFAULT_PAGE_SIZE = 10000
    MEDICINE_LIST_FILE = "medicine_list_nedrug.csv"
    HEADER_KEYWORD = "품목기준코드"

    def __init__(
        self,
        client: NedrugClient,
        local_path: str = "./data",
        page_size: int = DEFAULT_PAGE_SIZE,
    ):
        """
        DownloadParser 초기화
        
        Args:
            client: NedrugClient 인스턴스
            local_path: 로컬 저장 경로
            page_size: 페이지당 데이터 수
        """
        self._client = client
        self._local_path = local_path
        self._page_size = page_size
        self._excel_parser = ExcelParser(client)

    def fetch(self, search_params: Optional[SearchParams] = None) -> DownloadResult:
        """
        전체 의약품 데이터 다운로드 및 파싱
        
        Args:
            search_params: 검색 파라미터 (기본: 전체 조회)
            
        Returns:
            DownloadResult: 다운로드 결과
        """
        if search_params is None:
            search_params = SearchParams()

        page_num = 0
        all_medicines: list[Medicine] = []
        page_results: list[PageResult] = []

        while True:
            page_result = self._download_page(page_num, search_params)

            if page_result.is_empty:
                page_result.has_more = False
                break

            all_medicines.extend(page_result.medicines)
            page_results.append(page_result)

            logger.info(
                f"페이지 {page_num + 1} 완료: {page_result.medicine_count}개 의약품"
            )

            if not page_result.has_more:
                break

            page_num += 1

        result = DownloadResult(
            medicines=all_medicines,
            page_results=page_results,
            total_pages=page_num + 1,
        )

        logger.info(f"전체 다운로드 완료: {result.total_count}개 의약품")
        return result

    def fetch_and_save(
        self,
        search_params: Optional[SearchParams] = None,
        csv_path: Optional[str] = None,
    ) -> DownloadResult:
        """
        의약품 데이터 다운로드 후 CSV 저장
        
        Args:
            search_params: 검색 파라미터
            csv_path: CSV 저장 경로 (기본: medicine_list_nedrug.csv)
            
        Returns:
            DownloadResult: 다운로드 결과
        """
        result = self.fetch(search_params)

        if not result.is_empty:
            csv_path = csv_path or self.MEDICINE_LIST_FILE
            self.save_to_csv(result.medicines, csv_path)
            logger.info(f"CSV 저장 완료: {csv_path}")

        return result

    def save_to_csv(
        self,
        medicines: list[Medicine],
        file_path: str,
        encoding: str = "utf-8-sig",
    ) -> None:
        """
        Medicine 리스트를 CSV로 저장
        
        Args:
            medicines: Medicine 리스트
            file_path: 저장할 파일 경로
            encoding: 파일 인코딩
        """
        with open(file_path, "w", newline="", encoding=encoding) as file:
            writer = csv.writer(file)
            writer.writerow(["id", "name"])

            for medicine in medicines:
                writer.writerow([medicine.id, medicine.product_name])

    def save_full_to_csv(
        self,
        medicines: list[Medicine],
        file_path: str,
        encoding: str = "utf-8-sig",
    ) -> None:
        """
        Medicine 리스트를 전체 필드로 CSV 저장
        
        Args:
            medicines: Medicine 리스트
            file_path: 저장할 파일 경로
            encoding: 파일 인코딩
        """
        if not medicines:
            return

        with open(file_path, "w", newline="", encoding=encoding) as file:
            writer = csv.DictWriter(file, fieldnames=medicines[0].to_dict().keys())
            writer.writeheader()

            for medicine in medicines:
                writer.writerow(medicine.to_dict())

    def _download_page(
        self,
        page_num: int,
        search_params: SearchParams,
    ) -> PageResult:
        """
        단일 페이지 다운로드
        
        Args:
            page_num: 페이지 번호 (0부터 시작)
            search_params: 검색 파라미터
            
        Returns:
            PageResult: 페이지 다운로드 결과
        """
        payload = search_params.to_payload(page_num, self._page_size)
        url = _NEDRUG_EXCEL_URL_

        try:
            response = self._client._post(url, body=payload, timeout=60)
            headers = response.headers

            filename = get_filename(headers)
            if not filename:
                return PageResult(
                    page_num=page_num,
                    filename="",
                    download_file=None,
                    medicines=[],
                    has_more=False,
                )

            # URL 디코딩
            decoded_filename = unquote(filename)
            logger.debug(f"다운로드 파일: {decoded_filename}")

            # 엑셀 파싱
            excel_data = self._excel_parser.parse_excel_stream(
                response.content,
                decoded_filename,
            )

            if excel_data.row_count <= 1:
                return PageResult(
                    page_num=page_num,
                    filename=decoded_filename,
                    download_file=None,
                    medicines=[],
                    has_more=False,
                )

            # Medicine 객체로 변환
            medicines = self._convert_to_medicines(excel_data, page_num)

            # 파일명 생성 (페이지 정보 포함)
            final_filename = self._generate_filename(
                decoded_filename,
                page_num,
                len(medicines),
            )

            # 로컬 저장
            download_file = self._save_file(final_filename, response.content)

            # 다음 페이지 존재 여부
            has_more = len(excel_data.rows) >= (self._page_size + 1)

            return PageResult(
                page_num=page_num,
                filename=final_filename,
                download_file=download_file,
                medicines=medicines,
                has_more=has_more,
            )

        except Exception as e:
            logger.error(f"페이지 {page_num} 다운로드 실패: {e}")
            return PageResult(
                page_num=page_num,
                filename="",
                download_file=None,
                medicines=[],
                has_more=False,
            )

    def _convert_to_medicines(
        self,
        excel_data: ExcelData,
        page_num: int,
    ) -> list[Medicine]:
        """
        ExcelData를 Medicine 리스트로 변환
        
        Args:
            excel_data: 엑셀 데이터
            page_num: 페이지 번호
            
        Returns:
            Medicine 리스트
        """
        medicines = []
        base_index = page_num * self._page_size

        for idx, row in enumerate(excel_data.rows):
            if self._is_header_row(row):
                continue

            medicine = Medicine.from_tuple(
                row,
                GEMINI_COLUMNS,
                base_index + idx,
            )
            medicines.append(medicine)

        return medicines

    def _generate_filename(
        self,
        original_filename: str,
        page_num: int,
        row_count: int,
    ) -> str:
        """
        페이지 정보가 포함된 파일명 생성
        
        Args:
            original_filename: 원본 파일명
            page_num: 페이지 번호
            row_count: 행 수
            
        Returns:
            생성된 파일명
        """
        if row_count >= self._page_size:
            file_suffix = (page_num + 1) * self._page_size
        else:
            file_suffix = page_num * self._page_size + row_count

        if original_filename and ".xls" in original_filename.lower():
            return original_filename.replace(".xls", f"_{file_suffix}.xls")
        return f"medicine_data_{file_suffix}.xls"

    def _save_file(self, filename: str, content: bytes) -> DownloadFile:
        """
        파일을 로컬에 저장
        
        Args:
            filename: 파일명
            content: 파일 내용
            
        Returns:
            DownloadFile: 저장된 파일 정보
        """
        os.makedirs(self._local_path, exist_ok=True)

        path = os.path.join(self._local_path, filename)
        with open(path, "wb") as f:
            f.write(content)

        logger.debug(f"파일 저장: {path}")

        return DownloadFile(
            filename=filename,
            content=content,
            file_type=DownloadFile.detect_file_type(filename),
        )

    def _is_header_row(self, row: tuple) -> bool:
        """
        헤더 행인지 확인
        
        Args:
            row: 확인할 행
            
        Returns:
            True: 헤더 행인 경우
        """
        for item in row:
            if item and isinstance(item, str) and self.HEADER_KEYWORD in item:
                return True
        return False

    def _parse_params(self, query_string: str) -> dict:
        """
        쿼리 문자열 파싱
        
        Args:
            query_string: 쿼리 문자열
            
        Returns:
            파싱된 파라미터 딕셔너리
        """
        parsed_params = parse_qs(query_string.lstrip("?"))
        parsed_params = {k: v[0] if len(v) == 1 else v for k, v in parsed_params.items()}
        return parsed_params

    def _extract_ul(self, text: str) -> str:
        """
        HTML에서 <li> 태그의 텍스트를 추출하여 개행하여 반환
        
        Args:
            text: HTML 문자열
            
        Returns:
            개행된 문자열
        """
        soup = BeautifulSoup(text, "html.parser")
        li_texts = [
            unicodedata.normalize("NFKC", li.get_text(strip=True))
            for li in soup.find_all("li")
        ]
        return "\n".join(map(str, li_texts))

    def _convert_table_to_csv(self, table) -> list[list[str]]:
        """
        HTML 테이블을 CSV 형식으로 변환
        
        Args:
            table: BeautifulSoup 테이블 요소
            
        Returns:
            CSV 형식의 2차원 리스트
        """
        rows = []
        for row in table.find_all("tr"):
            cells = [cell.get_text(strip=True) for cell in row.find_all(["th", "td"])]
            rows.append(cells)
        return rows