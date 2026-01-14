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

"""Data models for medicine information."""

from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class Medicine:
    """의약품 정보를 담는 데이터 클래스."""
    
    name: str
    code: Optional[str] = None
    ingredient: Optional[str] = None
    effect: Optional[str] = None
    company: Optional[str] = None
    category: Optional[str] = None
    form: Optional[str] = None
    expert: Optional[str] = None
    insurance: Optional[str] = None
    bioequiv: Optional[str] = None
    image: Optional[str] = None

    def to_dict(self) -> dict:
        """데이터클래스를 딕셔너리로 변환."""
        return asdict(self)

    @classmethod
    def field_names(cls) -> list[str]:
        """필드명 목록 반환."""
        return [f.name for f in field(cls).__dataclass_fields__.values()]


@dataclass
class SearchPayload:
    """의약품 검색 요청 페이로드."""
    
    req_page: int = 1
    listup: int = 1000
    search_drugnm_initial: str = ""
    inner_search_word: str = ""
    origin_cnt: str = ""
    inner_search_flag: str = ""
    inner_match_value: str = ""
    input_drug_nm: str = ""
    input_upsoNm: str = ""
    cbx_sunbcnt: str = "0"
    cbx_class: str = "0"
    anchor_dosage_route_hidden: str = ""
    mfds_cd: str = ""
    mfds_cdword: str = ""
    input_hiraingdcd: str = ""
    search_sunb1: str = ""
    search_sunb2: str = ""
    search_sunb3: str = ""
    sunb_equals1: str = ""
    sunb_equals2: str = ""
    sunb_equals3: str = ""
    sunb_where1: str = "and"
    sunb_where2: str = "and"
    search_effect: str = ""
    cbx_bohtype: str = ""
    search_bohcode: str = ""
    anchor_form_info_hidden: str = ""
    cbx_narcotic: str = ""
    atccode_val: str = ""
    atccode_name: str = ""
    kpic_atc_nm_opener: str = ""
    kpic_atc_nm: str = ""
    cbx_bio: str = ""
    icode: str = ""
    ori_search_word: str = ""
    search_flag: str = ""
    movefrom: str = "drug"
    viewmode: str = ""
    more: str = ""

    def to_urlencoded(self) -> str:
        """URL 인코딩된 문자열로 변환."""
        parts = []
        for key, value in asdict(self).items():
            parts.append(f"{key}={value}")
        return "&".join(parts)