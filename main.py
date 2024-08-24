from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
import logging
from urllib.parse import quote

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
            encoded_url = quote(url, safe='')
            full_api_url = api.format(encoded_url)

            async with httpx.AsyncClient() as client:
                response = await client.get(full_api_url)
            
            logger.info(f"Response from {full_api_url}: {response.text}")

            if response.status_code == 200:
                result = response.json()
                if 'error' not in result:
                    return result
                else:
                    logger.error(f"Error response from {full_api_url}: {result.get('error')}")
            else:
                logger.error(f"Non-200 status code from {full_api_url}: {response.status_code}")

        except httpx.RequestError as e:
            logger.error(f"Request error for {full_api_url}: {e}")
            continue
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP status error for {full_api_url}: {e}")
            continue
        except Exception as e:
            logger.error(f"Unexpected error for {full_api_url}: {e}")
            continue

    return {"error": "Failed to bypass the URL or unsupported/invalid link."}

@app.exception_handler(Exception)
async def custom_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred."}
        )
