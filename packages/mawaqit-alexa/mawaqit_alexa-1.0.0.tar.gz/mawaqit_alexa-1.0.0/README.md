# Stopwatch

A simple stopwatch for measuring code performance.

## Installing

To install the library, you can just run the following command:

```shell
$ python3 -m pip install mawaqit_alexa
```

## Examples

```python
import datetime
import os
from typing import Literal

from examples import ttl_cache_config

from mawaqit_alexa.data_provider.scraping_mawaqit_provider import ScrapingMawaqitProvider
from mawaqit_alexa.data_provider.csv_mawaqit_provider import CsvMawaqitProvider
from mawaqit_alexa.exceptions.missing_param_exception import MissingParamException
from mawaqit_alexa.util.param import Param
from mawaqit_alexa.services.calendar_generator import MawaqitCalendarGenerator

## set directly the url of the mawaqit online link
data_url = 'https://mawaqit.net/fr/grande-mosquee-de-paris'
api_mawaqit_provider = ScrapingMawaqitProvider(data_url)
year_calendar = api_mawaqit_provider.get_current_year_calendar()
mosque_name = api_mawaqit_provider.masjid_endpoint
current_year = datetime.datetime.now().year
language: Literal['ar', 'en'] = 'ar'
output_file = f'./data/out/{mosque_name}_{language}_{Param.ALARM_BEFORE_MINUTES}_{current_year}.ics'
output_file = os.path.join(os.getcwd(), output_file)

# create the calendar
MawaqitCalendarGenerator.create_mawaqit_calendar(
    year_calendar=year_calendar,
    year=current_year,
    output_file=output_file,
    time_zone='Europe/Paris',
    language=language
)

```
