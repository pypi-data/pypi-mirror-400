#!/usr/bin/python3
from uvm_tb_gen.tb_config import *

def component(file_name: str, class_name: str, component_name: str, major: int,AGENTS:list):
    # -------------------------------------------------------------
    # 1. Register class-name globally EXACTLY like original code
    # -------------------------------------------------------------
    global driver_class_name, monitor_class_name, sequencer_class_name
    global agent_class_name, subscriber_class_name, scoreboard_class_name
    global environment_class_name, sequence_class_name

    if component_name == "uvm_driver":
        driver_class_name = class_name
    elif component_name == "uvm_monitor":
        monitor_class_name = class_name
    elif component_name == "uvm_sequencer":
        sequencer_class_name = class_name
    elif component_name == "uvm_agent":
        agent_class_name = class_name
    elif component_name == "uvm_env":
        environment_class_name = class_name
    elif component_name == "uvm_scoreboard":
        scoreboard_class_name = class_name
    elif component_name == "uvm_subscriber":
        subscriber_class_name = class_name
    elif component_name == "uvm_test":
        sequence_class_name = "base_sequence"

    # -------------------------------------------------------------
    # 2. Base template (single pass replace)
    # -------------------------------------------------------------
    base = f"""
class {class_name} extends {component_name};
    `uvm_component_utils({class_name})

    function new(string name="{class_name}", uvm_component parent=null);
        super.new(name, parent);
    endfunction

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);
    endfunction : build_phase

    function void connect_phase(uvm_phase phase);
        super.connect_phase(phase);
    endfunction : connect_phase

    virtual task run_phase(uvm_phase phase);
        super.run_phase(phase);
        `uvm_info("{class_name} ===> RUN_PHASE", "", UVM_DEBUG);
    endtask : run_phase

endclass : {class_name}
"""

    lines = base.splitlines(keepends=True)

    # -------------------------------------------------------------
    # 3. Insertion helper
    # -------------------------------------------------------------
    def insert_at(target, index):
        return lines[:index] + target + lines[index:]

    def replace_all(text_list, mapping):
        return [
            reduce(lambda x, kv: x.replace(kv[0], kv[1]), mapping.items(), line)
            for line in text_list
        ]

    # -------------------------------------------------------------
    # 4. MAJOR = 1 → AGENT CLASS MODIFICATIONS
    # -------------------------------------------------------------
    if major == 1:
        agent_inst = [
            f"\n\t{sequencer_class_name}\t{sequencer_class_name}_h;",
            f"\n\t{driver_class_name}\t{driver_class_name}_h;",
            f"\n\t{monitor_class_name}\t{monitor_class_name}_h;\n"
        ]

        agent_mem = [
            f"\t\t{sequencer_class_name}_h = {sequencer_class_name}::type_id::create(\"{sequencer_class_name}_h\", this);",
            f"\n\t\t{driver_class_name}_h = {driver_class_name}::type_id::create(\"{driver_class_name}_h\", this);",
            f"\n\t\t{monitor_class_name}_h = {monitor_class_name}::type_id::create(\"{monitor_class_name}_h\", this);\n"
        ]

        lines = insert_at(agent_inst, 3)
        lines = insert_at(agent_mem, 13)

    # -------------------------------------------------------------
    # 5. MAJOR = 2 → ENVIRONMENT CLASS
    # -------------------------------------------------------------
    elif major == 2:
        env_inst = [
            f"\n\t{scoreboard_class_name}\t{scoreboard_class_name}_h;",
            f"\n\t{subscriber_class_name}\t{subscriber_class_name}_h;\n"
        ]

        # Insert each agent inside these declarations
        for agent in AGENTS:
            nm = agent["agent_class"]["class_name"]
            env_inst.insert(-1, f"\n\t{nm}\t{nm}_h;")

        lines = insert_at(env_inst, 3)

        env_mem = [
            f"\n\t{scoreboard_class_name}_h = {scoreboard_class_name}::type_id::create(\"{scoreboard_class_name}_h\", this);",
            f"\n\t{subscriber_class_name}_h = {subscriber_class_name}::type_id::create(\"{subscriber_class_name}_h\", this);\n"
        ]

        for agent in AGENTS:
            nm = agent["agent_class"]["class_name"]
            env_mem.insert(0, f"\n\t{nm}_h = {nm}::type_id::create(\"{nm}_h\", this);")

        lines = insert_at(env_mem, 14)

    # -------------------------------------------------------------
    # 6. MAJOR = 3 → TEST CLASS
    # -------------------------------------------------------------
    elif major == 3:
        test_inst = [
            f"\n\t{environment_class_name}\t{environment_class_name}_h;",
            f"\n\t{sequence_class_name}\t{sequence_class_name}_h;\n"
        ]

        test_mem = [
            f"\t\t{environment_class_name}_h = {environment_class_name}::type_id::create(\"{environment_class_name}_h\", this);",
            f"\n\t\t{sequence_class_name}_h = {sequence_class_name}::type_id::create(\"{sequence_class_name}_h\", this);\n"
        ]

        lines = insert_at(test_inst, 3)
        lines = insert_at(test_mem, 12)

        # Insert topology print
        lines = insert_at(["\n\t\tuvm_top.print_topology();\n"], 18)

        # Insert pass/fail code
        pass_fail = [
            "\t", "    int err_count;\n", "    int fatal_count;\n",
            "    uvm_report_server server;\n",
            "\n    function void report_phase(uvm_phase phase);\n",
            "        super.report_phase(phase);\n",
            "        server = uvm_report_server::get_server();\n",
            "        err_count   = server.get_severity_count(UVM_ERROR);\n",
            "        fatal_count = server.get_severity_count(UVM_FATAL);\n",
            "        if (fatal_count == 0 && err_count == 0) begin\n",
            "            `uvm_info(\"*----------------------------------*\",\"\",UVM_NONE)\n"
            "            `uvm_info(\"**-------TEST STATUS : PASS-------**\",\"\",UVM_NONE)\n"
            "            `uvm_info(\"***------------------------------***\",\"\",UVM_NONE)\n",
            "        end\n",
            "        else begin\n",
            "            `uvm_info(\"*----------------------------------*\",\"\",UVM_NONE)\n"
            "            `uvm_info(\"**-------TEST STATUS : FAIL-------**\",\"\",UVM_NONE)\n"
            "            `uvm_info(\"***------------------------------***\",\"\",UVM_NONE)\n",
            "        end\n",
            "    endfunction : report_phase\n"
        ]

        lines = insert_at(pass_fail, 26)

    # -------------------------------------------------------------
    # 7. Subscriber write() injection
    # -------------------------------------------------------------
    if component_name == "uvm_subscriber":
        sub_write = [
            "\n    function void write(T t);\n",
            "        //sample the signals here\n",
            "    endfunction\n"
        ]
        lines = insert_at(sub_write, 20)

    # -------------------------------------------------------------
    # 8. Final file write
    # -------------------------------------------------------------
    with open(file_name, "w") as f:
        f.writelines(lines)

