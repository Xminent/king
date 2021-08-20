import random
from discord import Embed, Color


def success_embed(title, description):
    return Embed(
        title=title,
        description=description,
        color=0x00FF00
    )


def embed(title, description):
    return Embed(
        title=title,
        description=description,
        color=Color(value=random.randint(0x000000, 0xFFFFFF))
    )


def error_embed(title, description):
    return Embed(
        title=title,
        description=description,
        color=0xFF0000
    )
