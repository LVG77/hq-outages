import ast
import urllib.parse
import urllib.request
import json
from datetime import datetime

outage_status = {
    "N": "NA",
    "": "NA",
    "A": "Work assigned",
    "L": "Crew at work",
    "R": "Crew on the way",
}

cause_of_outage = {
    "Equipment failure": [
        "11",
        "12",
        "13",
        "14",
        "15",
        "58",
        "70",
        "72",
        "73",
        "74",
        "79",
        "defaut",
    ],
    "Weather conditions": ["21", "22", "24", "25", "26"],
    "Accident or incident": [
        "31",
        "32",
        "33",
        "34",
        "41",
        "42",
        "43",
        "44",
        "54",
        "55",
        "56",
        "57",
    ],
    "Damage due to vegetation": ["51"],
    "Damage caused by an animal": ["52", "53"],
}


def make_get_request(url: str, **kwargs):
    params = urllib.parse.urlencode(kwargs)
    url = f"{url}?{params}"
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())
    return data


def find_key(value):
    for k, v in cause_of_outage.items():
        if value in v:
            return k


def parse_datetime(s: str):
    if s:
        datetime_object = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
    else:
        datetime_object = None
    return datetime_object


def fill_output(data):
    out = []
    outages = dict(
        time_stamp="",
        num_of_customers="",
        start_time="",
        expected_end_time="",
        latitude="",
        longitude="",
        outage_status="",
        ignore="",
        cause_of_outage="",
        municipality="",
        code="",
    )
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for p in data["pannes"]:
        outages["time_stamp"] = time_now
        outages["num_of_customers"] = p[0]
        outages["start_time"] = p[1]
        outages["expected_end_time"] = p[2]
        outages["longitude"] = ast.literal_eval(p[4])[0]
        outages["latitude"] = ast.literal_eval(p[4])[1]
        outages["outage_status"] = outage_status[p[5]]
        outages["ignore"] = p[6]
        outages["cause_of_outage"] = find_key(p[7])
        outages["municipality"] = p[8]
        outages["code"] = p[9]
        out.append(outages.copy())
    return out


if __name__ == "__main__":
    time_stamp = make_get_request(
        "http://pannes.hydroquebec.com/pannes/donnees/v3_0/bisversion.json"
    )
    data = make_get_request(
        f"http://pannes.hydroquebec.com/pannes/donnees/v3_0/bismarkers{time_stamp}.json"
    )
    scraped_data = fill_output(data)
    with open("outages.json", "w") as f:
        f.write(json.dumps(scraped_data, indent=4, ensure_ascii=False))
