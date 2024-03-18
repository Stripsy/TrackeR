import requests
import discord
import maya
import asyncio
import pymongo
from pymongo import MongoClient
from maya import MayaInterval
from pprint import pprint
from discord.ext import commands, tasks
from requests.structures import CaseInsensitiveDict

client = commands.Bot(command_prefix='!', help_command=None)

cluster = MongoClient("")

chan = ""

db = cluster["db"]

collection = db["track"]

@client.command()
async def help(ctx):
    embed=discord.Embed(title="Help")
    embed.add_field(name="Suivre un colis", value="!track numero", inline=True)
    embed.add_field(name="Ajouter un colis à sa liste", value="!addtrack numero", inline=True)
    embed.add_field(name="Editer les notes d'un colis", value="!editnotes numero notes", inline=True)
    embed.add_field(name="Afficher la liste de colis", value="!listetrack", inline=True)
    embed.add_field(name="Retirer un colis de sa liste", value="!removetrack numero", inline=True)
    embed.add_field(name="Supprimer sa liste de colis", value="!removeliste", inline=True)
    embed.set_footer(text="Tracker v1.1")
    await ctx.send(embed=embed)


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name="suivre vos colis 📍"))

@client.command()
async def track(ctx, tracking):

    general_channel = client.get_channel(chan)

    url = "https://api.laposte.fr/suivi/v2/idships/"+tracking+"?lang=fr_FR"
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["X-Forwarded-For"] = "123.123.123.123"
    headers["X-Okapi-Key"] = ""
    resp = requests.get(url, headers=headers)

    if(resp.status_code == 200):
        toj = resp.json()

        track = toj["shipment"]["idShip"]
        try:
            depot = toj["shipment"]["entryDate"]

        except KeyError:
            depot = ""
        
        typecolis = toj["shipment"]["product"]
        devent = toj["shipment"]["event"][0]["date"]
        etat = toj["shipment"]["event"][0]["label"]

        cmaya = maya.parse(devent)

        embed = discord.Embed(title=tracking, color=0xfff700)

        if(typecolis == "colissimo" or typecolis == "chronopost"):

            if(typecolis == "colissimo"):
                embed.set_image(url="https://i.imgur.com/Sd0SzNK.png")
            
            else:
                embed.set_image(url="https://i.imgur.com/P8hE6p0.png")

        else:
            embed.set_image(url="https://i.imgur.com/kkU0MpI.png")


        embed.add_field(name="Type de colis", value=typecolis, inline=False)
        if(depot == ""):
            embed.add_field(name="Date de dépôt", value="Indisponible", inline=False)
        else:
            embed.add_field(name="Date de dépôt", value=maya.parse(depot), inline=False)

        embed.add_field(name="Date du dernier évènement", value=cmaya, inline=False)
        embed.add_field(name="Etat", value=etat, inline=False)
        embed.set_footer(text="v1.1")
        
        await general_channel.send(embed=embed)


# ERRORS
    if(resp.status_code == 400):
        embed400 = discord.Embed(title="Tracking invalide (ne respecte pas la syntaxe définie, 8RXXXXXXXXXXX)", color=0xff0000)
        await general_channel.send(embed=embed400)

    if(resp.status_code == 401):
        embed401 = discord.Embed(title="Non-autorisé (absence de la clé Okapi)", color=0xff0000)
        await general_channel.send(embed=embed401)

    if(resp.status_code == 404):
        embed404 = discord.Embed(title="Ressource non trouvée, suivi non disponible", color=0xff0000)
        await general_channel.send(embed=embed404)

    if(resp.status_code == 500):
        embed500 = discord.Embed(title="Erreur système (message non généré par l’application)", color=0xff0000)
        await general_channel.send(embed=embed500)

    if(resp.status_code == 504):
        embed504 = discord.Embed(title="Service indisponible (erreur technique sur service tiers)", color=0xff0000)
        await general_channel.send(embed=embed504)

