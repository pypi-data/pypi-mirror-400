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
from urllib.parse import unquote

logger = logging.getLogger(__name__)

_START_URL_ = "https://www.hira.or.kr/bbsDummy.do?pgmid=HIRAA030014050000"
_DOWNLOAD_BASE_URL_ = "https://www.hira.or.kr/bbs/bbsCDownLoad.do"

_OPENDATA_START_URL_ = "https://opendata.hira.or.kr/op/opc/selectOpenData.do?sno=11925"
_OPENDATA_SELECT_URL_ = "https://opendata.hira.or.kr/op/opc/selectOpenData.do?sno=11925"
_OPENDATA_DOWNLOAD_URL_ = "https://opendata.hira.or.kr/dext5upload/handler/upload.dx?callType=download&url=/op/opc/selectOpenData.do"

HOSPITAL_COLUMNS = {
    "encrypted_medical_institution_code" : "암호화요양기호", 
    "medical_institution_name" : "요양기관명", 
    "type_code" : "종별코드",
    "type_code_name" : "종별코드명",
    "city_province_code" : "시도코드",
    "city_province_code_name" : "시도코드명",
    "district_code" : "시군구코드",
    "district_code_name" : "시군구코드명",
    "town_village" : "읍면동",
    "postal_code" : "우편번호",
    "address" : "주소",
    "phone_number" : "전화번호",
    "hospital_website" : "병원홈페이지",
    "opening_date" : "개설일자",
    "total_doctors" : "총의사수",
    "medical_general_practitioner_count" : "의과일반의 인원수",
    "medical_intern_count" : "의과인턴 인원수",
    "medical_resident_count" : "의과레지던트 인원수",
    "medical_specialist_count" : "의과전문의 인원수",
    "dental_general_practitioner_count" : "치과일반의 인원수",
    "dental_intern_count" : "치과인턴 인원수",
    "dental_resident_count" : "치과레지던트 인원수",
    "dental_specialist_count" : "치과전문의 인원수",
    "korean_medicine_general_practitioner_count" : "한방일반의 인원수",
    "korean_medicine_intern_count" : "한방인턴 인원수",
    "korean_medicine_resident_count" : "한방레지던트 인원수",
    "korean_medicine_specialist_count" : "한방전문의 인원수",
    "midwife_count" : "조산사 인원수",
    "coordinate_x" : "좌표(X)",
    "coordinate_y" : "좌표(Y)"
}

PHARMACY_COLUMNS = {
    "encrypted_medical_institution_code" : "암호화요양기호", 
    "medical_institution_name" : "요양기관명", 
    "type_code" : "종별코드", 
    "type_code_name" : "종별코드명", 
    "city_province_code" : "시도코드", 
    "city_province_code_name" : "시도코드명", 
    "district_code" : "시군구코드", 
    "district_code_name" : "시군구코드명", 
    "town_village" : "읍면동", 
    "postal_code" : "우편번호", 
    "address" : "주소", 
    "phone_number" : "전화번호", 
    "opening_date" : "개설일자", 
    "coordinate_x" : "좌표(X)", 
    "coordinate_y" : "좌표(Y)"
}

def decode_euc_kr(response):
    """깨진 한글 인코딩 복원"""
    
    # 인코딩 변환 (EUC-KR Bytes -> Python Unicode String)
    # response.text를 바로 쓰지 않고, content(바이트)를 직접 디코딩하는 것이 안전합니다.
    try:
        content = response.content.decode('euc-kr')
        return content
    except UnicodeDecodeError:
        # euc-kr로 안 될 경우 cp949 시도 (확장 완성형)
        content = response.content.decode('cp949', errors='replace')
    
    return content

def get_filename(headers):
    content_disposition = headers.get("Content-Disposition", "")
    # filename="..." 또는 filename*=UTF-8''... 패턴 찾기
    matches = re.findall("filename=\"(.+)\"", content_disposition)
    if len(matches) == 0:
        return None
    
    encoded_filename = matches[0]
    filename = encoded_filename.encode('latin1').decode('utf-8')
    logger.debug('Content-Disposition', content_disposition)
    logger.info('filename', unquote(filename))

    return filename

def _get_filename(headers):
    filename = None

    content_disposition = headers.get("Content-Disposition", "")
    # filename="..." 또는 filename*=UTF-8''... 패턴 찾기
    match = re.search(r"filename\*?=['\"]?(?:UTF-8'')?([^'\";\n]+)", content_disposition)
    if match:
        filename = match.group(1)

        # URL 인코딩된 경우
        if '%' in filename:
            filename = unquote(filename)
        
        # 깨진 인코딩 복원
        filename = decode_euc_kr(filename)
            
        # .zip 확장자 제거하여 폴더명으로 사용
        #save_path = filename.replace('.zip', '')

    return filename
