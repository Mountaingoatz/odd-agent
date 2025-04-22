"""Fetch latest Form ADV and 13F filings using sec-api.io.

Requires:
  * env var SEC_API_KEY
"""
import os, requests, json, pathlib, datetime as dt

SEC_API_KEY = os.getenv("SEC_API_KEY")
BASE_URL = "https://api.sec-api.io"

def fetch_adv(crd: str):
    # First, search for the firm using the firm search endpoint
    search_url = f"{BASE_URL}/form-adv/firm?token={SEC_API_KEY}"
    
    # Create the search query
    search_payload = {
        "query": f"Info.FirmCrdNb:{crd}",
        "from": "0",
        "size": "1",
        "sort": [{"Info.FirmCrdNb": {"order": "desc"}}]
    }
    
    try:
        # Search for the firm
        print(f"Searching for firm with CRD {crd}")
        r = requests.post(search_url, json=search_payload, timeout=30)
        r.raise_for_status()
        search_results = r.json()
        
        if not search_results.get("filings"):
            raise ValueError(f"No ADV filings found for CRD {crd}")
            
        # Get the most recent filing
        filing = search_results["filings"][0]
        
        # Now fetch additional details from various schedules
        result = {
            "filing": filing,
            "direct_owners": fetch_schedule_a(crd),
            "indirect_owners": fetch_schedule_b(crd),
            "other_business_names": fetch_schedule_d_1b(crd),
            "brochures": fetch_brochures(crd)
        }
        
        return result
        
    except requests.exceptions.HTTPError as e:
        raise ValueError(f"Error fetching ADV data: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error processing ADV data: {str(e)}")

def fetch_schedule_a(crd: str):
    url = f"{BASE_URL}/form-adv/schedule-a-direct-owners/{crd}?token={SEC_API_KEY}"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.json()

def fetch_schedule_b(crd: str):
    url = f"{BASE_URL}/form-adv/schedule-b-indirect-owners/{crd}?token={SEC_API_KEY}"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.json()

def fetch_schedule_d_1b(crd: str):
    url = f"{BASE_URL}/form-adv/schedule-d-1-b/{crd}?token={SEC_API_KEY}"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.json()

def fetch_brochures(crd: str):
    url = f"{BASE_URL}/form-adv/brochures/{crd}?token={SEC_API_KEY}"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.json()

def fetch_13f(cik: str):
    url = f"{BASE_URL}/filings?forms=13F&cik={cik}"
    headers = {"Authorization": SEC_API_KEY}
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()

if __name__ == "__main__":
    sample_crd = "106176"  # Blackstone
    data = fetch_adv(sample_crd)
    pathlib.Path("sample_adv.json").write_text(json.dumps(data, indent=2))
    print("Sample ADV saved.")
