# ===================================================================
# File for Audio Handling Steps 3.0, 3.1, and 3.2 from NLP2026 paper
# 3.0: Downloading Audio from YouTube
# 3.1: Singing Voice Separation
# 3.2: Melody Extraction
# ===================================================================
import yt_dlp
import subprocess
import shutil 
from pathlib import Path
import argparse
import sys

def youtube_download(url: str, output: str="../output"):
    """
    3.0: Function to download a song from youtube 
    (https://qiita.com/make_kae/items/03eb1a2e7971cf748d12)
    
    :param url: Youtube ID or youtube url for an audio file (song)
    :type url: str
    :param output: Download file placing folder
    :type output: str

    :return: output filepath (str)
    """
    output_path = Path(output)
    output_path.mkdir(parents=True, exist_ok=True)
    if not url.startswith("https://"): url = f"https://www.youtube.com/watch?v={url}" #assuming it is youtube id
    
    outtmpl = str(output_path / "youtube_audio.%(ext)s")
    options = {
        'format': 'bestaudio/best',
        'outtmpl': outtmpl, 
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',  
        }],
        'quiet': False,
        'ignoreerrors': True,
        'jsruntimes': [],  
    }
    print(f"Downloding audio file ({url}) to {output}")
    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download([url])
        
    print("Finished!")
    return str(output_path / "youtube_audio.wav")

def voice_separation(file_path: str):
    """
    3.1 Split singing voice from the audio file using default Demucs model (as of 2026/01/19 it is HT-Demucs)
    
    :param file_path: path to the audio file (.wav); return from def youtube_download()
    :type file_path: str

    :return: output filepath (str)
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"{file_path} is not found.")
    song_folder = file_path.parent
    cmd = [
        "demucs",
        "--two-stems=vocals",
        "--out", str(song_folder),
        str(file_path)
    ]

    print(f"Separating vocal/voice from {file_path}")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Demucs failed for {file_path}: {e}")


    # Demucs creates output in output/model_folder/separated_audio
    # Move from model_folder to output folder and delete unnecessary files
    model_folder = next(p for p in song_folder.iterdir() if p.is_dir())
    track_folder = next(p for p in model_folder.iterdir() if p.is_dir())
    vocals_file = track_folder / "vocals.wav"
    final_vocals_path = song_folder / "vocals.wav"

    shutil.move(str(vocals_file), str(final_vocals_path))
    print(f"Vocals saved to: {final_vocals_path}")
    shutil.rmtree(model_folder)

    return str(final_vocals_path)

def voice2freq(file_path: str):
    """
    3.2: Melody Extraction function from vocal file using crepe. 
    Outputs vocals.f0.csv file with columns [time, frequency, confidence] in the same directory as input file

    :param file_path: path to the vocal file (.wav); return from def voice_separation
    :type file_path: str
    """
    print(f"Extracting melody information of {file_path} using Crepe.")
    subprocess.run([sys.executable, '-m', 'crepe', file_path])
    output = Path(file_path).with_suffix(".f0.csv")
    return output

# audio_path = youtube_download("WTCryF1J54Y", "./output/")
# vocal_path = voice_separation(audio_path)
# voice2freq(vocal_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "-i", "--youtube",
        required=True,
        help="YouTube ID/URL"
    )
    parser.add_argument(
        "-o", "--output",
        default="./output",
        help="Output directory/folder"
    )

    args = parser.parse_args()

    audio_path = youtube_download(args.youtube, args.output)
    vocal_path = voice_separation(audio_path)
    freq_path = voice2freq(vocal_path)

    BOLD = "\033[1m"
    GREEN = "\033[32m"
    RESET = "\033[0m"
    print(f"{BOLD}{GREEN}AUDIO PROCESSING: DONE{RESET}")