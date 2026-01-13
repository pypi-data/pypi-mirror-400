#!/usr/bin/python3
from pathlib import Path

def agent_pkg(
    file_name: str,
    transaction_file_name: str,
    sequencer_file_name: str,
    driver_file_name: str,
    monitor_file_name: str,
    agent_file_name: str,
    pkg_name: str
):
    template = f"""package {pkg_name};
    import uvm_pkg::*;
    `include "uvm_macros.svh"
    `include "{transaction_file_name}"
    `include "{sequencer_file_name}"
    `include "{driver_file_name}"
    `include "{monitor_file_name}"
    `include "{agent_file_name}"
endpackage
"""

    # Ensure the parent directory exists
    Path(file_name).parent.mkdir(parents=True, exist_ok=True)

    # Write the package file
    with open(file_name, 'w') as f:
        f.write(template)

