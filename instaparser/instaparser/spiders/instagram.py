import json
import re

import scrapy
from scrapy.http import HtmlResponse
from instaparser.instaparser.items import InstaparserItem
from urllib.parse import urlencode
from copy import deepcopy


with open('log_info.txt', 'r') as f:
   pwd = f.readline()

class InstaSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com']
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    inst_login = 'nikita_batumi'
    inst_pwd = pwd
    parse_users = ['learn_georgian_', 'learn.georgianlanguage']
    inst_followers_link = 'https://i.instagram.com/api/v1/friendships/'

    def parse(self, response: HtmlResponse):
        csrf = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.inst_login_link,
            method='POST',
            callback=self.login,
            formdata={'username': self.inst_login, 'enc_password': self.inst_pwd},
            headers={'X-CSRFToken': csrf}
        )

    def login(self, response: HtmlResponse):
        j_body = response.json()
        if j_body.get('authenticated'):
            for user in self.parse_users:
                yield response.follow(
                    f"/{user}",
                    callback=self.user_data_parse and self.user_data_parse_2,
                    cb_kwargs={'username': user}
                )

    def user_data_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        url_followers = f'{self.inst_followers_link}/{user_id}/followers/?count=12&max_id=12'
        yield response.follow(url_followers,
                              callback=self.user_followers_parse,
                              cb_kwargs={'username': username,
                                         'user_id': user_id})

    def user_data_parse_2(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        url_following = f'{self.inst_followers_link}/{user_id}/following/?count=12&max_id=12'
        yield response.follow(url_following,
                              callback=self.user_followers_parse,
                              cb_kwargs={'username': username,
                                         'user_id': user_id})

    def user_followers_parse(self, response: HtmlResponse, username, user_id, variables):
        j_data = response.json()
        page_info = j_data.get('data').get('user').get('edge_owner_to_timeline_media').get('page_info')
        if page_info.get('has_next_page'):
            variables['next_max_id'] = page_info.get('max_id')
            url_followers = f'{self.inst_followers_link}/{user_id}/followers/?count=12&max_id=12'
            url_following = f'{self.inst_followers_link}/{user_id}/following/?count=12&max_id=12'
            yield response.follow(url_followers and url_following,
                                  callback=self.user_followers_parse,
                                  cb_kwargs={'username': username,
                                             'user_id': user_id},
                                  headers={"User-Agent": 'Instagram 155.0.0.37.107'})

        posts = j_data.get('data')

        for post in posts:
            item = InstaparserItem(
                user_id=user_id,
                username=username,
                photo=post.get('node').get('display_url')
            )
            yield item

    def fetch_csrf_token(self, text):
        """Get CSRF token from auth"""
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        try:
            matched = re.search(
                '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
            ).group()
            return json.loads(matched).get('id')
        except:
            return re.findall('\"id\":\"\\d+\"', text)[-1].split('"')[-2]
