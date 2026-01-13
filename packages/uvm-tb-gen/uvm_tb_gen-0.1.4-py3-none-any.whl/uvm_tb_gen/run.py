#!/usr/bin/python3

import os
from pathlib import Path

from uvm_tb_gen.tb_config import build_config
from uvm_tb_gen.uvm_component import component
from uvm_tb_gen.uvm_object import object
from uvm_tb_gen.interface import interface
from uvm_tb_gen.agent_pkg import agent_pkg
from uvm_tb_gen.environment_pkg import environment_pkg
from uvm_tb_gen.test_pkg import test_pkg
from uvm_tb_gen.top_module import top_module


# ----------------------------------------------------------------------
# Helper Functions
# ----------------------------------------------------------------------
def safe_mkdir(path: str):
    Path(path).mkdir(parents=True, exist_ok=True)
    os.chdir(path)

# ----------------------------------------------------------------------
# Create Testbench Directories
# ----------------------------------------------------------------------
def main():
    cfg = build_config()

    BASE_PATH = cfg["BASE_PATH"]
    TB_DIR = cfg["TB_DIR"]
    INTERFACES = cfg["INTERFACES"]
    AGENTS = cfg["AGENTS"]
    ENV = cfg["ENV"]
    TEST = cfg["TEST"]
    TOP_FILE = cfg["TOP"]
    INTERFACE_DIR = cfg["INTERFACE_DIR"]
    ENVIRONMENT_DIR = cfg["ENVIRONMENT_DIR"]
    TEST_DIR = cfg["TEST_DIR"]
    TOP_DIR = cfg["TOP_DIR"]
    SCOREBOARD = ENV["SCOREBOARD"]
    SUBSCRIBER = ENV["SUBSCRIBER"]
    ENV_CLASS = ENV["ENV_CLASS"]
    ENV_PKG_FILE = ENV["ENV_PKG_FILE"]
    SEQUENCE = TEST["SEQUENCE"]
    TEST_CLASS = TEST["TEST_CLASS"]
    TEST_PKG_FILE = TEST["TEST_PKG_FILE"]
    
    safe_mkdir(BASE_PATH)
    safe_mkdir(TB_DIR)

