#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import argparse
import logging


import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions

# Parameters for beam pipeline options
PROJECT = "mlongcp"
region = "us-central1"
job_name = "pubsub-to-bigquery"
subnet = "test-vpc"
dataflow_gcs_bucket = "dataflow_beam_pipeline"


class SplitText():
    """Parse each line of input text into words."""

    def decodeToDict(self, element):
        text_line = element.strip()
        values = text_line.split("|")
        row = dict(zip(("userid", "latitude", "longitude", "event_time", "recommendations"), values))
        return row


def run(argv=None):
    """Build and run the pipeline."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_topic')
    parser.add_argument('--input_subscription')
    parser.add_argument('--output_table')

    argv = [
        '--project={0}'.format(PROJECT),
        '--job_name={}'.format(job_name),
        '--save_main_session',
        '--staging_location=gs://{0}/staging/'.format(dataflow_gcs_bucket),
        '--temp_location=gs://{0}/tmp/'.format(dataflow_gcs_bucket),
        '--input_topic=projects/mlongcp/topics/userinfo',
        '--output_table=mlongcp:staging.pubsub_to_gbq',
        '--streaming',
        '--runner=DirectRunner',
        '--subnetwork=regions/{0}/subnetworks/{1}'.format(region, subnet),
        '--no_use_public_ips',
        '--experiment=ignore_py3_minor_version',
        '--experiments=allow_non_updatable_job'
    ]

    known_args, pipeline_args = parser.parse_known_args(argv)
    pipeline_options = PipelineOptions(pipeline_args)

    with beam.Pipeline(options=pipeline_options) as p:

        split_text = SplitText()

        # Read from PubSub into a PCollection.
        if known_args.input_subscription:
            messages = (p
                        | beam.io.ReadFromPubSub(
                            subscription=known_args.input_subscription)
                        .with_output_types(bytes))
        else:
            messages = (p
                        | beam.io.ReadFromPubSub(topic=known_args.input_topic)
                        .with_output_types(bytes)
                        )

       # Implement transformation on text based on your data
        lines = (messages | 'Decode&Split' >> beam.Map(lambda x: split_text.decodeToDict(x)))

        #lines | beam.io.WriteToText("/home/mlongcp/video-streaming-app/test.txt")


        # Write data into BQ sink
        lines | "WritetoBQ" >> beam.io.WriteToBigQuery(
            known_args.output_table,
            schema='userid:STRING, latitude:STRING, longitude:STRING, event_time:TIMESTAMP, recommendations:STRING',
            create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
            write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND)


if __name__ == '__main__':
    #logging.getLogger().setLevel(logging.INFO)
    run()
