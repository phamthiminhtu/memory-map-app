# Quick Setup with uv (Recommended)

We recommend using [uv](https://github.com/astral-sh/uv) for faster dependency management:

```bash
# Option 1: Run the automated setup script
./scripts/setup.sh

# Option 2: Use the Makefile
make install
```

The script will:
1. Create a virtual environment at `~/workspace/memory-map-env`
2. Compile dependencies with locked versions
3. Install all packages using uv (much faster than pip)

**Run the application:**
```bash
source ~/workspace/memory-map-env/bin/activate  # Activate the environment
streamlit run app/main.py
```

**Other useful commands:**
```bash
make run        # Run the Streamlit app
make run-mcp    # Run the MCP server
make clean      # Remove virtual environment
make update     # Update all dependencies
```

**Note:** The virtual environment is stored at `~/workspace/memory-map-env` (or `%USERPROFILE%\workspace\memory-map-env` on Windows) to keep it separate from the project directory.