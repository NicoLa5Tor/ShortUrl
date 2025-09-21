#!/usr/bin/env python3

import uvicorn
from app.main import app

if __name__ == '__main__':
    from app.config import settings
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )