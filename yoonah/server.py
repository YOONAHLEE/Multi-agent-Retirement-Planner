from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
import traceback
import os

# 기존 파이프라인 코드 import
from financial_report_pipeline import adaptive_rag, SUMMARY_CACHE_PATH

app = FastAPI(
    title="Financial Report API",
    description="Generate daily financial reports using RAG pipeline",
    version="1.0.0"
)

class ReportRequest(BaseModel):
    query: str = Field(..., example="오늘의 금융 보고서를 작성해주세요")
    date: Optional[str] = Field(default_factory=lambda: date.today().isoformat(), example="2025-05-27")

class ReportResponse(BaseModel):
    status: str
    report: Optional[str] = None
    error: Optional[str] = None
    date: Optional[str] = None

@app.get("/health")
async def health_check():
    """
    헬스 체크 엔드포인트
    """
    return {"status": "ok"}

@app.post("/generate_report", response_model=ReportResponse)
async def generate_report(req: ReportRequest):
    try:
        # 입력 검증
        if not req.query or not isinstance(req.query, str):
            raise HTTPException(status_code=400, detail="Query must be a non-empty string.")

        # 파이프라인 입력 준비
        inputs = {
            "date": req.date,
            "query": req.query,
            "documents": [],
            "doc_summary_chunks": [],
            "doc_summary": "",
            "web_summary": "",
            "final_output": "",
            "db_path": SUMMARY_CACHE_PATH
        }

        # 파이프라인 실행
        result = adaptive_rag.invoke(inputs)
        report = result.get("final_output", "")

        if not report:
            raise HTTPException(status_code=500, detail="Report generation failed.")

        return ReportResponse(
            status="success",
            report=report,
            date=req.date
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        tb = traceback.format_exc()
        return ReportResponse(
            status="error",
            error=f"{str(e)}\n{tb}"
        )

@app.get("/download_report/{report_date}")
async def download_report(report_date: str):
    """
    생성된 보고서를 .md 파일로 다운로드
    """
    filename = f"reports/final_report_{report_date}.md"
    if not os.path.exists(filename):
        raise HTTPException(status_code=404, detail="Report file not found.")
    return FileResponse(filename, media_type="text/markdown", filename=os.path.basename(filename))

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    tb = traceback.format_exc()
    return JSONResponse(
        status_code=500,
        content={"status": "error", "error": f"{str(exc)}\n{tb}"}
    )