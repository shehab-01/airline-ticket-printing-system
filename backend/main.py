from fastapi import FastAPI, APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

# routes
from api.routers import ticket, agency


class HealthCheck(BaseModel):
    status: str = "ok"


@asynccontextmanager
async def lifespan(app: FastAPI):
    await server_startup()
    yield
    await server_shutdown()


app = FastAPI(
    title="Airline Ticketing System",
    description="A complete example with Pydantic, Router, and CORS",
    version="1.0.0",
    lifespan=lifespan,
)

# Origins 
origins = [
    "http://localhost",
    "http://localhost:3000", 

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows specific origins
    # allow_origins=["*"],  # Allows all origins (use with caution)
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"], # Allows all common methods
    allow_headers=["*"], # Allows all headers
)

@app.get("/", tags=["Root"])
async def read_root():
    """
    A simple root endpoint to know the API is running.
    """
    return {"message": "Welcome to the API!"}

@app.get("/health", response_model=HealthCheck, tags=["Health"])
async def health_check():
    """
    A simple health check endpoint.
    Responds with {"status": "ok"} if the app is healthy.
    """
    return HealthCheck(status="ok")


app.include_router(ticket.router)
app.include_router(agency.router, tags=["Agencies"])

async def server_startup():
    print(" starting ... ")
    # get_supabase()


async def server_shutdown():
    print(" Shutting down...")
    # close_supabase()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)