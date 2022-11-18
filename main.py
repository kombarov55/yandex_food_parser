from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

import yandex_food_parser
from config import database
from repository import xlsx_request_repository


def main():
    database.base.metadata.create_all(bind=database.engine)
    session = database.session_local()

    while True:
        xs = xlsx_request_repository.find_not_started(session)
        for xlsx_request_vo in xs:
            process_xlsx(session, xlsx_request_vo)
        time.sleep(5)
