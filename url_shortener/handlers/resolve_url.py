# -*- coding: utf-8 -*-

from tornado.web import RequestHandler


class ResolveURLHandler(RequestHandler):
    def initialize(self):
        self.redis = self.application.settings['redis']

    def get(self, short_id):
        if short_id == '':
            self.write('''Hello!<br> <br>
                       Available actions:<br>
                       POST /shorten_url - shorten URL specified in the json format: {"url": "https://www.example.com/"}<br>
                       GET shortened_url - resolve shortened URL''')
            self.finish()
            return
        url = self.redis.get_url(short_id)
        if url:
            self.redis.update_expiration(short_id)
            self.redirect(url.decode("utf-8"))
        else:
            self.send_error(404, reason='Shortened url not found')
