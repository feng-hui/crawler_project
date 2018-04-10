# -*- coding: utf-8 -*-
import re
import time
import scrapy
import hmac
import json
from scrapy.http import Request, FormRequest
from scrapy.loader import ItemLoader
from common_crawlers.items import ZhiHuQuestionsItem, ZhiHuAnswersItem
from scrapy.linkextractors import LinkExtractor
from urllib import parse
from common_crawlers.utils.common import timestamp_to_date


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['zhihu.com']
    start_urls = ['https://www.zhihu.com/']
    login_url = "https://www.zhihu.com/signup"
    login_url2 = "https://www.zhihu.com/api/v3/oauth/sign_in"
    test_url = "https://www.zhihu.com/inbox"
    test_url2 = "https://www.zhihu.com/question/266491546"
    host_url = "https://www.zhihu.com/"
    captcha_url = "https://www.zhihu.com/api/v3/oauth/captcha?lang=en"
    answer_api_url = "https://www.zhihu.com/api/v4/questions/{}/answers?sort_by=default" \
                     "&include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info" \
                     "%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason" \
                     "%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment" \
                     "%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2C" \
                     "comment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info" \
                     "%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting" \
                     "%2Cis_thanked%2Cis_nothelp%2Cupvoted_followees%3Bdata%5B%2A%5D.mark_infos" \
                     "%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%3F%28type" \
                     "%3Dbest_answerer%29%5D.topics&limit={}&offset={}"
    client_id = 'c3cef7c66a1843f8b3a9e6a1e3160e20'
    limit = 20
    offset = 0
    headers = {
        'authorization': 'oauth {}'.format(client_id),
        'host': 'www.zhihu.com',
        'origin': 'https://www.zhihu.com',
        'refer': 'https://www.zhihu.com/signup?next=%2F',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
    }
    custom_settings = {
        'COOKIES_ENABLED': True,
        'DOWNLOAD_DELAY': 1.5
    }

    def parse(self, response):
        # self.logger.info('正在抓取的url是：{}'.format(response.url))
        # pattern = '.*/question/(\d+)[/|$]'
        # link_extractor = LinkExtractor(allow=pattern, attrs=('href',), tags='a')
        # all_links = link_extractor.extract_links(response)
        # for each_link in all_links:
        #     each_link = parse.urljoin(self.host_url, each_link.url)
        #     question_link = re.search(r'(.*/question/(\d+)[/|$])', each_link)
        #     question_id = question_link.group(2)
        #     yield Request(question_link.group(1),
        #                   callback=self.parse_questions,
        #                   headers=self.headers,
        #                   meta={'question_id': question_id})
        # 测试用
        yield Request(self.test_url2,
                      callback=self.parse_questions,
                      headers=self.headers,
                      meta={'question_id': 266491546})

    def parse_questions(self, response):
        """问题页面的抓取items"""
        self.logger.info('正在抓取的url是：{}'.format(response.url))
        question_id = response.meta['question_id']
        loader = ItemLoader(item=ZhiHuQuestionsItem(), response=response)
        loader.add_xpath('title', '//h1[@class="QuestionHeader-title"]/text()')
        loader.add_xpath('content', '//div[@class="QuestionHeader-detail"]/div/div/span/text()')
        # loader.add_value('question_id', re.search(r'(\d+)', response.url).group(1))
        loader.add_value('question_id', question_id)
        loader.add_value('question_url', response.url)
        loader.add_xpath('comment_nums', '//div[@class="QuestionHeader-Comment"]/button/text()')
        loader.add_xpath('focused_nums', '//strong[@class="NumberBoard-itemValue"]/text()')
        loader.add_xpath('viewed_nums', '//strong[@class="NumberBoard-itemValue"]/text()')
        loader.add_xpath('answer_nums', '//h4[@class="List-headerText"]/span/text()')
        loader.add_xpath('topics', '//a[@class="TopicLink"]/div/div/text()')
        question_item = loader.load_item()
        yield question_item

        # 回答api的抓取
        # answer_url = self.answer_api_url.format(str(question_id), self.limit, self.offset)
        # yield Request(answer_url,
        #               callback=self.parse_answers,
        #               headers=self.headers)



    def parse_answers(self, response):
        """回答api抓取items"""
        self.logger.info('正在抓取的url是：{}'.format(response.url))
        answer_api_json = json.loads(response.text)
        is_end = answer_api_json['paging']['is_end']
        next_url = answer_api_json['paging']['next']
        all_answer_data = answer_api_json['data']
        for each_answer in all_answer_data:
            loader = ItemLoader(item=ZhiHuAnswersItem(), response=response)
            loader.add_value('answer_id', each_answer['id'])
            loader.add_value('answer_url', each_answer['url'])
            loader.add_value('question_id', each_answer['question']['id'])
            loader.add_value('author_id', each_answer['author']['id'])
            loader.add_value('answer_content', each_answer['content'])
            loader.add_value('answer_praise_nums', each_answer['voteup_count'])
            loader.add_value('answer_comments_nums', each_answer['comment_count'])
            loader.add_value('answer_create_time', timestamp_to_date(each_answer['created_time']))
            return loader.load_item()
        if not is_end:
            yield Request(next_url,
                          headers=self.headers,
                          callback=self.parse_answers)

    def get_signature(self, grant_type, source, timestamp):
        """获取签名"""
        r = hmac.new(b'd1b964811afb40118a12068ff74a12f4', digestmod='sha1')
        r.update(grant_type.encode('utf-8'))
        r.update(self.client_id.encode('utf-8'))
        r.update(source.encode('utf-8'))
        r.update(timestamp.encode('utf-8'))
        signature = r.hexdigest()
        return signature

    def start_requests(self):
        """请求开始"""
        yield Request(self.captcha_url, headers=self.headers, callback=self.to_login)

    def to_login(self, response):
        """登录"""
        show_captcha = json.loads(response.body.decode('utf-8'))
        # self.logger.info(show_captcha)
        grant_type = 'password'
        timestamp = str(int(time.time() * 1000))
        source = 'com.zhihu.web'
        username = '18610379194'
        password = 'tuyue7208562'
        try:
            is_show_captcha = show_captcha['show_captcha']
            if not is_show_captcha:
                # 不显示验证码
                params = {
                    'client_id': self.client_id,
                    'grant_type': grant_type,
                    'timestamp': timestamp,
                    'source': source,
                    'signature': self.get_signature(grant_type, source, timestamp),
                    'username': username,
                    'password': password,
                    'captcha': '',
                    'lang': 'en',
                    'ref_source': 'homepage',
                    'utm_source': ''
                }
                yield FormRequest(self.login_url2, headers=self.headers, formdata=params, method='POST',
                                  callback=self.is_login)
            else:
                # 需要验证码
                pass
        except KeyError:
            # client id 过期或其他原因
            self.logger.error(show_captcha['error']['message'])

    def is_login(self, response):
        """检测是否登录成功"""
        # login_json = json.loads(response.text)
        # print(login_json)
        self.logger.info('正在抓取的url是：{}'.format(response.url))
        for url in self.start_urls:
            yield Request(url, headers=self.headers)
