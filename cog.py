import io

import discord
from discord.ext import commands


MODULE_ID = "logger"


def is_channel_allowed(channel_id, module_config):
    return channel_id not in module_config.get("bannedChannels", [])


def is_user_allowed(user_id, module_config):
    return user_id not in module_config.get("bannedUsers", [])


def is_category_allowed(category_id, module_config):
    return category_id not in module_config.get("bannedCategories", [])


class Logger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.services = bot.r4_services
        self.config = self.services.config
        self.firebase = self.services.firebase
        self.module_config = self.services.module_config

    def get_core_server_data(self, guild_id: int):
        return self.config.get_servers_data().get(str(guild_id))

    def get_module_server_data(self, guild_id: int):
        return self.module_config.get_guild_config(MODULE_ID, guild_id)

    def should_log_message(self, message, module_config) -> bool:
        return (
            is_channel_allowed(message.channel.id, module_config)
            and is_user_allowed(message.author.id, module_config)
            and is_category_allowed(message.channel.category_id, module_config)
        )

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.guild is None or message.author.bot:
            return

        core_config = self.get_core_server_data(message.guild.id)
        module_config = self.get_module_server_data(message.guild.id)
        if not core_config or not module_config or not self.should_log_message(message, module_config):
            return

        channel = self.bot.get_channel(module_config.get("log_channel"))
        if channel is None:
            return

        author_id = str(message.author.id)
        user = self.firebase.get_from_record(str(message.guild.id), "Users", author_id)
        if user:
            self.firebase.update_record(str(message.guild.id), "Users", author_id, {"messages": user.get("messages", 0) - 1})
        else:
            self.firebase.create_record(str(message.guild.id), "Users", author_id, {"messages": -1, "timeouts": 0})

        embed = discord.Embed(
            title="Удалённое сообщение",
            description=message.content or "<без текста>",
            color=int(core_config.get("accent_color"), 16),
        )
        embed.add_field(name="Автор", value=f"<@{author_id}>")
        embed.add_field(name="Канал", value=f"<#{message.channel.id}>")

        if not message.attachments:
            await channel.send(embed=embed)
            return

        attachment = message.attachments[0]
        attachment_bytes = io.BytesIO(await attachment.read())
        await channel.send(file=discord.File(attachment_bytes, attachment.filename), embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.guild is None or before.author.bot:
            return

        core_config = self.get_core_server_data(before.guild.id)
        module_config = self.get_module_server_data(before.guild.id)
        if not core_config or not module_config:
            return

        if not self.should_log_message(before, module_config) or before.content == after.content:
            return

        channel = self.bot.get_channel(module_config.get("log_channel"))
        if channel is None:
            return

        embed = discord.Embed(color=int(core_config.get("accent_color"), 16))
        embed.add_field(name="Редактированное сообщение", value=after.content or "<без текста>", inline=False)
        embed.add_field(name="Оригинальное сообщение", value=before.content or "<без текста>", inline=False)
        embed.add_field(name="Автор", value=f"<@{before.author.id}>")
        embed.add_field(name="Канал", value=f"<#{before.channel.id}>")
        await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Logger(bot))
