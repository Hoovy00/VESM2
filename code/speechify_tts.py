# Don't overuse it can't be bothered to obfuscate it. It has a limited amount of credits about enough to run 5000 times with a 15 second clip.
api_key = "TxmdbaZY_N_aUwADv92NM6TQ8Ins3K5L2Fc4Afv23WY="
# Text to be converted into a WAV file that is subsequentially played when given a signal to.
tts_input = "This is but a start. Tis the start of my crazy adventures muahahaha. JUST KIDDING!"

import base64
import requests

resp = requests.post(
    "https://api.sws.speechify.com/v1/audio/speech",
    # Bearer is where the api key is.
    headers={f"Authorization": f"Bearer {api_key}"},
    # Input is the text that gets converted to speech. voice_id is the specific voice and audio format is how the stream of bytes we receive is formatted.
    json={"input": f"{tts_input}", "voice_id": "henry", "audio_format": "wav"}
)
payload = resp.json()

bdata = base64.b64decode(payload["audio_data"])  # raw bytes that are base64 encoded

# Path to write the wav file to on the esp32
out_path = "speech_test.wav"
# write bytes (wb) to out_path
with open(out_path, "wb") as f:
    f.write(bdata)
# All in all, from the point of making the request to having received and written it to the out_path around 2 seconds have elapsed.
# Obvious this could vary on the esp32 so we'll need to see if theres any significant delay. We can also choose to stream the ouput
# from the api straight into a local file which should reduce the speed it takes, only if neccessary though.
print("done writing")


# The api has a way to run asynchronously supposedly so it's worth check out if needed. Check documentation for further guidance.

# import asyncio

# from speechify import AsyncSpeechify

# client = AsyncSpeechify(
#     token="YOUR_TOKEN",
# )


# async def main() -> None:
#     await client.tts.audio.speech(
#         input="input",
#         voice_id="voice_id",
#     )