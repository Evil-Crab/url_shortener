# -*- coding: utf-8 -*-

from urllib.parse import urlparse
import json


from tornado.ioloop import IOLoop
import tornado.web
from tornado.httpserver import HTTPServer
import validators

from url_shortener import base62
from url_shortener.redis_wrapper import RedisWrapper

app = tornado.web.Application(debud=True)

server = HTTPServer(app)
server.bind(80)
server.start(8)

redis = RedisWrapper('localhost', 6379)


class ResolveURLHandler(tornado.web.RequestHandler):
    async def get(self, short_id):
        url = redis.get_url(short_id)
        if url:
            redis.update_expiration(short_id)
            self.redirect(url.decode("utf-8"))
        else:
            self.send_error(404, reason='Shortened url not found')


class ShortenURLHandler(tornado.web.RequestHandler):
    def prepare(self):
        if self.request.body:
            try:
                self.request.json = json.loads(self.request.body)
            except ValueError:
                self.send_error(400, reason='Malformed request')  # Bad Request

    async def post(self):
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

            short_id = redis.get_short_id(url)
            if short_id:
                self.set_status(200)
                redis.update_expiration(short_id)
                self.write({'shortened_url': f'http://{self.request.host}/{short_id.decode("utf-8")}'})
                self.finish()
            else:
                new_id = base62.generate_id()
                while redis.get_url(new_id) is not None:
                    new_id = base62.generate_id()
                redis.set_pair(new_id, url)
                self.set_status(201)
                self.write({'shortened_url': f'http://{self.request.host}/{new_id}'})
                self.finish()


app.add_handlers(".*$", [(r'/shorten_url', ShortenURLHandler),
                         (r'/(\w+)', ResolveURLHandler)])
IOLoop.instance().start()
