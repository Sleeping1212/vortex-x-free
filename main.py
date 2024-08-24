from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import httpx
import logging
from urllib.parse import quote

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bypass_apis = [
    "https://api.bypass.vip/bypass?url={encoded_url}",
    "https://hahabypasser-api.vercel.app/bypass?link={encoded_url}",
    "http://fi1.bot-hosting.net:6780/api/bypass?link={encoded_url}",
    "https://dlr.kys.gay/api/free/bypass?url={encoded_url}",
    "https://bypass-friezggs-projects.vercel.app/bypass?url={encoded_url}&api_key=speedbypasser"
]

# Timeout for each request in seconds
REQUEST_TIMEOUT = 3

async def fetch_bypass(client: httpx.AsyncClient, api_url: str) -> dict:
    try:
        response = await client.get(api_url, timeout=REQUEST_TIMEOUT)
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
        for api_url in api_urls:
            result = await fetch_bypass(client, api_url)
            if result.get("success"):
                return {"bypass_result": result["data"], "source": result["source"]}

    # If no successful result was obtained
    logger.error("All bypass attempts failed.")
    return JSONResponse(
        status_code=400,
        content={"error": "Failed to bypass the URL or unsupported/invalid link."}
    )

@app.exception_handler(Exception)
async def custom_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred. Please try again later."}
)
