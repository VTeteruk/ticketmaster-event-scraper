import time

from core.config import DOMAIN, EVENT, PRICE_FROM, PRICE_TO, QUANTITY, EXCLUDE_FIRST
from services.scraper import TicketmasterScraper


def main() -> None:
    with TicketmasterScraper() as scraper:
        scraper.open(f"{DOMAIN}{EVENT}")
        scraper.wait_for_tickets()
        scraper.accept_acknowledge()
        scraper.set_price_range(PRICE_FROM, PRICE_TO)
        scraper.select_quantity(QUANTITY)

        scraper.wait_for_tickets()

        scraper.book_tickets(EXCLUDE_FIRST)

        time.sleep(1000)


if __name__ == "__main__":
    main()
