
from datetime import datetime, timedelta
from agents import function_tool
import requests
from dotenv import load_dotenv
import os
import streamlit as st

load_dotenv()  


def convert_date(natural_language_date):
    # List of possible date formats
    date_formats = ['%b %d', '%B %d', '%b. %d', '%B. %d']

    for date_format in date_formats:
        try:
            # Try parsing the date with the current format
            parsed_date = datetime.strptime(natural_language_date, date_format)
            # Replace the year with 2023
            fixed_date = parsed_date.replace(year=2025)
            # Format the date to "YYYY-MM-DD"
            formatted_date = fixed_date.strftime('%Y-%m-%d')
            return formatted_date
        except ValueError:
            # If parsing fails, try the next format
            continue

    # If all formats fail, return an error message or handle it as needed
    return "Invalid date format. Please pick another date"


def has_date_passed(given_date_str):
    # Parse the given date string into a datetime object
    given_date = datetime.strptime(given_date_str, '%Y-%m-%d')

    # Get the current date (without time)
    current_date = datetime.now().date()

    # Check if the given date is before the current date
    if given_date.date() > current_date:
        return given_date_str
    elif given_date.date() == current_date:
        return 'We cannot cater same day schedule. Please pick another date'
    return 'The date has already passed. Please pick another date.'


def is_weekend(date_str):
    # Parse the date string into a datetime object
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')

    # Check if the day is a weekend (5 for Saturday, 6 for Sunday)
    if date_obj.weekday() < 5:
        return date_str
    return 'Sorry, we are only available at weekdays. Please pick another date'


def create_hourly_intervals(date_str):
    # Parse the input date string into a datetime object
    date = datetime.strptime(date_str, '%Y-%m-%d')

    # Create a list to hold all the intervals
    intervals = []

    # Iterate from 0 (12 AM) to 12 (12 PM)
    for hour in range(24):
        # Start time of the interval
        start_time = datetime(date.year, date.month, date.day, hour, 0)
        # End time of the interval (1 hour later)
        end_time = start_time + timedelta(hours=1)

        # Format the times into the required string format with timezone
        interval = {
            'start': start_time.strftime('%Y-%m-%dT%H:%M:%S+08:00'),
            'end': end_time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
        }

        intervals.append(interval)

    return intervals


def get_iso_min_max_dates(date_str):
    # Parse the input date string into a datetime object
    specified_date = datetime.strptime(date_str, '%Y-%m-%d')

    # Get the next date by adding one day
    next_date = specified_date + timedelta(days=1)

    # Format both dates to the desired string format with midnight time
    specified_date_str = specified_date.strftime('%Y-%m-%dT00:00:00.000Z')
    next_date_str = next_date.strftime('%Y-%m-%dT00:00:00.000Z')

    return specified_date_str, next_date_str


def get_busy_times(min_date, max_date, calendar_id):
    GOOGLE_CALENDAR_API_KEY = st.secrets['GOOGLE_CALENDAR_API_KEY']
    # GOOGLE_CALENDAR_API_KEY = os.getenv('GOOGLE_CALENDAR_API_KEY')

    url = f'https://www.googleapis.com/calendar/v3/freeBusy?key={GOOGLE_CALENDAR_API_KEY}'

    headers = {
        "Content-Type": "application/json"
    }

    data = {
            "timeMin": min_date,
            "timeMax": max_date,
            "timeZone": "GMT+8",
            "items": [
                {
                "id": calendar_id
                }
            ]
            }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        # print("Lead created successfully.")
        return response.json()
    else:
        return 'Error'


def parse_isoformat(time_str):
    return datetime.fromisoformat(time_str)

def subtract_intervals(first_list, second_list):
    # Convert start and end times to datetime objects for easier comparison
    first_list = [{k: parse_isoformat(v) for k, v in interval.items()} for interval in first_list]
    second_list = [{k: parse_isoformat(v) for k, v in interval.items()} for interval in second_list]

    # Function to check if two intervals overlap
    def intervals_overlap(first, second):
        return first['start'] < second['end'] and second['start'] < first['end']

    # Subtract the intervals
    result = []
    for interval1 in first_list:
        overlap = False
        for interval2 in second_list:
            if intervals_overlap(interval1, interval2):
                overlap = True
                break
        if not overlap:
            result.append(interval1)

    # Convert back to original format if necessary
    result = [{k: v.isoformat() for k, v in interval.items()} for interval in result]

    if len(result) >= 1:
        return result
    return "I'm sorry, there doesn't seem to be availability on that date. It is fully booked. Please pick another date"


def cas(appointment_date):
    """Use this tool to check the available slots in the calendar."""

    # print("> check slots")
    try:
        t1 = convert_date(appointment_date)

        t2 = has_date_passed(t1)

        t3 = is_weekend(t2)

        t4 = create_hourly_intervals(t3)[9:-6]

        specified_date_str, next_date_str = get_iso_min_max_dates(t3)

        t5 = get_busy_times(specified_date_str, next_date_str, calendar_id="tanstephenjireh@gmail.com")
        t6 = t5['calendars'][list(t5['calendars'].keys())[0]]['busy']

        available_slots = subtract_intervals(t4, t6)

        return available_slots

    except ValueError as e:
        d1 = str(e).split('time data ')
        d2 = d1[1].split(' does not match format \'%Y-%m-%d')[0]
        return {
        "error": d2
    }


@function_tool
def check_available_slots(appointment_date: str):
    """Use this tool to check the available slots in the calendar using the appointment date."""

    # print("> check slots")
    try:
        t1 = convert_date(appointment_date)
        print(t1)
        t2 = has_date_passed(t1)

        t3 = is_weekend(t2)

        t4 = create_hourly_intervals(t3)[9:-6]

        specified_date_str, next_date_str = get_iso_min_max_dates(t3)

        t5 = get_busy_times(specified_date_str, next_date_str, calendar_id="tanstephenjireh@gmail.com")
        t6 = t5['calendars'][list(t5['calendars'].keys())[0]]['busy']

        available_slots = subtract_intervals(t4, t6)

        formatted_slots = []

        for slot in available_slots:
            # Parse the ISO format timestamps
            start_time = datetime.fromisoformat(slot['start'].replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(slot['end'].replace('Z', '+00:00'))

            # # Format the times as 12-hour AM/PM format
            # start_str = start_time.strftime("%-I%p").lower()
            # end_str = end_time.strftime("%-I%p").lower()

            # # Remove the leading zero if any and capitalize AM/PM
            # start_str = start_str.replace('am', 'AM').replace('pm', 'PM')
            # end_str = end_str.replace('am', 'AM').replace('pm', 'PM')


            start_str = start_time.strftime("%I%p").lstrip("0").replace('am', 'AM').replace('pm', 'PM')
            end_str = end_time.strftime("%I%p").lstrip("0").replace('am', 'AM').replace('pm', 'PM')


            formatted_slots.append(f"⏰ {start_str} to {end_str}")
        # Build the complete message
        result = f"Available time slots for {appointment_date}:\n\n"
        result += "\n".join(formatted_slots)

        return result

    except ValueError as e:
        d1 = str(e).split('time data ')
        d2 = d1[1].split(' does not match format \'%Y-%m-%d')[0]
        return {
        "error": d2
    }