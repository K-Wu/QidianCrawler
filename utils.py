from __future__ import annotations
import logging
from typing import NamedTuple

from DrissionPage import ChromiumPage, ChromiumOptions
from rich.logging import RichHandler

logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, tracebacks_show_locals=True)],
)
log = logging.getLogger("rich")


class ChapterInfo(NamedTuple):
    name: str
    url: str


class Index(NamedTuple):
    name: str
    chpts: list[ChapterInfo]


class Crawler:
    def __init__(self, headless_flag: bool = True) -> None:
        if headless_flag:
            co = ChromiumOptions().headless()
            self.page = ChromiumPage(co)
        else:
            self.page = ChromiumPage()

    def __del__(self) -> None:
        self.page.quit()

    def get_index(self, url: str) -> Index:
        self.page.get(url)
        bookname = self.page.ele("#bookName").text
        elems = self.page.s_eles(".chapter-name")
        urls: list[ChapterInfo] = []
        for elem in elems:
            name = elem.text
            href = elem.attr("href")
            if href is not None:
                urls.append(ChapterInfo(name, href))
        return Index(bookname, urls)

    def get_chpt(self, chpt: str) -> str:
        self.page.get(chpt)
        content: list[str] = []
        title = self.page.ele(".:title").text
        content.append(title)
        for elem in self.page.eles(".content-text"):
            content.append(elem.text)
        return "\n".join(content)
