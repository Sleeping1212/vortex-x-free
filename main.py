from fastapi import FastAPI, HTTPException, Request
import httpx

app = FastAPI()

# List of bypass API endpoints with their respective URL query parameters
bypass_apis = [
    "https://api.bypass.vip/bypass?url=",
    "https://hahabypasser-api.vercel.app/bypass?link=",
    "http://fi1.bot-hosting.net:6780/api/bypass?link=",
    "https://dlr.kys.gay/api/free/bypass?url=",
    "https://bypass-friezggs-projects.vercel.app/bypass?url={}&api_key=speedbypasser"
]

@app.get("/api/bypass")
async def bypass(request: Request):
    # Get the URL parameter from the query string
    url = request.query_params.get('url')
    
    if not url:
        # No URL provided
        return {"error": "No URL provided."}

    for api in bypass_apis:
        try:
            # Format the bypass API URL with the encoded URL
            encoded_url = httpx.quote(url, safe='')
            full_api_url = api.format(encoded_url)

            # Call the bypass API
            async with httpx.AsyncClient() as client:
                response = await client.get(full_api_url)
            
            # Check if the response is successful
            if response.status_code == 200:
                result = response.json()
                if 'error' not in result:
                    # If the bypass is successful, return the result
                    return result
        except Exception as e:
            # Log the exception and continue to the next API
            print(f"Error calling {api}: {e}")
            continue

    # If all bypass attempts fail
    return {"error": "Failed to bypass the URL or unsupported/invalid link."}

# Start the FastAPI server with Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
