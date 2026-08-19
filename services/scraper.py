import random
import threading
import time
from contextlib import ExitStack
from typing import Optional

import seleniumbase

from core.config import DOMAIN


class TicketmasterScraper:
    """Preconfigured seleniumbase.SB context manager for this project."""

    _launch_lock = threading.Lock()

    def __init__(self, **kwargs):
        kwargs.setdefault("uc", True)
        kwargs.setdefault("pls", "none")
        kwargs.setdefault("ad_block", True)
        kwargs.setdefault("maximize", True)
        self._kwargs = kwargs
        self._stack = ExitStack()
        self.sb = None
        self.quantity = None
        self._toggled = False
        self._last_url = None

    def __enter__(self):
        with self._launch_lock:
            self.sb = self._stack.enter_context(seleniumbase.SB(**self._kwargs))
        return self

    def __exit__(self, *exc_info):
        return self._stack.__exit__(*exc_info)

    def __getattr__(self, name):
        return getattr(self.sb, name)

    def open_login(self, timeout: int = 20) -> None:
        self.sb.open(DOMAIN)
        self.sb.click("//button[@data-testid='accountLink']", by="xpath", timeout=timeout)

    def register(self, email, password, timeout: int = 20) -> None:
        self.sb.wait_for_element("//input[@name='email']", by="xpath", timeout=timeout)
        self.sb.clear("//input[@name='email']", by="xpath", timeout=timeout)
        self.sb.press_keys("//input[@name='email']", email, by="xpath", timeout=timeout)
        self.sb.click("//button[@name='sign-in']", by="xpath", timeout=timeout)
        self.sb.wait_for_element("//input[@name='password']", by="xpath", timeout=timeout)
        self.sb.clear("//input[@name='password']", by="xpath", timeout=timeout)
        self.sb.press_keys("//input[@name='password']", password, by="xpath", timeout=timeout)

        self.sb.click("//button[@name='sign-in']", by="xpath", timeout=timeout)

        self.sb.click('button:contains("Not Right Now")', timeout=timeout)


    def open_event(self, url: str) -> None:
        self.sb.open(url)

    def wait_for_filters(self, timeout=15) -> None:
        self.sb.wait_for_element("//span[@data-bdd='quick-picks-sort-button-asc']", by="xpath", timeout=timeout)

    def accept_acknowledge(self, timeout=15) -> None:
        self.sb.click("//button[@data-analytics='accept-modal-accept-button']", by="xpath", timeout=timeout)

    def set_price_range(self, price_from: int, price_to: int) -> None:
        self.sb.type("//input[@aria-describedby='label-description-min']", str(price_from), by="xpath")
        self.sb.type("//input[@aria-describedby='label-description-max']", f"{price_to}\n", by="xpath")

    def select_quantity(self, quantity: int) -> None:
        self.quantity = int(quantity)
        self._set_quantity(self.quantity)

    def _set_quantity(self, quantity: int) -> None:
        self.sb.execute_script("document.querySelector('select#filter-bar-quantity').focus();")
        self.sb.press_keys("select#filter-bar-quantity", str(quantity))

    def reload_tickets(self) -> None:
        step = 1 if self.quantity <= 2 else -1
        self._toggled = not self._toggled
        target = self.quantity + step if self._toggled else self.quantity
        self._set_quantity(target)

    def tickets_available(self, timeout: int = 15) -> bool:
        self.sb.wait_for_any_of_elements_present(
            "div[data-analytics='offer-card']", "#noMatching", timeout=timeout,
        )
        if not self.sb.is_element_present("div[data-analytics='offer-card']"):
            return False
        return self.current_quantity() != 1

    def current_quantity(self) -> int:
        return int(self.sb.execute_script("return document.querySelector('select#filter-bar-quantity').value;"))

    def book_tickets(self, exclude_first: int = 0, timeout: int = 20) -> None:
        tickets = self.sb.find_elements("div[data-analytics='offer-card']")
        start = min(exclude_first, len(tickets) - 1)
        ticket = random.choice(tickets[start:])
        ticket.click()

        self._last_url = self.sb.get_current_url()
        self.sb.click("[data-analytics='quick-pick-buy-now'], #offer-card-buy-button", timeout=timeout)

    def wait_for_redirecting(self, timeout: int = 15) -> Optional[str]:
        for _ in range(timeout):
            current_url = self.sb.get_current_url()
            if current_url != self._last_url:
                self._last_url = current_url
                return current_url
            time.sleep(1)
        return None
