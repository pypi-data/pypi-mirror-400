from pathlib import Path

def ask_int(prompt, min_val=0):
    while True:
        try:
            v = int(input(prompt))
            if v < min_val:
                raise ValueError
            return v
        except ValueError:
            print("Enter a valid number")

def ask_str(prompt):
    while True:
        v = input(prompt).strip()
        if v:
            return v
        print("Input cannot be empty")

def build_config():
    print("\n==============================================")
    print(" UVM TESTBENCH GENERATOR – INPUT GUIDELINES")
    print("==============================================\n")

    print("Please read carefully before entering inputs:\n")

    print("1. File names MUST:")
    print("   - End with '.sv'")
    print("   - Contain only letters, numbers, and underscores (_)")
    print("   - NOT contain spaces\n")

    print("2. Module/Class names are AUTO-DERIVED:")
    print("   - Module/Class name = file name without '.sv'")
    print("   - Do NOT enter module/class names manually\n")

    print("3. Avoid using SystemVerilog keywords as file names:")
    print("   - Examples to avoid: interface.sv, module.sv, class.sv")
    print("   - Examples to avoid: always.sv, begin.sv, end.sv\n")

    print("4. Agent, environment, and test names should be UNIQUE")
    print("   - Duplicate names may cause compilation issues\n")

    print("5. Directory names:")
    print("   - Should NOT contain spaces")
    print("   - Recommended: interface, agent, environment, test, top\n")

    print("6. Once inputs are accepted, files will be GENERATED automatically")
    print("   - Existing files with the same name may be overwritten\n")

    print("==============================================\n")

    print("\n=== UVM Testbench Configuration ===\n")

    base_path = Path.cwd()
    tb_dir = "TESTBENCH"
    INTERFACE_DIR = "INTERFACE"

    # ---------------- Interfaces ----------------
    interfaces = []
    n_if = ask_int("Number of interfaces: ", 1)
    

    for i in range(n_if):
        print(f"\nInterface {i+1}(eg. project_name_interface)")
        file_name = ask_str("  Interface file name (eg. project_name_interface_name.sv): ")
        if not file_name.endswith(".sv"):
                file_name += ".sv"
        module_name = file_name.replace(".sv", "")

        interfaces.append({
            "file_name": file_name,
            "module_name": module_name
        })

    # ---------------- Agents ----------------
    agents = []
    n_agents = ask_int("\nNumber of agents: ", 1)

    for i in range(n_agents):
        print(f"\nAgent {i+1}")
        agent_dir = ask_str("  Agent directory name(eg. project_name_agent_name): ").upper()
        if agent_dir.endswith(".SV"):
            agent_dir = agent_dir.replace(".SV", "")


        def block(name):
            file_name = ask_str(f"    {name} file name (format: <project>_{name.lower()}.sv, e.g. uart_{name.lower()}.sv): ")
        
            if not file_name.endswith(".sv"):
                file_name += ".sv"
        
            class_name = file_name.replace(".sv", "")

            return {
                "file_name": file_name,
                "class_name": class_name
            }
                
        agent = {
            "dir": agent_dir,
            "transaction": block("Transaction"),
            "sequencer": block("Sequencer"),
            "driver": block("Driver"),
            "monitor": block("Monitor"),
            "agent_class": block("Agent"),
            "pkg_file_name": f"{agent_dir}_pkg.sv"
        }

        agents.append(agent)

    # ---------------- Environment ----------------
    ENV_DIR = "ENVIRONMENT"
    scoreboard = {
    "file_name": "scoreboard.sv",
    "class_name": "scoreboard"
    }

    subscriber = {
        "file_name": "subscriber.sv",
        "class_name": "subscriber"
    }

    env_class = {
        "file_name": "environment.sv",
        "class_name": "environment"
    }

    env_pkg = "environment_pkg.sv"

    # ---------------- Test ----------------
    TEST_DIR = "TEST"
    sequence = {
        "file_name": "base_sequence.sv",
        "class_name": "base_sequence"
    }
    test_class = {
        "file_name": "test.sv",
        "class_name": "test"
    }
    test_pkg = "test_pkg.sv"

    # ---------------- Top ----------------
    TOP_DIR = "TOP"
    top_file = "top.sv"
    top_module = "tb_top"

    return {
        "BASE_PATH": base_path,
        "TB_DIR": tb_dir,

        "INTERFACE_DIR": INTERFACE_DIR,
        "ENVIRONMENT_DIR": ENV_DIR,
        "TEST_DIR": TEST_DIR,
        "TOP_DIR": TOP_DIR,

        "INTERFACES": interfaces,
        "AGENTS": agents,

        "ENV": {
            "SCOREBOARD": scoreboard,
            "SUBSCRIBER": subscriber,
            "ENV_CLASS": env_class,
            "ENV_PKG_FILE": env_pkg
        },

        "TEST": {
            "SEQUENCE": sequence,
            "TEST_CLASS": test_class,
            "TEST_PKG_FILE": test_pkg
        },

        "TOP": {
            "file_name": top_file,
            "module_name": top_module
        }
    }
    