# ---------------- CREATE INTERFACES ------------------
    safe_mkdir(INTERFACE_DIR)
    interface_pkg_pwd = os.getcwd()

    for iface in INTERFACES:
        file_name = iface["file_name"]
        interface_name = iface["module_name"]
        interface(file_name, interface_name)
    
    os.chdir("../")
    
    # ---------------- CREATE AGENTS ----------------------
    agent_pkg_paths = []  # store paths of each agent
    agent_pkg_files = []  # store package files of each agent
    
    for idx, agent in enumerate(AGENTS, start=1):
        safe_mkdir(agent["dir"])
        agent_path = os.getcwd()
        agent_pkg_paths.append(agent_path)
    
        # ---------------- Create Transaction ----------------
        t_file = agent["transaction"]["file_name"]
        t_class = agent["transaction"]["class_name"]
        object(t_file, t_class, "uvm_sequence_item")
    
        # ---------------- Create Sequencer -----------------
        s_file = agent["sequencer"]["file_name"]
        s_class = agent["sequencer"]["class_name"]
        component(s_file, s_class, "uvm_sequencer", major=0,AGENTS=None)
    
        # ---------------- Create Driver --------------------
        d_file = agent["driver"]["file_name"]
        d_class = agent["driver"]["class_name"]
        component(d_file, d_class, "uvm_driver", major=0,AGENTS=None)
    
        # ---------------- Create Monitor -------------------
        m_file = agent["monitor"]["file_name"]
        m_class = agent["monitor"]["class_name"]
        component(m_file, m_class, "uvm_monitor", major=0,AGENTS=None)
    
        # ---------------- Create Agent Class ----------------
        a_file = agent["agent_class"]["file_name"]
        a_class = agent["agent_class"]["class_name"]
        component(a_file, a_class, "uvm_agent", major=1,AGENTS=None)
    
        # ---------------- Create Agent Package --------------
        pkg_file = agent["pkg_file_name"]
        pkg_name = pkg_file.replace(".sv", "")
        agent_pkg_files.append(pkg_file)
        agent_pkg(pkg_file, t_file, s_file, d_file, m_file, a_file, pkg_name)
    
        os.chdir("../")
    
    # ---------------- CREATE ENVIRONMENT -----------------
    safe_mkdir(ENVIRONMENT_DIR)
    environment_pkg_pwd = os.getcwd()
    
    # Scoreboard
    component(SCOREBOARD["file_name"], SCOREBOARD["class_name"], "uvm_scoreboard", major=0,AGENTS=None)
    # Subscriber
    component(SUBSCRIBER["file_name"], SUBSCRIBER["class_name"], "uvm_subscriber", major=0,AGENTS=None)
    # Environment class
    component(ENV_CLASS["file_name"], ENV_CLASS["class_name"], "uvm_env", major=2, AGENTS=AGENTS)
    
    # Environment package
    environment_pkg(ENV_PKG_FILE, SCOREBOARD["file_name"], SUBSCRIBER["file_name"], ENV_CLASS["file_name"], AGENTS)
    
    os.chdir("../")
    
    # ---------------- CREATE TEST ------------------------
    safe_mkdir(TEST_DIR)
    test_pkg_pwd = os.getcwd()
    
    # Sequence
    object(SEQUENCE["file_name"], SEQUENCE["class_name"], "uvm_sequence")
    # Test class
    component(TEST_CLASS["file_name"], TEST_CLASS["class_name"], "uvm_test", major=3,AGENTS=None)
    
    # Test package
    test_pkg(TEST_PKG_FILE, SEQUENCE["file_name"], TEST_CLASS["file_name"], AGENTS)
    
    os.chdir("../")
    
    # ---------------- CREATE TOP -------------------------
    safe_mkdir(TOP_DIR)
    top_pkg_pwd = os.getcwd()
    top_module(TOP_FILE["file_name"], TOP_FILE["module_name"], TEST_CLASS["class_name"])
    
    os.chdir("../")
    
    # ---------------- CREATE FILES.F ----------------------
    safe_mkdir("FILES")
    files_f_path = os.path.join(os.getcwd(), "files.f")
    
    with open(files_f_path, "w") as f:
        # Include directories
        f.write(f"+incdir+{interface_pkg_pwd}\n")
        for agent_path in agent_pkg_paths:
            f.write(f"+incdir+{agent_path}\n")
        f.write(f"+incdir+{environment_pkg_pwd}\n")
        f.write(f"+incdir+{test_pkg_pwd}\n")
        f.write(f"+incdir+{top_pkg_pwd}\n\n")
    
        # Source files
        for iface in INTERFACES:
            f.write(f"{os.path.join(interface_pkg_pwd, iface['file_name'])}\n")
        for pkg_file, pkg_path in zip(agent_pkg_files, agent_pkg_paths):
            f.write(f"{os.path.join(pkg_path, pkg_file)}\n")
        f.write(f"{os.path.join(environment_pkg_pwd, ENV_PKG_FILE)}\n")
        f.write(f"{os.path.join(test_pkg_pwd, TEST_PKG_FILE)}\n")
        f.write(f"{os.path.join(top_pkg_pwd, TOP_FILE['file_name'])}\n")
    
    # ---------------- CREATE WORKSPACE & MAKEFILE ----------
    safe_mkdir("../work_space")
    os.chdir("../work_space")
    
    with open("Makefile", "w") as f:
        f.write("""run :\n\tvcs -V -R -sverilog -full64 -debug_access+all -ntb_opts uvm -kdb -f ../FILES/files.f -l sanity.log +UVM_VERBOSITY=UVM_DEBUG
    """)
    
    os.chdir("../")
    
    # ---------------- PRINT COMPLETION MESSAGE ------------
    print(f"\n\nTESTBENCH CREATED SUCCESSFULLY AT LOCATION: {BASE_PATH}/{TB_DIR}")
    print(f"\nTO RUN SIMULATION GO TO: {BASE_PATH}/{TB_DIR}/work_space")
    print("\nRUN COMMAND: make run\n")

    pass

if __name__ == "__main__":
    main()

