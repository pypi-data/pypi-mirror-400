import json
from pathlib import Path

def init_project():
    config = {
        "modules_dir": "mathlib",
        "registry_base": (
            "https://raw.githubusercontent.com/"
            "thekavikumar/pyfetchmath/master/apps/registry"
        )
    }

    Path("pyfetchmath.json").write_text(
        json.dumps(config, indent=2)
    )

    print("✔ pyfetchmath initialized")
