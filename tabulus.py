# Discord bot to track attendance each week
# Originally created by Ayden Bridges
# Ref material: https://docs.disnake.dev/en/stable/quickstart.html


import disnake
import logging
from datetime import datetime
import csv
import os
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(usecwd=True))

logging.basicConfig()

CLIENT_TOKEN = os.getenv("TOKEN")

DEBUG = True
ENABLE = True
DISABLE = False

ATTENDANCE_FORUM = "hack-night-attendance"

intents = disnake.Intents().all() # disnake.Intents(messages=True, guilds=True, message_content=True)
client = disnake.Client(intents=intents)

@client.event
async def on_ready():
    print(f"We have logged in as {client.user}\n")
    print("---\n")

@client.event
async def on_message(message):

    print("Received any message AT ALL")
    if DISABLE: print(message.channel.name)
    if DISABLE: print(message.channel.type)

    # Avoid a very dangerous self referential loop
    if message.author == client.user:
        return
    
    # Useful/relevant: https://stackoverflow.com/questions/29295654/what-does-python3-open-x-mode-do 

    # Block to grab attendance numbers from an attendance thread
    if str(message.channel.type) == "public_thread" or str(message.channel.type) == "private_thread":
        if "attendance" in message.channel.name.lower():
            channel_name = (message.channel.name.lower()).split()

            hack_version = ""

            if len(channel_name) >= 3: # [0] = "attendance", [1] = version number string, [2] = date string
                if channel_name[1][0].isnumeric() and channel_name[2] != "":
                    hack_version = channel_name[1]

            print(f"version number: {hack_version}, len: {len(channel_name)}")

            msg = message.content.split()

            if msg[0].isnumeric():
                data = {"date": datetime.now().strftime("%Y-%m-%d"), "time":datetime.now().strftime("%H:%M:%S"), "count":msg[0], "note":" ".join(msg[1:])}
                fieldnames = list(data.keys())
                
                # If the attendance tracking csv has not already been made, make it, then append to it.
                # Otherwise, just append to it.
                try:
                    with open("attendance_data.csv", "x", newline='') as csvfile:
                        data_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        data_writer.writeheader()
                        data_writer.writerow(data)
                # This feels so wack, I feel like it should be easier to enter headers on the first time the file is opened???
                except FileExistsError:
                    with open("attendance_data.csv", "a", newline='') as csvfile:
                        data_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        data_writer.writerow(data)

    if message.content.startswith("✍️ help"):
        list_of_commands = ["✍️ help: This command.\n", "✍️ readout: Uploads the attendance csv file.", "✍️ start attendance: Creates an attendance thread if one does not already exist.\n"]
        await message.channel.send(f"Here is a list of my commands:\n {list_of_commands}. I have no further information on them individually. Good luck!")

    # Uploads a csv of all the data collected so far.
    if message.content.startswith("✍️ readout"):
        await message.channel.send(file=disnake.File("attendance_data.csv"))

    # Starts an attendance thread if one does not already exist.
    # The thread is a private thread. Unclear how this affects things.
    if message.content.startswith("✍️ start attendance"):
        start_cmd = "✍️ start attendance" # Sort of a janky way to abstract this but whatever
        command = message.content

        command = command.removeprefix(start_cmd)

        command = command.split()

        hack_version = ""

        # Need to completely redo my flags system man
        # I think what I want to do is somehow iteratively cycle through the command string, detect if flags exist, 
        # and if a given flag exists check the few characters after it for the actual flag value.
        # Unfortunately, that is way harder than it sounds.
        # I think detecting if the first char is a writing hand emoji, and then if the next "word" is a command is a good start.
        # Then for each given command, check for a different set of flags/parameters.
        # The program flow is unfortunately cooked rn.
        for i in range(len(command)):
            if command[i] == "-v":
                try:
                    hack_version = command[i + 1]
                except:
                    print("For some reason the hack version isn't loading properly. Maybe a number was not specified after -v?")

        for channel in message.guild.channels:
            if channel.name == ATTENDANCE_FORUM:
                
                thread_names = []
                for thread in channel.threads:
                    thread_names.append(thread.name)

                _today_attendance_name = f"Attendance {hack_version} {datetime.now().strftime('%m/%d/%Y')}"
                print(thread_names)
                if _today_attendance_name not in thread_names: # type=disnake.ChannelType.private_thread
                    new_thread = await channel.create_thread(name=_today_attendance_name, content="Attendance thread created!") # Learned how to do the await thing on this line from here: https://stackoverflow.com/questions/42832543/how-to-return-value-from-async-method-in-python
                    await new_thread[0].add_user(message.author)
                else:
                    await message.channel.send("An attendance thread for today has already been created!")
            #print(channel)


    #if message.content.startswith("✍️ start attendance"):
    #    if f"{datetime.now().strftime("%m/%d/%Y")} Attendance" not in message.guild.threads: # If attendance hasn't been made yet
    #        message.guild.


    if DISABLE: print(message.content)

    print("\n---\n") # I just need some more spacing man
        
    # TODO:
    # Core function:
    # detect if a message is sent in an attendance thread
    # - if so, log the first number it finds, log the time, and log the rest of the message as a note (if there is one)
    #
    # Stretch goals:
    # priority 1:
    # ping everyone in the thread every hour.
    # - start at 8? or 9?
    # - go every hour until... idk what time. maybe like 6 am? can still log attendance afterwards. 
    # priority 2:
    # detect if a command is sent to start a thread.
    # - allow including a channel
    # - allow including a threadname to create it as (for events besides hack-night itself)

client.run(CLIENT_TOKEN)

