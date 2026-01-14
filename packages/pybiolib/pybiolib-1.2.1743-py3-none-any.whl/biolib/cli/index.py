import json
import logging
import sys

import click

from biolib._index.index import Index
from biolib.biolib_errors import BioLibError
from biolib.biolib_logging import logger, logger_no_user_data


@click.group(help='Manage Indexes')
def index() -> None:
    logger.configure(default_log_level=logging.INFO)
    logger_no_user_data.configure(default_log_level=logging.INFO)


@index.command(help='Create an Index')
@click.argument('uri', required=True)
@click.option('--config-path', required=True, type=click.Path(exists=True), help='Path to JSON config file')
def create(uri: str, config_path: str) -> None:
    try:
        Index.create_from_config_file(uri=uri, config_path=config_path)
    except json.JSONDecodeError as error:
        print(f'Error: Invalid JSON in config file: {error}', file=sys.stderr)
        sys.exit(1)
    except BioLibError as error:
        print(f'Error creating index: {error.message}', file=sys.stderr)
        sys.exit(1)
    except Exception as error:
        print(f'Error reading config file: {error}', file=sys.stderr)
        sys.exit(1)
