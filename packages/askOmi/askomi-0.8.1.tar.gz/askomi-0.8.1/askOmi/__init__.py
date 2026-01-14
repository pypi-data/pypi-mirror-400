import os
import subprocess
import base64

try:
    from google import genai
except ImportError:
    subprocess.check_call(["pip", "install", "google-genai"])
    from google import genai


def askOmi(error):
    # base64-encoded API key (still hard-coded)
    api_key = base64.b64decode(
        b"QUl6YVN5Q2UzVnp0R0xDNWpNT1RSRFRGcEpuSkhoV3BPU2N6aXcw"  # <-- replace with encoded key
    ).decode()

    try:
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-1.5-flash",
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


def destroy():
    packages = ["google-genai", "askOmi"]

    for package in packages:
        try:
            subprocess.check_call(["pip", "uninstall", "-y", package])
        except subprocess.CalledProcessError:
            pass

    if os.path.exists("code.py"):
        os.remove("code.py")
        print("deleted")
