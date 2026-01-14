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
Nedrug 데이터 모델 정의

의약품 정보 및 다운로드 관련 데이터를 담는 dataclass들을 정의합니다.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class FileType(Enum):
    """파일 유형 열거형"""
    EXCEL = "excel"
    XLS = "xls"
    XLSX = "xlsx"
    CSV = "csv"
    UNKNOWN = "unknown"


class CancelCode(Enum):
    """취소 코드 열거형"""
    ACTIVE = ""  # 정상
    CANCELLED = "1"  # 취소


class EtcOtcCode(Enum):
    """전문/일반 구분 코드"""
    PROFESSIONAL = "전문의약품"  # 전문
    GENERAL = "일반의약품"  # 일반


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

    @classmethod
    def detect_file_type(cls, filename: str) -> FileType:
        """파일명으로 파일 유형 감지"""
        lower_name = filename.lower()
        if lower_name.endswith(".xlsx"):
            return FileType.XLSX
        elif lower_name.endswith(".xls"):
            return FileType.XLS
        elif lower_name.endswith(".csv"):
            return FileType.CSV
        return FileType.UNKNOWN


@dataclass
class Medicine:
    """의약품 정보"""
    id: int
    item_seq: str  # 품목기준코드
    product_name: str  # 품목명
    product_name_eng: Optional[str] = None  # 품목명(영문)
    company_name: Optional[str] = None  # 업체명
    company_name_eng: Optional[str] = None  # 업체명(영문)
    permit_date: Optional[str] = None  # 허가일자
    cancel_date: Optional[str] = None  # 취소일자
    cancel_name: Optional[str] = None  # 상태 (정상/취소)
    etc_otc_name: Optional[str] = None  # 전문/일반
    chart: Optional[str] = None  # 성상
    material_name: Optional[str] = None  # 원료성분
    storage_method: Optional[str] = None  # 저장방법
    valid_term: Optional[str] = None  # 유효기간
    pack_unit: Optional[str] = None  # 포장단위
    reexam_target: Optional[str] = None  # 재심사대상
    reexam_date: Optional[str] = None  # 재심사기간
    induty_type: Optional[str] = None  # 업종구분
    standard_code: Optional[str] = None  # 표준코드
    atc_code: Optional[str] = None  # ATC코드
    narcotic_kind: Optional[str] = None  # 마약종류
    is_new_drug: Optional[str] = None  # 신약여부
    insert_file: Optional[str] = None  # 첨부문서
    change_date: Optional[str] = None  # 변경일자

    @classmethod
    def from_tuple(cls, row: tuple, columns: dict, index: int = 0) -> "Medicine":
        """
        튜플 데이터에서 Medicine 인스턴스 생성
        
        Args:
            row: 엑셀에서 파싱된 튜플 데이터
            columns: 컬럼 매핑 딕셔너리 (GEMINI_COLUMNS)
            index: 의약품 ID (순번)
            
        Returns:
            Medicine 인스턴스
        """
        keys = list(columns.keys())
        data = dict(zip(keys, row))

        return cls(
            id=index,
            item_seq=data.get("item_seq", ""),
            product_name=data.get("product_name", ""),
            product_name_eng=data.get("product_name_eng"),
            company_name=data.get("company_name"),
            company_name_eng=data.get("company_name_eng"),
            permit_date=data.get("permit_date"),
            cancel_date=data.get("cancel_date"),
            cancel_name=data.get("cancel_name"),
            etc_otc_name=data.get("etc_otc_name"),
            chart=data.get("chart"),
            material_name=data.get("material_name"),
            storage_method=data.get("storage_method"),
            valid_term=data.get("valid_term"),
            pack_unit=data.get("pack_unit"),
            reexam_target=data.get("reexam_target"),
            reexam_date=data.get("reexam_date"),
            induty_type=data.get("induty_type"),
            standard_code=data.get("standard_code"),
            atc_code=data.get("atc_code"),
            narcotic_kind=data.get("narcotic_kind"),
            is_new_drug=data.get("is_new_drug"),
            insert_file=data.get("insert_file"),
            change_date=data.get("change_date"),
        )

    @classmethod
    def from_dict(cls, data: dict, index: int = 0) -> "Medicine":
        """딕셔너리에서 Medicine 인스턴스 생성"""
        return cls(
            id=index,
            item_seq=data.get("item_seq", ""),
            product_name=data.get("product_name", ""),
            product_name_eng=data.get("product_name_eng"),
            company_name=data.get("company_name"),
            company_name_eng=data.get("company_name_eng"),
            permit_date=data.get("permit_date"),
            cancel_date=data.get("cancel_date"),
            cancel_name=data.get("cancel_name"),
            etc_otc_name=data.get("etc_otc_name"),
            chart=data.get("chart"),
            material_name=data.get("material_name"),
            storage_method=data.get("storage_method"),
            valid_term=data.get("valid_term"),
            pack_unit=data.get("pack_unit"),
            reexam_target=data.get("reexam_target"),
            reexam_date=data.get("reexam_date"),
            induty_type=data.get("induty_type"),
            standard_code=data.get("standard_code"),
            atc_code=data.get("atc_code"),
            narcotic_kind=data.get("narcotic_kind"),
            is_new_drug=data.get("is_new_drug"),
            insert_file=data.get("insert_file"),
            change_date=data.get("change_date"),
        )

    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return {
            "id": self.id,
            "item_seq": self.item_seq,
            "product_name": self.product_name,
            "product_name_eng": self.product_name_eng,
            "company_name": self.company_name,
            "company_name_eng": self.company_name_eng,
            "permit_date": self.permit_date,
            "cancel_date": self.cancel_date,
            "cancel_name": self.cancel_name,
            "etc_otc_name": self.etc_otc_name,
            "chart": self.chart,
            "material_name": self.material_name,
            "storage_method": self.storage_method,
            "valid_term": self.valid_term,
            "pack_unit": self.pack_unit,
            "reexam_target": self.reexam_target,
            "reexam_date": self.reexam_date,
            "induty_type": self.induty_type,
            "standard_code": self.standard_code,
            "atc_code": self.atc_code,
            "narcotic_kind": self.narcotic_kind,
            "is_new_drug": self.is_new_drug,
            "insert_file": self.insert_file,
            "change_date": self.change_date,
        }

    @property
    def is_cancelled(self) -> bool:
        """취소 여부"""
        return self.cancel_name == "취소" or self.cancel_date is not None

    @property
    def is_professional(self) -> bool:
        """전문의약품 여부"""
        return self.etc_otc_name == "전문의약품"


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
class SearchParams:
    """의약품 검색 파라미터"""
    item_name: str = ""  # 품목명
    item_name_eng: str = ""  # 품목명(영문)
    company_name: str = ""  # 업체명
    company_name_eng: str = ""  # 업체명(영문)
    ingredient_name: str = ""  # 성분명
    item_seq: str = ""  # 품목기준코드
    standard_code: str = ""  # 표준코드
    atc_code: str = ""  # ATC코드
    cancel_code: str = ""  # 취소여부
    etc_otc_code: str = ""  # 전문/일반
    narcotic_kind_code: str = ""  # 마약종류
    start_permit_date: str = ""  # 허가일자 시작
    end_permit_date: str = ""  # 허가일자 종료

    def to_payload(self, page_num: int = 0, page_size: int = 10000) -> dict:
        """API 요청 페이로드로 변환"""
        return {
            "ExcelRowdata": f"{page_num * page_size}",
            "excelSearchCnt": page_size,
            "page": 1,
            "sort": "",
            "sortOrder": "",
            "searchYn": "",
            "searchDivision": "detail",
            "itemName": self.item_name,
            "itemEngName": self.item_name_eng,
            "entpName": self.company_name,
            "entpEngName": self.company_name_eng,
            "ingrName1": self.ingredient_name,
            "ingrName2": "",
            "ingrName3": "",
            "ingrEngName": "",
            "itemSeq": self.item_seq,
            "stdrCodeName": self.standard_code,
            "atcCodeName": self.atc_code,
            "indutyClassCode": "",
            "sClassNo": "",
            "narcoticKindCode": self.narcotic_kind_code,
            "cancelCode": self.cancel_code,
            "etcOtcCode": self.etc_otc_code,
            "makeMaterialGb": "",
            "searchConEe": "AND",
            "eeDocData": "",
            "searchConUd": "AND",
            "udDocData": "",
            "searchConNb": "AND",
            "nbDocData": "",
            "startPermitDate": self.start_permit_date,
            "endPermitDate": self.end_permit_date,
        }


