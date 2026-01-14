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
HIRA 데이터 모델 정의

병원, 약국, 다운로드 파일 등의 데이터를 담는 dataclass들을 정의합니다.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from urllib.parse import unquote

class FileType(Enum):
    """파일 유형 열거형"""
    EXCEL = "excel"
    ZIP = "zip"
    CSV = "csv"
    UNKNOWN = "unknown"


@dataclass
class DownloadFile:
    """다운로드 파일 정보"""
    filename: str
    content: bytes
    file_type: FileType = FileType.UNKNOWN
    downloaded_at: datetime = field(default_factory=datetime.now)

    @property
    def size(self) -> int:
        """파일 크기 (bytes)"""
        return len(self.content)

    @property
    def size_kb(self) -> float:
        """파일 크기 (KB)"""
        return self.size / 1024

    @property
    def size_mb(self) -> float:
        """파일 크기 (MB)"""
        return self.size / (1024 * 1024)


@dataclass
class Hospital:
    """병원 정보"""
    id: int
    name: str
    address: str
    encrypted_institution_code: Optional[str] = None
    institution_type: Optional[str] = None
    sido: Optional[str] = None
    sigungu: Optional[str] = None
    zip_code: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    opening_date: Optional[str] = None
    total_beds: Optional[int] = None
    total_doctors: Optional[int] = None

    @classmethod
    def from_tuple(cls, row: tuple, columns: dict, index: int = 0) -> "Hospital":
        """
        튜플 데이터에서 Hospital 인스턴스 생성
        
        Args:
            row: 엑셀에서 파싱된 튜플 데이터
            columns: 컬럼 매핑 딕셔너리
            index: 병원 ID (순번)
            
        Returns:
            Hospital 인스턴스
        """
        keys = list(columns.keys())
        data = dict(zip(keys, row))
        
        return cls(
            id=index,
            name=data.get("medical_institution_name", ""),
            address=data.get("address", ""),
            encrypted_institution_code=data.get("encrypted_institution_code"),
            institution_type=data.get("institution_type"),
            sido=data.get("sido"),
            sigungu=data.get("sigungu"),
            zip_code=data.get("zip_code"),
            phone=data.get("phone"),
            website=data.get("website"),
            opening_date=data.get("opening_date"),
            total_beds=cls._parse_int(data.get("total_beds")),
            total_doctors=cls._parse_int(data.get("total_doctors")),
        )

    @staticmethod
    def _parse_int(value) -> Optional[int]:
        """안전하게 정수로 변환"""
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None


@dataclass
class Pharmacy:
    """약국 정보"""
    id: int
    name: str
    address: str
    encrypted_institution_code: Optional[str] = None
    sido: Optional[str] = None
    sigungu: Optional[str] = None
    zip_code: Optional[str] = None
    phone: Optional[str] = None
    opening_date: Optional[str] = None

    @classmethod
    def from_tuple(cls, row: tuple, columns: dict, index: int = 0) -> "Pharmacy":
        """
        튜플 데이터에서 Pharmacy 인스턴스 생성
        
        Args:
            row: 엑셀에서 파싱된 튜플 데이터
            columns: 컬럼 매핑 딕셔너리
            index: 약국 ID (순번)
            
        Returns:
            Pharmacy 인스턴스
        """
        keys = list(columns.keys())
        data = dict(zip(keys, row))
        
        return cls(
            id=index,
            name=data.get("pharmacy_name", ""),
            address=data.get("address", ""),
            encrypted_institution_code=data.get("encrypted_institution_code"),
            sido=data.get("sido"),
            sigungu=data.get("sigungu"),
            zip_code=data.get("zip_code"),
            phone=data.get("phone"),
            opening_date=data.get("opening_date"),
        )


@dataclass
class BoardItem:
    """게시판 항목 정보"""
    title: str
    brd_blt_no: str
    date: str
    file_type: Optional[str] = None
    author: Optional[str] = None
    views: Optional[int] = None

    @classmethod
    def from_row(cls, row: list) -> "BoardItem":
        """
        파싱된 행 데이터에서 BoardItem 인스턴스 생성
        
        Args:
            row: 파싱된 행 데이터 리스트
            
        Returns:
            BoardItem 인스턴스
        """
        return cls(
            title=row[1] if len(row) > 1 else "",
            brd_blt_no=row[2] if len(row) > 2 else "",
            date=row[4] if len(row) > 4 else "",
            file_type=row[-1] if len(row) > 0 else None,
        )


@dataclass
class ExcelData:
    """엑셀 파싱 결과 데이터"""
    filename: str
    rows: list[tuple]
    sheet_name: Optional[str] = None
    parsed_at: datetime = field(default_factory=datetime.now)

    @property
    def row_count(self) -> int:
        """데이터 행 수"""
        return len(self.rows)

    @property
    def is_empty(self) -> bool:
        """데이터가 비어있는지 확인"""
        return len(self.rows) == 0

    def get_header(self) -> Optional[tuple]:
        """헤더 행 반환"""
        return self.rows[0] if self.rows else None

    def get_data_rows(self) -> list[tuple]:
        """헤더를 제외한 데이터 행들 반환"""
        return self.rows[1:] if len(self.rows) > 1 else []


@dataclass
class OpenDataResult:
    """공공데이터 파싱 결과"""
    download_file: DownloadFile
    hospital_data: Optional[ExcelData] = None
    pharmacy_data: Optional[ExcelData] = None
    extracted_files: list[str] = field(default_factory=list)

    @property
    def has_hospital_data(self) -> bool:
        """병원 데이터 존재 여부"""
        return self.hospital_data is not None and not self.hospital_data.is_empty

    @property
    def has_pharmacy_data(self) -> bool:
        """약국 데이터 존재 여부"""
        return self.pharmacy_data is not None and not self.pharmacy_data.is_empty


@dataclass
class DownloadResult:
    """다운로드 파싱 결과"""
    filename: str
    excel_data: ExcelData
    board_items: list[BoardItem] = field(default_factory=list)

    @property
    def latest_item(self) -> Optional[BoardItem]:
        """가장 최신 게시물 반환"""
        if not self.board_items:
            return None
        return max(self.board_items, key=lambda x: x.date)