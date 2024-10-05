import subprocess

def test_ffmpeg_ffprobe():
    ffmpeg_path = r"your\ffmpeg.exe"
    ffprobe_path = r"your\ffprobe.exe"

    try:
        # Test FFmpeg
        ffmpeg_result = subprocess.run([ffmpeg_path, "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"FFmpeg test output: {ffmpeg_result.stdout.decode()}")
        
        # Test FFprobe
        ffprobe_result = subprocess.run([ffprobe_path, "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"FFprobe test output: {ffprobe_result.stdout.decode()}")

        return True
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return False

# Run the test
if not test_ffmpeg_ffprobe():
    print("FFmpeg or FFprobe not found or cannot be executed.")
