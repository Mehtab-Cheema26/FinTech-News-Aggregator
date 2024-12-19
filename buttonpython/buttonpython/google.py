import os
import httpx
import pandas as pd
from datetime import datetime

def fetch_google_data(query="stock market news"):
    try:
        api_key = 'AIzaSyDnK2VIxLMPymWjLCKlQM9HGXZ5eylHlC4'
        search_engine_id = 'd1e4d667b808f431f'
        
        base_url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': api_key,
            'cx': search_engine_id,
            'q': f"{query} (news OR headlines OR breaking)",
            'num': 10,  # Number of results
            'sort': 'date'
        }

        response = httpx.get(base_url, params=params)
        if response.status_code != 200:
            print(f"Error from Google API: {response.status_code}")
            return False

        data = response.json()
        
        # Get the file path
        csv_path = os.path.join(os.path.dirname(__file__), 'google_search_results.csv')
        
        # Write results to CSV
        with open(csv_path, 'w', newline='', encoding='utf-8') as file:
            writer = pd.DataFrame([{
                'title': item.get('title', 'No title'),
                'link': item.get('link', ''),
                'date': datetime.now().strftime('%Y-%m-%d')
            } for item in data.get('items', [])])
            
            writer.to_csv(csv_path, index=False)
            
        return True

    except Exception as e:
        print(f"Error in fetch_google_data: {str(e)}")
        return False

if __name__ == "__main__":
    fetch_google_data()
