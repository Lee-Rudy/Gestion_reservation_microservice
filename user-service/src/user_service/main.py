from fastapi import FastAPI

app = FastAPI(
    title="gestion_microservice",
    version="0.1.0",
)


def build_status() -> dict[str, str]:
    """Generate API status response.

    Returns:
        Dict containing the API status.
    """
    return {"status": "user-service"}


@app.get("/")
def root() -> dict[str, str]:
    """Root endpoint returning API health status.

    Returns:
        Dict with status information.
    """
    return build_status()
