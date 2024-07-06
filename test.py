import requests
import json

def main():
    url = "https://api.pcexpress.ca/pcx-bff/api/v2/listingPage/27985" #28195
    headers = {
        "Content-Type": "application/json", # not needed
        "Accept-Language": "en",
        "x-apikey":	"C1xujSegT5j3ap3yexJjqhOfELwGKYvz",
        "x-application-type": "Web",
        "x-loblaw-tenant-id": "ONLINE_GROCERIES",
    }
    payload = {
        "banner": "loblaw",
        "cart": {"cartId": "00000000-0000-0000-0000-000000000000"},
        "fulfillmentInfo": {
            "storeId": "1001", 
        },
        "listingInfo": {
            "sort": {},  # not needed
            "pagination": {"from": 1},  # not needed
            "includeFiltersInResponse": True # not needed
        },
    }

    response = requests.post(url, headers=headers, json=payload)
    response_data = response.json()


    with open('api_response.json', 'w') as f:
        json.dump(response_data, f, indent=4)
        
    # Print the entire JSON response
    print(json.dumps(response_data, indent=4))

if __name__ == "__main__":
    main()
