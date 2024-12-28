import os
import httpx
import pandas as pd
from datetime import datetime

def fetch_google_data(query="stock market news"):
    try:
        # Move these to environment variables
        api_key = os.getenv('GOOGLE_API_KEY')
        print(api_key)
        search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')

        if not api_key or not search_engine_id:
            print("Missing Google API credentials")
            return False

        base_url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': api_key,
            'cx': search_engine_id,
            'q': query,
            'num': 10,  # Number of results
            'dateRestrict': 'd1'  # Last 24 hours
        }

        response = httpx.get(base_url, params=params)

        # Add debug logging
        print(f"Google API Response Status: {response.status_code}")

        if response.status_code != 200:
            print(f"Error from Google API: {response.status_code}")
            print(f"Response content: {response.text}")
            return False

        data = response.json()

        if 'items' not in data:
            print("No results found in Google API response")
            print(f"Response data: {data}")
            return False

        # Get the file path
        csv_path = os.path.join(os.path.dirname(__file__), 'google_search_results.csv')

        # Write results to CSV
        results = []
        for item in data.get('items', []):
            results.append({
                'title': item.get('title', 'No title'),
                'link': item.get('link', ''),
                'date': datetime.now().strftime('%Y-%m-%d')
            })

        df = pd.DataFrame(results)
        df.to_csv(csv_path, index=False)

        return True

    except Exception as e:
        print(f"Error in fetch_google_data: {str(e)}")
        return False

if __name__ == "__main__":
    fetch_google_data()
