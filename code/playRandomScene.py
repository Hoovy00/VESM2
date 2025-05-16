from machine import Pin, ADC
import asyncio
from lib.dfplayer import DFPlayer
import json
import random
import requests
df = DFPlayer(2)
df.init(tx=17, rx=16)

async def pickScene():
    with open("audio.json", "r") as f:
        data = f.read()
    audioDict = json.loads(data)
    print(len(audioDict["greeting"]))
    print(audioDict.keys())
    scene = []
    rand_greeting = [1, random.randint(1, len(audioDict["greeting"]))]
    rand_context = [2, random.randint(1, len(audioDict["context"]))]
    
    rand_quirks1 = [6, random.randint(1, len(audioDict["quirks"]))]
    rand_quirks2 = [6, random.randint(1, len(audioDict["quirks"]))]
    
    rand_reactions = [7, random.randint(1, len(audioDict["reactions"]))]
    
    rand_pre_fortune = [4, random.randint(1, len(audioDict["pre_fortune"]))]
    rand_post_fortune = [3, random.randint(1, len(audioDict["post_fortune"]))]
    rand_lore = [5, random.randint(1, len(audioDict["lore"]))]
    
    scene.append([rand_greeting, rand_reactions, rand_context, rand_quirks1, rand_quirks2, rand_pre_fortune, rand_post_fortune, rand_quirks1, rand_lore])
    
    await asyncio.sleep_ms(0)
    return scene

async def main():
    scenes = await pickScene()
    await df.wait_available()
    await df.volume(20)
    print(int(scenes[0][1][0]))
    for i in range(len(scenes[0])):
        folder = int(scenes[0][i][0])
        file = int(scenes[0][i][1])
        print(folder, file)
        print("play file nr", i)
        playing = await df.play(folder, file)  # folder 1, file 1
        await playing
        print("finished", i)
        await asyncio.sleep_ms(50)
    await asyncio.sleep_ms(0)  # þarf ekki í þessu tilfelli en má vera

asyncio.run(main())
