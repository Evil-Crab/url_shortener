# -*- coding: utf-8 -*-

import json
from urllib.parse import urlparse

import validators
from tornado.web import RequestHandler

from url_shortener import base62


class ShortenURLHandler(RequestHandler):
    def initialize(self):
        self.redis = self.application.settings['redis']

    def prepare(self):
        if self.request.body:
            try:
                self.request.json = json.loads(self.request.body)
            except ValueError:
                self.send_error(400, reason='Malformed request')  # Bad Request

    def post(self):
        url = self.request.json.get('url')
        if not url:
            self.send_error(400, reason='Missing url to shorten')
            return
        else:
            if not urlparse(url).scheme:
                url = 'http://' + url
            if not validators.url(url):
                self.send_error(400, reason='Malformed url')
                return

            short_id = self.redis.get_short_id(url)
            if short_id:
                self.set_status(200)
                self.redis.update_expiration(short_id)
                self.write({'shortened_url': f'http://{self.request.host}/{short_id.decode("utf-8")}'})
                self.finish()
            else:
                new_id = base62.generate_id()
                while self.redis.get_url(new_id) is not None:
                    new_id = base62.generate_id()
                self.redis.set_pair(new_id, url)
                self.set_status(201)
                self.write({'shortened_url': f'http://{self.request.host}/{new_id}'})
                self.finish()
