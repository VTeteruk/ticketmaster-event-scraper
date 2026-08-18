import time

from core.config import DOMAIN, EVENT, PRICE_FROM, PRICE_TO, QUANTITY, EXCLUDE_FIRST, EMAIL, PASSWORD
from services.scraper import TicketmasterScraper


def main() -> None:
    with TicketmasterScraper() as scraper:
        scraper.register(EMAIL, PASSWORD)
        time.sleep(3)
        scraper.open(f"{DOMAIN}{EVENT}")
        scraper.accept_acknowledge()
        scraper.set_price_range(PRICE_FROM, PRICE_TO)
        scraper.select_quantity(QUANTITY)

        scraper.wait_for_filters()

        scraper.book_tickets(EXCLUDE_FIRST)

        url = scraper.wait_for_redirecting()

        print(f"url: {url}")

        time.sleep(1000)


if __name__ == "__main__":
    main()
