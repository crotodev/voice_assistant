import os
import requests
import yaml

import speech_recognition as sr
from gtts import gTTS
from playsound import playsound

tmp_path = os.path.join(".", "tmp")

if not os.path.exists(tmp_path):
    os.mkdir(tmp_path)

with open("config.yaml", "r") as f:
    config = yaml.load(f, yaml.Loader)

open_weather_url = config["rapid_api"]["open_weather"]["url"]
config["rapid_api"]["open_weather"]["url"] = (
    open_weather_url + config["rapid_api"]["open_weather"]["city"]
)


def say(text: str) -> None:
    audio_file = os.path.join(tmp_path, "audio.mp3")
    tts = gTTS(text)
    tts.save(audio_file)
    playsound(audio_file)


def find_numbers(text: str):
    split = text.split()
    nums = []
    for i in split:
        try:
            nums.append(int(i))
        except ValueError:
            pass
    return nums


def subtract(nums: list[int]):
    result = nums[0]
    for i in nums[1:]:
        result -= i

    return result


def divide(nums: list[int]):
    result = nums[0]
    for i in nums[1:]:
        result /= i

    return result


def multiply(nums: list[int]):
    result = 1
    for i in nums:
        result *= i

    return result


def make_rapid_api_request(key: str, url: str, host: str):
    headers = {
        "accept": "application/json",
        "X-RapidAPI-Key": key,
        "X-RapidAPI-Host": host,
    }
    response = requests.get(url, headers=headers)
    return response.json()


def say_arithmetic(text: str, operator: str) -> None:
    numbers = find_numbers(text)
    joined = f" {operator} ".join(map(str, numbers[1:]))
    text = ""
    if operator == "+":
        text = f"{numbers[0]} + {joined} is {sum(numbers)}"
    if operator == "-":
        text = f"{numbers[0]} - {joined} is {subtract(numbers)}"
    if operator == "/":
        text = f"{numbers[0]} / {joined} is {divide(numbers)}"
    if operator == "*":
        text = f"{numbers[0]} * {joined} is {multiply(numbers)}"
    print(text)
    say(text)


r = sr.Recognizer()

while True:
    with sr.Microphone() as source:
        print("Say something!")
        audio = r.listen(source)

    try:
        recognized = r.recognize_google(audio)
        if "hey pine" in recognized.lower():
            print(recognized)
            if "say" in recognized:
                say(recognized[2:])

            if "chuck norris" in recognized.lower():
                key = config["rapid_api"]["key"]
                url = config["rapid_api"]["chuck_norris"]["url"]
                host = config["rapid_api"]["chuck_norris"]["host"]
                say(make_rapid_api_request(key, url, host)["value"])

            if "weather" in recognized.lower():
                key = config["rapid_api"]["key"]
                url = config["rapid_api"]["open_weather"]["url"]
                host = config["rapid_api"]["open_weather"]["host"]
                result = make_rapid_api_request(key, url, host)

                temp = result["main"]["temp"]
                feels_like = result["main"]["feels_like"]
                temp_min = result["main"]["temp_min"]
                temp_max = result["main"]["temp_max"]
                humidity = result["main"]["humidity"]
                response = (
                    f"The temperature is {temp} degrees with a low of {temp_min} and a high of {temp_max}. It "
                    f"feels like {feels_like} degrees. The humidity is {humidity}"
                )
                say(response)

            if "how are you" in recognized:
                say("I'm doing okay!")

            if "+" in recognized:
                say_arithmetic(recognized, "+")

            if "-" in recognized:
                say_arithmetic(recognized, "-")

            if "/" in recognized or "divided" in recognized:
                say_arithmetic(recognized, "/")

            if "*" in recognized or "multiplied" in recognized:
                say_arithmetic(recognized, "*")

    except sr.UnknownValueError:
        pass
