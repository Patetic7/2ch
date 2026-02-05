import logging
import os
import re
import sys
import time
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S",
)
logger = logging.getLogger(__name__)

VALID_THREAD_REGEX = r"^https?://(?:2ch\.[a-z]{2,5}/[a-z]+/res/\d+\.html|arhivach\.[a-z]{2,5}/thread/\d+/?)$"

MEDIA_TYPES = {
    "img": ["jpg", "jpeg", "png", "gif", "webp"],
    "vid": ["mp4", "webm", "mkv", "avi", "mov"],
}
MEDIA_TYPES["both"] = MEDIA_TYPES["img"] + MEDIA_TYPES["vid"]


def download(client, output_path, media_types, thread):
    try:
        res = client.get(thread)
        res.raise_for_status()
    except Exception as e:
        logger.error(f"Ошибка загрузки {thread}: {e}")

    soup = BeautifulSoup(res.text, "html.parser")
    a = soup.find_all("a", href=True)

    links = set()
    for link in a:
        if link["href"].endswith(tuple(media_types)):
            links.add(urljoin(thread, link["href"]))

    if not links:
        logger.info(f"Нет медиафайлов в {thread}")
        return

    logger.info(f"Найдено {len(links)} медиафайлов в {thread}")

    thread_id = re.search(r"/(\d+)(?:\.html)?(?:#.*)?/?$", thread)

    if not thread_id:
        logger.error(f"Не удалось получить идентификатор треда: {thread}")
        return

    thread_id = thread_id.group(1)

    thread_folder = os.path.join(output_path, thread_id)
    os.makedirs(thread_folder, exist_ok=True)

    for link in links:
        filename = link.split("/")[-1]
        filepath = os.path.join(thread_folder, filename)
        try:
            res = client.get(link)
            res.raise_for_status()
        except Exception as e:
            logger.error(f"Ошибка загрузки {link}: {e}")
        else:
            with open(filepath, "wb") as f:
                f.write(res.content)
                logger.info(f"Сохранено: {filename}")


def main():
    if len(sys.argv) < 4:
        logger.error(
            "Использование: "
            "python "
            "2ch.py "
            "<путь к папке сохранения> "
            "<img | vid | both> "
            "<ссылка на первый тред> "
            "<ссылка на второй тред> ..."
        )
        sys.exit(1)

    output_path = sys.argv[1]
    if (
        not output_path
        or not os.path.exists(output_path)
        or not os.path.isdir(output_path)
    ):
        logger.error(
            "Путь к папке сохранения не указан, невалидный или такой папки не существует"
        )
        sys.exit(1)

    media_type = sys.argv[2]
    if media_type not in ["img", "vid", "both"]:
        logger.error("Неверный тип медиафайла")
        sys.exit(1)

    threads = sys.argv[3:]
    if not all(re.match(VALID_THREAD_REGEX, thread) for thread in threads):
        logger.error(f"Неверная ссылка на тред {thread}")
        sys.exit(1)

    if not threads:
        logger.error("Не указаны ссылки на треды")
        sys.exit(1)

    logger.info(f"Путь к папке сохранения: {output_path}")
    logger.info(f"Типы медиафайлов: {MEDIA_TYPES[media_type]}")
    logger.info(f"Ссылки на треды: {threads}")

    with httpx.Client(verify=False, timeout=30) as client:
        for thread in threads:
            download(client, output_path, MEDIA_TYPES[media_type], thread)


if __name__ == "__main__":
    start = time.perf_counter()
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Завершение...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Ошибка: {e}")
    finally:
        end = time.perf_counter()
        logger.info(f"Время выполнения: {end - start:.2f} секунд")
