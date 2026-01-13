#!/usr/bin/python3

from pathlib import Path

def interface(file_name: str, interface_name: str):
    template = f"""interface {interface_name};

    // DECLARE YOUR SIGNALS HERE

endinterface : {interface_name}
"""

    # Ensure the parent directory exists
    Path(file_name).parent.mkdir(parents=True, exist_ok=True)

    # Write the interface file
    with open(file_name, "w") as f:
        f.write(template)

