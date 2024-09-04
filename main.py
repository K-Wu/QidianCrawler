from __future__ import annotations
import argparse
import random
import time
from pathlib import Path
from typing import Optional

import os

from rich.progress import Progress

from utils import Crawler, log


def main() -> str | None:
    # Returns the absolute path of the saved file
    parser = argparse.ArgumentParser(
        description="🕸️ 基于DrissionPage库的起点小说爬虫。"
    )
    parser.add_argument(
        "-m",
        "--mode",
        choices=["full", "range", "word_count"],
        required=True,
        help='下载模式：选择 "full" 为全文下载，选择 "range" 为范围下载',
    )
    parser.add_argument("url", type=str, help="目录页的URL")

    # 这些参数仅在'range'模式下需要
    parser.add_argument(
        "-u",
        "--upper-bound",
        type=int,
        default=None,
        help='范围下载的上界（仅当选择 "range" 模式时有效）；或是字数下载的最大字数（"word_count"模式）',
    )
    parser.add_argument(
        "-l",
        "--lower-bound",
        type=int,
        default=None,
        help='范围下载的下界（仅当选择 "range" 模式时有效）',
    )
    args = parser.parse_args()

    if args.mode == "full":
        path = full_download(args.url)
    elif args.mode == "range":
        if args.upper_bound is None or args.lower_bound is None:
            parser.error(
                "在范围模式下，必须同时提供 --upper-bound 和 --lower-bound"
            )
        path = range_download(args.url, args.lower_bound, args.upper_bound)
    else:
        if args.upper_bound is None:
            parser.error("在字数模式下，必须提供 --upper-bound")
        path = full_download(args.url, word_limit=args.upper_bound)
    return path


def save(name: str, content: str) -> str:
    # Returns the absolute path of the saved file
    if not os.path.exists("qd_novels"):
        os.mkdir("qd_novels")
    path = Path(f"qd_novels/{name}.txt")
    path.write_text(content, "utf-8")
    return path.resolve().as_posix()


def full_download(url: str, word_limit: Optional[int] = None) -> str | None:
    # Returns the absolute path of the saved file
    crawler = Crawler()
    log.info("🎉 DrissionPage初始化完毕")

    index = crawler.get_index(url)
    log.info(f"🎈 正在下载《{index.name}》，具有{len(index.chpts)}章节的小说")

    chpts: list[str] = []
    word_count: int = 0
    with Progress() as progress:
        if word_limit is not None:
            download = progress.add_task("🛻 下载中", total=word_limit)
        else:
            download = progress.add_task("🛻 下载中", total=len(index.chpts))
        try:
            for info in index.chpts:
                chpt: str = crawler.get_chpt(info.url)
                # Count the number of words in the chapter
                if word_limit is not None:
                    progress.advance(download, advance=min(len(chpt), word_limit - word_count))
                    if word_count > word_limit:
                        break
                else:
                    progress.advance(download)
                word_count += len(chpt)
                chpts.append(chpt)
                # time.sleep(random.uniform(2, 5))
        except Exception as e:
            log.error(e)
        finally:
            content = "\n".join(chpts)
            save_name = index.name
            if word_limit is not None:
                save_name += f"-wl{word_limit}"
            path = save(save_name, content)
            log.info("✨ 小说保存完毕")
            return path


def range_download(url: str, lower_bound: int, upper_bound: int) -> str | None:
    if lower_bound > upper_bound:
        lower_bound, upper_bound = upper_bound, lower_bound
    lower_bound -= 1  # 更加符合习惯用法

    crawler = Crawler()
    log.info("🎉 DrissionPage初始化完毕")

    index = crawler.get_index(url)
    lower_name = index.chpts[lower_bound].name
    upper_name = index.chpts[upper_bound - 1].name
    log.info(
        f"🎈 正在下载《{index.name}》，范围从《{lower_name}》到《{upper_name}》"
    )

    chpts: list[str] = []
    with Progress() as progress:
        download = progress.add_task(
            "🛻 下载中", total=upper_bound - lower_bound
        )
        try:
            for info in index.chpts[lower_bound:upper_bound]:
                chpt = crawler.get_chpt(info.url)
                chpts.append(chpt)
                progress.advance(download)
                # time.sleep(random.uniform(5, 7))
        except Exception as e:
            log.error(e)
        finally:
            content = "\n".join(chpts)
            path = save(
                f"{index.name}-{lower_bound + 1}-{upper_bound}", content
            )
            log.info("✨ 小说保存完毕")
            return path


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log.error(e)
