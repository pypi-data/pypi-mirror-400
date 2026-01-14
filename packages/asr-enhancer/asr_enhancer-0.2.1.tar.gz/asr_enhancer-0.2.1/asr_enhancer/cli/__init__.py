"""
CLI Tool
========

Command-line interface for ASR Enhancement Layer.
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

import click


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """ASR Quality Enhancement Layer CLI.

    A tool for enhancing ASR transcripts with error detection,
    numeric reconstruction, and LLM-based polishing.
    """
    pass


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option(
    "--output", "-o",
    type=click.Path(),
    help="Output file path (default: stdout)",
)
@click.option(
    "--audio", "-a",
    type=click.Path(exists=True),
    help="Audio file for re-ASR processing",
)
@click.option(
    "--lexicon", "-l",
    type=click.Path(exists=True),
    help="Domain lexicon JSON file",
)
@click.option(
    "--format", "-f",
    type=click.Choice(["text", "json", "srt"]),
    default="text",
    help="Output format",
)
@click.option(
    "--config", "-c",
    type=click.Path(exists=True),
    help="Configuration file path",
)
def enhance(
    input_file: str,
    output: Optional[str],
    audio: Optional[str],
    lexicon: Optional[str],
    format: str,
    config: Optional[str],
):
    """Enhance a transcript file.

    INPUT_FILE should be a JSON file with the following structure:
    {
        "transcript": "raw transcript text",
        "word_timestamps": [{"word": "...", "start": 0.0, "end": 0.1}, ...],
        "word_confidences": [0.9, 0.8, ...]
    }
    """
    from ..core import EnhancementPipeline
    from ..utils import Config, load_config

    # Load config
    cfg = load_config(config) if config else Config()

    # Load input
    with open(input_file, "r") as f:
        data = json.load(f)

    # Load lexicon if provided
    domain_lexicon = None
    if lexicon:
        with open(lexicon, "r") as f:
            domain_lexicon = json.load(f)

    # Initialize pipeline
    pipeline = EnhancementPipeline(cfg)

    # Run enhancement
    async def run():
        return await pipeline.enhance(
            transcript=data["transcript"],
            word_timestamps=data["word_timestamps"],
            word_confidences=data["word_confidences"],
            audio_path=audio,
            domain_lexicon=domain_lexicon,
        )

    result = asyncio.run(run())

    # Format output
    if format == "text":
        output_content = result.enhanced_transcript
    elif format == "json":
        output_content = json.dumps({
            "original": result.original_transcript,
            "enhanced": result.enhanced_transcript,
            "confidence_improvement": result.confidence_improvement,
            "error_map": result.error_map,
            "diagnostics": result.diagnostics,
        }, indent=2)
    elif format == "srt":
        output_content = _generate_srt(result.word_timeline)
    else:
        output_content = result.enhanced_transcript

    # Write output
    if output:
        with open(output, "w") as f:
            f.write(output_content)
        click.echo(f"Output written to {output}")
    else:
        click.echo(output_content)


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option(
    "--output", "-o",
    type=click.Path(),
    help="Output file path (default: stdout)",
)
def analyze(input_file: str, output: Optional[str]):
    """Analyze a transcript without enhancement.

    Returns detected issues and recommendations.
    """
    from ..core import EnhancementPipeline
    from ..utils import Config

    # Load input
    with open(input_file, "r") as f:
        data = json.load(f)

    # Initialize pipeline
    pipeline = EnhancementPipeline(Config())

    # Run analysis
    async def run():
        return await pipeline.analyze_only(
            transcript=data["transcript"],
            word_timestamps=data["word_timestamps"],
            word_confidences=data["word_confidences"],
        )

    result = asyncio.run(run())

    # Format output
    output_content = json.dumps(result, indent=2)

    if output:
        with open(output, "w") as f:
            f.write(output_content)
        click.echo(f"Analysis written to {output}")
    else:
        click.echo(output_content)


@cli.command()
@click.option(
    "--host", "-h",
    default="0.0.0.0",
    help="Host to bind to",
)
@click.option(
    "--port", "-p",
    default=8000,
    type=int,
    help="Port to bind to",
)
@click.option(
    "--reload",
    is_flag=True,
    help="Enable auto-reload",
)
@click.option(
    "--config", "-c",
    type=click.Path(exists=True),
    help="Configuration file path",
)
def serve(host: str, port: int, reload: bool, config: Optional[str]):
    """Start the API server."""
    import os

    if config:
        os.environ["ASR_ENHANCER_CONFIG"] = config

    from ..api.main import run_server
    run_server(host=host, port=port, reload=reload)


@cli.command()
@click.option(
    "--output", "-o",
    type=click.Path(),
    default="config.json",
    help="Output path for config file",
)
def init(output: str):
    """Initialize a new configuration file."""
    from ..utils import Config

    config = Config()
    config_dict = config.to_dict()

    with open(output, "w") as f:
        json.dump(config_dict, f, indent=2)

    click.echo(f"Configuration written to {output}")


@cli.command()
def check():
    """Check system dependencies and configuration."""
    click.echo("Checking dependencies...")

    checks = []

    # Check Python version
    import sys
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    checks.append(("Python", py_version, sys.version_info >= (3, 11)))

    # Check required packages
    packages = [
        ("fastapi", "fastapi"),
        ("pydantic", "pydantic"),
        ("uvicorn", "uvicorn"),
    ]

    for name, import_name in packages:
        try:
            __import__(import_name)
            checks.append((name, "✓ installed", True))
        except ImportError:
            checks.append((name, "✗ not installed", False))

    # Check optional packages
    optional = [
        ("whisper", "openai-whisper"),
        ("librosa", "librosa"),
        ("torch", "torch"),
        ("transformers", "transformers"),
    ]

    click.echo("\nOptional dependencies:")
    for name, pkg in optional:
        try:
            __import__(name)
            checks.append((name, "✓ installed", True))
        except ImportError:
            checks.append((name, "○ not installed (optional)", None))

    # Print results
    click.echo("\nDependency Status:")
    click.echo("-" * 40)
    for name, status, ok in checks:
        if ok is True:
            click.secho(f"  {name}: {status}", fg="green")
        elif ok is False:
            click.secho(f"  {name}: {status}", fg="red")
        else:
            click.secho(f"  {name}: {status}", fg="yellow")


def _generate_srt(word_timeline: list) -> str:
    """Generate SRT subtitle format from word timeline."""
    lines = []
    idx = 1

    # Group words into ~5 second segments
    current_segment = []
    segment_start = None

    for token in word_timeline:
        if segment_start is None:
            segment_start = token.start_time

        current_segment.append(token.word)

        if token.end_time - segment_start >= 5.0 or token == word_timeline[-1]:
            # Write segment
            start_tc = _seconds_to_timecode(segment_start)
            end_tc = _seconds_to_timecode(token.end_time)
            text = " ".join(current_segment)

            lines.append(f"{idx}")
            lines.append(f"{start_tc} --> {end_tc}")
            lines.append(text)
            lines.append("")

            idx += 1
            current_segment = []
            segment_start = None

    return "\n".join(lines)


def _seconds_to_timecode(seconds: float) -> str:
    """Convert seconds to SRT timecode."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
