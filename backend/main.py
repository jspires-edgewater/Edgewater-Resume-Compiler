from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
import io
import re
from typing import Tuple


from converter import convert_to_standard_docx


MAX_BYTES = 20 * 1024 * 1024 # 20 MB
ALLOWED_TYPES = {
"application/pdf",
"application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


app = FastAPI(title="Resume Converter API")


# Allow your GitHub Pages site to call this API
app.add_middleware(
CORSMiddleware,
allow_origins=["*"], # for internal use; restrict later if desired
allow_credentials=False,
allow_methods=["POST", "GET"],
allow_headers=["*"],
)


@app.get("/healthz")
def healthz():
return {"ok": True}


@app.post("/convert")
async def convert(file: UploadFile = File(...)):
if file.content_type not in ALLOWED_TYPES:
raise HTTPException(status_code=415, detail="Upload a PDF or DOCX file.")


content = await file.read()
if len(content) > MAX_BYTES:
raise HTTPException(status_code=413, detail="File too large (max 20 MB).")


try:
out_bytes, out_name = convert_to_standard_docx(content, file.filename, file.content_type)
except Exception as e:
raise HTTPException(status_code=500, detail=f"Conversion error: {e}")


return StreamingResponse(
io.BytesIO(out_bytes),
media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
headers={"Content-Disposition": f"attachment; filename={out_name}"},
)
