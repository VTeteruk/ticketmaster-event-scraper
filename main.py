import time

from core.config import DOMAIN, EVENT, PRICE_FROM, PRICE_TO, QUANTITY
from services.scraper import TicketmasterScraper


def main() -> None:
    with TicketmasterScraper() as scraper:
        scraper.open(f"{DOMAIN}{EVENT}")
        scraper.wait_for_tickets()
        scraper.accept_acknowledge()
        scraper.set_price_range(PRICE_FROM, PRICE_TO)
        scraper.select_quantity(QUANTITY)

        scraper.wait_for_tickets()

        for _ in range(20):
            scraper.reload_tickets(QUANTITY)


if __name__ == "__main__":
    main()
