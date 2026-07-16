from pathlib import Path
import html
import re
import sys
import zipfile

path = Path(sys.argv[1])
with zipfile.ZipFile(path) as archive:
    slides = sorted(
        [name for name in archive.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)],
        key=lambda name: int(re.search(r"\d+", name).group()),
    )
    for index, name in enumerate(slides, 1):
        xml = archive.read(name).decode("utf-8")
        text = [html.unescape(value) for value in re.findall(r"<a:t>(.*?)</a:t>", xml)]
        print(f"--- SLIDE {index} ---")
        print(" | ".join(text))
