from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from routes import bootstrap_router
import jwt  # pip install PyJWT
import logging
from contextlib import asynccontextmanager
import asyncio


@asynccontextmanager
async def lifespan(app: FastAPI):
    from core.bootstrap import batch_update_worker

    worker_task = asyncio.create_task(batch_update_worker())
    yield
    worker_task.cancel()
    await asyncio.gather(worker_task, return_exceptions=True)


app = FastAPI(lifespan=lifespan)

app.include_router(bootstrap_router)
