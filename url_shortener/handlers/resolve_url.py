# -*- coding: utf-8 -*-

from tornado.web import RequestHandler


class ResolveURLHandler(RequestHandler):
    def initialize(self):
        self.redis = self.application.settings['redis']

    def get(self, short_id):
        url = self.redis.get_url(short_id)
        if url:
            self.redis.update_expiration(short_id)
            self.redirect(url.decode("utf-8"))
        else:
            self.send_error(404, reason='Shortened url not found')
