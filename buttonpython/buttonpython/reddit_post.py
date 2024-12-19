import time
import csv
import httpx
from datetime import datetime
import os

import pandas as pd


def fetch_reddit_data(subreddit="stocks"):
    base_url = "https://www.reddit.com"
    endpoint = f"/r/{subreddit}"
    category = "/hot"
    url = base_url + endpoint + category + ".json"

    after_post_id = None
    dataset = []

    try:
        # Update the file path to be relative to the script location
        csv_path = os.path.join(os.path.dirname(__file__), 'reddit_python.csv')

        for _ in range(5):
            params = {
                'limit': 100,
                't': 'year',
                'after': after_post_id
            }

            response = httpx.get(url, params=params)
            if response.status_code == 404:
                print(f"Subreddit '{subreddit}' not found")
                return False
            elif response.status_code != 200:
                print(f"Error accessing Reddit API: {response.status_code}")
                return False

            json_data = response.json()
            dataset.extend([rec['data'] for rec in json_data['data']['children']])

            after_post_id = json_data['data']['after']
            time.sleep(0.5)

        df = pd.DataFrame(dataset)
        df.to_csv(csv_path, index=False)
        return True

    except Exception as e:
        print(f"Error in fetch_reddit_data: {str(e)}")
        return False


if __name__ == "__main__":
    fetch_reddit_data()




