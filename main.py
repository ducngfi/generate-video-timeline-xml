import xml.etree.ElementTree as ET
import json
from xml.dom import minidom

# Provide the path to the video file
video_file_path = '/Users/duc/Videos/20240718_C0925_copy.MP4'
video_file_url = f'file://{video_file_path}'

# Load and parse the JSON file
with open('detect_non_silence.json') as f:
    data = json.load(f)

# Load and parse the existing XML file
tree = ET.parse('Timeline_Template.xml')
root = tree.getroot()

# Find the video and audio tracks
sequence = root.find('sequence')
media = sequence.find('media')
video = media.find('video')
audio = media.find('audio')

# Find the track elements
video_track = video.find('track')
audio_track = audio.find('track')

# Remove existing clipitems to start fresh
for element in video_track.findall('clipitem'):
    video_track.remove(element)
for element in audio_track.findall('clipitem'):
    audio_track.remove(element)

# Define a template for clipitem
def create_clipitem(id, name, duration, start, end, in_point, out_point, file_id, media_type):
    clipitem = ET.Element('clipitem', id=id)
    ET.SubElement(clipitem, 'name').text = name
    ET.SubElement(clipitem, 'duration').text = str(duration)
    
    rate = ET.SubElement(clipitem, 'rate')
    ET.SubElement(rate, 'timebase').text = '24'
    ET.SubElement(rate, 'ntsc').text = 'TRUE'
    
    ET.SubElement(clipitem, 'start').text = str(start)
    ET.SubElement(clipitem, 'end').text = str(end)
    ET.SubElement(clipitem, 'enabled').text = 'TRUE'
    ET.SubElement(clipitem, 'in').text = str(in_point)
    ET.SubElement(clipitem, 'out').text = str(out_point)
    
    file_element = ET.SubElement(clipitem, 'file', id=file_id)
    ET.SubElement(file_element, 'duration').text = str(duration)
    
    file_rate = ET.SubElement(file_element, 'rate')
    ET.SubElement(file_rate, 'timebase').text = '24'
    ET.SubElement(file_rate, 'ntsc').text = 'TRUE'
    
    ET.SubElement(file_element, 'name').text = name
    ET.SubElement(file_element, 'pathurl').text = video_file_url
    
    timecode = ET.SubElement(file_element, 'timecode')
    ET.SubElement(timecode, 'string').text = '00:00:00:00'
    ET.SubElement(timecode, 'displayformat').text = 'NDF'
    timecode_rate = ET.SubElement(timecode, 'rate')
    ET.SubElement(timecode_rate, 'timebase').text = '24'
    ET.SubElement(timecode_rate, 'ntsc').text = 'TRUE'
    
    media_element = ET.SubElement(file_element, 'media')
    
    if media_type == 'video':
        video_element = ET.SubElement(media_element, 'video')
        samplecharacteristics = ET.SubElement(video_element, 'samplecharacteristics')
        ET.SubElement(samplecharacteristics, 'width').text = '1920'
        ET.SubElement(samplecharacteristics, 'height').text = '1080'
    else:
        audio_element = ET.SubElement(media_element, 'audio')
        ET.SubElement(audio_element, 'channelcount').text = '2'
        
        sourcetrack = ET.SubElement(clipitem, 'sourcetrack')
        ET.SubElement(sourcetrack, 'mediatype').text = 'audio'
        ET.SubElement(sourcetrack, 'trackindex').text = '1'
    
    return clipitem

# Add each spoken period as a video and audio clipitem
for i, period in enumerate(data):
    start_frame = int(period['start'] * 24)
    end_frame = int(period['end'] * 24)
    duration_frames = int(period['duration'] * 24)
    
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
        media_type='video'
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
        media_type='audio'
    )
    audio_track.append(audio_clipitem)

# Function to pretty print XML without extra newlines
def pretty_print(element):
    rough_string = ET.tostring(element, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_string = reparsed.toprettyxml(indent="    ")
    return "\n".join([line for line in pretty_string.split("\n") if line.strip()])

# Write the modified and beautified XML back to a file
with open('Modified_Timeline_Template.xml', 'w') as f:
    f.write(pretty_print(root))
