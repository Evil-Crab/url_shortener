# -*- coding: utf-8 -*-

from datetime import datetime
from urllib.parse import urlparse
import json


from tornado.ioloop import IOLoop
import tornado.web
from tornado.httpserver import HTTPServer
from motor import MotorClient
from pymongo.errors import DuplicateKeyError
import validators

from url_shortener import base62

app = tornado.web.Application(debud=True)

server = HTTPServer(app)
server.bind(80)
server.start(8)


class ResolveURLHandler(tornado.web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        self.urls_coll = application.settings['db'].url_shortener.urls
        super().__init__(application, request, **kwargs)

    async def get(self, short_id):
        url_record = await self.urls_coll.find_one_and_update({'_id': short_id},
                                                              {'$set': {'last_access': datetime.utcnow()}})
        if url_record:
            self.redirect(url_record['url'])
        else:
            self.send_error(404, reason='Shortened url not found')


class ShortenURLHandler(tornado.web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        self.urls_coll = application.settings['db'].url_shortener.urls
        super().__init__(application, request, **kwargs)

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

            existing_record = await self.urls_coll.find_one({'url': url})
            if existing_record:
                self.set_status(200)
                self.write({'shortened_url': self.request.host + existing_record['_id']})
                self.finish()
            else:
                new_record = {'_id': base62.generate_id(),
                              'last_access': datetime.utcnow(),
                              'url': url}
                inserted = False
                while not inserted:
                    try:
                        await self.urls_coll.insert_one(new_record)
                        inserted = True
                    except DuplicateKeyError:
                        new_record['_id'] = base62.generate_id()
                self.set_status(201)
                self.write({'shortened_url': self.request.host + new_record['_id']})
                self.finish()


app.add_handlers(".*$", [(r'/shorten_url', ShortenURLHandler),
                         (r'/(\w+)', ResolveURLHandler)])
app.settings['db'] = MotorClient('mongodb://localhost:27017')
IOLoop.instance().start()
