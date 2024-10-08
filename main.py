from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import httpx
import logging
from urllib.parse import quote
import asyncio

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bypass_apis = [
    "https://hahabypasser-api.vercel.app/bypass?link={encoded_url}",
    "http://fi5.bot-hosting.net:20276/api/codex?link={encoded_url}",
    "https%3A%2F%2Fdlr.kys.gay%2Fapi%2Ffree%2Fbypass%3Furl%3D%7Bencoded_url%7D",  # Using the exact encoded URL
    "https://bypass-friezggs-projects.vercel.app/api/bypass?url={encoded_url}&api_key=speedbypasser",
    "http://fi1.bot-hosting.net:6780/api/bypass?link={encoded_url}",
]

# Timeout for each request in seconds
REQUEST_TIMEOUT = 1.5  # Lowered timeout for faster response

async def fetch_bypass(client: httpx.AsyncClient, api_url: str) -> dict:
    """Fetch the bypass result from a given API URL."""
    try:
        response = await client.get(api_url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        result = response.json()

        # Adjust the key handling based on response structure
        if 'error' not in result:
            if 'key' in result:
                bypassed_result = {'key': result['key']}
            else:
                bypassed_result = {'result': result.get('bypassed', result)}
            logger.info(f"Successfully bypassed URL with {api_url}")
            return {"success": True, **bypassed_result}
        else:
            logger.warning(f"Error in response from {api_url}: {result.get('error')}")
            return {"success": False, "error": result.get('error')}
    
    except (httpx.RequestError, httpx.HTTPStatusError, asyncio.TimeoutError) as e:
        logger.error(f"Error for {api_url}: {e}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error for {api_url}: {e}")
        return {"success": False, "error": "Unexpected error occurred."}

@app.get("/api/bypass")
async def bypass(request: Request):
    """Endpoint to bypass a URL using multiple APIs."""
    url = request.query_params.get('url')
    
    if not url:
        raise HTTPException(status_code=400, detail="No URL provided.")
    
    # Use quote to encode the URL properly
    encoded_url = quote(url, safe='')
    logger.info(f"Encoded URL: {encoded_url}")  # Log the encoded URL for debugging
    
    # Use the provided encoded URL for the dlr API and construct URLs for others
    api_urls = [api.format(encoded_url=encoded_url) if '{encoded_url}' in api else api for api in bypass_apis]

    async with httpx.AsyncClient() as client:
        tasks = [fetch_bypass(client, api_url) for api_url in api_urls]
        results = await asyncio.gather(*tasks)

        for result in results:
            if result.get("success"):
                return result  # Directly return the successful result

    # If no successful result was obtained
    logger.error("All bypass attempts failed.")
    return JSONResponse(
        status_code=400,
        content={"error": "Failed to bypass the URL or unsupported/invalid link."}
    )

@app.exception_handler(Exception)
async def custom_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred. Please try again later."}
        )
