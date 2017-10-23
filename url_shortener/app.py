#!/usr/bin/python3
#  -*- coding: utf-8 -*-

import argparse

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application

from url_shortener.handlers import *
from url_shortener.redis_wrapper import RedisWrapper


def main():
    parser = argparse.ArgumentParser(description='Run URL shortener')
    parser.add_argument('--redis_host', type=str, default='localhost', help='Redis host')
    parser.add_argument('--redis_port', type=int, default=6379, help='Redis port')
    parser.add_argument('--redis_db', type=int, default=0, help='Redis DB')
    parser.add_argument('--bind_port', type=int, default=80, help='Bind port')
    parser.add_argument('--processes', type=int, default=0, help='Number of processes. (0 - equal to the number of cores)')
    args = parser.parse_args()

    app = Application()

    server = HTTPServer(app)
    server.bind(args.bind_port)
    server.start(args.processes)

    app.settings['redis'] = RedisWrapper(args.redis_host, args.redis_port, args.redis_db)
    app.add_handlers(".*$", [(r'/shorten_url', ShortenURLHandler),
                             (r'/(\w+)', ResolveURLHandler)])

    IOLoop.instance().start()

if __name__ == "__main__":
    main()
