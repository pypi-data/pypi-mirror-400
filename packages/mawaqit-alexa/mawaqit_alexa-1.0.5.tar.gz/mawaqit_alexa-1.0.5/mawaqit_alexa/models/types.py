MawaqitDayCalendar = list[str]  # 6 elements fajr, sunrise, dhuhr, asr, maghrib, isha

MawaqitMonthCalendar = dict[str, MawaqitDayCalendar]  # maximum 31 elements: map day 'dd' to MawaqitDayCalendar

MawaqitYearCalendar = list[MawaqitMonthCalendar]  # 12 elements for each month

