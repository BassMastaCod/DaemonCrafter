from fastapi import FastAPI
import logging

from starlette.responses import PlainTextResponse

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)

app = FastAPI()

@app.get('/hello', response_class=PlainTextResponse)
def hello():
    logging.info('FastAPI Hello endpoint was called')
    return 'Hello World from FastAPI'
