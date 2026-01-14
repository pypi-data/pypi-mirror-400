# contracts/nfs/c104.py
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

Num = float | int | None
Row = dict[str, Num]                 # 예: {"2020/12": 1.0, "전년대비": 2.0, ...}
ItemsMap = dict[str, Row]            # 예: {"ROE": {...}, ...}

class C104DTO(BaseModel):
    코드: str
    수익성y: ItemsMap = Field(default_factory=dict)
    수익성q: ItemsMap = Field(default_factory=dict)
    성장성y: ItemsMap = Field(default_factory=dict)
    성장성q: ItemsMap = Field(default_factory=dict)
    안정성y: ItemsMap = Field(default_factory=dict)
    안정성q: ItemsMap = Field(default_factory=dict)
    활동성y: ItemsMap = Field(default_factory=dict)
    활동성q: ItemsMap = Field(default_factory=dict)
    가치분석y: ItemsMap = Field(default_factory=dict)
    가치분석q: ItemsMap = Field(default_factory=dict)


    model_config = ConfigDict(extra="ignore")