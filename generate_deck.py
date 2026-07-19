#!/usr/bin/env python3
"""
Reusable Anki Deck Generator

Reads a JSON file describing a deck and its cards, then produces an .apkg file.
Handles UTF-8 encoding properly for accented characters.

Usage:
    python generate_deck.py <input.json> [output.apkg] [--audio] [--voice VOICE]

JSON format:
{
    "deck_name": "My Deck",
    "deck_id": 1234567890,         // optional, auto-generated from name if omitted
    "model_id": 9876543210,        // optional, auto-generated from name if omitted
    "model_name": "Basic Card",    // optional
    "css": "...",                   // optional custom CSS
    "cards": [
        { "front": "...", "back": "..." },
        ...
    ]
}

Audio options:
    --audio         Generate TTS audio for each card and embed it in the .apkg
    --voice VOICE   edge-tts voice to use (default: zh-CN-XiaoxiaoNeural)
                    Run `edge-tts --list-voices` to see all available voices.
"""

import asyncio
import json
import hashlib
import re
import sys
import os
import tempfile

import genanki

try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False


DEFAULT_VOICE = "zh-CN-XiaoxiaoNeural"

DEFAULT_CSS = """\
.card {
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 24px;
    text-align: center;
    color: #333;
    background-color: #fff;
    padding: 20px;
}
.hint {
    font-size: 16px;
    color: #888;
    margin-top: 12px;
}
"""


def stable_id(name: str) -> int:
    """Generate a stable numeric ID from a string so decks are reproducible."""
    digest = hashlib.sha256(name.encode("utf-8")).hexdigest()
    return int(digest[:10], 16)


def extract_tts_text(back: str) -> str:
    """Extract speakable text from a 'Chinese characters (pinyin)' back field.

    Strips the parenthetical pinyin so TTS reads only the characters,
    producing cleaner pronunciation output.
    """
    match = re.match(r'^(.+?)\s*\(', back)
    if match:
        return match.group(1).strip()
    return back.strip()


def audio_filename(deck_name: str, index: int) -> str:
    """Build a unique, filesystem-safe audio filename for a card."""
    prefix = re.sub(r'[^a-zA-Z0-9]', '_', deck_name).lower()
    return f"{prefix}_{index:04d}.mp3"


# Because edge-tts sets limits for free users
AUDIO_BATCH_SIZE = 25 
AUDIO_BATCH_SLEEP = 1.0

async def _generate_all_audio(cards: list, deck_name: str, audio_dir: str, voice: str) -> list:
    """Generate one MP3 per card in batches. Returns list of file paths."""

    async def gen_one(text: str, path: str) -> None:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(path)

    paths = []
    tasks = []
    for i, card in enumerate(cards):
        text = extract_tts_text(card["back"])
        path = os.path.join(audio_dir, audio_filename(deck_name, i))
        paths.append(path)
        tasks.append(gen_one(text, path))

    for start in range(0, len(tasks), AUDIO_BATCH_SIZE):
        batch = tasks[start:start + AUDIO_BATCH_SIZE]
        await asyncio.gather(*batch)
        print(f"  {min(start + AUDIO_BATCH_SIZE, len(tasks))}/{len(tasks)} cards done...")
        if start + AUDIO_BATCH_SIZE < len(tasks):
            await asyncio.sleep(AUDIO_BATCH_SLEEP)

    return paths


def generate_audio(cards: list, deck_name: str, audio_dir: str, voice: str) -> list:
    """Synchronous wrapper around async audio generation."""
    return asyncio.run(_generate_all_audio(cards, deck_name, audio_dir, voice))


def build_deck(data: dict, audio_paths: list = None) -> tuple:
    """Build a genanki Deck. Returns (deck, media_files)."""
    deck_name = data["deck_name"]
    deck_id = data.get("deck_id", stable_id(deck_name))
    model_name = data.get("model_name", f"{deck_name} Model")
    model_id = data.get("model_id", stable_id(model_name))
    css = data.get("css", DEFAULT_CSS)

    model = genanki.Model(
        model_id,
        model_name,
        fields=[
            {"name": "Front"},
            {"name": "Back"},
        ],
        templates=[
            {
                "name": "Card 1",
                "qfmt": "{{Front}}",
                "afmt": '{{FrontSide}}<hr id="answer">{{Back}}',
            },
        ],
        css=css,
    )

    deck = genanki.Deck(deck_id, deck_name)

    for i, card in enumerate(data["cards"]):
        back = card["back"]
        if audio_paths and i < len(audio_paths):
            fname = os.path.basename(audio_paths[i])
            back = f"{back}[sound:{fname}]"

        note = genanki.Note(
            model=model,
            fields=[card["front"], back],
        )
        deck.add_note(note)

    return deck, (audio_paths or [])


def parse_args(argv: list) -> tuple:
    """Return (input_path, output_path, use_audio, voice)."""
    args = argv[1:]

    use_audio = "--audio" in args
    args = [a for a in args if a != "--audio"]

    voice = DEFAULT_VOICE
    if "--voice" in args:
        idx = args.index("--voice")
        if idx + 1 >= len(args):
            print("Error: --voice requires a voice name argument.")
            sys.exit(1)
        voice = args[idx + 1]
        args = args[:idx] + args[idx + 2:]

    if not args:
        print(f"Usage: {argv[0]} <input.json> [output.apkg] [--audio] [--voice VOICE]")
        sys.exit(1)

    input_path = args[0]
    if len(args) >= 2:
        output_path = args[1]
    else:
        base = os.path.splitext(os.path.basename(input_path))[0]
        output_path = f"{base}.apkg"

    return input_path, output_path, use_audio, voice


def main():
    input_path, output_path, use_audio, voice = parse_args(sys.argv)

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    audio_paths = None

    if use_audio:
        if not EDGE_TTS_AVAILABLE:
            print("Error: edge-tts is not installed. Run: pip install edge-tts")
            sys.exit(1)
        audio_dir = tempfile.mkdtemp()
        n = len(data["cards"])
        print(f"Generating audio for {n} cards using voice '{voice}'...")
        audio_paths = generate_audio(data["cards"], data["deck_name"], audio_dir, voice)
        print(f"Audio generation complete.")

    deck, media_files = build_deck(data, audio_paths)
    genanki.Package(deck, media_files=media_files).write_to_file(output_path)

    audio_note = f" with {len(media_files)} audio files" if media_files else ""
    print(f"Created {output_path} ({len(data['cards'])} cards{audio_note}).")


if __name__ == "__main__":
    main()
