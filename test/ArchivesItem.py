from ruia import AttrField, Item, Request, Response, Spider, TextField
from ruia_ua import middleware as ua_middleware


class ArchivesItem(Item):
    """
    eg: http://www.ruanyifeng.com/blog/archives.html
    """

    target_item = TextField(css_select="div#beta-inner li.module-list-item")
    href = AttrField(css_select="li.module-list-item>a", attr="href")


class ArticleListItem(Item):
    """
    eg: http://www.ruanyifeng.com/blog/essays/
    """

    target_item = TextField(css_select="div#alpha-inner li.module-list-item")
    title = TextField(css_select="li.module-list-item>a")
    href = AttrField(css_select="li.module-list-item>a", attr="href")


class BlogSpider(Spider):
    """
    针对博客源 http://www.ruanyifeng.com/blog/archives.html 的爬虫
    这里为了模拟ua，引入了一个Ruia的第三方扩展
        - Ruia-ua: https://github.com/howie6879/Ruia-ua
        - pipenv install Ruia-ua
        - 此扩展会自动为每一次请求随机添加 User-Agent
    """

    # 设置启动URL
    start_urls = ["http://www.ruanyifeng.com/blog/archives.html"]
    # 爬虫模拟请求的配置参数
    request_config = {"RETRIES": 3, "DELAY": 0, "TIMEOUT": 20}
    # 请求信号量
    concurrency = 10
    blog_nums = 0

    async def parse(self, res: Response):
        async for item in ArchivesItem.get_items(html=await res.text()):
            yield Request(item.href, callback=self.parse_item)

    async def parse_item(self, res: Response):
        async for item in ArticleListItem.get_items(html=await res.text()):
            self.logger.info(item)
            BlogSpider.blog_nums += 1


if __name__ == "__main__":
    BlogSpider.start(middleware=ua_middleware)
    print(f"博客总数为：{BlogSpider.blog_nums} 篇")