import random
from asyncio import sleep
from typing import Optional

import discord
import numpy
from bs4 import BeautifulSoup
from discord.ext import commands
from googlesearch import search
from youtubesearchpython import Search

from utils.image import get_bytes, image_to_ascii


def tiny_text(character: str):
    """replaces text with its subscript version"""
    regtext = "abcdefghijklmnopqrstuvwxyz"
    superscript = "ᵃᵇᶜᵈᵉᶠᵍʰᶦʲᵏˡᵐⁿᵒᵖᵠʳˢᵗᵘᵛʷˣʸᶻ"
    if character in regtext:
        return superscript[regtext.find(character)]
    else:
        return character


def gauss(x) -> float:
    peak = 0.3
    e_fun = numpy.e ** (-0.5 * ((x - 30) / 1.76) ** 2)
    y = peak * e_fun
    return y + 0.05


async def try_delete_message(message: discord.Message):
    try:
        await message.delete()
    except discord.Forbidden:
        pass


def luckynumber(number: int):
    snum = str(abs(number))
    while not len(snum) == 1:
        snum = str(sum([int(x) for x in snum]))
    return int(snum)


class Stuff(commands.Cog):
    """idk stuff i wanted to code"""

    def __init__(self, bot):
        self.bot = bot
        self.thoughts = {}
        self.wt_records = {}

    @commands.command()
    async def countdown(self, ctx, number: int = 3):
        """do a countdown from the number to zero.
        due to not wanting to make discord's api angry, let's keep the number below 10 okay"""
        if number > 10:
            return await ctx.send("what did i say >:(")
        nums = list(range(number))
        nums.reverse()
        nums = [i + 1 for i in nums]
        for i in nums:
            await ctx.send(f"{i}...")
            await sleep(1)
        await ctx.send("go!!")

    @commands.command(name="SCREAM", aliases=["scream"])
    async def scream(self, ctx, *, text: str):
        """LET'S HIT THAT CAPS BUTTON!"""
        text = text.upper()
        if text[-1] == ".":
            text = text[:-1] + "!"

        if not text.endswith("!"):
            text += "!"

        await try_delete_message(ctx.message)
        await ctx.send(text)

    @commands.command()
    async def botsend(self, ctx, *, text: str):
        """become a superior lifeform :)"""
        try:
            webhooks = await ctx.channel.webhooks()
            if not webhooks:
                webhook = await ctx.channel.create_webhook(name="made by autochip")
            else:
                webhook = webhooks[0]
        except discord.Forbidden:
            return await ctx.send(
                "sorry i can't make you a bot :(\ntry convincing a human to give me webhook permissions"
            )

        await try_delete_message(ctx.message)
        await webhook.send(
            text,
            username=ctx.author.display_name,
            avatar_url=str(ctx.author.avatar_url),
        )

    @commands.command()
    async def echo(self, ctx, *, text):
        """repeat what you tell me"""
        await try_delete_message(ctx.message)
        await ctx.send(text, allowed_mentions=discord.AllowedMentions.none())

    @commands.command(usage="<choices separated by comma>")
    async def choose(self, ctx, *, choices):
        """for when you cant decide"""
        if not choices:
            return await ctx.send("well, i choose nothing?")

        nchoices = [x.strip() for x in choices.split(",")]
        if len(nchoices) == 1:
            nchoices = [x.strip() for x in nchoices[0].split(" ")]
            if len(nchoices) == 1:
                return await ctx.send(f"tough choice huh...")

        final = random.choice(nchoices)
        await ctx.send(f"i chose **{final}** for you :)")

    @commands.command(aliases=["rps"])
    async def rockpaperscissors(self, ctx, choice: str):
        """lose a round of rock paper scissors against me :)"""
        if not choice.lower() in ["rock", "paper", "scissors"]:
            return await ctx.send(f"lol what's {choice} supposed to be")

        if random.randint(0, 100) == 69:
            # guess we'll make it a draw
            bchoice = choice
            outcome = "that's a draw"
        else:
            outcome = "you lost lol"
            if choice == "rock":
                bchoice = "paper"
            elif choice == "paper":
                bchoice = "scissors"
            else:
                bchoice = "rock"

        await ctx.send(f"you chose {choice}, i chose {bchoice}. {outcome}")

    @commands.command()
    async def whisper(self, ctx, *, text):
        """turn text into subscript making it freaking tiny"""
        textmap = map(tiny_text, list(text.lower()))
        whisper_text = ("".join(list(textmap))).rstrip(".?!")
        whisper_text += "..."
        await try_delete_message(ctx.message)
        await ctx.send(whisper_text)

    @commands.command(name="ascii", usage="<emoji or attached image>")
    async def make_ascii(self, ctx, emoji: discord.PartialEmoji = None):
        """turn an emoji or image into ascii art
        emoji have priority"""
        if not emoji:
            if not ctx.message.attachments:
                return await ctx.send("```\n```")
            url = str(ctx.message.attachments[0].url)
        else:
            url = str(emoji.url)
        ascii_art = image_to_ascii(await get_bytes(self.bot, url))
        await ctx.send(f"```{ascii_art}```")

    @commands.command(aliases=["temp", "temparature"])
    async def temperature(self, ctx, temp: str):
        """translate between celsius and fahrenheit
        expected inut is, for example would be 35c"""
        try:
            if temp[-1].lower() == "f":
                new_temp, unit = ((int(temp[:-1].strip()) - 32) * (5 / 9), "C")
            elif temp[-1].lower() == "c":
                new_temp, unit = ((int(temp[:-1].strip()) * (9 / 5)) + 32, "F")
            else:
                return await ctx.send(
                    "invalid temperature given, did you forget the c or f at the end?"
                )
        except ValueError:
            return await ctx.send(
                "invalid temperature format, try <number>[c/f], for example 35c"
            )

        await ctx.send(f"that's **{new_temp:,.1f}°{unit}**")

    @commands.command()
    async def google(self, ctx, *, query: str):
        """google something and I'll give you a (relevant?) link"""
        async with ctx.channel.typing():
            res = random.choice(
                [
                    "let's try this",
                    "give this one a try",
                    "this might be a good starting point",
                    "here u go",
                    "here you go",
                    "alright this one looks good",
                    "let's see... try this one",
                    "this might help",
                    "hope this is what you were looking for",
                    "i tried :)\n",
                    "this is the only one i could find",
                    "hope this is the right one",
                ]
            )
            src = search(
                query, safe="off" if ctx.channel.is_nsfw() else "on", stop=1, pause=0
            )
            link = list(src)[0]
        await ctx.send(f"{res} {link}")

    @commands.command(aliases=["yt"])
    async def youtube(self, ctx, *, query: str):
        """find a youtube video"""
        async with ctx.channel.typing():
            src = Search(query, limit=1).result()
        result = src["result"][0]
        link = result["link"]
        res = random.choice(
            [
                "let's try this one",
                "give this one a try",
                "this might be a good starting point",
                "here u go",
                "here you go",
                "alright this one looks good",
                "let's see... try this one",
                "hope this is what you were looking for",
                "i tried :)\n",
                "this is the best one i could find",
                "hope this is the right one",
            ]
        )
        await ctx.send(f"{res} {link}")

    @commands.command(usage="<content>")
    async def remember(self, ctx, *, content: str = ""):
        """remember text content to recall later
        also see commands recall and forget

        results are cached, meaning if the bot restarts, the remembered things are gone"""
        if not content:
            return await ctx.invoke(self.bot.get_command("recall"))
        self.thoughts[ctx.author.id] = content
        await ctx.send("alright, I'll remember that for later")

    @commands.command()
    async def recall(self, ctx):
        """recall the remembered text content
        also view commands remember and forget

        results are cached, meaning if the bot restarts, the remembered things are gone"""
        try:
            await ctx.send(self.thoughts[ctx.author.id])
        except KeyError:
            await ctx.send("i don't remember you telling me something...")

    @commands.command()
    async def forget(self, ctx):
        """forget the remembered text content
        also view commands remember and recall
        results are cached, meaning if the bot restarts, the remembered things are gone"""
        try:
            del self.thoughts[ctx.author.id]
            await ctx.send("alright, i forgot your content")
        except KeyError:
            await ctx.send("i don't remember you telling me something...")

    @commands.command(aliases=["rc", "randomcolour"])
    async def randomcolor(self, ctx):
        """show you a random color :)"""
        col = random.randint(0, 16777215)
        recol = str(hex(col).split("x")[1])
        r, g, b = recol[0:2], recol[2:4], recol[4:6]
        embed = discord.Embed(
            title="#" + recol.upper(),
            url=f"https://www.color-hex.com/color/{recol}",
            description=f"""Red: {int(r, base=16)}
Green: {int(g, base=16)}
Blue: {int(b, base=16)}""",
            color=col
        )
        embed.set_image(url=f"https://htmlcolors.com/color-image/{recol}.png")
        await ctx.send(embed=embed)

    @commands.command()
    async def submit(self, ctx, *, content: str = None):
        """submits an event submission anonymously to the event submission channel
        attached files will be sent as well"""
        attachments = ctx.message.attachments
        files = [await attachment.to_file() for attachment in attachments]
        await try_delete_message(ctx.message)
        guild = self.bot.get_guild(738627945056174230)
        channel = guild.get_channel(760366600284799016)
        try:
            await channel.send(content, files=files)
        except discord.HTTPException:
            # someone tried to send an empty message
            await ctx.send("You can't submit nothing :(", delete_after=5)

    @commands.group(aliases=["lucky", "luckynum"], invoke_without_command=True)
    async def luckynumber(self, ctx, num: int):
        """group command: gets the lucky number any number/user/the server"""
        lnum = luckynumber(num)
        await ctx.send(f"The lucky number for {num} is **{lnum}!**")

    @luckynumber.command()
    async def user(self, ctx, user: Optional[discord.Member]):
        user = user or ctx.author
        lnum = luckynumber(user.id)
        await ctx.send(f"{user.display_name}'s lucky number is **{lnum}!**")

    @luckynumber.command()
    async def server(self, ctx):
        if not ctx.guild:
            return await ctx.send("That won't work if you're using this in DMs :p")
        lnum = luckynumber(ctx.guild.id)
        await ctx.send(f"{ctx.guild.name}'s lucky number is **{lnum}!**")

    @commands.command(aliases=["wt", "timewaste", "tw"])
    async def wastetime(self, ctx):
        """waste time
        wasted time is decided at random
        leaderboard coming soon™"""
        msg = await ctx.send("Started wasting time... <a:loading:810551507694649366>")
        counter = 0
        out = gauss(0)
        rand = random.random()
        while out <= rand:
            rand = random.random()
            out = gauss(counter)
            counter += 1
            await sleep(1)

        personal_record = self.wt_records.get(ctx.author.id, 0)
        self.wt_records.update({ctx.author.id: counter})

        await msg.edit(content="Done wasting time!")

        await ctx.send(
            "{0} you successfully wasted **{1} seconds**!\n{2}".format(
                ctx.author.mention,
                counter,
                "That's a new personal record :)" if counter > personal_record else ""
            )
        )

    @commands.command()
    async def define(self, ctx, word: str):
        """define a word?"""
        async with self.bot.session.get(f"https://www.merriam-webster.com/dictionary/{word.lower()}") as r:
            html = await r.text()

        html = BeautifulSoup(html)
        # find the definition text
        with_tags = html.find_all("span", {"class": "dtText"})
        if not with_tags:
            return await ctx.send("this word was not found :(\nplease be precise in spelling")
        definitions = [BeautifulSoup(str(x)).get_text() for x in with_tags]
        await ctx.send("\n--\n".join(definitions))


def setup(bot):
    bot.add_cog(Stuff(bot))
