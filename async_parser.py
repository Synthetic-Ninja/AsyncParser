from typing import NamedTuple, TypedDict
import asyncio
from functools import partial




import aiohttp
import bs4.element
from bs4 import BeautifulSoup

from exeptions import PageGetException, \
    ElementGetException, ParserExeption


class ParsedPage(NamedTuple):
    TITLE: str
    LOCATION: str
    PRICE: str
    AREA: str


def get_parsed_pages(link: str,
                     page_count: int | None) -> list[ParsedPage]:
    loop = _get_loop()
    result = loop.run_until_complete(_get_parsed_pages_list(loop=loop,
                                                            url=link,
                                                            task_count=page_count
                                                            ))

    return result


def _get_loop() -> asyncio.AbstractEventLoop:
    loop = asyncio.new_event_loop()
    return loop


async def _async_get_page(url: str) -> str | None:
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh;'
                      ' Intel Mac OS X 10_15_7) AppleWebKit/'
                      '537.36 (KHTML, like Gecko) Chrome/'
                      '105.0.0.0 Safari/537.36'
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return
            html = await resp.text()
            return html


def _parse_page(html: str,
                tag: str,
                class_name: str) -> bs4.element.ResultSet:

    soup = BeautifulSoup(html, 'html.parser')
    return soup.find_all(tag, class_=class_name)


def _parse_elem(elem: bs4.element,
                tag: str,
                class_name: str) -> str | None:

    text = elem.find(tag, class_=class_name)
    if text is None:
        return None

    return text.text.replace('\n', '').replace('  ', '')


async def _get_count_of_pages(link: str) -> int:
    page = await _async_get_page(link)
    if page is None:
        raise PageGetException

    parsed = _parse_page(html=page,
                         tag='a',
                         class_name='pagination__link')
    if parsed is None:
        raise ElementGetException

    return int(parsed[-2].text)


async def _get_parsed_info(url: str,
                           loop):
    page = await _async_get_page(url)
    if page is None:
        raise PageGetException

    first_parse = partial(_parse_page,
                          html=page,
                          tag='section',
                          class_name='listing-search-item')

    parsed_page = await loop.run_in_executor(None, first_parse)

    for list_elem in parsed_page:

        parse_title = partial(_parse_elem,
                              elem=list_elem,
                              tag='a',
                              class_name='listing-search-item__link--title'
                              )

        parse_location = partial(_parse_elem,
                                 elem=list_elem,
                                 tag='div',
                                 class_name='listing-search-item__sub-title'
                                 )

        parse_price = partial(_parse_elem,
                              elem=list_elem,
                              tag='div',
                              class_name='listing-search-item__price'
                             )

        parse_area = partial(_parse_elem,
                              elem=list_elem,
                              tag='li',
                              class_name='illustrated-features__item'
                              )


        #### Get more

        parsed_title = await loop.run_in_executor(None,
                                                  parse_title)
        parsed_location = await loop.run_in_executor(None,
                                                     parse_location)
        parsed_price = await loop.run_in_executor(None,
                                                  parse_price)
        parsed_area = await loop.run_in_executor(None,
                                                  parse_area)

    return ParsedPage(
        TITLE=parsed_title,
        LOCATION=parsed_location,
        PRICE=parsed_price,
        AREA=parsed_area,
                    )


async def _get_parsed_pages_list(
        url: str,
        loop,
        task_count: int | None):
    if task_count is None:

        try:
            task_count = await _get_count_of_pages(link=url) + 1
        except [ElementGetException, PageGetException]:
            raise ParserExeption
    else:
        task_count += 1

    tasks = []
    for x in range(1, task_count):
        task = asyncio.create_task(_get_parsed_info(url=f'{url}/page-{x}',
                                                    loop=loop))
        tasks.append(task)

    async_tasks = asyncio.gather(*tasks)
    await async_tasks

    return async_tasks.result()
