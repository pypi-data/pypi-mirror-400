import math
from pydantic import BaseModel, field_validator
from typing import List, Optional, Any
import re

class C108DTO(BaseModel):
    코드: str
    날짜: Optional[str]
    제목: str
    작성자: Optional[str]
    제공처: Optional[str]
    투자의견: Optional[str]
    목표가: Optional[float]
    분량: Optional[str]
    내용: List[str]


    @field_validator("투자의견", mode="before")
    @classmethod
    def _coerce_opinion(cls, v):
        # pandas/bs4 parsing sometimes yields float('nan') for empty cells
        if v is None:
            return None
        if isinstance(v, float) and math.isnan(v):
            return None
        if isinstance(v, str):
            s = v.strip()
            if not s or s.lower() == "nan" or s in {"-", "N/A", "NA"}:
                return None
            return s
        # Any other type -> string fallback (keeps validation tolerant)
        return str(v)

    @field_validator("목표가", mode="before")
    @classmethod
    def _v_target_price(cls, v: Any):
        if v is None:
            return None

        # nan 방어
        if isinstance(v, float) and math.isnan(v):
            return None

        # 안내 문구/결측 문자열 방어
        if isinstance(v, str):
            s = v.strip()
            if not s or s in {"-", "N/A"} or "검색된 데이터가 없습니다" in s:
                return None

            # "123,456원" 같은 케이스에서 숫자만 추출
            m = re.findall(r"\d+(?:,\d+)*", s)
            if not m:
                return None
            return float(m[0].replace(",", ""))

        # 숫자면 그대로 float로
        if isinstance(v, (int, float)):
            return float(v)

        # 그 외 타입은 None 처리(또는 raise로 엄격하게)
        return None