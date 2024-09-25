import datetime
import json
import logging
import time
import urllib.request
import urllib.error
from typing import Callable, Any

from google.cloud import storage

import conf

def load_data(url: str, filename: str, parser: Callable[[dict[str, Any], str], None], force_download: bool = False, use_dummy_data: bool = False, ) -> None:
    ''' Loads data from API, filename in GCS or local file system.

       Args:
          url:             URL to API with api_key and paramters.
          filename:        A filename in GCS and the 'data' directory.
          force_download:  Force to download from the API.
          use_dummy_data:  True to use dummy data file.
    '''

    # first, we try the saved data in GCS or file if it has today's timestamp
    data_saved: dict|None = load_backup_data(filename)

    if data_saved and not force_download:
        timestamp: float = data_saved.get('timestamp', 0)
        timestamp_date: datetime.date = datetime.datetime.utcfromtimestamp(timestamp).date()
        if datetime.datetime.utcnow().date() == timestamp_date:  # today?
            parser(data_saved, 'backup file')
            return

    # not today's data. let's download data from the API.
    # a big thank you to all contributors to the data!
    try:
        with urllib.request.urlopen(url) as return_data:
            data_fetched = json.loads(return_data.read())
            assert data_fetched

            data_fetched['timestamp'] = time.time()
            store_backup_data(data_fetched, filename)             # save it with timestamp for the next time
            parser(data_fetched, 'API')                           # parse and store it

    except urllib.error.URLError as ex:
        # network error! we use the backup file.
        if data_saved:
            logging.warn(f'Failed to fetch data from {url}, falling down to the backup data')
            parser(data_saved, 'backup file')
        else:
            logging.error(f'Failed to fetch data from {url} and {filename}, give up: {str(ex)}.')


def store_backup_data(data: dict[str, Any], filename: str) -> None:
    """ Backup data to GCS or the local file.

    Args:
       data:          A dict data to be saved.
        filename:     A filename of the backup in GCS or the local file system.
    """

    if conf.GCS_BUCKET:
        storage.Client().bucket(conf.GCS_BUCKET).blob(filename).upload_from_string(json.dumps(data))
    else:
        with open('data/' + filename, 'w', newline='', encoding="utf_8_sig") as data_file:
            data_file.write(json.dumps(data))


def load_backup_data(filename: str) -> dict[str, Any] | None:
    """ Downloads data file from GCS or the file.

    Args:
        filename:     A filename of the backup in GCS or the local file system.
    Returns: The backed up data or None.

    """

    if conf.GCS_BUCKET:
        try:
            return json.loads(storage.Client().bucket(conf.GCS_BUCKET).blob(filename).download_as_string())
        except Exception as ex:
            logging.warn(f'Failed to download {filename} from GCS bucket {conf.GCS_BUCKET}: {str(ex)} ')

    try:
        with open('data/' + filename, newline='', encoding="utf_8_sig") as data_file:
            return json.load(data_file)
    except Exception as ex:
        logging.error(f'Failed to open saved data from data/{filename}: {str(ex)}')

    return None
