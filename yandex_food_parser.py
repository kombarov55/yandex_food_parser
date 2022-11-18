import time
import urllib
from datetime import datetime
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright, Page
from sqlalchemy.orm import Session

import api_service
import xlsx_service
from config import database
from model.restaurant import RestaurantVO
from model.xlsx_request import XlsxRequestVO, XlsxRequestStatus
from repository import restaurant_repository, food_repository, xlsx_request_repository


def set_location(page: Page):
    page.wait_for_selector("(//h2[@class='DesktopHeaderBlock_headerText DesktopHeaderBlock_headerTextBold'])[1]")
    location_text = page.locator("span.DesktopAddressButton_address").inner_text()
    if location_text == "Укажите адрес доставки":
        page.locator("button.DesktopHeader_addressButton").click()
    else:
        page.locator("button.DesktopUIButton_root").click()
        page.locator("div.UIPopupList_option").click()
    # page.click("svg.AppAddressInput_closeIcon");
    page.wait_for_selector(".DesktopLocationModal_wrapper")
    input_locator = page.locator("input.AppAddressInput_addressInput")
    input_locator.type("Москва, Красная площадь 3")
    page.click("div.react-autosuggest__suggestions-container")
    page.click("button.DesktopLocationModal_ok")
    page.wait_for_selector(
        "//span[@class='DesktopAddressButton_addressStreet' and contains(text(), 'Красная площадь')]")


def search(page, food_name):
    page.goto("https://eda.yandex.ru/search?query={}&type=all".format(food_name))
    page.wait_for_selector("//h1[contains(text(),'Найден')]")


def parse_all_shops(page, session):
    page.wait_for_load_state(state="networkidle")
    scroll_slowly_to_bottom(page)
    hrefs = get_hrefs(page)
    for href in hrefs:
        slug = get_query_param(href, "placeSlug")
        is_retail = href.startswith("/retail")
        page.goto("https://eda.yandex.ru/{}".format(href))
        page.wait_for_load_state(state="networkidle")

        if not is_retail:
            parse_restaurant(page, session, slug)
        else:
            parse_shop(session, page, slug)


def parse_restaurant(page, session, slug):
    page.wait_for_selector("div.NewCartFooterBottomBanner_root")
    time.sleep(1)

    if page.locator("div.Modal_modalWrapper").is_visible():
        page.click("div.ModalSurge_button")

    restaurant_name = page.locator("h1.RestaurantHeader_name").inner_text()
    rich_badges = page.locator("button.RestaurantHeader_richBadge")

    delivery_time = ""

    if rich_badges.count() == 2:
        delivery_badge = rich_badges.nth(0)
        delivery_time = delivery_badge.locator("div.RestaurantHeader_badgeTopLine").inner_text()

        rating_badge = rich_badges.nth(1)
        rating = rating_badge.locator("div.RestaurantHeader_badgeTopLine").inner_text()
        rating_count = rating_badge.locator("div.RestaurantHeader_badgeBottomLine").inner_text()
    else:
        rating_badge = rich_badges.nth(0)
        rating = rating_badge.locator("div.RestaurantHeader_badgeTopLine").inner_text()
        rating_count = rating_badge.locator("div.RestaurantHeader_badgeBottomLine").inner_text()

    page.click("button.RestaurantHeader_badge")
    page.wait_for_selector("div.RestaurantPopup_infoPopup")

    address = page.locator("span.RestaurantPopup_infoAddr").inner_text()

    vo = RestaurantVO(
        slug=slug,
        name=restaurant_name,
        rating=rating,
        rating_count=rating_count,
        delivery_time=delivery_time,
        address=address
    )
    print(f"{restaurant_name} {rating} {rating_count} {delivery_time} {address}")
    restaurant_repository.save(session, vo)
    food_list = api_service.load_restaurant_food(slug, slug)
    food_repository.save_all(session, food_list)


def parse_shop(session, page, slug):
    vo = api_service.load_retail_info(slug)
    restaurant_repository.save(session, vo)
    category_ids = get_retail_category_ids(page)
    food_list = api_service.load_retail_food(category_ids, slug)
    food_repository.save_all(session, food_list)


def get_retail_category_ids(page) -> list[int]:
    a_els = page.locator("a.UiKitDesktopShopMenuItem_menuLink")
    result = []
    for i in range(0, a_els.count()):
        a = a_els.nth(i)
        href = a.get_attribute("href")
        parse_result = urlparse(href)
        path_splitted = parse_result.path.split("/")
        category_id = path_splitted[len(path_splitted) - 1]
        result.append(int(category_id))
    return result


def get_hrefs(page):
    a_els = page.locator("a.DesktopSearchPlaceCarousel_link")
    result = []
    for i in range(0, a_els.count()):
        result.append(a_els.nth(i).get_attribute("href"))
    return result


def scroll(page, y):
    page.evaluate("window.scrollTo(0, {})".format(y))


def get_query_param(url, param):
    q = urllib.parse.urlparse(url)
    return urllib.parse.parse_qs(q.query)[param][0]


def scroll_slowly_to_bottom(page):
    current_height = 0
    delta = 500

    while True:
        page.evaluate("() => window.scrollTo(0, {});".format(current_height + delta))
        current_height += delta
        time.sleep(0.1)
        page_height = page.evaluate("() => document.body.scrollHeight;")
        if current_height > page_height:
            break


def process_xlsx(session: Session, xlsx_request_vo: XlsxRequestVO):
    with sync_playwright() as p:
        xlsx_request_vo.status = XlsxRequestStatus.started
        xlsx_request_vo.start_date = datetime.now()
        xlsx_request_repository.update(session, xlsx_request_vo)
        print("processing xlsx request: food_name={} start_date={}".format(xlsx_request_vo.food_name,
                                                                           xlsx_request_vo.start_date))

        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://eda.yandex.ru/moscow?shippingType=delivery")
        set_location(page)
        search(page, xlsx_request_vo.food_name)
        parse_all_shops(page, session)

        xs = food_repository.get_all(session)
        filename = "{}.xlsx".format(str(time.time()))
        path = "./reports/{}".format(filename)
        xlsx_service.to_csv(xs, path)

        xlsx_request_vo.status = XlsxRequestStatus.completed
        xlsx_request_vo.filename = filename
        xlsx_request_vo.end_date = datetime.now()
        xlsx_request_repository.update(session, xlsx_request_vo)
        print("completed")
# main()
