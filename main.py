from __future__ import annotations

import json
import os

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from metadata_service import (
    MetadataError,
    apply_exif_edits,
    build_edit_response,
    build_json_response,
    extract_metadata,
)

app = FastAPI(
    title="FastAPI All That Metadata",
    description="이미지 파일의 EXIF 메타데이터를 분석하고 편집할 수 있는 서비스",
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.mount("/static", StaticFiles(directory="static"), name="static")

MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB


@app.get("/")
async def serve_index() -> FileResponse:
    return FileResponse(os.path.join("static", "index.html"))


@app.get("/health", tags=["system"])
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}


@app.post("/api/exif", tags=["exif"])
async def analyze_exif(file: UploadFile = File(...)) -> dict:
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="업로드된 파일이 비어 있습니다.")
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="파일 용량이 25MB를 초과합니다.")

    try:
        result = extract_metadata(file_bytes, file.filename, file.content_type)
    except MetadataError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail="메타데이터 분석에 실패했습니다.") from exc

    return build_json_response(result)


@app.post("/api/exif/edit", tags=["exif"])
async def edit_exif(
    file: UploadFile = File(...),
    updates: str | None = Form(None, description="JSON 객체 형태의 수정할 EXIF 값"),
    removals: str | None = Form(None, description="JSON 배열 형태의 삭제할 태그 이름"),
) -> dict:
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="업로드된 파일이 비어 있습니다.")
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="파일 용량이 25MB를 초과합니다.")

    try:
        parsed_updates = json.loads(updates) if updates else {}
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="updates 필드는 올바른 JSON 이어야 합니다.") from exc

    try:
        parsed_removals = json.loads(removals) if removals else []
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="removals 필드는 올바른 JSON 배열이어야 합니다.") from exc

    if not isinstance(parsed_updates, dict):
        raise HTTPException(status_code=400, detail="updates 필드는 JSON 객체여야 합니다.")
    if not isinstance(parsed_removals, list):
        raise HTTPException(status_code=400, detail="removals 필드는 JSON 배열이어야 합니다.")

    try:
        original = extract_metadata(file_bytes, file.filename, file.content_type)
        modified_bytes, updated = apply_exif_edits(
            file_bytes,
            original,
            updates=parsed_updates,
            removals=parsed_removals,
        )
    except MetadataError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail="EXIF 편집에 실패했습니다.") from exc

    return build_edit_response(modified_bytes, file.filename, updated)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

