from pydantic import BaseModel
from typing import Literal

# 멤버 Agent 목록 정의
members = ["Retirement-pension-analysis-Agent", 
           "Pension-information-Agent", 
           "Tax-Savings-Agent",
           "Create-financial-report-Agent"]

# 다음 작업자 선택 옵션 목록 정의
options_for_next = ["FINISH"] + members


# 작업자 선택 응답 모델 정의: 다음 작업자를 선택하거나 작업 완료를 나타냄
class RouteResponse(BaseModel):
    next: Literal[*options_for_next]