#!/usr/bin/python3

from pathlib import Path

def environment_pkg(
    file_name: str,
    scoreboard_file_name: str,
    subscriber_file_name: str,
    environment_file_name: str,
    AGENTS: list
):
    # -----------------------------
    # Build dynamic agent imports
    # -----------------------------
    agent_imports = ""
    for agent in AGENTS:
        pkg_sv = agent["pkg_file_name"]           # e.g., "agent_pkg2.sv"
        pkg_base = pkg_sv.replace(".sv", "")      # e.g., "agent_pkg2"
        agent_imports += f"    import {pkg_base}::*;\n"

    # -----------------------------
    # Final template
    # -----------------------------
    template = f"""package environment_package;
    import uvm_pkg::*;
    `include "uvm_macros.svh"

{agent_imports}    `include "{scoreboard_file_name}"
    `include "{subscriber_file_name}"
    `include "{environment_file_name}"
endpackage
"""

    # Ensure the parent directory exists
    Path(file_name).parent.mkdir(parents=True, exist_ok=True)

    # Write the environment package file
    with open(file_name, 'w') as f:
        f.write(template)

