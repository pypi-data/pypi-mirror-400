from fastapi import FastAPI, HTTPException


EXCEPTION_MAP = {}


def setup_exception_handlers(app: FastAPI):
    for exc_class, status_code in EXCEPTION_MAP.items():

        @app.exception_handler(exc_class)
        async def generic_handler(_, exc, status_code=status_code):
            return HTTPException(status_code=status_code, detail=str(exc))
