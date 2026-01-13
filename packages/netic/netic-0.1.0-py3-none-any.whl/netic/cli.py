import sys
from netic.client import setapi, chat

def main():
    if len(sys.argv) < 2:
        print("Usage: netic setkey <key> | netic chat")
        return

    cmd = sys.argv[1]

    if cmd == "setkey":
        setapi(sys.argv[2])
        print("Clé API enregistrée")

    elif cmd == "chat":
        print("Netic chat lancé (Ctrl+C pour quitter)")
        try:
            while True:
                msg = input("> ")
                response = chat(msg)
                print(response)
        except KeyboardInterrupt:
            print("\nÀ bientôt")