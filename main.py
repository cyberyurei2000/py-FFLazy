# Copyright (c) cyberyurei2000 2024-2026
# Released under the BSD 3-Clause License
# https://opensource.org/license/bsd-3-clause

from pathlib import Path
import subprocess
import yaml


def run_ffmpeg(cmd: list[str]) -> None:
    """Run the command through ffmpeg."""
    print(*cmd)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"Success: {result.stderr[-200:] if result.stderr else 'OK'}")
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error (code {e.returncode}): {e.stderr}")
        raise


def get_config(data: dict) -> list:
    config = []
    audio = ["-map"]
    subtitles = ["-map"]
    fonts = ["-map", "0:t"]

    if data["config"][0]["audio"]:
        if data["config"][0]["num"] == 0:
            audio.append("0:a")
        else:
            audio.append(f"0:a:{data["config"][0]["num"] - 1}")
        config.extend(audio)

    if data["config"][1]["subtitles"]:
        if data["config"][0]["num"] == 0:
            subtitles.append("0:s")
        else:
            subtitles.append(f"0:s:{data["config"][0]["num"] - 1}")
        config.extend(subtitles)

    if data["config"][2]["fonts"]:
        config.extend(fonts)

    return config


def get_title(data: dict, counter: int) -> str:
    """Get the content's title."""
    episode = data["episodes"][counter]
    return f"{data["maintitle"]} - {episode["title"]}"


def get_filename(data: dict, counter: int) -> str:
    """Get the content's final filename."""
    episode = data["episodes"][counter]
    return f"{data["maintitle"]} - {episode["code"]} - {episode["title"]}"


def set_anime(data: dict) -> None:
    files = Path(data["dir"])

    for counter, file in enumerate(f for f in files.iterdir() if f.is_file()):
        if counter >= len(data["episodes"]):
            continue

        #cmd = [
        #    "ffmpeg", "-i", str(file), "-metadata", f"title={get_title(data, counter)}",
        #    "-map", "0:v", "-map", "0:a:0", "-map", "0:s:0", "-map", "0:t", "-c", "copy",
        #    str(files / "final" / f"{get_filename(data, counter)}.mkv")
        #]

        config = get_config(data)
        cmd = [
            "ffmpeg", "-i", str(file), "-metadata", f"title={get_title(data, counter)}",
            "-map", "0:v", "-c", "copy", str(files / "final" / f"{get_filename(data, counter)}.mkv")
        ]

        cmd[7:7] = config
        run_ffmpeg(cmd)


def set_series(data: dict) -> None:
    files = Path(data["dir"])

    for counter, file in enumerate(f for f in files.iterdir() if f.is_file()):
        if counter >= len(data["episodes"]):
            continue

        config = get_config(data)
        cmd = [
            "ffmpeg", "-i", str(file), "-metadata", f"title={get_title(data, counter)}",
            "-c:v", "copy", "-c", "copy", str(files / "final" / f"{get_filename(data, counter)}.mkv")
        ]

        cmd[7:7] = config
        run_ffmpeg(cmd)


def globo_aspectratio_fix(data: dict) -> None:
    files = Path(data["dir"])

    for counter, file in enumerate(f for f in files.iterdir() if f.is_file()):
        strfile = str(Path(file).stem)
        lenght = len(strfile)
        if strfile.endswith("A"):
            string = strfile[lenght - 4:]
            while "0" in string[0]:
                s = list(string)
                s.pop(0)
                string = "".join(s)
            chapter = string
        else:
            string = strfile[lenght - 3:]
            while "0" in string[0]:
                s = list(string)
                s.pop(0)
                string = "".join(s)
            chapter = string

        title = f"{data['maintitle']} - Capítulo {chapter}"
        filename = Path(file).stem

        # ffmpeg -i video.ts -vf setsar=1,setdar=4/3 -aspect 4:3 -c:a copy video-fixed.mkv
        cmd = [
            "ffmpeg", "-i", str(file), "-metadata", f"title={title}", "-vf", "setsar=1,setdar=4/3",
            "-aspect", "4:3", "-c:a", "copy", str(files / "final" / f"{filename}.mkv")
        ]
        run_ffmpeg(cmd)


def main():
    with open("./data.yml", "r") as stream:
        try:
            DATA = yaml.safe_load(stream)
            TYPE = DATA["type"]
            match TYPE:
                case "anime":
                    set_anime(DATA)
                case "series":
                    set_series(DATA)
        except yaml.YAMLError as err:
            print(err)


if __name__ == "__main__":
    main()
