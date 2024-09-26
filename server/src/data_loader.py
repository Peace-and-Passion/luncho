'''
  Luncho data loader

  @author HIRANO Satoshi
  @since  2024/09/25

'''
import datetime
import logging
import os
import time
import urllib.request
import urllib.error
from typing import Callable, Any

import json5
from google.cloud import storage

import conf

def load_data(url: str, filename: str, processor: Callable[[dict[str, Any]|None, str], bool], force_download: bool = False, use_test_data: bool = False, ) -> None:
    ''' Loads data from the backup file or using API.

        If we have today's backup file in GCS or in the data/ directory, we use it. If not, we load data using the API.

       Args:
          url:             URL to API with api_key and parameters.
          filename:        A backup filename in GCS and the 'data' directory.
          processor:       Data processor function. It will be passed data and a string representing its source,
                           such like processor(data, 'backup'). Valid source is 'API' for API, 'backup' for the backup file,
                           and 'fail' for failure.
                           If data is not availabe, None is passed and source is 'fail'.
                           If the processor function returns False, this falls back to the next data source.
          force_download:  Force to download using the API.
          use_test_data:  True to use dummy data file.
    '''
    data_fetched: dict[str, Any]|None
    data_backup: dict|None = load_backup_data(filename)  # load even if force_download is True for fetch failure

    # first, we try the backup data if with today's timestamp
    if data_backup and not force_download:
        timestamp: float = data_backup.get('timestamp', 0)
        timestamp_date: datetime.date = datetime.datetime.utcfromtimestamp(timestamp).date()
        # use backup data if with today's timestamp
        if datetime.datetime.utcnow().date() == timestamp_date:
            if processor(data_backup, 'backup'):
                return

    # we don't have today's data. let's download data using the API.
    # a big thank you to all contributors to the data!
    try:
        with urllib.request.urlopen(url) as return_data:
            data_fetched = json5.loads(return_data.read())
            assert data_fetched

            data_fetched['timestamp'] = time.time()
            store_backup_data(data_fetched, filename)             # save it with timestamp for the next time
            if processor(data_fetched, 'API'):                           # parse and store it
                return
    except urllib.error.URLError as ex:
        logging.warn(f'Falling down to the backup data due to failure in fetching data from {url} with error {str(ex)}. ')
        pass

    # network error! we use the backup file.
    if data_backup and processor(data_backup, 'backup'):
        return

    logging.error(f'Failed to load data.')
    processor(None, 'fail')

def store_backup_data(data: dict[str, Any], filename: str) -> None:
    """ Backup data to GCS or the local file.

    Args:
       data:          A dict data to be saved.
        filename:     A filename of the backup in GCS or the local file system.
    """

    if conf.GCS_BUCKET:
        storage.Client().bucket(conf.GCS_BUCKET).blob(filename).upload_from_string(json5.dumps(data))
    else:
        with open(os.path.join(conf.Top_Dir, filename), 'w', newline='', encoding="utf_8_sig") as data_file:
            data_file.write(json5.dumps(data))


def load_backup_data(filename: str) -> dict[str, Any] | None:
    """ Downloads data file from GCS or the file.

    Args:
        filename:     A filename of the backup in GCS or the local file system.
    Returns: The backed up data or None.

    """

    if conf.GCS_BUCKET:
        try:
            return json5.loads(storage.Client().bucket(conf.GCS_BUCKET).blob(filename).download_as_string())
        except Exception as ex:
            logging.warn(f'Failed to download {filename} from GCS bucket {conf.GCS_BUCKET}: {str(ex)} ')

    try:
        with open(os.path.join(conf.Top_Dir, filename), newline='', encoding="utf_8_sig") as data_file:
            return json5.load(data_file)
    except Exception as ex:
        logging.error(f'Failed to open saved data from data/{filename}: {str(ex)}')

    return None
