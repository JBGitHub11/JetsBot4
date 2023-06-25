import requests, json, os
from dotenv import load_dotenv

def get_live_video_id(user_id):
    load_dotenv()
    api_key = os.getenv('YOUTUBE_API_KEY')
    response = requests.get(f"https://www.googleapis.com/youtube/v3/search?part=snippet&eventType=live&type=video&maxResults=50&channelId={user_id}&key={api_key}")
    data = json.loads(response.text)
    print(data)  # Add this line to print the raw API response
    if len(data['items']) > 0:
        print(f"{user_id} is live!\nVideo ID: {data['items'][0]['id']['videoId']}")
    else:
        print(f"{user_id} is not live.")


get_live_video_id('UCA_KjizAMeuEKL9d7dkvPeg')