@client.command()
async def addtrack(ctx, tracking, *,notes=""):

    general_channel = client.get_channel(chan)

    url = "https://api.laposte.fr/suivi/v2/idships/"+tracking+"?lang=fr_FR"
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["X-Forwarded-For"] = "123.123.123.123"
    headers["X-Okapi-Key"] = ""
    resp = requests.get(url, headers=headers)

    if notes == "":
        notes="/"

    if(resp.status_code == 200):
        suivi = {"pseudo": ctx.message.author.name,"tracking": tracking,"notes":notes}
        try:
            collection.insert_one(suivi)
            embed1 = discord.Embed(title="Ajout en cours 🔄", color=0xFFA500)
            embed2 = discord.Embed(title="Tracking ajouté ! ✅", color=0x00ff00)

            state = await ctx.send(embed=embed1)
            await asyncio.sleep(2)
            await state.edit(embed=embed2)
            await listetrack(ctx)
        except:
            embed = discord.Embed(title="Tracking déjà enregistré ! ⚠️", color=0xff0000)
            await general_channel.send(embed=embed)

    # ERRORS
    if(resp.status_code == 400):
        embed400 = discord.Embed(title="Tracking invalide (ne respecte pas la syntaxe définie, 8RXXXXXXXXXXX)", color=0xff0000)
        await general_channel.send(embed=embed400)

    if(resp.status_code == 401):
        embed401 = discord.Embed(title="Non-autorisé (absence de la clé Okapi)", color=0xff0000)
        await general_channel.send(embed=embed401)

    if(resp.status_code == 404):
        embed404 = discord.Embed(title="Ressource non trouvée, suivi non disponible", color=0xff0000)
        await general_channel.send(embed=embed404)

    if(resp.status_code == 500):
        embed500 = discord.Embed(title="Erreur système (message non généré par l’application)", color=0xff0000)
        await general_channel.send(embed=embed500)

    if(resp.status_code == 504):
        embed504 = discord.Embed(title="Service indisponible (erreur technique sur service tiers)", color=0xff0000)
        await general_channel.send(embed=embed504)

    
@client.command()
async def listetrack(ctx):

    general_channel = client.get_channel(chan)
    
    embed = discord.Embed(title="Hey "+ctx.message.author.name+" ! Vous avez "+ str(collection.count({"pseudo": ctx.message.author.name}))+" colis. 📦", color=0xfff700)

    for x in collection.find({"pseudo": ctx.message.author.name}):

        url = "https://api.laposte.fr/suivi/v2/idships/"+x["tracking"]+"?lang=fr_FR"
        headers = CaseInsensitiveDict()
        headers["Accept"] = "application/json"
        headers["X-Forwarded-For"] = "123.123.123.123"
        headers["X-Okapi-Key"] = ""
        resp = requests.get(url, headers=headers)

        if(resp.status_code == 200):
            toj = resp.json()

            track = toj["shipment"]["idShip"]
            try:
                depot = toj["shipment"]["entryDate"]

            except KeyError:
                depot = ""
        
            typecolis = toj["shipment"]["product"]
            devent = toj["shipment"]["event"][0]["date"]
            etat = toj["shipment"]["event"][0]["label"]

            embed.add_field(name=x["tracking"], value="**Etat : **"+"`"+etat+"`"+"\n"+"**Date event. :**"+"`"+str(maya.parse(devent))+"`"+"\n"+"**Notes :** "+"`"+x["notes"]+"`", inline=True)
            embed.set_image(url="https://i.imgur.com/n7sUuD4.png")
            embed.set_footer(text="v1.1")
        
    await general_channel.send(embed=embed)

@client.command()
async def removeliste(ctx):
    general_channel = client.get_channel(chan)

    suivi = {"pseudo": ctx.message.author.name}
    collection.delete_many(suivi)

    embed1 = discord.Embed(title="Liste de colis en cours de suppression 🔄", color=0xFFA500)
    embed2 = discord.Embed(title="Liste de colis supprimée ! ✅", color=0x00ff00)

    state = await ctx.send(embed=embed1)
    await asyncio.sleep(5)
    await state.edit(embed=embed2)

@client.command()
async def removetrack(ctx, tracking):
    general_channel = client.get_channel(chan)

    suivi = {"pseudo": ctx.message.author.name,"tracking": tracking}

    collection.delete_one(suivi)
    embed = discord.Embed(title="Tracking supprimé ! ✅", color=0x00ff00)
    await general_channel.send(embed=embed)
    await asyncio.sleep(2)
    await listetrack(ctx)

@client.command()
async def editnotes(ctx, tracking, *,notes):
    general_channel = client.get_channel(chan)
    collection.update_one({"tracking":tracking}, {"$set" :{"notes":notes}})

    embed = discord.Embed(title="Notes éditées ! ✅", color=0x00ff00)
    await general_channel.send(embed=embed)
    await asyncio.sleep(2)
    await listetrack(ctx)

    

client.run('')