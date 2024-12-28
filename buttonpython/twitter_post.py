import csv
import os

import requests


def fetch_twitter_posts(twitterTopic='stocks'):
    # Get the absolute path to the CSV file
    csv_path = os.path.join(os.path.dirname(__file__), 'tweets_data.csv')

    print(f"Writing to CSV file at: {csv_path}")  # Debug print

    # Replace with the user-defined query and your Bearer Token
    print("We have gotten till the method")
    query = f"{twitterTopic}"
    # url = f"https://api.twitter.com/2/tweets/search/recent?query={twitterTopic}&max_results=10&tweet.fields=created_at,attachments,public_metrics&expansions=author_id"

    url = (
        f"https://api.twitter.com/2/tweets/search/recent"
        f"?query={twitterTopic}&max_results=10"
        f"&tweet.fields=created_at,public_metrics"
        f"&expansions=author_id"
        f"&user.fields=username"
    )

    # Bearer Token
    headers = {
        "Authorization": "Bearer " + os.getenv("TWITTER_BEARER_TOKEN") # bearer token here
    }

    # Make the request
    response = requests.get(url, headers=headers)
    print(f"API Response Status: {response.status_code}")  # Add this debug print

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        print(f"Number of tweets received: {len(data.get('data', []))}")  # Add this debug print

        # Create a dictionary to map author IDs to their usernames
        # user_mapping = {user['id']: user['name'] for user in data["includes"]["users"]}

        # Map author IDs to usernames
        user_mapping = {user['id']: user['username'] for user in data.get("includes", {}).get("users", [])}

        # Use the absolute path when opening the file
        with open(csv_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)

            # Write the header row
            writer.writerow(["Tweet Text", "Creator", "Time Posted", "Likes", "Tweet Link"])

            # Write the tweet data
            for tweet in data["data"]:
                tweet_text = tweet.get("text", "No text available")
                author_id = tweet.get("author_id", "Unknown")
                created_at = tweet.get("created_at", "No date available")
                likes = tweet.get("public_metrics", {}).get("like_count", 0)
                creator_name = user_mapping.get(author_id, "Unknown author")
                # creator_name.replace(' ', '')
                tweet_id = tweet.get("id", "")

                # Construct the tweet URL
                tweet_link = f"https://twitter.com/{creator_name}/status/{tweet_id}"
                # Write each tweet's details as a row in the CSV file
                writer.writerow([tweet_text, creator_name, created_at, likes, tweet_link])

        print("Data saved to tweets_data.csv successfully.")


    else:
        print(f"Error: {response.status_code}")
        print(response.text)  # Print error details if something went wrong

if __name__ == "__main__":
    fetch_twitter_posts()
