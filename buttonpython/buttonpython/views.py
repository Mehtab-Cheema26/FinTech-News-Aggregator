import os
from datetime import datetime
import csv
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .reddit_post import fetch_reddit_data
from .twitter_post import fetch_twitter_posts
from .google import fetch_google_data

def button(request):
    # Clear all CSV files when page first loads
    clear_csv_files()
    return render(request, 'home.html')

@csrf_exempt
def get_twitter_posts(request):
    if request.method != 'POST':
        return render(request, 'home.html')

    twitter_data = []
    twitterTopic = request.POST.get('tweets', 'stocks')
    fetch_twitter_posts(twitterTopic)

    try:
        csv_path = os.path.join(os.path.dirname(__file__), 'tweets_data.csv')
        with open(csv_path, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file)
            headers = next(csv_reader)

            text_idx = headers.index('Tweet Text')
            creator_idx = headers.index('Creator')
            date_idx = headers.index('Time Posted')
            likes_idx = headers.index('Likes')
            link_idx = headers.index("Tweet Link")

            for row in csv_reader:
                timestamp = datetime.strptime(row[date_idx], "%Y-%m-%dT%H:%M:%S.%fZ")
                current_time = datetime.utcnow()
                time_difference = current_time - timestamp
                minutes_ago = int(time_difference.total_seconds() / 60)

                data_dict = {
                    'text': row[text_idx],
                    'creator': row[creator_idx],
                    'date': minutes_ago,
                    'likes': row[likes_idx],
                    'url': row[link_idx]
                }
                twitter_data.append(data_dict)
    except Exception as e:
        print(f"Error reading Twitter data: {str(e)}")
        return render(request, 'home.html', {
            'twitter_error': "Error reading Twitter data"
        })

    return render(request, 'home.html', {
        'twitter': twitter_data
    })

@csrf_exempt
def get_reddit_posts(request):
    # First try to load existing Google data
    google_data = []
    try:
        google_csv_path = os.path.join(os.path.dirname(__file__), 'google_search_results.csv')
        if os.path.exists(google_csv_path) and os.path.getsize(google_csv_path) > 0:
            with open(google_csv_path, mode='r', encoding='utf-8') as csv_file:
                csv_reader = csv.reader(csv_file)
                headers = next(csv_reader)
                
                title_idx = headers.index('title')
                url_idx = headers.index('link')
                date_idx = headers.index('date')
                
                for row in csv_reader:
                    google_data.append({
                        'title': row[title_idx],
                        'url': row[url_idx],
                        'date': row[date_idx]
                    })
    except Exception as e:
        print(f"Error loading Google data in Reddit view: {str(e)}")

    if request.method != 'POST':
        return render(request, 'home.html', {'google': google_data})

    data_list = []
    subreddit = request.POST.get('subreddit', 'stocks')
    
    if not fetch_reddit_data(subreddit):
        return render(request, 'home.html', {
            'reddit_error': f"Subreddit '{subreddit}' not found or there was an error accessing it.",
            'subreddit': subreddit,
            'google': google_data
        })

    try:
        csv_path = os.path.join(os.path.dirname(__file__), 'reddit_python.csv')
        with open(csv_path, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file)
            headers = next(csv_reader)
            
            title_idx = headers.index('title')
            url_idx = headers.index('url')
            date_idx = headers.index('created_utc')
            
            for row in csv_reader:
                created_date = datetime.fromtimestamp(float(row[date_idx])).strftime('%Y-%m-%d %H:%M:%S')
                data_dict = {
                    'title': row[title_idx],
                    'url': row[url_idx],
                    'date': created_date
                }
                data_list.append(data_dict)

        return render(request, 'home.html', {
            'reddit': data_list,
            'subreddit': subreddit,
            'google': google_data
        })

    except Exception as e:
        print(f"Error reading Reddit data: {str(e)}")
        return render(request, 'home.html', {
            'reddit_error': "Error reading Reddit data",
            'subreddit': subreddit,
            'google': google_data
        })

@csrf_exempt
def get_google(request):
    if request.method != 'POST':
        try:
            csv_path = os.path.join(os.path.dirname(__file__), 'google_search_results.csv')
            if os.path.exists(csv_path) and os.path.getsize(csv_path) > 0:
                data_list = []
                with open(csv_path, mode='r', encoding='utf-8') as csv_file:
                    csv_reader = csv.reader(csv_file)
                    headers = next(csv_reader)
                    
                    title_idx = headers.index('title')
                    url_idx = headers.index('link')
                    date_idx = headers.index('date')
                    
                    for row in csv_reader:
                        data_dict = {
                            'title': row[title_idx],
                            'url': row[url_idx],
                            'date': row[date_idx]
                        }
                        data_list.append(data_dict)
                return render(request, 'home.html', {'google': data_list})
        except Exception as e:
            print(f"Error loading existing Google data: {str(e)}")
        return render(request, 'home.html')

    query = request.POST.get('google_query', 'stock market news')
    
    if not fetch_google_data(query):
        return render(request, 'home.html', {
            'google_error': "Error fetching Google data"
        })

    try:
        csv_path = os.path.join(os.path.dirname(__file__), 'google_search_results.csv')
        data_list = []
        
        if os.path.exists(csv_path) and os.path.getsize(csv_path) > 0:
            with open(csv_path, mode='r', encoding='utf-8') as csv_file:
                csv_reader = csv.reader(csv_file)
                headers = next(csv_reader)
                
                title_idx = headers.index('title')
                url_idx = headers.index('link')
                date_idx = headers.index('date')
                
                for row in csv_reader:
                    data_dict = {
                        'title': row[title_idx],
                        'url': row[url_idx],
                        'date': row[date_idx]
                    }
                    data_list.append(data_dict)

        return render(request, 'home.html', {
            'google': data_list,
            'google_query': query
        })

    except Exception as e:
        print(f"Error in get_google: {str(e)}")
        return render(request, 'home.html', {
            'google_error': "Error reading Google data"
        })

def clear_csv_files():
    try:
        # Clear Twitter CSV
        csv_path = os.path.join(os.path.dirname(__file__), 'tweets_data.csv')
        with open(csv_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Tweet Text", "Creator", "Time Posted", "Likes", "Tweet Link"])

        # Clear Reddit CSV
        with open('reddit_python.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['title', 'url', 'created_utc'])

        # Clear Google CSV
        csv_path = os.path.join(os.path.dirname(__file__), 'google_search_results.csv')
        with open(csv_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['title', 'link', 'date'])

    except Exception as e:
        print(f"Error in clear_csv_files: {str(e)}")


