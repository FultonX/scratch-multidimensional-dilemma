from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parent
GENERATED = ROOT / "assets" / "generated"

# Extract the original assets from the checked-in Scratch project.
subprocess.run(
    ["python", str(ROOT / "tools" / "extract_sb3.py")],
    check=True,
    cwd=ROOT,
)

images = sorted((GENERATED / "images").glob("*.png"))
audio = sorted((GENERATED / "audio").glob("*.wav"))

# Balance audio files across three independently extractable ZIP archives.
audio_groups = [[], [], []]
audio_sizes = [0, 0, 0]

for path in sorted(audio, key=lambda item: (-item.stat().st_size, item.name)):
    group = min(range(3), key=audio_sizes.__getitem__)
    audio_groups[group].append(path)
    audio_sizes[group] += path.stat().st_size

archives = [
    ("TheMultidirectionalDilemma-assets-images.zip", images),
    *[
        (f"TheMultidirectionalDilemma-assets-audio-{number:02}.zip", paths)
        for number, paths in enumerate(audio_groups, 1)
    ],
]

for filename, paths in archives:
    output = ROOT / filename
    with zipfile.ZipFile(
        output,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        for path in sorted(paths):
            archive.write(path, path.relative_to(ROOT))

    print(f"Created {output.name}: {len(paths)} files")