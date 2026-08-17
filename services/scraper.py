import random
from contextlib import ExitStack

import seleniumbase


class TicketmasterScraper:
    """Preconfigured seleniumbase.SB context manager for this project."""

    def __init__(self, **kwargs):
        kwargs.setdefault("uc", True)
        kwargs.setdefault("test", True)
        kwargs.setdefault("pls", "none")
        kwargs.setdefault("ad_block", True)
        kwargs.setdefault("maximize", True)
        self._kwargs = kwargs
        self._stack = ExitStack()
        self.sb = None

    def __enter__(self):
        self.sb = self._stack.enter_context(seleniumbase.SB(**self._kwargs))
        return self

    def __exit__(self, *exc_info):
        return self._stack.__exit__(*exc_info)

    def __getattr__(self, name):
        return getattr(self.sb, name)

    def open_event(self, url: str) -> None:
        self.sb.open(url)

    def wait_for_tickets(self, timeout=15) -> None:
        self.sb.wait_for_element("//span[@data-bdd='quick-picks-sort-button-asc']", by="xpath", timeout=timeout)

    def accept_acknowledge(self) -> None:
        self.sb.click("//button[@data-analytics='accept-modal-accept-button']", by="xpath")

    def set_price_range(self, price_from: int, price_to: int) -> None:
        self.sb.type("//input[@aria-describedby='label-description-min']", str(price_from), by="xpath")
        self.sb.type("//input[@aria-describedby='label-description-max']", f"{price_to}\n", by="xpath")

    def select_quantity(self, quantity: int) -> None:
        self.sb.execute_script("document.querySelector('select#filter-bar-quantity').focus();")
        self.sb.press_keys("select#filter-bar-quantity", str(quantity))

    def book_tickets(self) -> None:
        count = len(self.sb.find_elements("div[data-analytics='offer-card']"))
        index = random.randint(3, count) # NOT TO CHOSE FIRST ONES TODO: move to env
        self.sb.click(f"(//div[@data-analytics='offer-card'])[{index}]", by="xpath")
