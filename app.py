from flask import Flask, request, render_template, jsonify
import googleapiclient.discovery
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_shorts_links', methods=['GET'])
def get_shorts_links():
    api_key = 'AIzaSyCUoU2Qb7y-SURv_8UkiCUh-HzKr37ZYUg'  
    keyword = request.args.get('keyword')
    limit = int(request.args.get('limit', 0))

    if not keyword:
        return jsonify({"error": "Keyword parameter is required."}), 400

    shorts_links = get_youtube_shorts_links(api_key, keyword, limit)

    return jsonify({"shorts_links": shorts_links})

def get_youtube_shorts_links(api_key, keyword, limit=None):
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
    next_page_token = None
    shorts_links = []

    while True:
        request = youtube.search().list(
            part="snippet",
            q=keyword,
            maxResults=min(limit - len(shorts_links), 50) if limit else 50,
            type="video",
            videoDuration="short",
            pageToken=next_page_token
        )
        response = request.execute()

        for item in response["items"]:
            if "id" in item and "videoId" in item["id"]:
                video_id = item["id"]["videoId"]
                s_url = f"https://www.youtube.com/shorts/{video_id}"
                resp = requests.get(s_url)
                if resp.status_code == 200 and "watch" not in resp.url:
                    shorts_links.append(s_url)
                resp.close()

                if limit and len(shorts_links) >= limit:
                    return shorts_links

        if "nextPageToken" in response:
            next_page_token = response["nextPageToken"]
        else:
            break

    return shorts_links

if __name__ == '__main__':
    app.run(debug=True)
