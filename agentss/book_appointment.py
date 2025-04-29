
from agents import function_tool
from langchain_openai import ChatOpenAI
import ast
import requests
from agentss.check_slots import cas
import pytz
from datetime import datetime
import streamlit as st

from dotenv import load_dotenv
import os

load_dotenv()  

llm = ChatOpenAI(
    model_name="gpt-4o",
    temperature=0.0,
)

def match_time_to_slot(input_time_str, slots):
    """
    Match a time string like '2pm' to the corresponding time slot.

    Args:
        slots (list): List of dictionaries with 'start' and 'end' keys
        input_time_str (str): Time string (e.g., '2pm', '14:00')

    Returns:
        dict: The matching slot or None if not found
    """
    # Convert input time to 24-hour format
    prompt = f""" Given the time, match it to the appropriate ISO 8601 time format,
    only return the appropriate element from the list of slots. If the given time is
    not the exact time from any of the given slots then return 'Invalid time'

    Sample reponse is: '{{'start': '2025-04-03T14:00:00+08:00', 'end': '2025-04-03T15:00:00+08:00'}}'

    time: {input_time_str}
    slots: {slots}


    """
    out = llm.invoke(prompt)

    return out.content


@function_tool
def book_appointment(name: str, phone_number: str, email: str, service:str, date: str, time: str):
    '''This is responsible to book an appointment using:
    name - name of the user
    phone_number - phone number of the user
    email - email of the user
    service - What kind of service or procedure that the user wants
    date - date of the appointment
    time - time of the appointment
    '''

    missing_params = []

    if not name:
        missing_params.append("name")
    if not phone_number:
        missing_params.append("phone number")
    if not email:
        missing_params.append("email")
    if not service:
        missing_params.append("service")
    if not date:
        missing_params.append("date")
    if not time:
        missing_params.append("time")

    # This extracts the start_time & end_time from time parameter that is needed to pass to make
    start_end_time = match_time_to_slot(time, cas(date))
    # Correct the data type format which is the dictionary
    start_end_time = ast.literal_eval(start_end_time)

    start_time = start_end_time['start']
    end_time = start_end_time['end']


    # Process through make
    webhook_url = 'https://hook.eu2.make.com/xo5cn6j9asp7b3xkgh5ohonybiwoq341'

    data = {
        "records": [{
            "fields": {
                "full_name":name,
                "start_time":start_time,
                "end_time":end_time,
                "service":service,
                "email_address":email
            }
        }]
    }
    response_create_appointment = requests.get(url=webhook_url, json=data)

    if response_create_appointment.status_code == 200:

        air_api_key = st.secrets['AIRTABLE_API_KEY']
        # air_api_key = os.getenv('AIRTABLE_API_KEY')

        # Add to airtable 'booked appointments'
        url = "https://api.airtable.com/v0/appeCc2gb9GAQHKhz/Booked%20Appointments"
        headers = {
            "Authorization": air_api_key,  # NOTE: When adding your Airtable API key in secrets it must include "Bearer YOURKEY", keeping the Bearer and the space. If you don't add this then it won't work!
            "Content-Type": "application/json"
        }

        # platform = request.args.get('platform', 'Not Specified')

        # Define the timezone for the Philippines
        manila_tz = pytz.timezone('Asia/Manila')

        # Get current datetime in Manila timezone and format it
        current_datetime_manila = datetime.now(manila_tz).strftime(
            "%m/%d/%Y %I:%M %p").lower()

        data = {
            "records": [{
                "fields": {
                    "Name": name,
                    "Phone": phone_number,
                    "Email Address": email,
                    "Appointment Start": start_time,
                    "Appointment End": end_time,
                    "Date Created": current_datetime_manila, 
                    "Service": service,
                    "Platform": 'Website',
                    "Status": "Todo"
                }
            }]
        }
        response_book_appointment = requests.post(url, headers=headers, json=data)
        if response_book_appointment.status_code == 200:
            api_response = {'success': True, 'message': 'Successfully booked the appointment 🚀'}
            return api_response["message"]
    else:
        return f"Missing required parameters: {', '.join(missing_params)}"