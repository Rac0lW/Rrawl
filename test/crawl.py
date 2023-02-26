import asyncio

from ruia import Item, TextField


class DoubanItem(Item):
    title = TextField(css_select='#content > h1 > span:nth-child(1)')

async_func = DoubanItem.get_item(url="https://movie.douban.com/subject/1292052/")

item = asyncio.get_event_loop().run_until_complete(async_func)

print(item)