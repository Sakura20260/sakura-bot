import discord
from discord.ext import commands
from utils.auto_moderation import auto_moderator
from utils.embeds import warning_embed
from utils.logging_utils import log_moderation
from utils.database import db
import logging

logger = logging.getLogger(__name__)

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Modération automatique des messages"""
        if message.author.bot:
            return
        
        reasons = []
        
        # Vérifications
        if auto_moderator.check_banned_words(message.content):
            reasons.append("Mot interdit détecté")
        
        if auto_moderator.check_spam(message.author.id):
            reasons.append("Spam détecté")
        
        if auto_moderator.check_excessive_caps(message.content):
            reasons.append("Majuscules excessives")
        
        if auto_moderator.check_links(message.content):
            reasons.append("Lien non autorisé")
        
        if auto_moderator.check_mentions(message):
            reasons.append("Trop de mentions")
        
        # Supprimer le message si violation
        if reasons:
            try:
                await message.delete()
                
                embed = warning_embed(
                    "⚠️ Message supprimé",
                    f"**Raison(s):** {', '.join(reasons)}"
                )
                
                await message.author.send(embed=embed)
                
                await db.add_warning(
                    message.author.id,
                    self.bot.user.id,
                    f"Auto-mod: {', '.join(reasons)}"
                )
                
                logger.info(f"Message supprimé: {message.author} - {reasons}")
            
            except discord.Forbidden:
                logger.warning(f"Impossible de supprimer message de {message.author}")

async def setup(bot):
    await bot.add_cog(AutoMod(bot))