# crawler_project
爬虫项目集锦(all about crawlers)

# f139
富宝废有色抓取项目，可以通过phantomjs或headless chrome进行模拟登录，然后序列化登录获取到的session到本地文件，每次抓取前判断是否登录。

直接执行命令python main.py。

# xici

单机抓取xicidaili.com网站所有的代理ip

使用python3.5+、scrapy>=1.4,抓取数据超过62w+。

抓取过程截图如下：

![](https://github.com/feng-hui/crawler_project/blob/master/xici/crawler_process.png)

# login_zhihu

通过已经登录过的cookies来登录知乎，可以通过使用cookies参数或headers参数来登录，必须使用的参数为User-Agent，否则会报400错误