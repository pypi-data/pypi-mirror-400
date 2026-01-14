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

import re
from urllib.parse import unquote

# 의약품안전나라 > 통합검색 > 의약품등 정보검색 > 엑셀다운로드
_NEDRUG_EXCEL_URL_ = "https://nedrug.mfds.go.kr/searchDrug/getExcel"

# Gemini 답변
GEMINI_COLUMNS = {
    "item_code": "품목기준코드",
    "product_name": "제품명",
    "product_name_eng": "제품영문명",
    "company_name": "업체명",
    "company_name_eng": "업체영문명",
    "approval_date": "허가일",
    "item_category": "품목구분",
    "approval_number": "허가번호",
    "cancel_status": "취소/취하",
    "cancel_date": "취소/취하일자",
    "main_ingredient": "주성분",
    "additives": "첨가제",
    "item_classification": "품목분류",
    "prescription_type": "전문의약품",
    "finished_or_raw": "완제/원료",
    "approval_type": "허가/신고",
    "manufacture_or_import": "제조/수입",
    "narcotic_classification": "마약구분",
    "shape": "모양",
    "color": "색상",
    "formulation": "제형",
    "major_axis": "장축",
    "minor_axis": "단축",
    "new_drug_status": "신약구분",
    "standard_code_name": "표준코드명",
    "atc_code": "ATC코드",
    "bundled_drug_info": "묶음의약품정보",
    "e_drug_info": "e은약요",
    "import_country": "수입제조국",
    "main_ingredient_eng": "주성분영문"
}

# ChatGPT 답변
CHATGPT_COLUMNS = {
    "item_code": "품목기준코드",
    "product_name": "제품명",
    "product_name_eng": "제품영문명",
    "company_name": "업체명",
    "company_name_eng": "업체영문명",
    "approval_date": "허가일",
    "item_category": "품목구분",
    "approval_number": "허가번호",
    "cancellation_status": "취소/취하",
    "cancellation_date": "취소/취하일자",
    "active_ingredient": "주성분",
    "additives": "첨가제",
    "item_classification": "품목분류",
    "prescription_medicine": "전문의약품",
    "finished_or_raw": "완제/원료",
    "approval_or_report": "허가/신고",
    "manufacture_or_import": "제조/수입",
    "narcotic_classification": "마약구분",
    "shape": "모양",
    "color": "색상",
    "dosage_form": "제형",
    "long_axis": "장축",
    "short_axis": "단축",
    "new_drug_classification": "신약구분",
    "standard_code_name": "표준코드명",
    "atc_code": "ATC코드",
    "bundle_medicine_info": "묶음의약품정보",
    "e_pharmacy": "e은약요",
    "importing_country": "수입제조국",
    "active_ingredient_eng": "주성분영문"
}

def decode_euc_kr(content):
    """깨진 한글 인코딩 복원"""
    
    # 인코딩 변환 (EUC-KR Bytes -> Python Unicode String)
    # response.text를 바로 쓰지 않고, content(바이트)를 직접 디코딩하는 것이 안전합니다.
    try:
        content = content.decode('euc-kr')
        return content
    except UnicodeDecodeError:
        # euc-kr로 안 될 경우 cp949 시도 (확장 완성형)
        content = content.decode('cp949', errors='replace')
    
    return content

def get_filename(headers):
    content_disposition = headers.get("Content-Disposition", "")
    # filename="..." 또는 filename*=UTF-8''... 패턴 찾기
    matches = re.findall("filename=\"(.+)\"", content_disposition)
    if len(matches) == 0:
        return None
    
    encoded_filename = matches[0]
    filename = encoded_filename.encode('latin1').decode('utf-8')
    print('Content-Disposition', content_disposition)
    print('filename', filename)

    return filename
