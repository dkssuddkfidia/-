from discord.ext import commands
import os

# .env에서 ADMIN_IDS 불러오기
# 예: ADMIN_IDS=1161936890845470720,1234567890
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))

def is_admin():
    async def predicate(ctx):
        return ctx.author.id in ADMIN_IDS
    return commands.check(predicate)
