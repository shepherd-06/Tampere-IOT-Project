import requests
import json


def fetch_metadata(url):
    response = requests.get(url)
    if response.status_code == 200:
        metadata = response.json()
        with open('metadata.json', 'w') as outfile:
            json.dump(metadata, outfile)
        print("Metadata fetched and saved successfully.")
    else:
        print(f"Failed to fetch metadata. Status code: {response.status_code}")


if __name__ == "__main__":
    api_url = "https://iot.tampere.fi/externaldataapi/v1/metadata?orderNumber=363_6zALv0wwm2aed"
    fetch_metadata(api_url)
