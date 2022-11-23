import time

import yandex_food_parser
from config import database
from repository import xlsx_request_repository


def main():
    database.base.metadata.create_all(bind=database.engine)
    session = database.session_local()

    while True:
        xs = xlsx_request_repository.find_not_started(session)
        for xlsx_request_vo in xs:
            yandex_food_parser.process_xlsx(session, xlsx_request_vo)
        time.sleep(5)

main()
