import random
import re
import discord
from datetime import datetime
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="%", intents=intents)
transmission_rate = .87
roles = {'covid': 'Covided',
         'dr': 'Dr Raoult le Fédérateur',
         '5g': '5G'}
suffixes_peu_glorieux = [" le gilet jaune",
                         " le malade",
                         " l'inutile",
                         " le gras",
                         " le gros",
                         " le socialiste",
                         " le terroriste",
                         " le gauchiste",
                         " le droitard",
                         " le sous-être",
                         " le contagieux",
                         " le zoophile",
                         " le sale",
                         " le malpropre",
                         " le boiteux",
                         " le clandestin",
                         " le migrant",
                         " le parasite",
                         " le puant",
                         " le pédant",
                         " le suceur",
                         " l'ordure",
                         " le cocu",
                         " le puceau",
                         " le con",
                         " l'idiot",
                         " le fourbe",
                         " l'incel",
                         " l'enfoiré",
                         " le dingue",
                         " le cinglé",
                         " l'invalide",
                         " le consanguin",
                         " le furry",
                         " le casse-couilles",
                         " le fan de pieds",
                         " le mécréant",
                         " l'infidèle",
                         " le porc",
                         " le ramolo",
                         " le relou",
                         " le soumis",
                         " le bâtard",
                         " le nul",
                         " le faible",
                         " le malhonnête",
                         " le brise-burnes",
                         " le clochard",
                         " l'abruti",
                         " le pauvre",
                         " le drogué",
                         " le boulimique",
                         " l'anorexique",
                         " l'obsédé",
                         " le pervers"
                         ]


# Fonction Usage et Help (erreur mauvais paramètres + description du jeu)
# Fonction infection_passive, qui infecte les membres côte à côte dans la liste alphabétique des users
# Fonction %geste_barrière, si invoquée le membre ne peut pas être infecté en postant son message
# Fonction %vaccin, divise par 10 les chances d'être infecté
# Fonction %stats, qui indique le nombre de personnes infectées sur l'ensemble du serveur, hors bot
# Autre idée si Covid, le membre est en slowmode car insuffisance respiratoire


@bot.command()
@commands.has_role('Admin')
async def setup(ctx):
    for role in roles.values():
        if discord.utils.get(ctx.guild.roles, name=role):
            print(f"Role {role} exists")
        else:
            await ctx.guild.create_role(name=role, colour=discord.Colour(random.randint(0, 0xFFFFFF)))
            print(f"Role {role} created")


async def show_symptoms(message):
    proba_symptom = 0.20
    role_covid = discord.utils.get(message.guild.roles, name=roles['covid'])
    if role_covid in message.author.roles and random.random() <= proba_symptom:
        suffixe = random.choice(suffixes_peu_glorieux)
        await message.author.edit(nick=message.author.name + suffixe)
        print(f'Nickname changed: {message.author}')


def risk_infection(message):
    role_covid = discord.utils.get(message.guild.roles, name=roles['covid'])
    return role_covid in message.author.roles


@bot.event
async def on_ready() -> None:
    print("{} : Démarrage de bot".format(datetime.now()))


async def get_covid(message):
    if message.author.bot:
        return
    role = discord.utils.get(message.author.guild.roles, name=roles['covid'])
    await message.author.add_roles(role)
    await show_symptoms(message)
    await message.channel.send(f"{message.author.name} est maintenant {role.name}")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        print("Erreur perms")

    if isinstance(error, commands.CommandOnCooldown):
        em = discord.Embed(title=f":warning: Cooldown",
                           description=f"Retentez la commande dans {error.retry_after:.2f} secondes.")
        if ctx.command.qualified_name == "ondes5g":
            em = discord.Embed(title=f":warning: Alerte gilets Jaunes",
                               description=f":signal_strength: Oh non, les gilets jaunes bloquent le rond-point!\n\
                                             Tu pourras installer une antenne 5G dans {error.retry_after:.2f} secondes.")
        elif ctx.command.qualified_name == "heal":
            em = discord.Embed(title=f":warning: Rupture de stock",
                               description=f":medical_symbol: Oh non Docteur, nous n'avons plus de chloroquine!\n\
                                        Nous en aurons à nouveau dans {error.retry_after:.2f} secondes.")

        await ctx.send(embed=em)


# Si Installateur 5G, peut installer une antenne 5G près d'un membre qui a une chance de refiler le covid
@bot.command(pass_context=True, aliases=['antenne5g', 'antenne5G', 'ondes5G', '5g', '5G'])
@commands.has_role(roles['5g'])
@commands.cooldown(1, 60, commands.BucketType.guild)
async def ondes5g(ctx, user_client: discord.Member):
    """
    Dose de 5G - Usage: %5G @member
    :return: null, a une chance d'infecter du Covid (parce que la 5G refile le coronavirus, c'est scientifique)
    """
    role_covid = discord.utils.get(ctx.message.guild.roles, name=roles['covid'])
    proba_covid = 0.70
    if user_client.bot:
        return

    if role_covid in user_client.roles:
        await ctx.send(f":signal_strength: {user_client.name} a déjà la 5G.")
    elif random.random() <= proba_covid:
        await ctx.send(f":signal_strength: {user_client.name} a la 5G, et le covid.")
        await user_client.add_roles(role_covid)
    else:
        replies = [
            ":signal_strength: Rien ne s'est produit, mais j'ai un meilleur réseau!",
            ":signal_strength: L'antenne 5G est installée, mais personne n'est malade... Pour l'instant"
        ]
        await ctx.send(random.choice(replies))


