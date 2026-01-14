import click
import os
from .inference import run_llm
from .utils import download_model_if_needed

@click.group()
def cli():
    """Pixel-AI LLM CLI for Raspberry Pi"""
    pass

@cli.command()
def run():
    """Run LLM for emotion responses"""
    download_model_if_needed()
    run_llm()

@cli.command()
def install():
    """Download model weights and quantized LLM"""
    download_model_if_needed()
    click.echo("Model installed and ready!")

if __name__ == "__main__":
    cli()
