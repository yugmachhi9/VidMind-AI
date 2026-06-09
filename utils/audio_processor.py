import yt_dlp
import os
import subprocess

DOWNLOAD_DIR = "downloades"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def download_youtube_audio(url: str) -> str:
    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        file_path = ydl.prepare_filename(info)

    wav_path = file_path.rsplit(".", 1)[0] + ".wav"

    # Convert using ffmpeg (Render-safe)
    subprocess.run([
        "ffmpeg", "-y",
        "-i", file_path,
        "-ar", "16000",
        "-ac", "1",
        wav_path
    ])

    return wav_path


def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list:
    import wave

    chunks = []
    chunk_seconds = chunk_minutes * 60

    cmd = [
        "ffmpeg", "-i", wav_path,
        "-f", "segment",
        "-segment_time", str(chunk_seconds),
        "-ar", "16000",
        "-ac", "1",
        os.path.join(DOWNLOAD_DIR, "chunk_%03d.wav")
    ]

    subprocess.run(cmd)

    for file in sorted(os.listdir(DOWNLOAD_DIR)):
        if file.startswith("chunk_") and file.endswith(".wav"):
            chunks.append(os.path.join(DOWNLOAD_DIR, file))

    return chunks


def process_input(source: str) -> list:
    if source.startswith("http"):
        print("Downloading YouTube audio...")
        wav_path = download_youtube_audio(source)
    else:
        wav_path = source

    print("Chunking audio...")
    return chunk_audio(wav_path)