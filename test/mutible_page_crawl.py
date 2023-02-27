from ruia import Item, Spider, TextField


class DoubanItem(Item):
    """
    定义爬虫的目标字段
    """

    target_item = TextField(css_select="div.item")
    title = TextField(css_select="span.title")

    async def clean_title(self, title):
        if isinstance(title, str):
            return title
        else:
            return "".join([i.text.strip().replace("\xa0", "") for i in title])


class DoubanSpider(Spider):
    start_urls = ["https://movie.douban.com/top250"]

    async def parse(self, response):
        html = await response.text()
        etree = response.html_etree(html=html)
        pages = ["?start=0&filter="] + [
            i.get("href") for i in etree.cssselect(".paginator>a")
        ]
        for index, page in enumerate(pages):
            url = self.start_urls[0] + page
            yield self.request(
                url=url, metadata={"index": index}, callback=self.parse_item
            )

    async def parse_item(self, res):
        # 这里可以对结果做任何操作
        res_list = []
        async for item in DoubanItem.get_items(html=await res.text()):
            res_list.append(item)


if __name__ == "__main__":
    DoubanSpider.start()