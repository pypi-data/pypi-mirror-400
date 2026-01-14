import os
import subprocess
import base64

try:
    from google import genai
except ImportError:
    subprocess.check_call(["pip", "install", "--upgrade", "google-genai"])
    from google import genai


def askOmi(error):
    api_key = base64.b64decode(
        b"QUl6YVN5Q2UzVnp0R0xDNWpNT1RSRFRGcEpuSkhoV3BPU2N6aXcw"  # your encoded key
    ).decode()

    try:
        client = genai.Client(
            vertexai=True,   # 🔥 THIS IS THE KEY FIX
            api_key=api_key
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",   # 🔥 NOW VALID
            contents=error
        )
        return response.text

    except Exception as e:
        return f"# Gemini API error:\n# {e}"


def gen(error):
    reply = askOmi(error)

    with open("code.py", "w", encoding="utf-8") as f:
        f.write(reply)

    print("Done")
