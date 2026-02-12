# Certified mesh bound (Arb / python-flint)

Companion code for the certified mesh maximum computation appearing in our forthcoming paper.

This repository contains a single script `cert_mesh_arb.py` that computes a **rigorous upper bound**
for a mesh maximum using Arb ball arithmetic via `python-flint` (FLINT/Arb bindings for Python).

## Requirements

- Python 3.11+ (3.12 is fine)
- `python-flint`

## Installation

### Windows (using a specific Python executable)

If your Python executable is `D:\python\python.exe`, then your commands are essentially correct:

```powershell
D:\python\python.exe -m pip install -U pip
D:\python\python.exe -m pip install -U python-flint
````

To verify the installation:

```powershell
D:\python\python.exe -c "from flint import arb, acb, ctx; print(ctx); print(arb.pi().str(20, radius=False))"
```

### macOS / Linux (venv recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -U python-flint
```

## Running the script

From the repository directory, run:

### Windows (PowerShell)

```powershell
D:\python\python.exe cert_mesh_arb.py --M 2000000 --dps 90 --workers 1
```

### macOS / Linux

```bash
python cert_mesh_arb.py --M 2000000 --dps 90 --workers 1
```

To use multiple CPU cores (faster):

```powershell
D:\python\python.exe cert_mesh_arb.py --M 2000000 --dps 90 --workers 8
```
