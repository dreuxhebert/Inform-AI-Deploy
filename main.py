from aiohttp.hdrs import ORIGIN
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn
from Routs.CallsRouts import router as CallsRouts
from Routs.Elevate_API_Routs import router as ElevateAPIRouts
import os

load_dotenv()

app = FastAPI()
app.include_router(CallsRouts)
app.include_router(ElevateAPIRouts)

origins = os.getenv("ORIGINs").split(",")
for origin in origins:
    print(origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5001, reload=True)