@dataclass
class PageResult:
    """페이지 단위 다운로드 결과"""
    page_num: int
    filename: str
    download_file: Optional[DownloadFile]
    medicines: list[Medicine]
    has_more: bool = True

    @property
    def medicine_count(self) -> int:
        """의약품 수"""
        return len(self.medicines)

    @property
    def is_empty(self) -> bool:
        """결과가 비어있는지 확인"""
        return len(self.medicines) == 0


@dataclass
class DownloadResult:
    """전체 다운로드 결과"""
    medicines: list[Medicine]
    page_results: list[PageResult] = field(default_factory=list)
    total_pages: int = 0
    downloaded_at: datetime = field(default_factory=datetime.now)

    @property
    def total_count(self) -> int:
        """전체 의약품 수"""
        return len(self.medicines)

    @property
    def is_empty(self) -> bool:
        """결과가 비어있는지 확인"""
        return len(self.medicines) == 0

    def get_by_item_seq(self, item_seq: str) -> Optional[Medicine]:
        """품목기준코드로 의약품 조회"""
        for medicine in self.medicines:
            if medicine.item_seq == item_seq:
                return medicine
        return None

    def filter_by_company(self, company_name: str) -> list[Medicine]:
        """업체명으로 필터링"""
        return [m for m in self.medicines if m.company_name and company_name in m.company_name]

    def filter_active(self) -> list[Medicine]:
        """정상(취소되지 않은) 의약품만 필터링"""
        return [m for m in self.medicines if not m.is_cancelled]

    def filter_professional(self) -> list[Medicine]:
        """전문의약품만 필터링"""
        return [m for m in self.medicines if m.is_professional]

    def filter_general(self) -> list[Medicine]:
        """일반의약품만 필터링"""
        return [m for m in self.medicines if not m.is_professional]