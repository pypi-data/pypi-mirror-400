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

import logging
import re
from typing import Optional

from lxml import html
from lxml.html import HtmlElement

from ..models import Medicine

logger = logging.getLogger(__name__)


class MedicineTableParser:
    """의약품 테이블 HTML을 파싱하는 클래스."""

    TABLE_XPATH = '//table[@id="tbl_pro"]//tr'
    EMPTY_IMAGE_PATH = "/images/img_empty3.jpg"

    # 의약품 코드 추출 정규식 패턴
    IDFY_POP_PATTERN = re.compile(r"show_idfypop\('(.+?)'\)")
    DETAIL_HREF_PATTERN = re.compile(r"drug_detailHref\('(.+?)'\)")

    def parse(self, html_content: bytes) -> list[Medicine]:
        """
        HTML 콘텐츠에서 의약품 목록을 파싱.
        
        Args:
            html_content: HTML 바이트 데이터.
            
        Returns:
            파싱된 Medicine 객체 목록.
        """
        page = html.fromstring(html_content)
        table_rows = page.xpath(self.TABLE_XPATH)
        #print(table_rows)
        
        medicines = []
        for row in table_rows:
            medicine = self._parse_row(row)
            if medicine:
                medicines.append(medicine)
        
        #print(medicines)
        return medicines

    def _parse_row(self, row: HtmlElement) -> Optional[Medicine]:
        """
        테이블 행을 파싱하여 Medicine 객체 반환.
        
        Args:
            row: 테이블 행 요소.
            
        Returns:
            파싱된 Medicine 객체. 헤더 행이면 None.
        """
        # 헤더 행 스킵
        th_texts = [th.text_content().strip() for th in row.xpath(".//th")]
        if th_texts:
            return None

        td_texts = [td.text_content().strip() for td in row.xpath(".//td")]
        if not td_texts:
            return None

        medicine_code = self._extract_medicine_code(row)
        image_url = self._extract_image_url(row)

        # 첫 번째 열 제거 (인덱스 또는 체크박스 열)
        td_texts.pop(0)

        return Medicine(
            name=td_texts[0] if len(td_texts) > 0 else "",
            code=medicine_code,
            ingredient=td_texts[1] if len(td_texts) > 1 else None,
            effect=td_texts[2] if len(td_texts) > 2 else None,
            company=td_texts[3] if len(td_texts) > 3 else None,
            category=td_texts[4] if len(td_texts) > 4 else None,
            form=td_texts[5] if len(td_texts) > 5 else None,
            expert=td_texts[6] if len(td_texts) > 6 else None,
            insurance=td_texts[7] if len(td_texts) > 7 else None,
            bioequiv=td_texts[8] if len(td_texts) > 8 else None,
            image=image_url,
        )

    def _extract_medicine_code(self, row: HtmlElement) -> Optional[str]:
        """onclick 속성에서 의약품 코드 추출."""
        # 이미지 클릭에서 추출 시도
        for img in row.xpath('.//td[@class="img"]/img'):
            onclick = img.get("onclick", "")
            match = self.IDFY_POP_PATTERN.search(onclick)
            if match:
                return match.group(1)

        # 텍스트 셀 클릭에서 추출 시도
        for td in row.xpath('.//td[@class="txtL"]'):
            onclick = td.get("onclick", "")
            match = self.DETAIL_HREF_PATTERN.search(onclick)
            if match:
                return match.group(1)

        return None

    def _extract_image_url(self, row: HtmlElement) -> Optional[str]:
        """이미지 URL 추출. 빈 이미지면 None 반환."""
        img_srcs = row.xpath('.//td[@class="img"]/img/@src')
        if img_srcs and img_srcs[0] != self.EMPTY_IMAGE_PATH:
            return img_srcs[0]
        return None