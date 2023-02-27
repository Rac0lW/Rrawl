import asyncio

from ruia import Item, TextField

class DoubanItem(Item):
    target_item = TextField(css_select="div.item")
    title = TextField(css_select="span.title")

    async def cleam_title(self, title):
        if isinstance(title, str):
            return title
        else:
            return "".join([i.text.strip().replace("\xa0", "") for i in title])

async def run_item(url: str):
    async for item in DoubanItem.get_items(url=url):
        print(item)

items = asyncio.get_event_loop().run_until_complete(
    run_item("https://movie.douban.com/top250")
)