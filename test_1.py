# import apache_beam as beam
# from apache_beam.options.pipeline_options import PipelineOptions

# class MyOptions(PipelineOptions):
#     @classmethod
#     def _add_argparse_args(cls, parser):
#         parser.add_argument('--input_file_loc'.
#                             help='input for pipeline',
#                             default='gcs://nsefno-historical-data/data_2022_unzipped')
#         parser.add_argument('--output',
#                         help='Output for the pipeline',
#                         default='gcs://nsefno-historical-data/ab_test')

#         parser.add_value_provider_argument('--runner',
#                         help='Output for the pipeline',
#                         defaul='localrunner')

# def main():
#     options = PipelineOptions(Options=MyOptions)
#     with beam.pipeline() as pipeline:
#         readable_file = (
#                 pipeline
#                 | fileio.MatchFile('gcs://nsefno-historical-data/data_2022_unzipped')
#                 | fileio.ReadMatches()
#                 | beam.Reshuffle())
#         files_and_contents = (
#                 readable_files
#                 | beam.Map(lambda x: (x.metadata.path, x.read_utf8())


# if __name__ == "__main__":
#     main()


#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""A word-counting workflow."""

# pytype: skip-file

# beam-playground:
#   name: WordCount
#   description: An example that counts words in Shakespeare's works.
#   multifile: false
#   pipeline_options: --output output.txt
#   context_line: 44
#   categories:
#     - Combiners
#     - Options
#     - Quickstart
#   complexity: MEDIUM
#   tags:
#     - options
#     - count
#     - combine
#     - strings

import argparse
import logging
import re

import apache_beam as beam
from apache_beam.io import ReadFromText
from apache_beam.io import WriteToText
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions


class WordExtractingDoFn(beam.DoFn):
  """Parse each line of input text into words."""
  def process(self, element):
    """Returns an iterator over the words of this element.

    The element is a line of text.  If the line is blank, note that, too.

    Args:
      element: the element being processed

    Returns:
      The processed element.
    """
    return re.findall(r'[\w\']+', element, re.UNICODE)


def run(argv=None, save_main_session=True):
    """Main entry point; defines and runs the wordcount pipeline."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input',
        dest='input',
        default='test_input.txt',
        help='Input file to process.')
    parser.add_argument(
        '--output',
        dest='output',
        required=True,
        help='Output file to write results to.')

    parser.add_argument(
      '--runner',
      dest='runner',
      required=True,
      help='Output file to write results to.',
      default='dataflow')
    known_args, pipeline_args = parser.parse_known_args(argv)

    # We use the save_main_session option because one or more DoFn's in this
    # workflow rely on global context (e.g., a module imported at module level).
    options = {
    'project': 'tb-sandbox-338012',
    'region': 'asia-south1',
    'temp_location': 'gs://nsefno-historical-data/temp_loc/',
    'staging_location': 'gs://nsefno-historical-data/staging_loc/',
    'runner': 'DataflowRunner',
    'streaming': False
    }
    pipeline_options = PipelineOptions(pipeline_args, **options)
    pipeline_options.view_as(SetupOptions).save_main_session = save_main_session

    # The pipeline will be run on exiting the with block.
    with beam.Pipeline(options=pipeline_options) as p:

        # Read the text file[pattern] into a PCollection.
        lines = p | 'Read' >> ReadFromText(known_args.input)

        counts = (
            lines
            | 'Split' >> (beam.ParDo(WordExtractingDoFn()).with_output_types(str))
            | 'PairWithOne' >> beam.Map(lambda x: (x, 1))
            | 'GroupAndSum' >> beam.CombinePerKey(sum))

        # Format the counts into a PCollection of strings.
        def format_result(word, count):
            return '%s: %d' % (word, count)

        output = counts | 'Format' >> beam.MapTuple(format_result)

        # Write the output using a "Write" transform that has side effects.
        # pylint: disable=expression-not-assigned
        output | 'Write' >> WriteToText(known_args.output)


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()