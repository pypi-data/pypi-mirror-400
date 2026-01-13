# UVM Testbench Generator (uvm-tb-gen)

`uvm-tb-gen` is a Python-based command-line tool that automates the generation of complete UVM (Universal Verification Methodology) testbench architectures.  
It is designed to reduce repetitive boilerplate work and help verification engineers quickly bootstrap scalable and maintainable UVM environments.

# Features

- Interactive CLI-driven configuration
- Automatic generation of:
  - Interfaces
  - Transactions
  - Sequencers
  - Drivers
  - Monitors
  - Agents
  - Environment (env, scoreboard, subscriber)
  - Tests and sequences
  - Top-level module
- Supports multiple agents and interfaces
- Enforces consistent naming conventions
- Generates simulator-ready `files.f` and Makefile
- Works across Linux environments (bash, csh, HPC systems)

# Installation

```bash
pip install uvm-tb-gen

