import httpx
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="API Gateway - Gestion Reservation",
    version="0.1.0",
    description="Gateway central pour tous les microservices",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://front:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SERVICES = {
    "auth": "http://auth-service:8001",
    "users": "http://user-service:8002",
    "reservations": "http://reservation-service:8003",
    "paiements": "http://paiement-service:8004",
}


@app.get("/")
def root():
    return {"status": "api-gateway", "services": list(SERVICES.keys())}


@app.get("/health")
def health():
    return {"status": "healthy"}


async def _proxy_request(service_url: str, path: str, request: Request):
    async with httpx.AsyncClient(timeout=30.0) as client:
        headers = dict(request.headers)
        headers.pop("host", None)

        url = f"{service_url}{path}"

        if request.method == "GET":
            response = await client.get(url, headers=headers, params=request.query_params)
        elif request.method == "POST":
            body = await request.body()
            response = await client.post(url, headers=headers, content=body)
        elif request.method == "PUT":
            body = await request.body()
            response = await client.put(url, headers=headers, content=body)
        elif request.method == "DELETE":
            response = await client.delete(url, headers=headers)
        else:
            return Response(status_code=405)

        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
        )


@app.api_route("/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_auth(path: str, request: Request):
    return await _proxy_request(SERVICES["auth"], f"/auth/{path}", request)


@app.api_route("/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_users(path: str, request: Request):
    return await _proxy_request(SERVICES["users"], f"/users/{path}", request)


@app.get("/reservations")
async def get_reservations(request: Request):
    return await _proxy_request(SERVICES["reservations"], "/reservations", request)

@app.api_route("/reservations/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_reservations(path: str, request: Request):
    return await _proxy_request(SERVICES["reservations"], f"/reservations/{path}", request)


@app.get("/categories")
async def get_categories(request: Request):
    return await _proxy_request(SERVICES["reservations"], "/categories", request)

@app.api_route("/categories/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_categories(path: str, request: Request):
    return await _proxy_request(SERVICES["reservations"], f"/categories/{path}", request)


@app.api_route("/paiements/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_paiements(path: str, request: Request):
    return await _proxy_request(SERVICES["paiements"], f"/{path}", request)


@app.get("/admin/stats")
async def admin_stats():
    stats = {"users": 0, "reservations": 0, "paiements": 0}

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            users_resp = await client.get(f"{SERVICES['users']}/users/")
            if users_resp.status_code == 200:
                stats["users"] = len(users_resp.json())
    except Exception:
        pass

    return stats


@app.get("/admin/logs")
async def admin_logs(limit: int = 50):
    logs = []
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{SERVICES['reservations']}/logs?limit={limit}")
            if resp.status_code == 200:
                logs.extend(resp.json())
    except Exception:
        pass

    return logs
