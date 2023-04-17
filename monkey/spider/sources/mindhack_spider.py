import sys
sys.path.append('E://Project/Rrawl')

from ruia import AttrField, Item, Request, Spider, TextField
from ruia_ua import middleware as ua_middleware


from monkey.database.motor_base import MotorBase


class ArchivesItem(Item):
    # TODO: target_item is not used
    target_item = TextField(css_select="")
    href = AttrField(css_select="", attr="href")


class ArticleListItem(Item):
    target_item = TextField(css_select="div.row h2.entry-title")
    title = TextField(css_select="h2.entry-title>a")
    href = AttrField(css_select="h2.entry-title>a", attr="href")


class BlogSpider(Spider):
    # 设置启动URL
    start_urls = ["http://mindhacks.cn/"]
    # 爬虫模拟请求的配置参数
    request_config = {"RETRIES": 5, "DELAY": 0, "TIMEOUT": 5}
    # 请求信号量
    concurrency = 10
    blog_nums = 0

    async def parse(self, res):
        try:
            # 用于获取MongoDB数据库的实例。它创建了MotorBase类的新实例，并使用get_db()方法获取数据库实例。
            self.mongo_db = MotorBase(loop=self.loop).get_db()

        except Exception as e:
            # 如果获取数据库实例时出现异常，它将记录异常信息并打印出来
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

    # 保存数据
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
    # 启动程序
    BlogSpider.start(middleware=ua_middleware)


if __name__ == "__main__":
    main()