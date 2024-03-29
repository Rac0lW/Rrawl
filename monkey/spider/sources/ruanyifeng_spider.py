import sys
sys.path.append('E://Project/Rrawl')

from ruia import AttrField, Item, Request, Spider, TextField
from ruia_ua import middleware as ua_middleware
from monkey.database.motor_base  import MotorBase


class ArchivesItem(Item):
    target_item = TextField(css_select="div#beta-inner li.module-list-item")
    href = AttrField(css_select="li.module-list-item>a", attr="href")


class ArticleListItem(Item):
    target_item = TextField(css_select="div#alpha-inner li.module-list-item")
    title = TextField(css_select="li.module-list-item>a")
    href = AttrField(css_select="li.module-list-item>a", attr="href")


class BlogSpider(Spider):
    """
    针对博客源 http://www.ruanyifeng.com/blog/archives.html 的爬虫
    这里为了模拟ua，引入了一个 ruia 的第三方扩展
        - ruia-ua: https://github.com/ruia-plugins/ruia-ua
        - pipenv install ruia-ua
        - 此扩展会自动为每一次请求随机添加 User-Agent
    """

    # 设置启动URL
    start_urls = ["http://www.ruanyifeng.com/blog/archives.html"]
    # 爬虫模拟请求的配置参数
    request_config = {"RETRIES": 10, "DELAY": 0, "TIMEOUT": 5}
    # 请求信号量
    concurrency = 10
    blog_nums = 0

    async def parse(self, res):
        try:
            self.mongo_db = MotorBase(loop=self.loop).get_db()
        except Exception as e:
            self.logger.exception(e)
        async for item in ArchivesItem.get_items(html=await res.text()):
            yield Request(
                item.href,
                callback=self.parse_item,
                request_config=self.request_config,
            )

    async def parse_item(self, res):
        async for item in ArticleListItem.get_items(html=await res.text()):
            # 已经抓取的链接不再请求
            is_exist = (
                await self.mongo_db.source_docs.find_one({"url": item.href}) or {}
            )

            if not is_exist.get("html"):
                yield Request(
                    item.href,
                    callback=self.save,
                    metadata={"title": item.title},
                    request_config=self.request_config,
                )

    async def save(self, res):
        html = await res.text()
        data = {"url": res.url, "title": res.metadata["title"], "html": html}
        if html:
            try:
                await self.mongo_db.source_docs.update_one(
                    {"url": data["url"]}, {"$set": data}, upsert=True
                )
            except Exception as e:
                self.logger.exception(e)


def main():
    # 启用代理池插件
    BlogSpider.start(middleware=ua_middleware)


if __name__ == "__main__":
    main()