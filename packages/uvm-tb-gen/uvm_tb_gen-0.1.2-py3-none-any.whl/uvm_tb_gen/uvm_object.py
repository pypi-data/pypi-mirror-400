#!/usr/bin/python3

def object(file_name: str, class_name: str, object_name: str):

    template = f"""
class {class_name} extends {object_name};
    `uvm_object_utils({class_name})

    function new(string name="{class_name}");
        super.new(name);
    endfunction

endclass : {class_name}
"""

    # Write final template directly — no multiple read/replace passes
    with open(file_name, "w") as f:
        f.write(template.lstrip())

