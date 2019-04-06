import os
from data_prep_tools.constants import base_dir_2

transcript_count = 0
response_id_to_count = {}
for i in range(1,17):
    dir = base_dir_2 + str(i)
    audio_files = os.listdir(dir+"/pseudocode")
    transcript_files = os.listdir(dir+"/transcripts")
    stripped_audio = [audio_file.strip(".txt") for audio_file in audio_files]
    stripped_trans = [trans_file.strip(".txt") for trans_file in transcript_files]
    transcript_count += len(transcript_files)
    for audio_file in stripped_audio:
        if audio_file not in response_id_to_count.keys():
            response_id_to_count[audio_file] = 1
        else:
            response_id_to_count[audio_file] += 1
        if audio_file not in stripped_trans:
            print("ISSUE(missing transcript): " + str(i) + " file: " + audio_file)
    for trans_file in stripped_trans:
        if trans_file not in stripped_audio:
            print("ISSUE(missing audio): " + str(i) + " file: " + trans_file)
print(transcript_count)
print(response_id_to_count)