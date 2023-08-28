import time, winsound, subprocess, random, os
from mutagen.mp3 import MP3
path = 'C:\\Users\\code\\Music'

def start(dur, drct, xdrct):
    subprocess.Popen(['C:\\Program Files (x86)\\Windows Media Player\\wmplayer.exe',
                        drct])
    content.remove(xdrct)
    time.sleep(int(dur))

content = os.listdir(path)
while True:
    for i in content:
        file = random.choice(content)
        if file.endswith('.mp3') or file.endswith('.m4a'):
            abspath = os.path.join(path, file)
            songdet = MP3(abspath)
            duration = songdet.info.length
            start(duration, abspath, file)
            break
        else:
            content.remove(file)
            continue
    if content == []:
        break



        
