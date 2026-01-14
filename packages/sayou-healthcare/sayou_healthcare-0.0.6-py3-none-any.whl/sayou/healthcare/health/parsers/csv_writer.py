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

"""CSV export functionality for medicine data."""

import csv
import logging
from pathlib import Path
from typing import Sequence

from ..models import Medicine

logger = logging.getLogger(__name__)


class MedicineCsvWriter:
    """의약품 데이터를 CSV 파일로 저장하는 클래스."""

    DEFAULT_FILENAME = "medicine_list_health.csv"

    def __init__(self, output_path: str | Path | None = None):
        """
        Args:
            output_path: 저장할 CSV 파일 경로. None이면 기본 파일명 사용.
        """
        self._output_path = Path(output_path) / self.DEFAULT_FILENAME if output_path else Path(self.DEFAULT_FILENAME)

    @property
    def output_path(self) -> Path:
        """출력 파일 경로."""
        return self._output_path

    def save(self, medicines: Sequence[Medicine]) -> Path:
        """
        의약품 목록을 CSV 파일로 저장.
        
        Args:
            medicines: 저장할 Medicine 객체 목록.
            
        Returns:
            저장된 파일 경로.
        """
        with open(self._output_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["id", "name"])
            
            for index, medicine in enumerate(medicines, start=1):
                writer.writerow([index, medicine.name])

        logger.info("Saved %d medicines to %s", len(medicines), self._output_path)
        return self._output_path

    def save_full(self, medicines: Sequence[Medicine]) -> Path:
        """
        의약품 목록을 모든 필드와 함께 CSV 파일로 저장.
        
        Args:
            medicines: 저장할 Medicine 객체 목록.
            
        Returns:
            저장된 파일 경로.
        """
        if not medicines:
            logger.warning("No medicines to save")
            return self._output_path

        fieldnames = list(medicines[0].to_dict().keys())
        print(fieldnames)
        
        with open(self._output_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["id"] + fieldnames)
            writer.writeheader()
            
            for index, medicine in enumerate(medicines, start=1):
                row = {"id": index, **medicine.to_dict()}
                writer.writerow(row)

        logger.info("Saved %d medicines (full) to %s", len(medicines), self._output_path)
        return self._output_path