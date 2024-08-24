from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx

app = FastAPI()

bypass_apis = [
    "https://api.bypass.vip/bypass?url=",
    "https://hahabypasser-api.vercel.app/bypass?link=",
    "http://fi1.bot-hosting.net:6780/api/bypass?link=",
    "https://dlr.kys.gay/api/free/bypass?url=",
    "https://bypass-friezggs-projects.vercel.app/bypass?url={}&api_key=speedbypasser"
]

@app.get("/api/bypass")
async def bypass(request: Request):
    url = request.query_params.get('url')
    
    if not url:
        return {"error": "No URL provided."}

    for api in bypass_apis:
        try:
            encoded_url = httpx.quote(url, safe='')
            full_api_url = api.format(encoded_url)

            async with httpx.AsyncClient() as client:
                response = await client.get(full_api_url)
            
            if response.status_code == 200:
                result = response.json()
                if 'error' not in result:
                    return result
        except Exception:
            continue

    return {"error": "Failed to bypass the URL or unsupported/invalid link."}

@app.exception_handler(Exception)
async def custom_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred."}
    )
