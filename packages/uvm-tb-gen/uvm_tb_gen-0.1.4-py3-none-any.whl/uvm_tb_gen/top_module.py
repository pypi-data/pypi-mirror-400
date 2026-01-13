#!/usr/bin/python3

from pathlib import Path

def top_module(file_name: str, module_name: str, test_class_name: str):
    template = f"""import uvm_pkg::*;
`include "uvm_macros.svh"

module {module_name};

    // INSTANTIATE THE DESIGN HERE

    initial begin
        run_test("{test_class_name}");
    end

endmodule : {module_name}
"""

    # Ensure the parent directory exists
    Path(file_name).parent.mkdir(parents=True, exist_ok=True)

    # Write the file
    with open(file_name, "w") as f:
        f.write(template)

