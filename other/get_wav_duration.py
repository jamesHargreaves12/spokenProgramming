import subprocess
from mutagen.mp3 import MP3
import os

FNULL = open(os.devnull, 'w')
def get_length_of_file(original_data_set:bool,q_num,name_prefix):
    base_dir_1 = '/Users/james_hargreaves/Documents/ThirdYear/Part2ProjectData'
    base_dir_2 = '/Users/james_hargreaves/Documents/ThirdYear/Part2ProjectData_2'
    basedir = base_dir_1 if original_data_set else base_dir_2
    folder = basedir +'/{}/audio/'.format(q_num)
    src_names = [x for x in os.listdir(folder) if x.startswith(name_prefix)]
    assert(len(src_names) == 1)
    src = folder + src_names[0]
    trg = '/Users/james_hargreaves/Documents/ThirdYear/tmp/temp.mp3'
    subprocess.call(['ffmpeg', '-i', src, trg],stdout=FNULL,stderr=subprocess.STDOUT)
    # subprocess.call(['ffmpeg', '-i', src, trg])
    audio = MP3(trg)
    os.remove(trg)
    return audio.info.length

list_of_files = [
    (False, 12, "280"),
    (False, 11, "402"),
    (True, 14, "780"),
    (True, 16, "812"),
    (True, 1, "780"),
    (False, 11, "280"),
    (True, 15, "596"),
    (True, 8, "762"),
    (True, 6, "372"),
    (False, 2, "301"),
    (True, 12, "812"),
    (True, 15, "875"),
    (True, 12, "762"),
    (True, 7, "546"),
    (False, 12, "402")
]


def get_audio_lengths_of_fold_1():
    results = []
    for og_files,q_num,prefix in list_of_files:
        results.append(get_length_of_file(og_files,q_num,prefix))
    return results

print(get_audio_lengths_of_fold_1())