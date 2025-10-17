import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from datetime import datetime, timezone

import database as db

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("Coloca DISCORD_TOKEN en .env")

intents = discord.Intents.default()
intents.guilds = True
intents.members = True     # útil para resolver nombres
intents.voice_states = True
intents.message_content = True  # necesario para comandos con texto
bot = commands.Bot(command_prefix="!", intents=intents)

# Inicializa DB
db.init_db()

def is_muted(vs: discord.VoiceState):
    # cuenta tanto mute por servidor (vs.mute) como self mute (vs.self_mute)
    if vs is None:
        return False
    return bool(vs.self_mute or vs.mute)

def is_deaf(vs: discord.VoiceState):
    return bool(vs.self_deaf or vs.deaf)

@bot.event
async def on_ready():
    print(f"{bot.user} conectado. Listo para trackear estados de voz.")

@bot.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    now = datetime.now(timezone.utc)
    guild_id = member.guild.id
    user_id = member.id

    # --- MUTE tracking ---
    before_muted = is_muted(before)
    after_muted = is_muted(after)
    if not before_muted and after_muted:
        # empezó a estar muteado
        if not db.is_session_active(guild_id, user_id, "mute"):
            db.start_session(guild_id, user_id, "mute", now)
    elif before_muted and not after_muted:
        # terminó el mute
        duration = db.end_session_and_accumulate(guild_id, user_id, "mute", now)
        # opcional: notificar en consola
        print(f"[MUTE] {member.display_name} estuvo muteado {duration:.1f}s en guild {guild_id}")

    # --- DEAF tracking ---
    before_deaf = is_deaf(before)
    after_deaf = is_deaf(after)
    if not before_deaf and after_deaf:
        if not db.is_session_active(guild_id, user_id, "deaf"):
            db.start_session(guild_id, user_id, "deaf", now)
    elif before_deaf and not after_deaf:
        duration = db.end_session_and_accumulate(guild_id, user_id, "deaf", now)
        print(f"[DEAF] {member.display_name} estuvo ensordecido {duration:.1f}s en guild {guild_id}")

# ---------------- Commands ----------------

def pretty_time(seconds: float):
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours}h {minutes}m {secs}s" if hours else (f"{minutes}m {secs}s" if minutes else f"{secs}s")

@bot.command(name="tiempo")
async def tiempo(ctx, member: discord.Member = None):
    member = member or ctx.author
    m, d = db.get_totals(ctx.guild.id, member.id)
    # Si hay sesión activa, sumar tiempo hasta ahora
    import datetime as _dt
    now = datetime.now(timezone.utc)
    if db.is_session_active(ctx.guild.id, member.id, "mute"):
        # fetch start_ts from DB (quick and dirty)
        # reuse database.get_conn for a small query
        from database import get_conn
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT start_ts FROM active_sessions WHERE guild_id=? AND user_id=? AND typ='mute'", (ctx.guild.id, member.id))
        r = cur.fetchone()
        conn.close()
        if r:
            start = datetime.fromisoformat(r["start_ts"])
            m += (now - start).total_seconds()
    if db.is_session_active(ctx.guild.id, member.id, "deaf"):
        from database import get_conn
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT start_ts FROM active_sessions WHERE guild_id=? AND user_id=? AND typ='deaf'", (ctx.guild.id, member.id))
        r = cur.fetchone()
        conn.close()
        if r:
            start = datetime.fromisoformat(r["start_ts"])
            d += (now - start).total_seconds()

    await ctx.send(f"🕒 **{member.display_name}** ha estado:\n• Muteado: **{pretty_time(m)}**\n• Ensordecido: **{pretty_time(d)}**")

@bot.command(name="topmute")
async def topmute(ctx, limit: int = 10):
    rows = db.get_top(ctx.guild.id, "mute", limit)
    if not rows:
        await ctx.send("No hay datos aún.")
        return
    lines = []
    for i, (user_id, seconds) in enumerate(rows, start=1):
        member = ctx.guild.get_member(user_id)
        name = member.display_name if member else f"ID:{user_id}"
        lines.append(f"{i}. {name} — {pretty_time(seconds)}")
    await ctx.send("🏆 **Top muteados**\n" + "\n".join(lines))

@bot.command(name="topdeaf")
async def topdeaf(ctx, limit: int = 10):
    rows = db.get_top(ctx.guild.id, "deaf", limit)
    if not rows:
        await ctx.send("No hay datos aún.")
        return
    lines = []
    for i, (user_id, seconds) in enumerate(rows, start=1):
        member = ctx.guild.get_member(user_id)
        name = member.display_name if member else f"ID:{user_id}"
        lines.append(f"{i}. {name} — {pretty_time(seconds)}")
    await ctx.send("🏆 **Top ensordecidos**\n" + "\n".join(lines))

# Admin command para resetear totales (solo por el owner o con permisos)
@bot.command(name="reset_totals")
@commands.has_permissions(administrator=True)
async def reset_totals(ctx):
    from database import get_conn
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM totals WHERE guild_id=?", (ctx.guild.id,))
    conn.commit()
    conn.close()
    await ctx.send("Totales reseteados para este servidor.")


@bot.command(name="ping")
async def ping(ctx):
    await ctx.send("🏓 Pong!")

@bot.command(name="ayudame")
async def ayudame(ctx):
    await ctx.send("!tiempo - Para ver tu tiempo ⛅\n" \
    "!topmute - Para ver el top de muteados 🏆\n" \
    "!topdeaf - Para ver el top de ensordecidos 🏆\n")
    
# Run
bot.run(TOKEN)
