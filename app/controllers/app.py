from fastapi import APIRouter
from typing import Optional

import datetime

router = APIRouter()

@router.get("/")
async def read_root():
    return {"message": "Welcome to FastAPI"}

@router.get("/xx")
async def xx():
    love = str
    days = int
    day_in_love = datetime.datetime(2018,10,13,0,0,0)
    now = datetime.datetime.now()
    times = now - day_in_love
    days = times.days
    hours, remainder = divmod(times.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    test_message = f"LOVE XX {days} DAYS {hours} HOURS {minutes} MINUTES {seconds} SECONDS"
    return {'YXN': test_message}
