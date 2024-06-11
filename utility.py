import requests
from datetime import datetime

def process_attribute_name(attr_name):
    parts_to_remove = [
        "Päätaso",
        "Tampere (tilannekuva)",
        "Keskusta",
        "➞",
        "Koko alue",
        "use_seconds",
        "user_count",
        "visit_count"
    ]
    for part in parts_to_remove:
        attr_name = attr_name.replace(part, "")

    return "||".join([part.strip() for part in attr_name.split("➞") if part.strip()])


def call_external_api(attr_id):
    # Actual API call
    # Replace with actual API URL
    print(f"API call is happening at {datetime.now()}")
    url = f"https://iot.tampere.fi/externaldataapi/v1/meas/stat?orderNumber=363_6zALv0wwm2aed&productId=gr5OWJy87FUnUfI0Oq57_m_GPnndze_5&id={attr_id}&startTime=1701388800000&endTime=1717200000000&period=CurrentYear&dimension=Hour"
    response = requests.get(url)
    if response.status_code == 200:
        response = response.json()
        print(f"Api call finished at {datetime.now()}")
        return response
    else:
        return {"error": f"Failed to fetch data for attribute ID {attr_id}"}
