from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
import os
import json

file = open("api_key.json")
api_key = json.load(file)['api_key']
file.close
CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ["https://www.googleapis.com/auth/youtube"]


def main():
    print("Enter a youtube channel handle (e.g. @markiplier), without the @ sign:")
    handle = input()
    print("Enter a desired keyword to filter for:")
    keyword = input()
    print("Enter the title of your new playlist:")
    playlist_title = input()

    credentials = None

    if os.path.exists("token.json"):
        try:
            credentials = Credentials.from_authorized_user_file("token.json", SCOPES)
        except (ValueError, KeyError):
            print("Invalid token.json file. It might be expired or corrupted.")

    if not credentials:
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
        credentials = flow.run_local_server(port=8000)

        with open("token.json", "w") as token:
            token.write(credentials.to_json())

    youtube = build(
        'youtube', 
        'v3', 
        developerKey=api_key,
        credentials=credentials
    )

    channels_request = youtube.channels().list(
        part="contentDetails",
        forHandle = handle,
    )

    channels_response = channels_request.execute()
    # Uncomment for full response report
    # print(channels_response)

    if (channels_response['items'] == []) or ('@' in handle):
        print("No channel with the given handle exists.")
    else:
        uploads_id = channels_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        videos = []
        next_page_token = None

        # Gets all the uploads of the channel
        while True:
            playlist_items_response = youtube.playlistItems().list(
                part = "snippet, contentDetails",
                playlistId = uploads_id,
                maxResults = 50,
                pageToken = next_page_token,
            ).execute()

            videos += playlist_items_response['items']
            
            next_page_token = playlist_items_response.get('nextPageToken')

            if not next_page_token:
                break

        # Reverses the list of uploads so older stuff is first in playlist
        videos_reverse = []
        for video in videos:
            videos_reverse.insert(0, video)

        # Creates an empty playlist
        playlist_request = youtube.playlists().insert(
            part = 'snippet, status',
            body = {
                "snippet": {
                    "title": playlist_title,
                    "description": "",
                    "defaultLanguage": "en",
                },
                "status": {
                    "privacyStatus": "private",
                }
            }
        )

        playlist_response = playlist_request.execute()
        # Uncomment for full response report
        # print(playlist_response)

        playlist_id = playlist_response['id']

        playlist_videos = []
        
        for video in videos_reverse:
            title = video['snippet']['title']
            video_id = video['snippet']['resourceId']['videoId']
            if keyword in title:
                playlist_videos.append(video_id)


        # Populates the playlist with videos whose titles contain keyword, with a max of 50 videos.
        count = 0
        for video_id in playlist_videos:
            if count < 50:
                populate_request = youtube.playlistItems().insert(
                        part = 'snippet',
                        body = {
                            "snippet": {
                                "playlistId": playlist_id,
                                "resourceId": {"kind": "youtube#video", "videoId": video_id},
                            },
                        }
                    )
                populate_response = populate_request.execute()
                # Uncomment for full response report
                # print(populate_response)
                count += 1
        if count == 50:
            print("Limit of 50 videos reached. This limit can be changed inside the script.")


if __name__ == '__main__':
    main()