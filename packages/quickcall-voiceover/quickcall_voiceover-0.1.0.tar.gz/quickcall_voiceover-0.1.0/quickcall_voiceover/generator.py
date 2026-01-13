"""Voice-over generation using Piper TTS."""

from __future__ import annotations

import json
import subprocess
import sys
import wave
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rich.console import Console


def load_config(config_path: Path) -> dict:
    """Load configuration from JSON file."""
    with open(config_path, "r") as f:
        return json.load(f)


def ensure_voice_downloaded(model: str, models_dir: Path, console: Console | None = None) -> Path:
    """Download voice model if not present, return path to onnx file."""
    from piper.download_voices import download_voice

    model_file = models_dir / f"{model}.onnx"
    if model_file.exists():
        if console:
            console.print(f"[green]✓[/green] Voice model cached: [cyan]{model}[/cyan]")
        else:
            print(f"Voice model already downloaded: {model}")
        return model_file

    if console:
        console.print(f"[yellow]↓[/yellow] Downloading voice model: [cyan]{model}[/cyan]...")
    else:
        print(f"Downloading voice model: {model}...")

    download_voice(model, models_dir)

    if console:
        console.print(f"[green]✓[/green] Downloaded to: [dim]{models_dir}[/dim]")
    else:
        print(f"Downloaded to: {models_dir}")

    return model_file


