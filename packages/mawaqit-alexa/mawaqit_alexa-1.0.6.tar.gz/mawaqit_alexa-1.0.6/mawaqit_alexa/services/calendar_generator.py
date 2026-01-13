import datetime
import os
from typing import Literal, Optional, Set

from icalendar import Calendar, Event, Alarm

from mawaqit_alexa.models.types import MawaqitYearCalendar, PrayerType
from mawaqit_alexa.util.util import Util


class MawaqitCalendarGenerator:
    EN_PRAYER_NAMES = ['fajr', 'shuruk', 'dhuhr', 'asr', 'maghrib', 'isha']
    AR_PRAYER_NAMES = ['صلاة الفجر', 'الشروق', 'صلاة الظهر', 'صلاة العصر', 'صلاة المغرب', 'صلاة العشاء']
    FR_PRAYER_NAMES = ['Fajr', 'Shuruk', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']

    @staticmethod
    def get_single_prayer_event(en_prayer_name: str,
                                desired_notification_prayer_name: str,
                                year: int,
                                month: int,
                                day: int,
                                time: str,
                                time_zone="Europe/Paris",
                                suffix_id="",
                                trigger_before_min=0,
                                event_summary="",
                                summary_prefix=""
                                ):
        prayer_datetime = datetime.datetime(
            year,
            month,
            day,
            int(time.split(':')[0]),
            int(time.split(':')[1])
        )
        # create event for the prayer
        event = Event()
        # join summary prefix and prayer name with a space if summary prefix is not empty
        event_summary = event_summary if event_summary else desired_notification_prayer_name
        event_summary = f'{summary_prefix} {event_summary}' if summary_prefix else event_summary
        event.add('summary', event_summary)
        event.add('dtstart', prayer_datetime)
        event.add('dtend', prayer_datetime)
        # set timezone to Europe/Paris
        event.add('tzid', time_zone)
        # Unique identifier for the event
        event['uid'] = f'{en_prayer_name}-{year}-{month}-{day}-{suffix_id}'

        # Create an alarm x minutes before the event
        # even if trigger time is zero has effect at the time of the event
        alarm = Alarm()
        alarm.add('action', 'DISPLAY')
        alarm.add('description', f'{en_prayer_name} prayer time before {trigger_before_min} minutes')
        alarm.add('trigger', datetime.timedelta(minutes=-trigger_before_min))
        event.add_component(alarm)
        return event

    @staticmethod
    def save_calendar_to_file(cal: Calendar, filename: str):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'wb') as f:
            f.write(cal.to_ical())
        print(f'Calendar saved to {filename}')

    @staticmethod
    def create_mawaqit_calendar(year_calendar: MawaqitYearCalendar,
                                year: int,
                                output_file: str,
                                time_zone: str = 'Europe/Paris',
                                language: Literal['en', 'ar', 'fr'] = 'en',
                                alarm_before_minutes: int = 15,
                                summary_prefix: str = '',
                                months_filter: Optional[Set[int]] = None,
                                prayers_filter: Optional[Set[PrayerType]] = None
                                ) -> Calendar:
        # Create a new iCal calendar
        cal = Calendar()
        for month_idx, month in enumerate(year_calendar):
            month_number = month_idx + 1
            # Filter by months if specified
            if months_filter is not None and month_number not in months_filter:
                continue
            for day, prayer_times in month.items():
                # skip leap days
                day = int(day)
                if day == 29 and month_number == 2 and not Util.is_leap_year(year):
                    continue
                for prayer_nb, prayer_time in enumerate(prayer_times):
                    en_prayer_name = MawaqitCalendarGenerator.EN_PRAYER_NAMES[prayer_nb].capitalize()
                    # Filter by prayers if specified
                    if prayers_filter is not None and PrayerType(en_prayer_name.lower()) not in prayers_filter:
                        continue
                    ar_prayer_name = MawaqitCalendarGenerator.AR_PRAYER_NAMES[prayer_nb]
                    fr_prayer_name = MawaqitCalendarGenerator.FR_PRAYER_NAMES[prayer_nb]

                    if language.lower() == 'ar':
                        desired_prayer_name = ar_prayer_name
                    elif language.lower() == 'fr':
                        desired_prayer_name = fr_prayer_name
                    else:
                        desired_prayer_name = en_prayer_name

                    event_params = {
                        'en_prayer_name': en_prayer_name,
                        'desired_notification_prayer_name': desired_prayer_name,
                        'year': year,
                        'month': month_number,
                        'day': day,
                        'time': prayer_time,
                        'time_zone': time_zone,
                        'event_summary': '',
                        'summary_prefix': summary_prefix
                    }
                    if alarm_before_minutes > 0:
                        event_before_time = MawaqitCalendarGenerator.get_single_prayer_event(**event_params,
                                                                                             suffix_id='before',
                                                                                             trigger_before_min=alarm_before_minutes)
                        cal.add_component(event_before_time)

                    event_at_time = MawaqitCalendarGenerator.get_single_prayer_event(**event_params,
                                                                                     suffix_id='at',
                                                                                     trigger_before_min=0)
                    cal.add_component(event_at_time)

        MawaqitCalendarGenerator.save_calendar_to_file(cal, output_file)
        return cal
