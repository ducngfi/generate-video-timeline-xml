import xml.etree.ElementTree as ET
import json
from xml.dom import minidom
import os

def create_clipitem(id, name, duration, start, end, in_point, out_point, file_id, video_file_url, media_type, timebase):
    clipitem = ET.Element('clipitem', id=id)
    ET.SubElement(clipitem, 'name').text = name
    ET.SubElement(clipitem, 'duration').text = str(duration)
    
    rate = ET.SubElement(clipitem, 'rate')
    ET.SubElement(rate, 'timebase').text = str(timebase)
    ET.SubElement(rate, 'ntsc').text = 'TRUE'
    
    ET.SubElement(clipitem, 'start').text = str(start)
    ET.SubElement(clipitem, 'end').text = str(end)
    ET.SubElement(clipitem, 'enabled').text = 'TRUE'
    ET.SubElement(clipitem, 'in').text = str(in_point)
    ET.SubElement(clipitem, 'out').text = str(out_point)
    
    file_element = ET.SubElement(clipitem, 'file', id=file_id)
    ET.SubElement(file_element, 'duration').text = str(duration)  # Set to duration
    
    file_rate = ET.SubElement(file_element, 'rate')
    ET.SubElement(file_rate, 'timebase').text = str(timebase)
    ET.SubElement(file_rate, 'ntsc').text = 'TRUE'
    
    ET.SubElement(file_element, 'name').text = name
    ET.SubElement(file_element, 'pathurl').text = video_file_url
    
    timecode = ET.SubElement(file_element, 'timecode')
    ET.SubElement(timecode, 'string').text = '00:00:00:00'
    ET.SubElement(timecode, 'displayformat').text = 'DF'  # Drop Frame
    timecode_rate = ET.SubElement(timecode, 'rate')
    ET.SubElement(timecode_rate, 'timebase').text = str(timebase)
    ET.SubElement(timecode_rate, 'ntsc').text = 'TRUE'
    
    media_element = ET.SubElement(file_element, 'media')
    
    if media_type == 'video':
        video_element = ET.SubElement(media_element, 'video')
        samplecharacteristics = ET.SubElement(video_element, 'samplecharacteristics')
        ET.SubElement(samplecharacteristics, 'width').text = '1920'
        ET.SubElement(samplecharacteristics, 'height').text = '1080'
        rate = ET.SubElement(samplecharacteristics, 'rate')
        ET.SubElement(rate, 'timebase').text = str(timebase)
        ET.SubElement(rate, 'ntsc').text = 'TRUE'
    else:
        audio_element = ET.SubElement(media_element, 'audio')
        ET.SubElement(audio_element, 'channelcount').text = '2'
        
        sourcetrack = ET.SubElement(clipitem, 'sourcetrack')
        ET.SubElement(sourcetrack, 'mediatype').text = 'audio'
        ET.SubElement(sourcetrack, 'trackindex').text = '1'
    
    return clipitem

def pretty_print(element):
    rough_string = ET.tostring(element, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_string = reparsed.toprettyxml(indent="    ")
    return "\n".join([line for line in pretty_string.split("\n") if line.strip()])

def generate_timeline(video_file_path, json_file_path, xml_template_path, timebase=30, duration=9915):
    video_file_url = f'file://{video_file_path}'
    output_xml_path = os.path.join(os.path.dirname(video_file_path), 'Modified_Timeline_Template.xml')

    # Load and parse the JSON file
    with open(json_file_path) as f:
        data = json.load(f)

    # Load and parse the existing XML file
    tree = ET.parse(xml_template_path)
    root = tree.getroot()

    # Find the video and audio tracks
    sequence = root.find('sequence')
    sequence.find('rate').find('timebase').text = str(timebase)
    sequence.find('rate').find('ntsc').text = 'TRUE'
    sequence.find('duration').text = str(duration)

    timecode = sequence.find('timecode')
    timecode.find('rate').find('timebase').text = str(timebase)
    timecode.find('rate').find('ntsc').text = 'TRUE'
    timecode.find('displayformat').text = 'DF'  # Drop Frame

    media = sequence.find('media')
    video = media.find('video')
    audio = media.find('audio')

    # Update the format rate
    format_samplecharacteristics = video.find('format').find('samplecharacteristics')
    format_samplecharacteristics.find('rate').find('timebase').text = str(timebase)
    format_samplecharacteristics.find('rate').find('ntsc').text = 'TRUE'

    # Find the track elements
    video_track = video.find('track')
    audio_track = audio.find('track')

    # Remove existing clipitems to start fresh
    for element in video_track.findall('clipitem'):
        video_track.remove(element)
    for element in audio_track.findall('clipitem'):
        audio_track.remove(element)

    # Add each spoken period as a video and audio clipitem
    for i, period in enumerate(data):
        start_frame = int(period['start'] * timebase)
        end_frame = int(period['end'] * timebase)
        duration_frames = int(period['duration'] * timebase)
        
        # Ensure the duration frames do not exceed the duration
        if end_frame > duration:
            end_frame = duration
            duration_frames = end_frame - start_frame
        
        # Create video clipitem
        video_clipitem = create_clipitem(
            id=f"spoken_video_{i}",
            name=f"Spoken Video {i}",
            duration=duration_frames,
            start=start_frame,
            end=end_frame,
            in_point=start_frame,
            out_point=end_frame,
            file_id=f"file_video_{i}",
            video_file_url=video_file_url,
            media_type='video',
            timebase=timebase
        )
        video_track.append(video_clipitem)
        
        # Create audio clipitem
        audio_clipitem = create_clipitem(
            id=f"spoken_audio_{i}",
            name=f"Spoken Audio {i}",
            duration=duration_frames,
            start=start_frame,
            end=end_frame,
            in_point=start_frame,
            out_point=end_frame,
            file_id=f"file_audio_{i}",
            video_file_url=video_file_url,
            media_type='audio',
            timebase=timebase
        )
        audio_track.append(audio_clipitem)

    # Write the modified and beautified XML back to a file
    with open(output_xml_path, 'w') as f:
        f.write(pretty_print(root))

def main():
    video_file_path = '/Users/duc/Desktop/Marketing_Insider/26_new_plan_for_youtube_channel/raw_video/20240721_C0942.MP4'
    json_file_path = '/Users/duc/Desktop/Marketing_Insider/26_new_plan_for_youtube_channel/raw_video/detect_non_silence.json'
    xml_template_path = 'Timeline_Template.xml'
    timebase = 30  # Change this to 24, 30, or 60 as needed
    duration = 9915  # Set both sequence duration and video duration to 9915 frames
    
    generate_timeline(video_file_path, json_file_path, xml_template_path, timebase, duration)

if __name__ == '__main__':
    main()
