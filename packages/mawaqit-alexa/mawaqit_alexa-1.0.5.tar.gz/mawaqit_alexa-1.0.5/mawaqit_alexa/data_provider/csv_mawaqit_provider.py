import csv

from mawaqit_alexa.data_provider.mawaqit_provider import MawaqitProvider
from mawaqit_alexa.models.types import MawaqitYearCalendar


class CsvMawaqitProvider(MawaqitProvider):

    def __init__(self, all_csv_source_folder: str):
        super().__init__()
        self.all_csv_source_folder = all_csv_source_folder
        self.year_calendar: MawaqitYearCalendar = []
        self._parse_csv()

    def _parse_csv(self):
        # List all files in the current directory
        # files = os.listdir(current_directory)
        # files are from 01.csv to 12.csv
        i = 1
        files = []
        while i <= 12:
            # print digit with leading zero
            files.append(f'{i:02}.csv')
            i += 1
        # Iterate over each file in the directory
        self.year_calendar = []
        for file in files:
            # Check if the file is a CSV
            if not file.endswith('.csv'):
                continue
            current_month = int(file[:2])
            # Append a new dictionary to the year_calendar list
            i = current_month - 1
            self.year_calendar.append({})
            # Open the CSV file
            with open(f"{self.all_csv_source_folder}/{file}", 'r') as csv_file:
                # Create a CSV reader object
                csv_reader = csv.reader(csv_file)

                # Skip the first line
                next(csv_reader)

                # Read and append the remaining lines to the combined_data list
                for row in csv_reader:
                    # Day,Fajr,Shuruk,Duhr,Asr,Maghrib,Isha
                    # 1,07:34,08:54,13:15,15:09,17:30,18:46
                    day = row[0]
                    fajr = row[1]
                    shuruk = row[2]
                    duhr = row[3]
                    asr = row[4]
                    maghrib = row[5]
                    isha = row[6]
                    self.year_calendar[i][day] = [fajr, shuruk, duhr, asr, maghrib, isha]

    def get_current_year_calendar(self) -> MawaqitYearCalendar:
        return self.year_calendar
