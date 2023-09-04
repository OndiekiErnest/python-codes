
import json
import yt_dlp

URL = "https://www.xvideos.com/video75534141/stepmom_on_the_prowl_for_a_big_cock_-_daphne_rosen"

# See help(yt_dlp.YoutubeDL) for a list of available options and public functions
ydl_opts = {}
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(URL, download=False)

    # ydl.sanitize_info makes the info json-serializable
    print(json.dumps(ydl.sanitize_info(info)))
