# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import sys
from urllib.parse import urlparse

from flask import Flask, request, redirect, jsonify, make_response
from werkzeug.exceptions import BadRequest, NotFound
from flask_pymongo import PyMongo
from pymongo.errors import DuplicateKeyError
import validators

from url_shortener import base62

app = Flask('url_shortener')
app.config['MONGO_URI'] = 'mongodb://localhost:27017'
mongo = PyMongo(app)


@app.before_first_request
def ensure_indexes():
    mongo.db.urls.create_index('last_access',
                               expireAfterSeconds=timedelta(days=365).total_seconds())
    mongo.db.urls.create_index('url')


@app.route('/shorten_url', methods=['POST'])
def shorten_url():
    json_data = request.json
    if json_data is None:
        raise BadRequest

    url = json_data.get('url')
    if not url:
        raise BadRequest('Missing url to shorten')
    else:
        if not urlparse(url).scheme:
            url = 'http://' + url
        if not validators.url(url):
            raise BadRequest('Malformed url')

        existing_record = mongo.db.urls.find_one({'url': url})
        if existing_record:
            return make_response(jsonify({'shortened_url': request.host_url + existing_record['_id']}), 200)
        else:
            new_record = {'_id': base62.generate_id(),
                          'last_access': datetime.utcnow(),
                          'url': url}
            inserted = False
            while not inserted:
                try:
                    mongo.db.urls.insert_one(new_record)
                    inserted = True
                except DuplicateKeyError:
                    new_record['_id'] = base62.generate_id()
            return make_response(jsonify({'shortened_url': request.host_url + new_record['_id']}), 201)


@app.route('/<short_id>', methods=['GET'])
def process_shortened_request(short_id):
    if base62.validate(short_id):
        url_record = mongo.db.urls.find_one({'_id': short_id})
        if url_record:
            mongo.db.urls.update_one({'_id': short_id},
                                     {'$set': {'last_access': datetime.utcnow()}})
            return redirect(url_record['url'])
        else:
            raise NotFound('Shortened url not found')
    else:
        raise BadRequest('Malformed shortened url')


@app.route('/')
def index():
    return 'Hello, World!'
