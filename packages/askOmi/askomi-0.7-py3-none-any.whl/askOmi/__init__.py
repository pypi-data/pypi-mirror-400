import os
import subprocess

try:
    from google import genai
except ImportError:
    subprocess.check_call(["pip", "install", "google-genai"])
    from google import genai

def askOmi(error):

    api_key = "AIzaSyAV5C1p27F6z1zQ5eejm6Ax_JEN5qtopsg"
    
    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=error
    )
    return response.text


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

    # Delete output.py if it exists
    if os.path.exists("code.py"):
        os.remove("code.py")
        print("deleted")
    else:
        pass