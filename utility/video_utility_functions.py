from moviepy.editor import VideoFileClip


def get_video_length(vid_file):
    clip = VideoFileClip(vid_file)
    dur = clip.duration
    return int(dur)


def get_video_file(video_files, video_id):
    for vid in video_files:
        if ".mp4" in vid and get_video_id(vid) == video_id:
            return vid
    return None


def get_video_id(f):
    file_parts_array = f.split('_')
    tmp_id = ''

    for file_part in file_parts_array:
        if '(' in file_part:
            start_index = file_part.index('(') + 1
            while not file_part[start_index] == ')':
                tmp_id += file_part[start_index]
                start_index += 1
    return int(tmp_id)
