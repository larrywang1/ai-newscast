# Two Host AI Newscast

Generate a short podcast with two customized AI hosts with today's top news.


# Requirements

Python 3.12.7

.env file with keys for NewsAPI, OpenAI, Cartesia TTS

personas.json file with specifications of name, personality, style, voice for the two hosts  
For voice, you may use the following ids or find other ones for the Sonic 3 model of Cartesia:  
    Stable, realistic male: "228fca29-3a0a-435c-8728-5cb483251068"  
    Stable, realistic female: "f786b574-daa5-4673-aa0c-cbe3e8534c02"  
    Expressive, emotive male: "c961b81c-a935-4c17-bfb3-ba2239de8c2f"  
    Expressive, emotive female: "6ccbfb76-1fc6-48f7-b71d-91ac6298247b"

ffmpeg

# Installation

1. Clone the repository:  
git clone https://github.com/larrywang1/ai-newscast.git  
cd ai-newscast

2. Optional: Create a virtual environment:  
python -m venv venv  
venv\Scripts\activate

3. Install dependencies  
pip install -r requirements.txt

4. Create a .env file with your keys and a personas.json file with your desired attributes


# Usage

Run the following command in the command line:

python main.py --personas personas.json --minutes (integer) --topics (topic1,topic2) --profanity (boolean value)  
--personas : path to personas.json with host attributes  
--minutes : target length of episode in minutes, default is 5 minutes  
--topics : comma separated list of topic  
--profanity : whether the profanity filter is on or off, default is off


# Outputs

All outputted files are written to /out:

episode.mp3 - mixed podcast audio  
transcript.jsonl - JSONL transcript with speaker, text, and source  
show_notes.md - list of sources with indice and notes  
transcript.vtt - transcript with timestamps