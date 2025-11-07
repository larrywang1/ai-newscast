import os
import json
import time
import argparse
import re
from news import fetch_stories
from dotenv import load_dotenv
import openai
from cartesia import Cartesia
from pydub import AudioSegment

# this loads the environment (for safe storage of api keys)
load_dotenv()

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
CARTESIA_KEY = os.getenv("CARTESIA_API_KEY")
client = Cartesia(api_key=os.getenv("CARTESIA_API_KEY"))

# makes sure that the out folder exists
os.makedirs("out", exist_ok=True)

# parses arguments based on the example - added profanity argument
parser = argparse.ArgumentParser()
parser.add_argument("--personas", required=True)
parser.add_argument("--minutes", type=int, default=5)
parser.add_argument("--topics", default="")
parser.add_argument("--profanity", type=bool, default=False)
args = parser.parse_args()

# opens the personas.json file
with open(args.personas, "r") as file:
    personas = json.load(file)

HOST_1 = personas["hosts"][0]
HOST_2 = personas["hosts"][1]

# gets stories using the news.py script
print("Getting stories...")
stories = fetch_stories(args.topics, max_stories=6)
if not stories:
    print("No stories fetched. Exiting.")
    exit()

print("Completed.", end="", flush=True)
openai.api_key = OPENAI_KEY

def generate_script(stories, host1, host2):
    # creates prompts for the system and the user 
    system_prompt = f"""
You are generating a dialogue for a 2-host podcast.
Host1: {host1['name']}, personality: {host1['personality']}
Host2: {host2['name']}, personality: {host2['personality']}
Ensure each host is distinct with different vocabulary, energy, and POV. 
Use only these stories as sources. Annotate each line with [src: i] where i is the story index.
Make sure there there are no invented details.
Alternate turns, light disagreement and callbacks, smart accessible tone.
Make the dialogue decently fast paced, and relatively short, with more banter.
Generate between {str(args.minutes * 4)} - {str(args.minutes * 5)} lines of dialogue.
Generate between {str(args.minutes * 130)} - {str(args.minutes * 150)} words in the dialogue.
Profanity filter is set to {args.profanity}.
"""
    stories_text = "\n".join([f"[{s['index']}] {s['title']}: {s['summary']}" for s in stories])
    
    user_prompt = f"""
Stories:
{stories_text}

Create a dialogue where hosts alternate turns as JSON array:
[
  {{"speaker": "HostName", "text": "...", "src": i }},
]
Each line must be grounded in the fetched facts (no invented details) and annotated with `[src: i]` indices. 
Make sure that i is the index of the story and not the link.
Tone: smart, accessible, no clickbait; add a one‑sentence disclaimer if topics are sensitive.
Do not impersonate real voices; use “celebrity‑style” as personality, not literal cloning.
No medical/financial advice; avoid slurs/harassment.

"""
    response = openai.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role":"system","content":system_prompt},
                  {"role":"user","content":user_prompt}],
        temperature=0.8
    )
    text = response.choices[0].message.content
    return json.loads(text)

print("\nGenerating script...")
script = generate_script(stories, HOST_1, HOST_2)
print("Completed.", end="", flush=True)

# writes the script to file - "w" is write, utf-8 for safety - unicode
print("\nWriting script to file...")
with open("out/transcript.jsonl", "w", encoding="utf-8") as f:
    for line in script:
        f.write(json.dumps(line) + "\n")

with open("out/show_notes.md", "w", encoding="utf-8") as f:
    f.write("Show Notes\n\n")
    for s in stories:
        # default values if not available
        title = s.get("title", "Untitled Story")
        url = s.get("url", "#")
        source = s.get("source", "Unknown Source")
        summary = s.get("summary", "No summary available.")
        
        f.write(f"- [{title}]({url}) ({source}): {summary}\n")
    
    f.write("\n*Parody/transformative use. Not financial/medical advice.*\n")
print("Completed.", end="", flush=True)

# create variable for the full episode and variables for the transcript.vtt
episode_audio = AudioSegment.silent(duration=0) 
timestamps = [] 
current_time = 0.0
# total lines just for console display purposes
total_lines = len(script)

# enumerate for the line counter
for i, line in enumerate(script, start=1):
    voice_id = HOST_1['voice'] if line['speaker'] == HOST_1['name'] else HOST_2['voice']
    # remove the [src:i] from the text
    clean_text = re.sub(r'\[src:\s*\d+\]', '', line["text"]).strip()
    
    audio_chunks = client.tts.bytes(
        model_id="sonic-3",
        transcript=clean_text,
        voice={"mode": "id", "id": voice_id},
        output_format={
            "container": "wav",
            "sample_rate": 44100,
            "encoding": "pcm_s16le",  # compatible with pydub wav to mp3
        }
    )

    # save as a temporary wav
    temp_filename = "out/temp.wav"
    with open(temp_filename, "wb") as f:
        for chunk in audio_chunks:
            f.write(chunk)

    # load from pydub
    segment = AudioSegment.from_wav(temp_filename)
    os.remove(temp_filename)

    # append to episode.mp3
    episode_audio += segment
    segment_duration_sec = segment.duration_seconds
    pause_duration = 1.0 
    episode_audio += AudioSegment.silent(duration=pause_duration * 1000)

    # add stuff to timestamps
    timestamps.append({
        "start": current_time,
        "end": current_time + segment_duration_sec,
        "speaker": line['speaker'],
        "text": line['text'],
        "src": line['src']
    })
    current_time += segment_duration_sec + pause_duration

    print(f"\rProcessing text to speech: {i}/{total_lines}", end="", flush=True)

# export mp3
episode_filename = "out/episode.mp3"
episode_audio.export(episode_filename, format="mp3")

# save the vtt
vtt_filename = "out/episode.vtt"
with open(vtt_filename, "w", encoding="utf-8") as f:
    f.write("Episode Transcript\n\n")
    for t in timestamps:
        start = time.strftime('%H:%M:%S', time.gmtime(t["start"]))
        end = time.strftime('%H:%M:%S', time.gmtime(t["end"]))
        f.write(f"{start} --> {end}\n")
        f.write(f"{t['speaker']}: {t['text']}\n\n")

print("\nPodcast generation complete.")