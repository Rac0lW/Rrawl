
import sys
import subprocess
sys.path.append("..")
sys.path.append('E://Project/Rrawl')


import time
from sanic import Blueprint

from jinja2 import Environment, PackageLoader, select_autoescape
from sanic.response import html, json, text

from monkey.common.doc_search import doc_search
from monkey.config.config import Config

bp_home = Blueprint('monkey_views_bp_home')
bp_home.static('/statics', Config.BASE_DIR + '/statics/')

# 开启异步特性  要求3.6+
enable_async = sys.version_info >= (3, 6)

# jinjia2 config
env = Environment(
    loader=PackageLoader('bp_home', '../templates'),
    autoescape=select_autoescape(['html', 'xml', 'tpl']),
    enable_async=enable_async)


async def template(tpl, **kwargs):
    template = env.get_template(tpl)
    rendered_template = await template.render_async(**kwargs)
    return html(rendered_template)


@bp_home.route('/', methods=['GET', 'POST'], name = 'fuck')
async def index(request):
    if request.method == 'POST':
        if request.form.get('active') == 'true':
            # active the crawl
            print("active the crawl!")
            subprocess.call("python ../spider/spider_console.py", shell=True)
            return await template('index.html', title="active") 

            
        if request.form.get('indexandcompress') == 'true':
            # index and compress
            print("index and compress!")
            subprocess.call("python ../common/doc_tools.py", shell=True)
            return await template('index.html', title="indexandcompress") 
    return await template('index.html')


@bp_home.route('/search', name = 'fuck2')
async def index(request):
    start = time.time()
    # 获取查询参数
    query = str(request.args.get('q', '')).strip()
    if query:
        # 从缓存中查询
        cache_result = await request.app.ctx.cache.get(query)
        # 如果缓存存在
        if cache_result:
            result = cache_result
        else:
        # 如果缓存不存在，从数据库中查询，并将结果存入缓存
            mongo_db = request.app.ctx.mongo_db
            result = await doc_search(query=query, mongo_db=mongo_db)
            await request.app.ctx.cache.set(query, result)
        
        # 计算查询时间
        time_cost = float('%.6f' % (time.time() - start))
        # pay ..
        return await template(
            'search.html',
            title=query,
            result=result,
            count=len(result),
            time_cost=time_cost
        )

        # mongo_db = request.app.ctx.mongo_db
        # result = await doc_search(query=query, mongo_db=mongo_db)
        # return await template('search.html', title=query, result=result)
    else:
        return await template('index.html')

