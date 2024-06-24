import os
from flask import Flask, jsonify, request
import requests
from collections import deque
import time
import hashlib
import logging


app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)

# Global variables
window_size = 10
number_window = deque(maxlen=window_size)
qualifiers = {
    "p": "primes",
    "f": "fibo",
    "e": "even",
    "r": "rand"
}
test_server_url = "http://20.244.56.144/test/{}"

access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiZXhwIjoxNzE5MjEzOTUwLCJpYXQiOjE3MTkyMTM2NTAsImlzcyI6IkFmZm9yZG1lZCIsImp0aSI6ImIyNGViNGI4LTlmN2MtNGU3Ny05NDkzLThhYzFmMmEwZWNkMyIsInN1YiI6ImtyaXNobmF0ZWphc2lydmlzZXR0aUBnbWFpbC5jb20ifSwiY29tcGFueU5hbWUiOiJhZmZvcmRtZWQiLCJjbGllbnRJRCI6ImIyNGViNGI4LTlmN2MtNGU3Ny05NDkzLThhYzFmMmEwZWNkMyIsImNsaWVudFNlY3JldCI6IlBvQXBWa0NQa1l1cUdQb0UiLCJvd25lck5hbWUiOiJTaXJ2aXNldHRpIEtyaXNobmEgVGVqYSIsIm93bmVyRW1haWwiOiJrcmlzaG5hdGVqYXNpcnZpc2V0dGlAZ21haWwuY29tIiwicm9sbE5vIjoiMjFLTjFBNDQ1NiJ9.wqIcuqmpouSCBMXb6Jl-mUbZaeA9I9LAY7xqf1616Zk"


ecommerce_companies = ["AMZ", "FLE", "SHB", "I", "AZO"]
categories = ["Phone", "Computer", "Pendrive", "Remote", "Speaker", "House", "Keypad", "Bluetooth"]

@app.route('/numbers/<qualifier>', methods=['GET'])
def get_numbers(qualifier):
    app.logger.debug(f"Received request for qualifier: {qualifier}")
    if qualifier not in qualifiers:
        app.logger.error(f"Invalid qualifier: {qualifier}")
        return jsonify({"error": "Invalid qualifier"}), 400
    
    endpoint = qualifiers[qualifier]
    url = test_server_url.format(endpoint)
    headers = {"Authorization": f"Bearer {access_token}"}
    print(headers)
    
    try:
        start_time = time.time()
        response = requests.get(url, headers=headers, timeout=0.5)
        
        response_time = time.time() - start_time
        
        app.logger.debug(f"Request to {url} took {response_time} seconds and returned status code {response.status_code}")
        
        if response.status_code != 200 or response_time > 0.5:
            app.logger.error(f"Failed to fetch numbers from test server, status: {response.status_code}, response_time: {response_time}")
            return jsonify({"error": "Failed to fetch numbers from test server"}), 500
        
        numbers = response.json().get("numbers", [])
        app.logger.debug(f"Fetched numbers: {numbers}")
        
        # Store numbers in the sliding window, ensuring uniqueness
        previous_state = list(number_window)
        for number in numbers:
            if number not in number_window:
                number_window.append(number)
        
        current_state = list(number_window)
        average = sum(current_state) / len(current_state) if current_state else 0
        
        app.logger.debug(f"Previous window state: {previous_state}")
        app.logger.debug(f"Current window state: {current_state}")
        app.logger.debug(f"Average: {average}")
        
        return jsonify({
            "numbers": numbers,
            "windowPrevState": previous_state,
            "windowCurrState": current_state,
            "avg": round(average, 2)
        })
    
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Request to test server failed: {e}")
        return jsonify({"error": "Request to test server failed"}), 500

if __name__ == '__main__':
    app.run(port=9876, debug=True)