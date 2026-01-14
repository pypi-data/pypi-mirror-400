import click

from .chat import chat
from .db import db
from .image import image
from .search import search
from .video import video
from .voice import asr, tts


@click.group()
@click.version_option(version="0.5.0", prog_name="coze-coding-ai")
def main():
    """Coze Coding CLI - AI-powered tools for video generation and more."""
    pass


main.add_command(video)
main.add_command(image)
main.add_command(search)
main.add_command(tts)
main.add_command(asr)
main.add_command(chat)
main.add_command(db)


if __name__ == "__main__":
    main()
