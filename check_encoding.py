import os

for root, dirs, files in os.walk("."):
    for f in files:
        if f.endswith(".py"):
            path = os.path.join(root, f)
            try:
                with open(path, "r", encoding="utf-8") as fin:
                    fin.read()
            except UnicodeDecodeError as e:
                print("Arquivo problemático:", path, "|", str(e))
