from urllib.request import Request
import requests
import inquirer
import xlsxwriter
import json
from concurrent.futures import ThreadPoolExecutor, thread
from time import perf_counter

# CHANGE THIS
BASE_URL = "http://127.0.0.1:8200"
REGISTER_URL = f"{BASE_URL}/api/v1/user/register"

# VARIABLE DECLARATION, DONT CHANGE THIS!
DATA_BUFFER = []

# QUESTION
questions = [
    inquirer.List(
        "test",
        message="What API testing program do you want to do?",
        choices=["Register User"],
    ),
]
testingType = inquirer.prompt(questions)
filePath = input("Testing data source path: ")
outputFile = input("Output testing file name: ")
threadSize = int(input("How many thread you want to use: "))

# OPEN DATA SOURCE
FILE = open(f'{filePath}')
if not filePath.endswith(".json"):
    print("ONLY JSON FILE ALLOW TO BE DATA SOURCE!")
    exit()
DATA_SORUCE = json.load(FILE)
FILE.close()

# START WOORKBOOK
workbook = xlsxwriter.Workbook(f'{outputFile}.xlsx')


# HTTP REQUEST WRAPPER
def httpRequest(url, body: None, method):
    with requests.Session() as client:
        if method == "POST":
            if body != None:
                resp = client.post(f'{url}', json=body)
                return resp

        if method == "GET":
            if body != None:
                resp = client.get(f'{url}', json=body)
                return resp
            if body == None:
                resp = client.get(f'{url}')
                return resp


def registerUser(body, no, worksheet):
    resp = httpRequest(url=REGISTER_URL, body=body, method="POST")
    worksheet.write(f"A{no}", f"{no-1}")
    worksheet.write(f"B{no}", str(body))
    worksheet.write(f"C{no}", str(resp.json()))
    worksheet.write(f"D{no}", round(
        float(resp.elapsed.total_seconds()), 3)*1000)
    body["Authorization"] = resp.cookies["Authorization"]
    DATA_BUFFER.append(body)


if testingType.get("test") == "Register User":
    print("--------START REGISTERING USER USER--------")
    START_TIME = perf_counter()
    registerWorksheet = workbook.add_worksheet("REGISTER")
    registerWorksheet.write("A1", "NO")
    registerWorksheet.write("B1", "BODY DATA")
    registerWorksheet.write("C1", "RESPONSE DATA")
    registerWorksheet.write("D1", "RESPON TIME")
    with ThreadPoolExecutor(threadSize) as executor:
        executor.map(registerUser, DATA_SORUCE, range(
            2, len(DATA_SORUCE)+2), [registerWorksheet] * len(DATA_SORUCE))
        executor.shutdown(wait=True)

    file = open(f'{filePath.replace(".json","")}_WITH_AUTH_COOKIE.json', "x")
    file.write(json.dumps(DATA_BUFFER))
    file.close()
    print("Execution time:",
          f"{round((perf_counter() - START_TIME),3) * 1000}ms")

workbook.close()
