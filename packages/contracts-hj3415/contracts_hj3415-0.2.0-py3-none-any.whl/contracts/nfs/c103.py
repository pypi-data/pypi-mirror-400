# contracts/nfs/c103.py
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

Num = float | int | None
Row = dict[str, Num]                 # 예: {"2020/12": 1.0, "전년대비": 2.0, ...}
ItemsMap = dict[str, Row]            # 예: {"매출액(수익)": {...}, ...}

class C103DTO(BaseModel):
    코드: str
    손익계산서y: ItemsMap = Field(default_factory=dict)
    손익계산서q: ItemsMap = Field(default_factory=dict)
    재무상태표y: ItemsMap = Field(default_factory=dict)
    재무상태표q: ItemsMap = Field(default_factory=dict)
    현금흐름표y: ItemsMap = Field(default_factory=dict)
    현금흐름표q: ItemsMap = Field(default_factory=dict)

    model_config = ConfigDict(extra="ignore")