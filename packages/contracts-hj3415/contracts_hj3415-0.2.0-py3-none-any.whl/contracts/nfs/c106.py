# contracts/nfs/c106.py
from __future__ import annotations

from pydantic import BaseModel, Field, ConfigDict

NumMap = dict[str, float | None]


class C106Block(BaseModel):
    전일종가: NumMap = Field(default_factory=dict)
    시가총액: NumMap = Field(default_factory=dict)
    자산총계: NumMap = Field(default_factory=dict)
    부채총계: NumMap = Field(default_factory=dict)

    매출액: NumMap = Field(default_factory=dict)
    영업이익: NumMap = Field(default_factory=dict)
    당기순이익: NumMap = Field(default_factory=dict)
    당기순이익_지배: NumMap = Field(default_factory=dict)

    영업이익률: NumMap = Field(default_factory=dict)
    순이익률: NumMap = Field(default_factory=dict)
    ROE: NumMap = Field(default_factory=dict)
    부채비율: NumMap = Field(default_factory=dict)

    PER: NumMap = Field(default_factory=dict)
    PBR: NumMap = Field(default_factory=dict)

    투자의견: NumMap = Field(default_factory=dict)
    목표주가: NumMap = Field(default_factory=dict)

    model_config = ConfigDict(extra="ignore")


class C106DTO(BaseModel):
    코드: str
    q: C106Block
    y: C106Block