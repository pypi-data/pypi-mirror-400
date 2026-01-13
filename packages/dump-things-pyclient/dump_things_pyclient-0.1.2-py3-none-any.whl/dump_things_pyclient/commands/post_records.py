from __future__ import annotations

import argparse
import json
import os
import sys

from ..communicate import (
    collection_write_record,
    curated_write_record,
)


def main():
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('base_url')
    argument_parser.add_argument('collection')
    argument_parser.add_argument('cls', metavar='class')
    argument_parser.add_argument('--curated', action='store_true', help='bypass inbox, requires curator token')

    arguments = argument_parser.parse_args()

    token = os.environ.get('DUMPTHINGS_TOKEN')
    if token is None:
        print(
            'WARNING: environment variable DUMPTHINGS_TOKEN not set',
            file=sys.stderr,
            flush=True,
        )

    if arguments.curated:
        write_record = curated_write_record
    else:
        write_record = collection_write_record

    posted = False
    for line in sys.stdin:
        record = json.loads(line)
        try:
            write_record(
                service_url=arguments.base_url,
                collection=arguments.collection,
                class_name=arguments.cls,
                record=record,
                token=token,
            )
        except Exception as e:
            print(f'Error: {e}', file=sys.stderr, flush=True)
        else:
            posted = True
            print('.', end='', flush=True)

    if posted:
        # final newline
        print('')


if __name__ == '__main__':
    sys.exit(main())