@ondes5g.error  # <- name of the command + .error
async def help_mod_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send(":x: Encore un mec de Free qui se prend pour un Technicien Orange. Pas de 5G pour toi!")


# Si le membre a le covid, seul Dr Raoult peut utiliser la commande Chloroquine sur ce membre
# Cependant, la cholorquine a X% de chances de tuer le patient (kick serveur)
# Comme la chloroquine devient rare, Dr Raoult ne peut utiliser la choloroquine que 2 fois toutes les minutes
@bot.command(pass_context=True, aliases=['chloroquine'])
@commands.has_role(roles['dr'])
@commands.cooldown(2, 60, commands.BucketType.guild)
async def heal(ctx, user_patient: discord.Member):
    """
    Dose de choloroquine - Usage: %chloroquine @member
    :return: null, a une chance de soigner du Covid ou de kick le membre
    """
    role_covid = discord.utils.get(ctx.message.guild.roles, name=roles['covid'])
    proba_kick = 0.05
    # Idée historique patient, injections ratées augmentent risque de mort
    proba_guerison = 0.80
    if user_patient.bot:
        return

    if role_covid in user_patient.roles:
        if random.random() <= proba_kick:
            await user_patient.send(":medical_symbol: Le Covid n'a pas eu raison de toi, mais le docteur, oui.\n\
Pour revenir: https://discord.gg/6QEvgHWnM3")
            await ctx.guild.kick(user_patient, reason="Chloroquined")
            await ctx.send(f":medical_symbol: {user_patient.name} n'a pas survécu à sa dose de choloroquine!")
        elif random.random() <= proba_guerison:
            await user_patient.remove_roles(role_covid)
            await ctx.send(f":medical_symbol: {user_patient.name} est guéri, merci Docteur!")
            await user_patient.edit(nick='')
        else:
            await ctx.send(":medical_symbol: Le patient n'est pas guéri... Mais au moins, il n'est pas mort !")
    else:
        replies = [
            ":medical_symbol: Mais enfin Docteur, ce patient est sain",
            ":medical_symbol: Docteur, vous avez (encore) bu?",
            ":medical_symbol: Ce patient est guéri !... Mais n'était pas malade."
        ]
        await ctx.send(random.choice(replies))


@heal.error  # <- name of the command + .error
async def help_mod_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send(":x: Vous n'êtes pas Docteur, sale usurpateur ! Cassez-vous !")


@bot.command(pass_context=True)
async def pcr(ctx, user: discord.Member):
    """
    PCR test - Usage: %pcr @member
    :return: si le membre a le covid ou pas
    """
    role = discord.utils.get(ctx.message.guild.roles, name=roles['covid'])
    if role in user.roles:
        await ctx.send("{} a le Covid".format(user))
    else:
        await ctx.send("{} est sain".format(user))


@bot.event
async def on_message(message):
    # Besoin de cette ligne pour ne pas bloquer les bot.commands()
    await bot.process_commands(message)
    # Logging
    last_message = await message.channel.history(limit=2).flatten()
    last_message = last_message[1]

    if message.author == bot.user:
        return

    await show_symptoms(message)
    print("{} répond à {} - {}".format(message.author, last_message.author, message.content.lower()))
    if message.content == "%geste_barrière" \
            or message.content == "%geste_barriere" \
            or message.content == "%gestes_barrieres" \
            or message.content == "%gestes_barrières":
        return

    # FONCTIONS BONUS
    if "covid" in message.content:
        await message.channel.send("On m'a appelé?")
        return
    if "pied" in message.content or "feet" in message.content:
        await message.channel.send("Ah, ça parle de pied? <@!830199237856723004> est fétichiste!")
        return
    if "éthique" in message.content:
        await message.channel.send("> L'éthique, c'est pour les pauvres.\n- <@!307964302533591050>")
        return

    # détection cyrillique => cyka
    if re.search('[а-яА-Я]', message.content):
        await message.channel.send("сука блять")
        return

    if ''.join(filter(str.isalpha, message.content.lower())).endswith("quoi") \
            and not message.content.lower().endswith(">"):
        await message.channel.send("FEUR!")
        return

    if not message.author.bot and risk_infection(last_message):
        if risk_infection(message) or random.random() >= transmission_rate:
            return
        else:
            await get_covid(message)
            return


if __name__ == '__main__':
    discord_key = open("key.txt", "r").read()
    bot.run(discord_key)
