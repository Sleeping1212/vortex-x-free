from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import httpx
import logging
from urllib.parse import quote
from asyncio import gather, TimeoutError

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bypass_apis = [
    "https://api.bypass.vip/bypass?url={}",
    "https://hahabypasser-api.vercel.app/bypass?link={}",
    "http://fi1.bot-hosting.net:6780/api/bypass?link={}",
    "https://dlr.kys.gay/api/free/bypass?url={}",
    "https://bypass-friezggs-projects.vercel.app/bypass?url={}&api_key=speedbypasser"
]

async def fetch_bypass(client: httpx.AsyncClient, api_url: str) -> dict:
    try:
        response = await client.get(api_url, timeout=10)
        response.raise_for_status()
        result = response.json()

        if 'error' not in result:
            logger.info(f"Successfully bypassed URL with {api_url}")
            return {"success": True, "data": result, "source": api_url}
        else:
            logger.warning(f"Error in response from {api_url}: {result.get('error')}")
            return {"success": False, "error": result.get('error')}

    except httpx.RequestError as e:
        logger.error(f"Request error for {api_url}: {e}")
        return {"success": False, "error": str(e)}
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP status error for {api_url}: {e}")
        return {"success": False, "error": f"HTTP error: {e.response.status_code}"}
    except Exception as e:
        logger.error(f"Unexpected error for {api_url}: {e}")
        return {"success": False, "error": "Unexpected error occurred."}

@app.get("/api/bypass")
async def bypass(request: Request):
    url = request.query_params.get('url')
    
    if not url:
        raise HTTPException(status_code=400, detail="No URL provided.")
    
    encoded_url = quote(url, safe='')
    api_urls = [api.format(encoded_url) for api in bypass_apis]

    async with httpx.AsyncClient() as client:
        tasks = [fetch_bypass(client, api_url) for api_url in api_urls]
        results = await gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, dict) and result.get("success"):
                return {"bypass_result": result["data"], "source": result["source"]}

        error_messages = [result.get("error") for result in results if isinstance(result, dict)]
        logger.error(f"All bypass attempts failed: {error_messages}")
        return JSONResponse(
            status_code=400,
            content={"error": "Failed to bypass the URL or unsupported/invalid link.", "details": error_messages}
        )

@app.exception_handler(Exception)
async def custom_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred. Please try again later."}
            )
