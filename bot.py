import os
import discord
from discord.ext import commands

# Enable necessary intents so the bot can read messages
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Define the scoring system
SCORING = {
    "round1": {"1": 2.0, "2": 1.0, "3": 0.5},
    "round2": {"1": 4.0, "2": 2.0, "3": 1.0},
    "final":  {"1": 5.0, "2": 4.0, "3": 2.0}
}

# Dictionary to store scores (User ID -> Total Points)
# Note: This is in-memory. If the bot restarts, scores will reset.
scores = {}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}!")

@bot.command()
async def addpoints(ctx, round_name: str, *, data: str):
    """
    Usage: !addpoints <round_name> @user <placements>
    Example: !addpoints round1 @PlayerOne 1 1 2 @PlayerTwo 3 1
    """
    round_name = round_name.lower()
    
    # Check if the round exists
    if round_name not in SCORING:
        await ctx.send("❌ Invalid round! Please use `round1`, `round2`, or `final`.")
        return

    parts = data.split()
    current_user_id = None
    updates = []

    for part in parts:
        # Check if the part is a Discord mention (e.g., <@123456789>)
        if part.startswith("<@") and part.endswith(">"):
            # Clean the string to extract just the numeric ID
            user_id_str = part.replace("<@", "").replace("!", "").replace(">", "")
            
            if user_id_str.isdigit():
                current_user_id = int(user_id_str)
                # Initialize the user in the dictionary if they don't exist
                if current_user_id not in scores:
                    scores[current_user_id] = 0.0

        # Check if the part is a valid placement number (1, 2, or 3)
        elif part in SCORING[round_name]:
            if current_user_id is None:
                await ctx.send(f"⚠️ Error: You must mention a user before typing their placements (`{part}`).")
                return
            
            # Calculate and add the points
            points = SCORING[round_name][part]
            scores[current_user_id] += points
            updates.append(f"Gave **{points}** pts to <@{current_user_id}> for finishing **{part}**")
            
        else:
            await ctx.send(f"⚠️ Ignored invalid placement or formatting: `{part}`")

    # Send a confirmation message
    if updates:
        await ctx.send("✅ **Points successfully recorded:**\n" + "\n".join(updates))
    else:
        await ctx.send("No valid placements were found in your message.")

@bot.command()
async def leaderboard(ctx):
    """Shows the current total scores for all players."""
    if not scores:
        await ctx.send("No points have been recorded yet!")
        return
    
    # Sort the scores from highest to lowest
    sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    
    leaderboard_text = "🏆 **Current Leaderboard** 🏆\n"
    for rank, (user_id, pts) in enumerate(sorted_scores, 1):
        leaderboard_text += f"**{rank}.** <@{user_id}> — {pts} points\n"
    
    await ctx.send(leaderboard_text)

# Retrieve token securely from environment variables
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError("ERROR: DISCORD_TOKEN environment variable is missing!")

# Run the bot
bot.run(TOKEN)
