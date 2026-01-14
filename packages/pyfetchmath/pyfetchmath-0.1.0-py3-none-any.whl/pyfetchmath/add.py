import json
import requests
from pathlib import Path

def add_component(name: str):
    config = json.loads(Path("pyfetchmath.json").read_text())

    base = config["registry_base"]

    registry_url = f"{base}/registry/{name}.json"
    registry = requests.get(registry_url).json()

    modules_dir = Path(config["modules_dir"])
    modules_dir.mkdir(exist_ok=True)

    for file in registry["files"]:
        file_url = f"{base}/templates/python/{file}"
        code = requests.get(file_url).text

        output = modules_dir / file
        output.write_text(code)

        print(f"✔ Added {output}")