def generate_segment(
    text: str,
    output_path: Path,
    model_path: Path,
    length_scale: float = 1.0,
    noise_scale: float = 0.667,
    noise_w: float = 0.8,
    sentence_silence: float = 0.5,
) -> bool:
    """Generate a single audio segment using piper CLI."""
    cmd = [
        sys.executable,
        "-m",
        "piper",
        "--model",
        str(model_path),
        "--output_file",
        str(output_path),
        "--length_scale",
        str(length_scale),
        "--noise_scale",
        str(noise_scale),
        "--noise_w",
        str(noise_w),
        "--sentence_silence",
        str(sentence_silence),
    ]

    try:
        subprocess.run(
            cmd,
            input=text,
            text=True,
            capture_output=True,
            check=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error generating audio: {e.stderr}")
        return False


def combine_wav_files(
    wav_files: list[Path], output_path: Path, console: Console | None = None
) -> bool:
    """Combine multiple WAV files into a single file."""
    if not wav_files:
        return False

    try:
        # Read first file to get parameters
        with wave.open(str(wav_files[0]), "rb") as first:
            params = first.getparams()

        # Combine all files
        with wave.open(str(output_path), "wb") as output:
            output.setparams(params)
            for wav_file in wav_files:
                with wave.open(str(wav_file), "rb") as w:
                    output.writeframes(w.readframes(w.getnframes()))

        return True
    except Exception as e:
        msg = f"Error combining WAV files: {e}"
        if console:
            console.print(f"[red]{msg}[/red]")
        else:
            print(msg)
        return False


def generate_from_text(
    lines: list[str],
    voice: str = "en_US-hfc_male-medium",
    output_dir: Path | None = None,
    models_dir: Path | None = None,
    combine: bool = False,
    combined_filename: str = "combined_voiceover.wav",
    console: Console | None = None,
) -> bool:
    """
    Generate voice-over audio from a list of text lines.

    Args:
        lines: List of text strings, each becomes a segment
        voice: Voice model name
        output_dir: Directory for output files (default: ./output)
        models_dir: Directory for voice models (default: ./models)
        combine: If True, also create a single combined audio file
        combined_filename: Name for the combined output file
        console: Rich console for styled output

    Returns:
        True if all segments generated successfully
    """
    # Setup directories
    if output_dir is None:
        output_dir = Path.cwd() / "output"
    if models_dir is None:
        models_dir = Path.cwd() / "models"

    output_dir = Path(output_dir)
    models_dir = Path(models_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    models_dir.mkdir(parents=True, exist_ok=True)

    # Download voice model if needed
    model_path = ensure_voice_downloaded(voice, models_dir, console)

    if console:
        console.print(f"\n[bold]Generating {len(lines)} segments...[/bold]\n")

    # Generate each segment
    success_count = 0
    generated_files: list[Path] = []

    for i, text in enumerate(lines, 1):
        segment_id = f"segment_{i:03d}"
        output_file = output_dir / f"{segment_id}.wav"

        display_text = text[:40] + "..." if len(text) > 40 else text
        if console:
            console.print(f"  [{i}/{len(lines)}] {display_text}")

        success = generate_segment(
            text=text,
            output_path=output_file,
            model_path=model_path,
        )

        if success:
            if console:
                console.print(f"       [green]✓[/green] {output_file.name}")
            success_count += 1
            generated_files.append(output_file)
        else:
            if console:
                console.print("       [red]✗ FAILED[/red]")

    if console:
        console.print(f"\n[bold]Completed:[/bold] {success_count}/{len(lines)} segments")

    # Combine files if requested
    if combine and generated_files:
        combined_path = output_dir / combined_filename
        if console:
            console.print(f"\n[yellow]⊕[/yellow] Combining into: [cyan]{combined_path}[/cyan]")

        if combine_wav_files(generated_files, combined_path, console):
            if console:
                console.print("[green]✓[/green] Combined file saved")
        else:
            if console:
                console.print("[red]✗ Failed to create combined file[/red]")

    return success_count == len(lines)


def generate_voiceover(
    config_path: Path,
    output_dir: Path | None = None,
    models_dir: Path | None = None,
    combine: bool = False,
    combined_filename: str = "combined_voiceover.wav",
    console: Console | None = None,
) -> bool:
    """
    Generate voice-over audio from a config file.

    Args:
        config_path: Path to the JSON configuration file
        output_dir: Directory for output files (default: ./output)
        models_dir: Directory for voice models (default: ./models)
        combine: If True, also create a single combined audio file
        combined_filename: Name for the combined output file
        console: Rich console for styled output

    Returns:
        True if all segments generated successfully
    """
    config_path = Path(config_path)

    # Setup directories
    if output_dir is None:
        output_dir = Path.cwd() / "output"
    if models_dir is None:
        models_dir = Path.cwd() / "models"

    output_dir = Path(output_dir)
    models_dir = Path(models_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    models_dir.mkdir(parents=True, exist_ok=True)

    # Load config
    if console:
        console.print(f"[dim]Loading config: {config_path}[/dim]")
    config = load_config(config_path)

    # Voice settings
    voice = config.get("voice", {})
    model_name = voice.get("model", "en_US-hfc_male-medium")
    output_format = config.get("output", {}).get("format", "wav")

    # Download voice model if needed
    model_path = ensure_voice_downloaded(model_name, models_dir, console)

    segments = config.get("segments", [])

    if console:
        console.print(f"[dim]Output: {output_dir}[/dim]")
        console.print(f"\n[bold]Generating {len(segments)} segments...[/bold]\n")
    else:
        print(f"Using voice model: {model_path}")
        print(f"Output directory: {output_dir}")
        print(f"Total segments: {len(segments)}")
        print("-" * 50)

    # Generate each segment
    success_count = 0
    generated_files: list[Path] = []

    for i, segment in enumerate(segments, 1):
        segment_id = segment.get("id", f"segment_{i:03d}")
        text = segment.get("text", "")
        output_file = output_dir / f"{segment_id}.{output_format}"

        display_text = text[:40] + "..." if len(text) > 40 else text

        if console:
            console.print(f"  [{i}/{len(segments)}] [cyan]{segment_id}[/cyan]")
            console.print(f"       {display_text}")
        else:
            print(f"Generating: {segment_id}")
            print(f"  Text: {display_text}")

        success = generate_segment(
            text=text,
            output_path=output_file,
            model_path=model_path,
            length_scale=voice.get("length_scale", 1.0),
            noise_scale=voice.get("noise_scale", 0.667),
            noise_w=voice.get("noise_w", 0.8),
            sentence_silence=voice.get("sentence_silence", 0.5),
        )

        if success:
            if console:
                console.print(f"       [green]✓[/green] {output_file.name}")
            else:
                print(f"  Saved: {output_file}")
            success_count += 1
            generated_files.append(output_file)
        else:
            if console:
                console.print("       [red]✗ FAILED[/red]")
            else:
                print("  FAILED!")

    if console:
        console.print(f"\n[bold]Completed:[/bold] {success_count}/{len(segments)} segments")
    else:
        print("-" * 50)
        print(f"Completed: {success_count}/{len(segments)} segments")

    # Combine files if requested
    if combine and generated_files:
        combined_path = output_dir / combined_filename

        if console:
            console.print(f"\n[yellow]⊕[/yellow] Combining into: [cyan]{combined_path}[/cyan]")
        else:
            print("-" * 50)
            print(f"Combining {len(generated_files)} files into: {combined_path}")

        if combine_wav_files(generated_files, combined_path, console):
            if console:
                console.print("[green]✓[/green] Combined file saved")
            else:
                print(f"Combined file saved: {combined_path}")
        else:
            if console:
                console.print("[red]✗ Failed to create combined file[/red]")
            else:
                print("Failed to create combined file")

    all_success = success_count == len(segments)
    if not console:
        if all_success:
            print("All voice-over segments generated successfully!")
        else:
            print("Some segments failed. Check errors above.")

    return all_success
