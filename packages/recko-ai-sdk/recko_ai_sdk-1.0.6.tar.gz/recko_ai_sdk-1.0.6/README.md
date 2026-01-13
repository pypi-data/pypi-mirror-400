# 🚀 Reckomate SDK

**Reckomate SDK** is an official Python SDK for securely interacting with the Reckomate backend platform.  
It supports **admin APIs, user APIs, MCQ workflows, Excel ingestion, scheduling, and gateway-based secure access**.

This SDK is designed to be:
- 🔐 Secure (gateway + project identity enforced)
- 📦 Modular (service-based architecture)
- 🚀 Production-ready
- 🔄 Future-proof (easy to add new services)

---

## 📦 Installation

```bash
pip install recko-ai-sdk
```

## ⚙️ Quickstart (gateway) 

```text
1. Create the project folder,
        - Register with project name 
http://52.87.148.155:8000/project/register
 
2. Create the Virtual Environment 
	-  python -m venv reckovenv
 
3. Activate our Virtual Environment
        - .\reckovenv\Scripts\activate  
4. Install sdk with following with below command
	 # pip install recko-ai-sdk==1.0.4
5. create one file main.py with below code.
 
#main.py
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from reckomate_sdk.client import ReckomateClient
 
# Load .env
load_dotenv()
 
PROJECT_NAME = os.getenv("RECKOMATE_PROJECT_NAME")
MAIN_BACKEND = os.getenv("RECKOMATE_MAIN_BACKEND")
 
if not PROJECT_NAME:
    raise RuntimeError("RECKOMATE_PROJECT_NAME is missing in .env")
 
if not MAIN_BACKEND:
    raise RuntimeError("RECKOMATE_MAIN_BACKEND is missing in .env")
 
app = FastAPI(title=f"{PROJECT_NAME.upper()} Gateway")
 
# SDK low-level client
client = ReckomateClient(base_url=MAIN_BACKEND)
 
 
@app.get("/health")
def health():
    return {
        "status": "gateway-ok",
        "project": PROJECT_NAME
    }
 
 
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_all(path: str, request: Request):
    try:
        headers = dict(request.headers)
        headers.pop("host", None)
        headers.pop("content-length", None)
 
        # 🔐 Project identity (checked by gateway_guard.py)
        headers["x-internal-proxy"] = PROJECT_NAME
 
        body = await request.body()
 
        resp = client.proxy_request(
            method=request.method,
            path=f"/{path}",
            headers=headers,
            body=body,
            params=dict(request.query_params),
        )
 
        return JSONResponse(
            status_code=resp.status_code,
            content=resp.json() if resp.content else None
        )
 
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": "GATEWAY_ERROR",
                "message": str(e)
            }
        )
 
 
6. Create .env file into project folder 
#.env 
# =====================================
# Project Identity (MANDATORY)
# MUST match the name registered via
# POST /project/register on main backend
# =====================================
RECKOMATE_PROJECT_NAME=inobeta
 
 
# =====================================
# Gateway URL (PUBLIC ENTRY POINT)
# Used by Postman / React Native / Flutter
# =====================================
RECKOMATE_GATEWAY_URL=http://52.87.148.155:5000

 
 
6. After that, needs to install three packages
          # pip install uvicorn fastapi dotenv
 
7. After run the project using command 
          # uvicorn main:app --port (any port)

 

