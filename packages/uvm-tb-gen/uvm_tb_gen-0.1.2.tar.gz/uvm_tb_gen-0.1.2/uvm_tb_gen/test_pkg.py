#!/usr/bin/python3

from pathlib import Path

def test_pkg(
    file_name: str,
    sequence_file_name: str,
    test_file_name: str,
    AGENTS: list
):
    # -----------------------------
    # Build dynamic agent imports
    # -----------------------------
    agent_imports = ""
    for agent in AGENTS:
        pkg_file = agent.get("pkg_file_name")
        if pkg_file:
            pkg_name = pkg_file.replace(".sv", "")  # Remove .sv for import
            agent_imports += f"    import {pkg_name}::*;\n"

    # -----------------------------
    # Test package template
    # -----------------------------
    template = f"""package test_package;
    import uvm_pkg::*;
    `include "uvm_macros.svh"

{agent_imports}    import environment_package::*;
    `include "{sequence_file_name}"
    `include "{test_file_name}"
endpackage
"""

    # Ensure the parent directory exists
    Path(file_name).parent.mkdir(parents=True, exist_ok=True)

    # Write the test package file
    with open(file_name, 'w') as f:
        f.write(template)

