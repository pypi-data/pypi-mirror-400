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
다운로드 페이지 파싱 모듈

HIRA 다운로드 페이지를 파싱하여 최신 파일을 다운로드합니다.
"""

import logging
import os
import pandas as pd

from lxml import html
from typing import Optional
from urllib.parse import parse_qs

from ..client import HiraClient
from ..models import BoardItem, DownloadFile, DownloadResult, ExcelData, FileType
from ..utils import (
    _START_URL_,
    _DOWNLOAD_BASE_URL_,
    decode_euc_kr,
    get_filename,
)
from .excel import ExcelParser

logger = logging.getLogger(__name__)


class DownloadParser:
    """다운로드 페이지 파싱 클래스"""

    def __init__(self, client: HiraClient, local_path: str = "./data"):
        """
        DownloadParser 초기화
        
        Args:
            client: HiraClient 인스턴스
            local_path: 로컬 저장 경로
        """
        self._client = client
        self._local_path = local_path
        self._excel_parser = ExcelParser(client, local_path)

    def fetch(self) -> Optional[DownloadResult]:
        """
        다운로드 페이지를 파싱하여 최신 파일 다운로드
        
        Returns:
            DownloadResult: 다운로드 결과 객체 (실패 시 None)
        """
        board_items = self._parse_board_page()
        
        if not board_items:
            logger.warning("게시판에서 항목을 찾을 수 없습니다.")
            return None

        # 가장 최신 항목 선택
        latest_item = max(board_items, key=lambda x: x.date)
        logger.info(f"최신 항목 선택: {latest_item.title} ({latest_item.date})")

        # 파일 다운로드
        download_file = self._download_file(latest_item.brd_blt_no)
        if download_file is None:
            return None

        # 엑셀 파싱
        excel_data = self._excel_parser.parse_excel_stream(
            download_file.content,
            download_file.filename,
        )

        # 로컬에 파일 저장
        self._save_file(download_file)

        return DownloadResult(
            filename=download_file.filename,
            excel_data=excel_data,
            board_items=board_items,
        )

    def _parse_board_page(self) -> list[BoardItem]:
        """
        게시판 페이지 파싱
        
        Returns:
            BoardItem 리스트
        """
        url = _START_URL_
        response = self._client._get(url, timeout=60)

        page = html.fromstring(response.content)
        table_rows = page.xpath('//div[@class="tb-type01"]/table/tbody/tr')

        board_items = []
        for row in table_rows:
            td_texts = [td.text_content().strip() for td in row.xpath(".//td")]
            link = row.xpath('.//td[@class="col-tit"]/a/@href')
            file_type = row.xpath('.//td[@class="col-file"]/i/@title')

            brd_blt_no = None
            if link:
                parsed_params = self._parse_params(link[0])
                brd_blt_no = parsed_params.get("brdBltNo")

            if brd_blt_no:
                board_item = BoardItem(
                    title=td_texts[1] if len(td_texts) > 1 else "",
                    brd_blt_no=brd_blt_no,
                    date=td_texts[4] if len(td_texts) > 4 else "",
                    file_type=file_type[0] if file_type else None,
                )
                board_items.append(board_item)

        return board_items

    def _download_file(self, brd_blt_no: str) -> Optional[DownloadFile]:
        """
        파일 다운로드
        
        Args:
            brd_blt_no: 게시물 번호
            
        Returns:
            DownloadFile: 다운로드된 파일 정보 (실패 시 None)
        """
        url = _DOWNLOAD_BASE_URL_
        params = {
            "apndNo": 1,
            "apndBrdBltNo": brd_blt_no,
            "apndBrdTyNo": 1,
            "apndBltNo": 59,
        }

        try:
            response = self._client._get(url, params=params)
            headers = response.headers

            filename = get_filename(headers)
            file_type = self._detect_file_type(filename)

            return DownloadFile(
                filename=filename,
                content=response.content,
                file_type=file_type,
            )
        except Exception as e:
            logger.error(f"파일 다운로드 실패: {e}")
            return None

    def _save_file(self, download_file: DownloadFile) -> str:
        """
        파일을 로컬에 저장
        
        Args:
            download_file: 저장할 파일 정보
            
        Returns:
            저장된 파일 경로
        """
        os.makedirs(self._local_path, exist_ok=True)
        path = os.path.join(self._local_path, download_file.filename)
        
        with open(path, "wb") as file:
            file.write(download_file.content)
        
        logger.info(f"파일 저장 완료: {path}")
        return path

    def _detect_file_type(self, filename: str) -> FileType:
        """
        파일명으로 파일 유형 감지
        
        Args:
            filename: 파일명
            
        Returns:
            FileType: 파일 유형
        """
        lower_name = filename.lower()
        if lower_name.endswith((".xlsx", ".xls")):
            return FileType.EXCEL
        elif lower_name.endswith(".zip"):
            return FileType.ZIP
        elif lower_name.endswith(".csv"):
            return FileType.CSV
        return FileType.UNKNOWN

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