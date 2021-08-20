import logging
from pathlib import Path
from discord import Intents
from core.bot import KingBot


# LOGS
log = logging.getLogger('king')
log.setLevel(logging.INFO)

# INTENTS
intents = Intents.all()

# CONFIG YAML
config = Path("config.yaml")


bot = KingBot(
    command_prefix=KingBot.get_prefix,
    intents=intents,
    config=config
)

if __name__ == '__main__':
    bot.run()
