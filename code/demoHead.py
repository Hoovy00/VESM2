import asyncio as aio
import ujson, random, gc, urequests
from mqtt_as import MQTTClient, config

from machine import Pin
from lib.dfplayer import DFPlayer
from wavplayer import WavPlayer
import neopixel

def do_connect():
    import machine, network
    SSID = "TskoliVESM"
    LYKILORD = "Fallegurhestur"
    wlan = network.WLAN()
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(SSID, LYKILORD)
        while not wlan.isconnected():
            machine.idle()
    #print('network config:', wlan.ipconfig('addr4'))
do_connect()

from machine import Pin, I2S
import ustruct
# # 
# # # ── open WAV file and extract header fields ──────────────────────────



print("wifi connected!!!")
# WIFI stillingar
config["ssid"] = "TskoliVESM"
config["wifi_pw"] = "Fallegurhestur"

# MQTT þjónninn
config["server"] = "broker.emqx.io" # eða broker.emqx.io (þarf að vera það sama á sendir og móttakara)
config["queue_len"] = 1
config["port"] = 1883

TOPIC_PROMPT = 'esp/prompt'   # where we send text → Pi
TOPIC_WAV_READY = 'pi/wav'       # Pi notifies wav is up
CLIENT_ID = 'lich_esp'

# DFPlayer on UART2
df = DFPlayer(2)
df.init(tx=17, rx=16)

# WAV player on I2S0

# ── GLOBAL SYNC EVENT ─────────────────────────────────────────────────────
wav_ready = aio.Event()
event = aio.Event()
# ── Load audio.json once ─────────────────────────────────────────────────
with open("audio.json") as f:
    AUDIO = ujson.load(f)

def pick_scene():
    print("picking scene")
    """ Return a list of tuples:
        (folder, file, category, text)
        with an 'fortune' placeholder in the right spot.
    """
    scene = []
    # greeting
    n = random.randint(1, len(AUDIO['greeting']))
    scene.append((1, n, 'greeting', AUDIO['greeting'][n-1]))
    # context
    n = random.randint(1, len(AUDIO['context']))
    scene.append((2, n, 'context', AUDIO['context'][n-1]))
    # quirks
    for _ in range(2):
        n = random.randint(1, len(AUDIO['quirks']))
        scene.append((6, n, 'quirks', AUDIO['quirks'][n-1]))
    # reaction
    n = random.randint(1, len(AUDIO['reactions']))
    scene.append((7, n, 'reactions', AUDIO['reactions'][n-1]))
    # pre-fortune
    n = random.randint(1, len(AUDIO['pre_fortune']))
    scene.append((4, n, 'pre_fortune', AUDIO['pre_fortune'][n-1]))
    # post-fortune
    n = random.randint(1, len(AUDIO['post_fortune']))
    scene.append((3, n, 'post_fortune', AUDIO['post_fortune'][n-1]))
    # lore
    n = random.randint(1, len(AUDIO['lore']))
    scene.append((5, n, 'lore', AUDIO['lore'][n-1]))
    print("finished picking scene")
    return scene

async def led_augu(color):
    # ── CONFIG ────────────────────────────────────────────────────────────────
    NUM_PIXELS = 8
    DATA_PIN   = 35       # change if you wired to a different GPIO
    BRIGHTNESS = 0.2      # scale 0.0–1.0 to avoid drawing too much current
    # ── SETUP ─────────────────────────────────────────────────────────────────
    pin = Pin(DATA_PIN, Pin.OUT)
    neo = neopixel.NeoPixel(pin, NUM_PIXELS)
    neo.fill([0, 0, 0]) # turns off ring
    neo.write()
    if color == 'red':
        neo.fill([0, 0, 0]) # turns off ring
        neo.write()
        neo.fill([0, 0, 244]) # turns off ring
        neo.write()
        return
    flag = True
    while True:
        if flag:
            # Good
            neo.fill([0, 50, 0]) #fills with a darker green
            neo.write()
            
        elif not flag:
            # bad
            neo.fill([50, 0, 0]) #fills with a darker red
            neo.write()
        flag = not flag
        await aio.sleep_ms(500)
        
            
        
def open_wav(path):
    f = open(path, "rb")
    if f.read(4) != b'RIFF':
        raise ValueError("Not a WAV file")
    f.seek(22)                       # NumChannels
    channels = ustruct.unpack("<H", f.read(2))[0]
    rate     = ustruct.unpack("<I", f.read(4))[0]
    f.seek(34)                       # BitsPerSample
    bits     = ustruct.unpack("<H", f.read(2))[0]
    # find the 'data' chunk
    while True:
        chunk_id = f.read(4)
        size     = ustruct.unpack("<I", f.read(4))[0]
        if chunk_id == b'data':
            break
        f.seek(size, 1)
    return f, channels, rate, bits, size    # leave file at data start
