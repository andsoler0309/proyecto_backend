from flask import request
from functools import wraps
import datetime


def monitor_registration_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Call the wrapped function
        message, status_code = func(*args, **kwargs)

        if status_code in [200, 201, 204]:
            return message, status_code

        # Log errors if the response code is not 200
        # get the message of the response
        try:
            error_response = message.get("error", "")
            if message["error"] == "Respuesta vacia del register API":
                error_response = "Respuesta vacia del register API"

            print(f"{datetime.datetime.now()} - Error: {error_response} - status code {status_code}\n")

            # with open("error.log", "a") as f:
            #     f.write(f"{datetime.datetime.now()} - Error: {error_response}\n")
        except Exception as e:
            print(f"{datetime.datetime.now()} - Error on call - status code {status_code} - {e}\n")
            # with open("error.log", "a") as f:
            #     f.write(
            #         f"{datetime.datetime.now()} - Error:  - Could not decode json \n"
            #     )

        return message, status_code

    return wrapper
