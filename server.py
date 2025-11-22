from flask import Flask, request, jsonify, send_file
import yt_dlp
import os
import uuid

app = Flask(__name__)

# Temporary download folder
TEMP_DIR = "tmp_downloads"
os.makedirs(TEMP_DIR, exist_ok=True)

@app.get("/mp4")
def mp4():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Missing URL"}), 400

    # Extract metadata without downloading
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        # Find the best MP4 format
        mp4_format = None
        for f in info.get("formats", []):
            if f.get("ext") == "mp4" and f.get("url"):
                mp4_format = f["url"]

        if not mp4_format:
            return jsonify({"error": "No MP4 format available"}), 404

        return jsonify({"download": mp4_format})
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.get("/mp3")
def mp3():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Missing URL"}), 400

    # Unique filename
    file_id = str(uuid.uuid4())
    output_path = os.path.join(TEMP_DIR, f"{file_id}.mp3")

    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "no_warnings": True,
        "outtmpl": output_path,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ]
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Send MP3 file to user
        return send_file(output_path, as_attachment=True, download_name="audio.mp3")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # Clean up after send_file finishes
        try:
            if os.path.exists(output_path):
                os.remove(output_path)
        except:
            pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)