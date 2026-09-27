import sys

if sys.platform == "win32":
    try:
        import uvicorn.loops.asyncio
        uvicorn.loops.asyncio.asyncio_setup = lambda *args, **kwargs: None
    except ImportError:
        pass