"""Command-line interface for QuickCall VoiceOver."""

import argparse
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from quickcall_voiceover.generator import generate_from_text, generate_voiceover

console = Console()

# Popular voice models with descriptions
POPULAR_VOICES = {
    "en_US-hfc_male-medium": ("Male (US)", "Clear male voice, medium quality"),
    "en_US-hfc_female-medium": ("Female (US)", "Clear female voice, medium quality"),
    "en_US-amy-medium": ("Amy (US)", "Natural female voice"),
    "en_US-joe-medium": ("Joe (US)", "Natural male voice"),
    "en_US-ryan-high": ("Ryan (US)", "High quality male voice"),
    "en_US-lessac-high": ("Lessac (US)", "High quality female voice"),
    "en_GB-alan-medium": ("Alan (UK)", "British male voice"),
    "en_GB-alba-medium": ("Alba (UK)", "British female voice"),
    "en_GB-cori-high": ("Cori (UK)", "High quality British female"),
}

DEFAULT_VOICE = "en_US-hfc_male-medium"


def show_banner() -> None:
    """Display the CLI banner."""
    console.print()
    console.print(
        Panel(
            "[bold cyan]QuickCall VoiceOver[/bold cyan]\n"
            "[dim]Config-driven TTS powered by Piper[/dim]",
            border_style="cyan",
            padding=(0, 2),
        )
    )
    console.print()


def show_voice_table() -> None:
    """Display available voices in a table."""
    table = Table(title="Popular Voice Models", show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim", width=3)
    table.add_column("Model ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Description", style="white")

    for i, (model_id, (name, desc)) in enumerate(POPULAR_VOICES.items(), 1):
        default_mark = " [yellow](default)[/yellow]" if model_id == DEFAULT_VOICE else ""
        table.add_row(str(i), model_id, name + default_mark, desc)

    console.print(table)
    console.print()
    console.print("[dim]Browse all voices: https://rhasspy.github.io/piper-samples/[/dim]")
    console.print()


def select_voice() -> str:
    """Interactive voice selection."""
    show_voice_table()

    choice = Prompt.ask(
        "[bold]Select a voice[/bold]",
        choices=[str(i) for i in range(1, len(POPULAR_VOICES) + 1)] + ["custom"],
        default="1",
    )

    if choice == "custom":
        return Prompt.ask("[bold]Enter custom model ID[/bold]", default=DEFAULT_VOICE)

    voice_list = list(POPULAR_VOICES.keys())
    return voice_list[int(choice) - 1]


def interactive_text_mode() -> int:
    """Interactive text-based voice-over generation."""
    show_banner()

    console.print(
        Panel(
            "[bold]Text Mode[/bold]\n\n"
            "Generate voice-over from text directly.\n"
            "Each line becomes a separate audio segment.",
            title="Mode",
            border_style="blue",
        )
    )
    console.print()

    # Select voice
    voice = select_voice()
    console.print(f"\n[green]✓[/green] Selected voice: [cyan]{voice}[/cyan]\n")

    # Confirm before proceeding
    if not Confirm.ask(f"[bold]Use voice model '[cyan]{voice}[/cyan]'?[/bold]", default=True):
        voice = select_voice()

    # Get output settings
    output_dir = Path(Prompt.ask("[bold]Output directory[/bold]", default="./output"))
    combine = Confirm.ask("[bold]Combine all segments into one file?[/bold]", default=False)

    # Get text input
    console.print("\n[bold]Enter your text[/bold] (one segment per line, empty line to finish):\n")

    lines = []
    while True:
        try:
            line = input()
            if not line:
                break
            lines.append(line)
        except EOFError:
            break

    if not lines:
        console.print("[red]No text provided. Exiting.[/red]")
        return 1

    console.print(f"\n[green]✓[/green] Got {len(lines)} segments\n")

    # Generate
    with console.status("[bold green]Generating voice-over..."):
        success = generate_from_text(
            lines=lines,
            voice=voice,
            output_dir=output_dir,
            combine=combine,
            console=console,
        )

    if success:
        console.print(
            Panel(
                "[bold green]✓ All segments generated successfully![/bold green]",
                border_style="green",
            )
        )
    else:
        console.print(Panel("[bold red]✗ Some segments failed[/bold red]", border_style="red"))

    return 0 if success else 1


def config_mode(args: argparse.Namespace) -> int:
    """Config file based generation."""
    show_banner()

    console.print(
        Panel(
            f"[bold]Config Mode[/bold]\n\n"
            f"Config: [cyan]{args.config}[/cyan]\n"
            f"Output: [cyan]{args.output or './output'}[/cyan]\n"
            f"Combine: [cyan]{args.combine}[/cyan]",
            title="Settings",
            border_style="blue",
        )
    )
    console.print()

    if not args.config.exists():
        console.print(f"[red]Error: Config file not found: {args.config}[/red]")
        return 1

    success = generate_voiceover(
        config_path=args.config,
        output_dir=args.output,
        models_dir=args.models,
        combine=args.combine,
        combined_filename=args.combined_name,
        console=console,
    )

    if success:
        console.print(
            Panel(
                "[bold green]✓ All segments generated successfully![/bold green]",
                border_style="green",
            )
        )
    else:
        console.print(Panel("[bold red]✗ Some segments failed[/bold red]", border_style="red"))

    return 0 if success else 1


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="quickcall-voiceover",
        description="Generate voice-over audio using Piper TTS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  quickcall-voiceover config.json              Generate from config file
  quickcall-voiceover config.json --combine    Generate and combine into one file
  quickcall-voiceover --text                   Interactive text mode
  quickcall-voiceover --voices                 Show available voices
        """,
    )
    parser.add_argument(
        "config",
        type=Path,
        nargs="?",
        help="Path to the JSON configuration file",
    )
    parser.add_argument(
        "-t",
        "--text",
        action="store_true",
        help="Interactive text mode: enter text line by line",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output directory for generated audio files (default: ./output)",
    )
    parser.add_argument(
        "-m",
        "--models",
        type=Path,
        default=None,
        help="Directory for voice models (default: ./models)",
    )
    parser.add_argument(
        "-c",
        "--combine",
        action="store_true",
        help="Also create a single combined audio file from all segments",
    )
    parser.add_argument(
        "--combined-name",
        type=str,
        default="combined_voiceover.wav",
        help="Filename for the combined output (default: combined_voiceover.wav)",
    )
    parser.add_argument(
        "--voices",
        action="store_true",
        help="Show available voice models and exit",
    )

    args = parser.parse_args()

    # Show voices and exit
    if args.voices:
        show_banner()
        show_voice_table()
        return 0

    # Text mode
    if args.text:
        return interactive_text_mode()

    # Config mode requires a config file
    if not args.config:
        parser.print_help()
        console.print("\n[yellow]Tip: Use --text for interactive text mode[/yellow]")
        return 1

    return config_mode(args)


if __name__ == "__main__":
    sys.exit(main())
