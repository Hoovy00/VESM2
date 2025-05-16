import os, json, time, requests, paho.mqtt.client as mqtt
import base64

# ------------- CONFIG ----------------------------------------------------
ID = "vesm"                       # same stub the ESP uses
BROKER = "broker.emqx.io"
OPENAI_API_KEY = ""
MODEL = "gpt-4o-mini-2024-07-18"

TOPIC_IN = f"esp/prompt"
TOPIC_OUT = f"pi/wav"

SYSTEM_PROMPT = (
    "You are a ancient skeleton lich, mystical and a cryptic fortune teller."
    "You speak in both a poetic yet eerie tone with a hint of chaotic eccentricism."
    "Write a natural bridge between these two sentences so that they flow well."
    "The sentences are seperated by two pipe symbols ||"
    "The natural bridge should not be more than 5 words."
    "If the content mentions fortune then you can make the bridge 10 words or less long"
    "You should return the text that should be spoken to connect the two texts, nothing else."
)

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPENAI_API_KEY}",
}
# -------------------------------------------------------------------------

def speechifyTTS(prompt):
    api_key = ""
    print("started")
    # The voice id.
    voice_id = "853881d5-42f4-4ba4-a79b-526d9f9a9d93"
    # Text to be converted into a WAV file that is subsequentially played when given a signal to.
    tts_input = prompt

    resp = requests.post(
        "https://api.sws.speechify.com/v1/audio/speech",
        # Bearer is where the api key is.
        headers={f"Authorization": f"Bearer {api_key}"},
        # Input is the text that gets converted to speech. voice_id is the specific voice and audio format is how the stream of bytes we receive is formatted.
        json={"input": f"{tts_input}", "voice_id": f"{voice_id}", "audio_format": "wav", "response_type": "url"}
    )
    payload = resp.json()

    bdata = base64.b64decode(payload["audio_data"])  # raw bytes that are base64 encoded

    # Path to write the wav file to on the esp32
    out_path = "./hosting/pitest.wav"
    # write bytes (wb) to out_path
    with open(out_path, "wb") as f:
        f.write(bdata)

    print("done writing")

def ask_openai(question: str) -> str:
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": question}
        ],
        "temperature": 0.9,
        "max_tokens": 220
    }
    r = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()


def handle_telemetry(client, userdata, msg):
    """Called when ESP publishes a prompt."""
    try:
        print(client, userdata, msg.payload.decode())
        prompt = msg.payload.decode()
        print("ESP says ?", prompt)

        reply = ask_openai(prompt)
        print("OpenAI reply ?", reply)
        speechifyTTS(reply)
        client.publish(TOPIC_OUT, '1', qos=1)
        print("Sent to ESP on", TOPIC_OUT)

    except Exception as e:
        print("Error handling message:", e)


def main():
    mqttc = mqtt.Client()
    mqttc.connect(BROKER, 1883, keepalive=60)
    mqttc.on_message = handle_telemetry
    mqttc.subscribe(TOPIC_IN, qos=1)

    mqttc.loop_start()
    print("?  Waiting for prompts on", TOPIC_IN)
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        print("bye")
    finally:
        mqttc.loop_stop()
        mqttc.disconnect()


if __name__ == "__main__":
    main()
