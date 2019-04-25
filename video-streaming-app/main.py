#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from flask import Flask, request, render_template, jsonify
from google.cloud import pubsub

import argparse
import numpy as np
import random

from datetime import datetime

#from recommendations import Recommendations
#rec_util = Recommendations()

DEFAULT_RECS = 3

TOPIC = 'userinfo'
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

app = Flask(__name__)

@app.route('/')
def stream_video():
    if request.method == 'GET':
        return render_template('index.html')


@app.route('/location', methods=['POST'])
def getUserLocation():
    curr_time = datetime.utcnow().strftime(TIME_FORMAT)

    if request.method == 'POST':
        lat = request.form['lat']
        lon = request.form['lon']

        # get recommendations
        #rec_list = rec_util.get_recommendations(500, num_recs)
        rec_list = random.sample([124,433, 8932,5323,312,5959,323,3,5,3],3)

        json_response = jsonify({'articles': [str(i) for i in rec_list]})

        # Publish data into pubsub stream for analytics
        #data = str(user_id) + "|" + str(lat) + "|" + str(lon) + "|" + curr_time + "|" + str(rec_list)
        #publisher.publish(event_type, data=data.encode('utf-8'))

        print('Success')

        return json_response, 200


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Send user info to Pub/Sub')
    parser.add_argument('--project', required=True)
    args = parser.parse_args()

    # create Pub/Sub notification topic
    publisher = pubsub.PublisherClient()
    event_type = publisher.topic_path(args.project, TOPIC)
    """
    try:
        publisher.get_topic(event_type)
        logging.info('Reusing pub/sub topic {}'.format(TOPIC))
    except:
        publisher.create_topic(event_type)
        logging.info('Creating pub/sub topic {}'.format(TOPIC))
    """
    app.run(host='127.0.0.1', port=8086, debug=True)
