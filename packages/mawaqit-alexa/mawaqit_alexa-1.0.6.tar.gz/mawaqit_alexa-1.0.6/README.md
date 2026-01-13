# Mawaqit Alexa

A Python library to scrape prayer times from [Mawaqit](https://mawaqit.net) and generate iCalendar (.ics) files for integration with calendar apps and Alexa.

## Features

- Scrape prayer times from any mosque on Mawaqit
- Generate iCalendar (.ics) files with prayer time events
- Support for both Arabic and English prayer names
- Configurable alarm notifications before prayer times
- CSV data provider for offline/exported data
- TTL-based caching to avoid excessive requests

## Installing

To install the library, you can run the following command:

```shell
pip install mawaqit_alexa
```

## Usage

### Basic Example

```python
import datetime
import os
from typing import Literal

from mawaqit_alexa.data_provider.scraping_mawaqit_provider import ScrapingMawaqitProvider
from mawaqit_alexa.services.calendar_generator import MawaqitCalendarGenerator

# Configure parameters
alarm_before_minutes = 15  # Alarm 15 minutes before prayer
summary_prefix = ''  # Optional prefix for event summary

# Set the mawaqit mosque URL
data_url = 'https://mawaqit.net/fr/grande-mosquee-de-paris'

# Fetch prayer times
api_mawaqit_provider = ScrapingMawaqitProvider(data_url)
year_calendar = api_mawaqit_provider.get_current_year_calendar()
mosque_name = api_mawaqit_provider.masjid_endpoint
current_year = datetime.datetime.now().year

# Choose language: 'ar' for Arabic, 'en' for English
language: Literal['ar', 'en'] = 'ar'

# Set output file path
output_file = f'./data/out/{mosque_name}_{language}_{alarm_before_minutes}_{current_year}.ics'
output_file = os.path.join(os.getcwd(), output_file)

# Create the calendar
MawaqitCalendarGenerator.create_mawaqit_calendar(
    year_calendar=year_calendar,
    year=current_year,
    output_file=output_file,
    time_zone='Europe/Paris',
    language=language,
    alarm_before_minutes=alarm_before_minutes,
    summary_prefix=summary_prefix
)
```

### Using CSV Data Provider

If you have exported prayer times data from Mawaqit, you can use the CSV provider:

```python
from mawaqit_alexa.data_provider.csv_mawaqit_provider import CsvMawaqitProvider

data_folder = './data/Nantes'
csv_provider = CsvMawaqitProvider(data_folder)
year_calendar = csv_provider.get_current_year_calendar()
```

## Configuration

The `create_mawaqit_calendar` function accepts the following parameters:

- `year_calendar`: The prayer times calendar data
- `year`: The calendar year
- `output_file`: Path to save the generated .ics file
- `time_zone`: Timezone for the calendar events (default: 'Europe/Paris')
- `language`: Language for prayer names - 'en', 'ar', or 'fr' (default: 'en')
- `alarm_before_minutes`: Minutes before prayer time to trigger an alarm (default: 15)
- `summary_prefix`: Prefix to add to calendar event summaries (default: '')

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Author

Ahmad SAID - [GitHub](https://github.com/Ahmad-Said)

