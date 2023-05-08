from pytube import YouTube, request, Playlist

import os
from pathlib import Path

request.default_range_size = 500000

def get_video(url, save_location, in_progress, on_complete, handle_error):
    try:
        filename = str(Path(save_location).name)
        output_path = str(os.path.split(Path(save_location))[0])
        download = YouTube(url, on_progress_callback=in_progress, on_complete_callback=on_complete)
        stream = download.streams.filter(progressive=True).get_highest_resolution()
        stream.download(filename=filename, output_path=output_path)
        return  
    except:
        error = True
        handle_error()
        return

def get_playlist(url, save_location, in_progress, on_complete, handle_error):
    try:
        filename = str(Path(save_location).name)
        output_path = str(os.path.split(Path(save_location))[0])
        playlist = Playlist(url=url)
        print(playlist.title, playlist.length)
        for i, nxt_url in enumerate(playlist.video_urls):
            save_location = f'{output_path}/{playlist.title}_{i}.mp4'
            get_video(url=nxt_url, save_location=save_location, in_progress=in_progress, on_complete=on_complete, handle_error=handle_error)
        return
    except:
        error = True
        handle_error()
        return
    pass
