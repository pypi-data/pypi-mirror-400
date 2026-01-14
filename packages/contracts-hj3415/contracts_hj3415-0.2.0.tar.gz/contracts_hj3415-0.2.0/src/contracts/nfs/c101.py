# contracts/nfs/c101.py
from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional


class C101DTO(BaseModel):
    # 기본 식별 정보
    종목명: str
    코드: str
    날짜: str
    업종: str

    # 재무 지표
    eps: Optional[int] = None
    bps: Optional[int] = None
    per: Optional[float] = None
    업종per: Optional[float] = None
    pbr: Optional[float] = None
    배당수익률: Optional[float] = None

    # 주가 정보
    주가: Optional[int] = None
    전일대비: Optional[int] = None
    수익률: Optional[float] = None

    최고52: Optional[int] = None
    최저52: Optional[int] = None

    거래량: Optional[int] = None
    거래대금: Optional[int] = None
    시가총액: Optional[int] = None

    베타52주: Optional[float] = None

    발행주식: Optional[int] = None
    유동비율: Optional[float] = None
    외국인지분율: Optional[float] = None

    # 기간 수익률
    수익률1M: Optional[float] = None
    수익률3M: Optional[float] = None
    수익률6M: Optional[float] = None
    수익률1Y: Optional[float] = None

    # 텍스트 정보
    개요: str = ""

    class Config:
        # 한글 필드명을 그대로 쓰기 위한 옵션
        populate_by_name = True