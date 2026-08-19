import time
import threading
from concurrent.futures import ThreadPoolExecutor
from itertools import repeat

from core.config import (
    DOMAIN, EVENT, PRICE_FROM, PRICE_TO, QUANTITY, EXCLUDE_FIRST, EMAIL, PASSWORD, BROWSER_COUNT,
)
from core.shcemas import Tickets
from services.scraper import TicketmasterScraper


def run_worker(worker_id: int, stop_event: threading.Event, active_lock: threading.Lock) -> None:
    while not stop_event.is_set():
        try:
            if stop_event.is_set():
                return
            with TicketmasterScraper() as scraper:
                scraper.open(f"{DOMAIN}{EVENT}")
                scraper.accept_acknowledge()
                scraper.set_price_range(PRICE_FROM, PRICE_TO)
                scraper.select_quantity(QUANTITY)

                while not active_lock.acquire(timeout=1):
                    if stop_event.is_set():
                        return

                try:
                    while not scraper.tickets_available():
                        if stop_event.is_set():
                            return
                        scraper.reload_tickets()

                    if stop_event.is_set():
                        return

                    scraper.book_tickets(EXCLUDE_FIRST)

                    scraper.wait_for_redirecting()  # -> auth.ticketmaster.com
                    scraper.register(EMAIL, PASSWORD)

                    url = scraper.wait_for_redirecting()  # -> checkout url

                    tickets = Tickets(
                        url=url,
                        event_url=f"{DOMAIN}{EVENT}",
                        email=EMAIL,
                        quantity=scraper.quantity,
                    )

                    print(f"[worker {worker_id}] {tickets}")
                    stop_event.set()

                    time.sleep(1000)
                finally:
                    active_lock.release()
            return
        except Exception as e:
            print(f"[worker {worker_id}] error, restarting: {e}")


def main() -> None:
    stop_event = threading.Event()
    active_lock = threading.Lock()
    with ThreadPoolExecutor(max_workers=BROWSER_COUNT) as pool:
        list(pool.map(run_worker, range(BROWSER_COUNT), repeat(stop_event), repeat(active_lock)))


if __name__ == "__main__":
    main()
