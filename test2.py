import requests
import json

def main():
    url = "https://www.loblaws.ca/api/pickup-locations"
    headers = {
        "Accept-Language": "en",
        "x-apikey": "C1xujSegT5j3ap3yexJjqhOfELwGKYvz",
        "x-application-type": "Web",
        "x-loblaw-tenant-id": "ONLINE_GROCERIES",
    }
    params = {
        "banner": "loblaw",
        "cartId": "00000000-0000-0000-0000-000000000000",
        "storeId": "1001",
        "includeFiltersInResponse": "true"
    }

    response = requests.get(url, headers=headers, params=params)
    print("Status Code:", response.status_code)  # Check the status code
    if response.status_code == 200:
        try:
            response_data = response.json()
            print(json.dumps(response_data, indent=4))
        except json.JSONDecodeError:
            print("Failed to decode JSON from response:")
            print(response.text)  # Print the raw response text to understand what was returned
    else:
        print("Received non-200 response:")
        print(response.text)  # This will help diagnose what went wrong

if __name__ == "__main__":
    main()
