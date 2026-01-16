# src/service_a/main.py
from __future__ import annotations

from fastapi import FastAPI

app = FastAPI(title="service_a")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def main() -> None:
    import uvicorn

    uvicorn.run("service_a.main:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    main()