event_mp3 = aio.Event()
received_wav = False
finished_playing = False
# ── PLAYERS ────────────────────────────────────────────────────────────────
async def play_mp3(folder, file):
    global event_mp3
    await df.wait_available()
    await df.volume(10)

    print("starting mp3:", folder, file)
    done = await df.play(folder, file)  # returns awaitable
    await done                         # wait for actual end
    print("played mp3")
    finished_playing = True
    event_mp3.set()
    # gives us time for the MP3 to actually finish
    await aio.sleep_ms(50)

def download_and_play_wav():
    """Download the single tts.wav from Pi and play it."""
    global finished_playing, received_wav, event
    led_augu('red')
    resp = urequests.get("http://10.201.48.74:8000/pitest.wav", stream=True)        # no RAM blow-ups  :contentReference[oaicite:3]{index=3}
    print("downloading")
    with open("/tts.wav", "wb") as f:
        while True:
            chunk = resp.raw.read(4096)           # 4 kB DMA-friendly block
            if not chunk:
                break
            f.write(chunk)
    print("finished downloading file")
    resp.close()
    gc.collect()
    wav, ch, fs, bits, remaining = open_wav("tts.wav")

# Notes on pins i wrote: din=14 sck=20 bck=21 lck=47
# ── configure I2S TX channel ─────────────────────────────────────────
    audio = I2S(
        0,                                # use I2S peripheral 0
        sck = Pin(21),                    # BCK
        ws  = Pin(47),                    # LRCK
        sd  = Pin(14),                    # DIN
        # mck = Pin(0),                  # uncomment only if your DAC needs MCLK
        mode   = I2S.TX,
        bits   = bits,                    # 16 or 32
        format = I2S.STEREO if ch == 2 else I2S.MONO,
        rate   = fs,                      # sample-rate from the file
        ibuf   = 8192)                   # ~40 ms @ 44.1 kHz/16-bit stereo

# ── stream the samples ───────────────────────────────────────────────
    buf = bytearray(4096)
    while remaining > 0:
        n = wav.readinto(buf)
        if n == 0:
            break
        audio.write(buf[:n])
        remaining -= n

    audio.deinit()
    wav.close()
    # let it finish
    print("got here downloads")
    finished_playing = False
    received_wav = False
    import os
    os.remove('tts.wav')
    gc.collect()
    event.set()


# ── MQTT HANDLER ──────────────────────────────────────────────────────────
async def mqtt_handler(client):
    global received_wav, finished_playing, event_mp3
    async for topic, msg, _ in client.queue:
        print("played mp3")
        t = topic.decode()
        print("topic and msg:", t, msg.decode())
        if t == TOPIC_WAV_READY:
            if not finished_playing:
                event_mp3.wait()
                await download_and_play_wav()
            else:
                await download_and_play_wav()
        await aio.sleep_ms(10)
            
async def askrift(client):
    while True:
        await client.up.wait()
        client.up.clear()
        # Topik-ið (eitt eða fleiri) sem á að gerast áskrifandi að
        await client.subscribe(TOPIC_WAV_READY, 1)
        await aio.sleep_ms(1)

async def run_scene(client):
    scene = pick_scene()
    print("scene obj: ", scene)
    global finished_playing, received_wav
    # 1) play everything up to pre-fortune
    global event_mp3, event
    for i in range(len(scene)):
        folder = scene[i][0]
        idx = scene[i][1]
        cat = scene[i][2]
        text = scene[i][3]['id']
        print(folder, idx, cat, text)
        if i == 5:
            prompt = text + " {fill in the fortune here} " + scene[i+1][3]['id']
        elif i == len(scene):
            prompt = text + " || " + scene[i+1][3]['id']
        else:
            prompt = text + " || " + scene[i+1][3]['id']
        await client.publish(TOPIC_PROMPT, prompt, qos=1)
        if finished_playing:
            event.wait()
        await play_mp3(folder, idx)

async def main(client):
    await client.connect()
    #await client.subscribe(TOPIC_WAV_READY, 1)
    aio.create_task(askrift(client))
    # start consuming incoming messages
    aio.create_task(mqtt_handler(client))
    aio.create_task(led_augu('blue'))
    # run one scene
    await run_scene(client)
    # optionally loop or idle
    print("Scene complete.")

MQTTClient.DEBUG = True

# Búa til tilvik af MQTTClient og senda inn stillingarnar
client = MQTTClient(config)

# mqtt_as styður ekki context manager og því þarf að hafa try/finally í stað with
try:
# Ræsa async main fallið og senda þangað tilvik af client-num
    aio.run(main(client))
finally:
    client.close()
