# biochemHH

**biochemHH** is a Python package developed by a wet lab researcher.

It provides tools for:
- **Batch-mode DNA cloning primer design**, prioritizing primer reuse
- **Protein-ligand interaction analysis**
- **Editing and processing of PDB, CIF, and GenBank (GB) files**


It can be used for:
- Studying of an underinvestigated protein (**module Homolog**)
- Preparing PDB inputs for AI protein design tools (**module StructureHH**)
- Analyzing PDB outputs from AI protein design tools (**module StructureHH**)
- Constructing plasmids for experimental protein screening (**module GBparser**)



## Quick Start (Installation & Accessing Example Files)

biochemHH is designed for wet lab scientists who may be new to programming.  
Ready-to-run example code blocks are provided to get started quickly.


**Step 0. Install Python and PyCharm**
  - Download and install the latest versions of Python and PyCharm.


**Step 1. Create a PyCharm project**
  - Go to File → New Project. A new window will open.
  - Change and record your ***project location*** shown at the top.
  - Keep the default settings (Project venv), then click `Create`.


**Step 2. Install biochemHH in your project environment**
  - Open CMD (Win+R → type `cmd` → Enter).
  - Run the following commands  
    (replace the path in the first line with your ***project location***):

```
cd "C:\Users\ees26\PycharmProjects\project3"
IF NOT EXIST .venv IF EXIST venv ren venv .venv
.\.venv\Scripts\activate.bat
pip install biochemHH
```

**Step 3. Copy example files to your working directory**
  - In your PyCharm project, create a new Python file named `temporary.py`.
  - Paste the code below into `temporary.py` and set your ***working directory*** (wd)  
    (no Chinese characters allowed).

```
from pathlib import Path
import shutil, importlib.resources as ir, biochemHH

wd = r'C:\Users\ees26\Desktop\playground3'  # replace the path with your working directory

Path(wd).mkdir(exist_ok=True)
with ir.as_file(ir.files(biochemHH)/"example_input") as src:
    shutil.copytree(src, wd, dirs_exist_ok=True) 
with ir.as_file(ir.files(biochemHH)/"example_script") as src:
    shutil.copytree(src, f'{wd}/example_script', dirs_exist_ok=True)
```

  - Right-click → Run `temporary.py`. This creates an `example_script` subfolder  
    in your ***working directory***, containing example scripts and `playground.py`.
 

**Step 4. Open `playground.py` and an example script in PyCharm**
  - Go to File → Open and navigate to the `example_script` folder.
  - Select `playground.py` and one of the `examples_{}.py` files, then click OK.


**Step 5. Working in the playground**
  - Set the same ***working directory*** in `playground.py` as in step 3.  
    ***All input/output files will be read/written in this folder***.
  - Copy a code block from the example and paste it into `playground.py`.
  - Modify variable values to your own data.
  - Right-click → Run `playground.py`.


**Step 6. Optional: download & install PYMOL for protein visualization**


## Suggested:
  - Do not modify the example scripts. Work only in the `playground.py`.
  - For beginners, start with these examples:
    - `examples_Cloning_(batch-mode).py`
    - `examples_Protein_analyses.py`
  - Run scripts in the PyCharm console (supports unlimited line length).  
    Terminal may truncate GBparser output due to line limits.
  - If you are new to Python, always copy example code blocks completely,  
    including the `# { ... # }` lines, to avoid indentation errors.

