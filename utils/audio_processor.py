import yt_dlp #that use for downloading audio from YouTube videos, allowing you to specify the desired format and quality of the downloaded audio.
from pydub import AudioSegment #that use for audio processing and manipulation, such as converting formats, changing sample rates, and splitting audio into chunks.
import os

DOWNLOAD_DIR = 'downloades'
os.makedirs(DOWNLOAD_DIR,exist_ok = True)

def download_youtube_audio(url :str) ->str:
    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info).replace(".webm", ".wav").replace(".m4a", ".wav") #yt_dlp will download the best audio format available, and then use FFmpeg to convert it to WAV format. The filename is adjusted to reflect the WAV extension after conversion.
    return filename



def convert_to_wav(input_path: str) -> str: #this for converting local audio/video files to WAV format.
    """Convert any audio/video file to WAV format using pydub."""
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"
    audio = AudioSegment.from_file(input_path) #load the input file (supports various formats like MP3, MP4, etc.)
    audio = audio.set_channels(1).set_frame_rate(16000) #16khz #convert to mono and set sample rate to 16kHz for better ASR performance
    audio.export(output_path, format="wav") #export the processed audio to WAV format because ASR models typically perform better with WAV files
    return output_path



def chunk_audio(wav_path : str , chunk_minutes : int = 10) -> list: #divided audio into chunks of specified duration (default is 10 minutes) and saves them as separate WAV files.
    audio = AudioSegment.from_wav(wav_path) #load the WAV file using pydub
    chunk_ms = chunk_minutes * 60 * 1000  #convert minutes to milliseconds

    chunks = []

    for i, start in enumerate(range(0,len(audio),chunk_ms)):
        chunk = audio[start : start + chunk_ms] #extract a chunk of audio from the specified start time to the end of the chunk duration
        chunk_path = f"{wav_path}_chunk_{i}.wav" # where i is the chunk index for example, if the original file is "audio.wav", the chunks will be named "audio_chunk_0.wav", "audio_chunk_1.wav", etc.
        chunk.export(chunk_path , format = "wav") #export the chunked audio to a new WAV file, which can then be processed by ASR models that may have limitations on input length.

        chunks.append(chunk_path)
    
    return chunks

def process_input(source: str) -> list:
    if source.startswith("http://") or source.startswith("https://"):
        print("Detected YouTube URL. Downloading audio...")
        wav_path = download_youtube_audio(source)
    else:
        print("Detected local file. Converting to WAV...")
        wav_path = convert_to_wav(source)

    print("Chunking audio...")
    chunks = chunk_audio(wav_path)
    print(f"Audio ready — {len(chunks)} chunk(s) created.")
    return chunks
