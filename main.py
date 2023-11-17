import logging
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi


from celery.result import AsyncResult

from db_utils import models, schemas
from db_utils.database import engine

from routers import studies, data, admin

models.Base.metadata.create_all(bind=engine)  # create all tables

app = FastAPI()

# add routers
app.include_router(studies.router)
app.include_router(data.router)
app.include_router(admin.router)

# specify CORS valid origins
origins = [
# FIXME: add cors valid origins
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# custom openapi spec text


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="RESPIRE",
        description="Lung disease data portal API specification",
        version='0.0.1',
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi



# exception handling -- log 422 results to console


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
    logging.error(f"{request}: {exc_str}")
    content = {'status_code': 10422, 'message': exc_str, 'data': None}
    return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

# keeping this method around for later when we put an admin interface in front of this
# will allow us to poll this endpoint for status of long-running tasks
@app.get("/v1/tasks/{task_id}", response_model=schemas.Status)
def get_status(task_id):
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result
    }
    return JSONResponse(result)