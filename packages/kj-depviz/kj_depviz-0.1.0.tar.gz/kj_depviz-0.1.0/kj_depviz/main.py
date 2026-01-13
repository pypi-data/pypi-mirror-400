import sys
import uvicorn
import os
import shutil 
import tempfile 
import subprocess 
import re 
from textwrap import dedent # NEW: To fix markdown formatting
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from collections import defaultdict
from typing import Optional, List
from google import genai
import argparse

# --- 1. ROBUST PARSING LOGIC (UNCHANGED) ---
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        print("Error: Python 3.11+ or 'tomli' required.")
        sys.exit(1)

def ensure_uv_files_exist():
    """
    Checks for uv.lock. If missing but requirements.txt exists,
    it converts pip requirements to uv format via a temp directory.
    """
    if os.path.exists("uv.lock") and os.path.exists("pyproject.toml"):
        print("✅ UV project files found. Starting server...")
        return

    if not os.path.exists("requirements.txt"):
        print("ℹ️ No uv.lock or requirements.txt found. Starting with empty/dummy data.")
        return

    print("⚠️ 'uv.lock' not found, but 'requirements.txt' detected.")
    print("🔄 Converting to UV project format...")
    
    # Take Python version from user
    target_py_ver = input("👉 Please enter target Python version (e.g., 3.10, 3.11): ").strip()
    if not target_py_ver:
        target_py_ver = f"{sys.version_info.major}.{sys.version_info.minor}"
        print(f"   No input. Defaulting to system version: {target_py_ver}")

    requirements_path = os.path.abspath("requirements.txt")
    
    # 1. Get folder name (e.g., "My-Awesome-Project")
    cwd_name = os.path.basename(os.getcwd())
    # 2. Clean it: lowercase, replace spaces with dashes, remove special chars
    project_name = re.sub(r'[^a-z0-9\-]', '', cwd_name.lower().replace(" ", "-"))
    # 3. Fallback if name becomes empty
    if not project_name: project_name = "root-project"

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"   📂 Working in temp dir: {temp_dir}")
            
            # --- FIX: Pass --name explicitly ---
            print(f"   ⚙️ Initializing uv project '{project_name}'...")
            subprocess.run(
                ["uv", "init", "--name", project_name, "--no-workspace", "--python", target_py_ver], 
                cwd=temp_dir, 
                check=True,
                capture_output=True # Hide the noise
            )

            # 2. Add dependencies
            print("   📦 Resolving dependencies (this may take a moment)...")
            shutil.copy(requirements_path, os.path.join(temp_dir, "requirements.txt"))
            
            subprocess.run(
                ["uv", "add", "-r", "requirements.txt"], 
                cwd=temp_dir, 
                check=True,
                capture_output=True # Hide the noise
            )

            # 3. Copy back
            print("   💾 Saving pyproject.toml and uv.lock...")
            shutil.copy(os.path.join(temp_dir, "pyproject.toml"), ".")
            shutil.copy(os.path.join(temp_dir, "uv.lock"), ".")
            
            print("✅ Conversion complete!")

    except subprocess.CalledProcessError as e:
        print(f"❌ Error during conversion: {e}")
        # If capture_output=True, the error details are in e.stderr
        if e.stderr:
            print(f"   Details: {e.stderr.decode().strip()}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

def clean_name(name):
    return name.lower().replace("_", "-").strip()

def parse_graph_data():
    nodes = []
    edges = []
    
    try:
        with open("pyproject.toml", "rb") as f:
            pyproject = tomllib.load(f)
        with open("uv.lock", "rb") as f:
            uv_lock = tomllib.load(f)
    except FileNotFoundError:
        return get_dummy_data()

    project_info = pyproject.get("project", {})
    raw_name = project_info.get("name", "Project")
    project_id = clean_name(raw_name)
    python_ver = project_info.get("requires-python", "Unknown")
    root_id = "ROOT"

    # Maps
    ver_map = {} 
    deps_map = defaultdict(list)
    used_by_map = defaultdict(list)
    
    # Direct Deps
    direct_dep_ids = set()
    for d in project_info.get("dependencies", []):
        name_part = d.split(">")[0].split("<")[0].split("=")[0].split("[")[0]
        c_name = clean_name(name_part)
        direct_dep_ids.add(c_name)
        used_by_map[c_name].append("ROOT Project")

    # Lock File
    for pkg in uv_lock.get("package", []):
        p_name = clean_name(pkg.get("name"))
        if p_name == project_id: continue
        ver_map[p_name] = pkg.get("version", "?")
        p_deps = []
        for d in pkg.get("dependencies", []):
            if isinstance(d, str):
                d_clean = d.split(">")[0].split("<")[0].split("=")[0].split("[")[0]
                p_deps.append(clean_name(d_clean))
            elif isinstance(d, dict):
                p_deps.append(clean_name(d.get("name")))
        deps_map[p_name] = p_deps
        for child in p_deps:
            used_by_map[child].append(p_name)

    # Build Nodes
    added_ids = set()
    nodes.append({
        "data": {
            "id": root_id, 
            "label": raw_name,
            "sublabel": f"Py {python_ver}",
            "type": "root",
            "version": python_ver,
            "raw_version": python_ver,
            "deps_count": len(direct_dep_ids),
            "deps_list": list(direct_dep_ids),
            "used_by_count": 0,
            "used_by_list": []
        }
    })
    added_ids.add(root_id)

    def add_node_to_graph(n_id, n_ver, n_type):
        if n_id not in added_ids:
            nodes.append({
                "data": {
                    "id": n_id,
                    "label": n_id,
                    "sublabel": f"v{n_ver}",
                    "version": f"v{n_ver}",
                    "raw_version": n_ver,
                    "type": n_type,
                    "deps_count": len(deps_map.get(n_id, [])),
                    "deps_list": deps_map.get(n_id, []),
                    "used_by_count": len(used_by_map.get(n_id, [])),
                    "used_by_list": used_by_map.get(n_id, [])
                }
            })
            added_ids.add(n_id)

    transitive_count = 0
    for name, version in ver_map.items():
        if name in direct_dep_ids:
            ctype = "direct"
        else:
            ctype = "transitive"
            transitive_count += 1
        add_node_to_graph(name, version, ctype)

    # Build Edges
    for dep_id in direct_dep_ids:
        if dep_id not in added_ids:
            add_node_to_graph(dep_id, ver_map.get(dep_id, "?"), "direct")
        edges.append({"data": {"source": root_id, "target": dep_id}})

    for parent, children in deps_map.items():
        for child in children:
            if child in added_ids:
                edges.append({"data": {"source": parent, "target": child}})

    return {
        "elements": nodes + edges,
        "stats": {
            "total": len(ver_map),
            "direct": len(direct_dep_ids),
            "transitive": transitive_count,
            "python_version": python_ver
        }
    }

def get_dummy_data():
    return {"elements": [], "stats": {"total":0, "direct":0, "transitive":0, "python_version": "3.x"}}

# --- 2. SERVER & SAAS UI ---
app = FastAPI()

# --- 3. NEW AI & PLAYGROUND BACKEND LOGIC ---
class AIRequest(BaseModel):
    api_key: str
    model: str 
    mode: str 
    package_name: Optional[str] = None
    target_version: str

class ModelListRequest(BaseModel):
    api_key: str

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    favicon_path = os.path.join(os.path.dirname(__file__), "dep.png")
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path)
    return HTMLResponse(status_code=404)

# --- HELPER FOR PLAYGROUND COMMANDS ---
def run_uv_command(args, cwd):
    """Runs a UV command in the specific directory and captures output."""
    try:
        # We set text=True to get string output, capture_output=True to get stdout/stderr
        result = subprocess.run(
            args, 
            cwd=cwd, 
            text=True, 
            capture_output=True, 
            check=True # Raises CalledProcessError on non-zero exit code
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        # Return False and the error output (stderr usually contains the conflict info)
        return False, e.stderr + "\n" + e.stdout
    except FileNotFoundError:
        return False, "Error: 'uv' executable not found. Please install uv."

@app.get("/data")
async def get_data():
    return parse_graph_data()

@app.post("/models")
async def list_models(req: ModelListRequest):
    try:
        client = genai.Client(api_key=req.api_key)
        models = []
        for m in client.models.list():
            models.append(m.name.split("/")[-1]) 
        models.sort(key=lambda x: "flash" not in x)
        return {"models": models}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid Key or Network Error: {str(e)}")

# --- EXISTING STATIC ANALYSIS ENDPOINT ---
@app.post("/analyze")
async def analyze_dependency(req: AIRequest):
    graph_data = parse_graph_data()
    elements = graph_data["elements"]
    dependencies_summary = []
    root_py_ver = "Unknown"
    
    for el in elements:
        data = el["data"]
        if "source" in data: continue 
        if data["type"] == "root":
            root_py_ver = data["raw_version"]
            continue
        
        used_by_str = ", ".join(data.get('used_by_list', []))
        dep_str = f"- {data['id']}=={data['raw_version']}"
        if used_by_str:
            dep_str += f"  <-- USED BY: [{used_by_str}]"
        dependencies_summary.append(dep_str)
    
    context_str = "\n".join(dependencies_summary)

    system_instruction = (
        "You are a strict Python Dependency Resolver (like pip or uv). "
        "Your job is to predict dependency conflicts based on the provided dependency tree. "
        "Do not be conversational. You must output your answer in the following specific Markdown format:\n\n"
        "## 🚦 VERDICT: [SAFE / CONFLICT / WARNING]\n"
        "**Risk Level:** [None / Low / High]\n\n"
        "### 💥 Conflict Source (The Culprit)\n"
        "*(If Safe, write 'None')*\n"
        "* **Package:** [Name of the existing package causing the issue]\n"
        "* **Constraint:** [e.g., 'pandas 1.5 requires numpy<2.0, but target is 2.1']\n\n"
        "### 📝 Technical Explanation\n"
        "[Brief, technical explanation of the resolution path or error.]"
    )
    
    user_prompt = ""
    
    if req.mode == "modify":
        user_prompt = f"""
        CURRENT STATE:
        Python: {root_py_ver}
        Dependencies:
        {context_str}
        
        ACTION:
        The user wants to **CHANGE** '{req.package_name}' to version '{req.target_version}'.
        
        ANALYSIS INSTRUCTIONS:
        1. Look at '{req.package_name}' in the list above. See who uses it (marked as <-- USED BY).
        2. Check if those parents (the packages using it) are compatible with version {req.target_version}.
        3. Check if {req.target_version} is compatible with Python {root_py_ver}.
        4. If a parent package requires an older version, that is a CONFLICT.
        
        Output the STRICT report.
        """
    elif req.mode == "add":
        user_prompt = f"""
        CURRENT STATE:
        Python: {root_py_ver}
        Dependencies:
        {context_str}
        
        ACTION:
        The user wants to **ADD** a new package '{req.package_name}' version '{req.target_version}'.
        
        ANALYSIS INSTRUCTIONS:
        1. Based on your knowledge of '{req.package_name} {req.target_version}', does it have requirements that conflict with the 'Dependencies' list above?
        2. Example: If adding 'scipy 1.10' requires 'numpy<1.23', but the list has 'numpy==1.26', that is a CONFLICT.
        3. Check Python {root_py_ver} compatibility.
        
        Output the STRICT report.
        """
    elif req.mode == "python_ver":
        user_prompt = f"""
        CURRENT STATE:
        Current Python: {root_py_ver}
        Dependencies:
        {context_str}
        
        ACTION:
        The user wants to **CHANGE Python Version** to '{req.target_version}'.
        
        ANALYSIS INSTRUCTIONS:
        1. Scan the dependencies list.
        2. Identify any packages that are known to be incompatible, deprecated, or broken on Python {req.target_version} (e.g. distutils removal in 3.12, syntax changes, binary wheel availability).
        3. If a major package (like numpy, pandas, tensorflow) in the list is too old for this new Python version, that is a CONFLICT.
        
        Output the STRICT report.
        """

    try:
        client = genai.Client(api_key=req.api_key)
        model_name = req.model if req.model else "gemini-1.5-flash"
        
        response = client.models.generate_content(
            model=model_name, 
            config={"system_instruction": system_instruction, "temperature": 0.3},
            contents=dedent(user_prompt)
        )
        return {"markdown": response.text}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- REPLACE THIS FUNCTION IN YOUR MAIN.PY ---

@app.post("/playground")
async def playground_simulation(req: AIRequest):
    """
    Simulates dependency changes in an isolated environment using real UV commands.
    If it fails, it asks Gemini to explain the error based on the CLI output.
    """
    
    # 1. Setup Temporary Directory (Sandbox)
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # 2. Replicate Project State
            if os.path.exists("pyproject.toml"):
                shutil.copy("pyproject.toml", temp_dir)
            if os.path.exists("uv.lock"):
                shutil.copy("uv.lock", temp_dir)
            
            # 3. Execution Logic
            success = False
            output_log = ""
            command_desc = ""

            if req.mode in ["add", "modify"]:
                pkg_str = f"{req.package_name}=={req.target_version}" if req.target_version else req.package_name
                command_desc = f"uv add {pkg_str}"
                success, output_log = run_uv_command(["uv", "add", pkg_str], cwd=temp_dir)

            elif req.mode == "python_ver":
                command_desc = f"Change Python to {req.target_version}"
                
                # A. Modify pyproject.toml
                toml_path = os.path.join(temp_dir, "pyproject.toml")
                if os.path.exists(toml_path):
                    with open(toml_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    # Regex replace requires-python
                    new_content = re.sub(
                        r'requires-python\s*=\s*".*?"', 
                        f'requires-python = ">={req.target_version}"', 
                        content
                    )
                    
                    with open(toml_path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                
                # B. Create venv
                success, venv_log = run_uv_command(["uv", "venv", "--python", req.target_version], cwd=temp_dir)
                
                if not success:
                    output_log = venv_log 
                else:
                    # C. Sync dependencies
                    success, sync_log = run_uv_command(["uv", "sync"], cwd=temp_dir)
                    output_log = venv_log + "\n\n" + sync_log

            # 4. Result Handling
            if success:
                formatted_success = dedent(f"""
                ## ✅ Simulation Successful

                **Command:** `{command_desc}`

                The dependency tree resolved without errors.

                <details class="terminal-logs">
                <summary><strong>📋 View Execution Log</strong></summary>

                ```bash
                {output_log}
                ```
                </details>
                """)
                return {
                    "status": "success",
                    "markdown": formatted_success
                }
            
            else:
                # 5. FAILURE -> GENAI ANALYSIS
                client = genai.Client(api_key=req.api_key)
                
                # --- SUPER-CHARGED PROMPT FOR EXPERT INSIGHT ---
                system_instruction = dedent("""
                You are an elite Python Packaging & DevOps Engineer. Your job is to analyze failed dependency resolution logs from 'uv' and translate them into actionable, high-level insights for a developer.

                **ANALYSIS RULES:**
                1.  **Identify the Root Cause:** Don't just read the error. Interpret it.
                    * If it's a "Build Failure" (CMake/gcc error), it usually means the Python version is too new (no binary wheels exist yet) or the OS is missing compilers.
                    * If it's a "Resolution Impossible", it's a mathematical conflict between two package requirements.
                2.  **Be Strategic:** Don't just say "install X". Explain the trade-offs.
                3.  **Tone:** Professional, technical, concise, and helpful.

                **REQUIRED OUTPUT FORMAT (Markdown):**

                ### 🛑 The Blocker
                * **Package:** `[Name of the package failing]`
                * **Issue:** [One sentence summary, e.g., "Missing binary wheels for Python 3.14" or "Incompatible version constraint with pandas"]

                ### 🧠 Expert Insight
                [A deep-dive paragraph. Explain *why* this is happening. E.g., "You are trying to use Python 3.14, which is in pre-release. Complex libraries like PyArrow rely on C++ extensions. They have not released compiled wheels for 3.14 yet, forcing your computer to try (and fail) to compile it from scratch."]

                ### ⚡ Recommended Strategy
                * **Option A (Recommended):** [The best fix, e.g., "Downgrade Python to 3.12 (Stable)."]
                * **Option B (Alternative):** [The workaround, e.g., "Wait for library updates or install Visual Studio C++ Build Tools."]
                """)
                
                prompt = f"""
                CONTEXT: The user ran `{command_desc}`.
                
                RAW ERROR LOG FROM UV:
                {output_log}
                """
                
                response = client.models.generate_content(
                    model=req.model if req.model else "gemini-1.5-flash",
                    config={"system_instruction": system_instruction},
                    contents=dedent(prompt)
                )
                
                formatted_markdown = dedent(f"""
                ## ❌ Simulation Failed

                **Command:** `{command_desc}`

                {response.text}

                <br>

                <details class="terminal-logs">
                <summary><strong>📜 View Raw Error Log</strong> (Debug Info)</summary>

                ```bash
                {output_log}
                ```
                </details>
                """)
                
                return {
                    "status": "error",
                    "markdown": formatted_markdown
                }

        except Exception as e:
            return {
                "status": "error",
                "markdown": f"## ⚠️ System Error\n\nFailed to run simulation.\n\nError: {str(e)}"
            }
        
@app.get("/", response_class=HTMLResponse)
async def get_ui():
    return """
    <!DOCTYPE html>
    <html lang="en" class="dark">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DependencyViz</title>
        
        <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.26.0/cytoscape.min.js"></script>
        <script src="https://unpkg.com/dagre@0.8.5/dist/dagre.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/cytoscape-dagre@2.5.0/cytoscape-dagre.min.js"></script>
        <script src="https://unpkg.com/@popperjs/core@2"></script>
        <script src="https://unpkg.com/tippy.js@6"></script>
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script> <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        
        <script src="https://cdn.tailwindcss.com"></script>
        <script>
            tailwind.config = {
                darkMode: 'class',
                theme: {
                    extend: {
                        fontFamily: { sans: ['Inter', 'sans-serif'], mono: ['JetBrains Mono', 'monospace'] },
                        colors: {
                            zinc: { 850: '#1f1f22', 900: '#18181b', 950: '#09090b' },
                            accent: { 500: '#6366f1', 600: '#4f46e5' },
                            ai: { 500: '#8b5cf6', 600: '#7c3aed' },
                            uv: { 500: '#10b981', 600: '#059669' }
                        }
                    }
                }
            }
        </script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">

        <style>
            body { transition: background-color 0.3s, color 0.3s; overflow: hidden; }
            
            /* Backgrounds */
            .dark body { background-color: #050505; background-image: radial-gradient(#27272a 1px, transparent 0); background-size: 24px 24px; }
            html:not(.dark) body { background-color: #f8fafc; background-image: radial-gradient(#e2e8f0 1px, transparent 0); background-size: 24px 24px; }

            /* Glassmorphism */
            .glass-panel { backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border: 1px solid; transition: all 0.3s; }
            .dark .glass-panel { background: rgba(18, 18, 18, 0.75); border-color: rgba(255, 255, 255, 0.08); box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3); }
            html:not(.dark) .glass-panel { background: rgba(255, 255, 255, 0.85); border-color: rgba(0, 0, 0, 0.05); box-shadow: 0 4px 15px -3px rgba(0, 0, 0, 0.1); }

            /* Text & Colors */
            .text-main { color: #f4f4f5; } html:not(.dark) .text-main { color: #0f172a; }
            .text-muted { color: #a1a1aa; } html:not(.dark) .text-muted { color: #64748b; }
            
            #cy { width: 100vw; height: 100vh; position: absolute; top: 0; left: 0; z-index: 0; }
            
            /* Custom Range Slider */
            input[type=range] { -webkit-appearance: none; background: transparent; }
            input[type=range]::-webkit-slider-thumb { -webkit-appearance: none; height: 14px; width: 14px; border-radius: 50%; background: #6366f1; cursor: pointer; margin-top: -5px; }
            input[type=range]::-webkit-slider-runnable-track { width: 100%; height: 4px; cursor: pointer; background: #3f3f46; border-radius: 2px; }
            html:not(.dark) input[type=range]::-webkit-slider-runnable-track { background: #cbd5e1; }

            /* Hover Tooltip */
            #hover-tooltip { position: absolute; pointer-events: none; z-index: 9999; padding: 6px 10px; border-radius: 6px; font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 500; transform: translate(-50%, -150%); opacity: 0; transition: opacity 0.1s; white-space: nowrap; box-shadow: 0 4px 12px rgba(0,0,0,0.2); }
            .dark #hover-tooltip { background: #18181b; color: #fff; border: 1px solid #3f3f46; }
            html:not(.dark) #hover-tooltip { background: #fff; color: #0f172a; border: 1px solid #e2e8f0; }

            /* --- FIXED MARKDOWN STYLES --- */
            .markdown-body { font-size: 0.85rem; line-height: 1.6; color: inherit; }
            .dark .markdown-body { color: #e4e4e7; } 
            
            /* Enhanced Headers */
            .markdown-body h2 { font-weight: 700; margin-top: 0.5em; margin-bottom: 0.5em; color: #ef4444; border-bottom: 1px solid rgba(239, 68, 68, 0.2); padding-bottom: 4px; }
            .markdown-body h3 { font-weight: 600; margin-top: 1.2em; margin-bottom: 0.4em; color: #a78bfa; }
            
            .markdown-body p { margin-bottom: 0.8em; }
            .markdown-body ul { list-style-type: disc; padding-left: 1.5em; margin-bottom: 0.8em; }
            .markdown-body strong { color: #f4f4f5; font-weight: 700; }
            html:not(.dark) .markdown-body strong { color: #000; }
            
            /* Inline code */
            .markdown-body code { background: rgba(100,100,100,0.2); padding: 2px 4px; border-radius: 4px; font-family: 'JetBrains Mono', monospace; font-size: 0.9em; }

            /* Add spacing between list items */
            .markdown-body li {
                margin-bottom: 0.5em; 
            }

            /* Ensure ordered lists have numbers */
            .markdown-body ol {
                list-style-type: decimal;
                padding-left: 1.5em;
                margin-bottom: 0.8em;
            }
            /* --- DROPDOWN STYLES --- */
            .dark select option { background-color: #18181b; color: #f4f4f5; }
            select { color-scheme: light dark; } 
            
            /* --- NEW TERMINAL LOGS STYLING --- */
            details.terminal-logs {
                background: #09090b;
                border: 1px solid #27272a;
                border-radius: 8px;
                overflow: hidden;
                margin-top: 1rem;
            }
            details.terminal-logs summary {
                padding: 8px 12px;
                cursor: pointer;
                font-size: 0.7rem;
                font-weight: 600;
                color: #a1a1aa;
                background: #18181b;
                user-select: none;
                transition: color 0.2s;
                list-style: none;
                border-bottom: 1px solid #27272a;
            }
            details.terminal-logs summary::-webkit-details-marker { display: none; }
            details.terminal-logs summary:hover { color: #f4f4f5; background: #27272a; }
            details.terminal-logs summary:after { content: "+"; float: right; font-weight: bold; }
            details[open].terminal-logs summary:after { content: "-"; }
            
            /* The actual terminal block */
            details.terminal-logs pre { 
                margin: 0 !important; 
                border-radius: 0 !important; 
                background: #000000 !important; /* Pure Black */
                padding: 1rem !important;
                overflow-x: auto;
            }
            details.terminal-logs code { 
                background: transparent !important;
                padding: 0 !important;
                display: block; 
                font-family: 'JetBrains Mono', monospace; 
                font-size: 0.7rem !important; 
                line-height: 1.5;
                color: #d4d4d8; /* Light Grey Text */
                white-space: pre; /* Keep formatting */
            }
        </style>
    </head>
    <body class="antialiased selection:bg-accent-500 selection:text-white">

        <div id="hover-tooltip">v1.0.0</div>

        <div class="fixed top-6 left-6 z-40">
            <div class="glass-panel rounded-2xl p-5 w-64 flex flex-col gap-4">
                <div class="flex items-center gap-3">
                    <div class="w-8 h-8 rounded-lg bg-indigo-500/20 flex items-center justify-center text-indigo-500"><i class="fas fa-cubes text-lg"></i></div>
                    <div>
                        <h1 class="font-bold text-sm text-main leading-tight">DependencyViz</h1>
                        <p class="text-[10px] text-muted font-medium uppercase tracking-wider">Graph Explorer</p>
                    </div>
                </div>
                <div class="h-px bg-zinc-800/50 dark:bg-zinc-800/50 bg-slate-200"></div>
                <div class="flex flex-col gap-2.5">
                    <div class="flex items-center gap-3 text-xs font-medium text-muted"><div class="w-2.5 h-2.5 rounded bg-yellow-500 shadow-[0_0_8px_rgba(234,179,8,0.4)]"></div><span class="text-main">Root Project</span></div>
                    <div class="flex items-center gap-3 text-xs font-medium text-muted"><div class="w-2.5 h-2.5 rounded bg-orange-500 shadow-[0_0_8px_rgba(249,115,22,0.4)]"></div><span class="text-main">Direct Deps</span></div>
                    <div class="flex items-center gap-3 text-xs font-medium text-muted"><div class="w-2.5 h-2.5 rounded bg-sky-500 shadow-[0_0_8px_rgba(14,165,233,0.4)]"></div><span class="text-main">Transitive Deps</span></div>
                </div>
                <div class="bg-zinc-500/5 rounded-lg p-3 border border-zinc-500/10">
                    <p class="text-[10px] text-muted leading-relaxed">
                        <i class="fas fa-mouse-pointer mr-1 opacity-70"></i> <b>Single-click</b> to view details.<br>
                        <i class="fas fa-copy mr-1 opacity-70"></i> <b>Double-click</b> to copy ID.<br>
                        <i class="fas fa-eye mr-1 opacity-70"></i> <b>Hover</b> node for version.
                    </p>
                </div>
            </div>
        </div>

        <div class="fixed top-6 left-1/2 -translate-x-1/2 z-40">
            <div class="glass-panel rounded-full px-6 py-2.5 flex items-center gap-6">
                <div class="flex gap-6 text-xs font-medium uppercase tracking-wide text-muted">
                    <div class="flex flex-col items-center leading-none gap-1"><span id="stat-total" class="text-main text-sm font-bold font-mono">0</span><span>Total</span></div>
                    <div class="w-px h-6 bg-zinc-700/50"></div>
                    <div class="flex flex-col items-center leading-none gap-1"><span id="stat-direct" class="text-orange-500 text-sm font-bold font-mono">0</span><span>Direct</span></div>
                    <div class="w-px h-6 bg-zinc-700/50"></div>
                    <div class="flex flex-col items-center leading-none gap-1"><span id="stat-trans" class="text-sky-500 text-sm font-bold font-mono">0</span><span>Deep</span></div>
                </div>
            </div>
        </div>

        <div id="cy"></div>

        <div id="settings-popover" class="fixed bottom-24 left-1/2 -translate-x-1/2 z-50 glass-panel rounded-xl p-4 w-64 opacity-0 pointer-events-none transition-all duration-200 transform translate-y-4">
            <div class="text-xs font-bold text-muted uppercase tracking-wider mb-3 pb-2 border-b border-zinc-500/10">Graph Settings</div>
            
            <div class="mb-4">
                <div class="flex justify-between text-xs text-main mb-1">
                    <span>Edge Width</span>
                    <span id="val-width" class="font-mono text-muted">0.5px</span>
                </div>
                <input type="range" min="0.5" max="5" step="0.5" value="0.5" class="w-full" oninput="updateEdgeSettings('width', this.value)">
            </div>

            <div>
                <div class="flex justify-between text-xs text-main mb-1">
                    <span>Edge Visibility</span>
                    <span id="val-opacity" class="font-mono text-muted">100%</span>
                </div>
                <input type="range" min="0.1" max="1" step="0.1" value="1" class="w-full" oninput="updateEdgeSettings('opacity', this.value)">
            </div>
        </div>

        <div class="fixed bottom-8 left-1/2 -translate-x-1/2 z-40">
            <div class="glass-panel rounded-xl p-2 flex items-center gap-2">
                <div class="relative group">
                    <i class="fas fa-search absolute left-3 top-2.5 text-muted text-xs"></i>
                    <input type="text" id="search-box" placeholder="Search..." 
                        class="pl-8 pr-3 py-1.5 rounded-lg text-sm w-40 bg-transparent border border-transparent focus:border-indigo-500 focus:bg-zinc-500/10 text-main placeholder-zinc-500 outline-none transition-all"
                        onkeyup="if(event.key==='Enter') search()">
                </div>
                <div class="w-px h-5 bg-zinc-500/20 mx-1"></div>
                <button onclick="cy.zoom(cy.zoom()*1.2)" class="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-zinc-500/10 text-muted hover:text-indigo-500 transition"><i class="fas fa-plus text-xs"></i></button>
                <button onclick="cy.zoom(cy.zoom()*0.8)" class="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-zinc-500/10 text-muted hover:text-indigo-500 transition"><i class="fas fa-minus text-xs"></i></button>
                <button onclick="resetView()" class="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-zinc-500/10 text-muted hover:text-indigo-500 transition" title="Fit"><i class="fas fa-compress text-xs"></i></button>
                <div class="w-px h-5 bg-zinc-500/20 mx-1"></div>
                
                <button onclick="toggleSettings()" id="btn-settings" class="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-zinc-500/10 text-muted hover:text-indigo-500 transition" title="Graph Settings"><i class="fas fa-sliders-h text-xs"></i></button>
                
                <button onclick="toggleLayout()" class="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-zinc-500/10 text-muted hover:text-indigo-500 transition" title="Rotate Layout"><i class="fas fa-retweet text-xs"></i></button>
                <button onclick="toggleTheme()" class="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-zinc-500/10 text-muted hover:text-yellow-500 transition" title="Toggle Theme"><i class="fas fa-sun text-xs" id="theme-icon"></i></button>
                
                <button onclick="toggleAI()" id="btn-ai" class="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-ai-500/20 text-muted hover:text-ai-500 transition" title="AI Analyst"><i class="fas fa-wand-magic-sparkles text-xs"></i></button>

                <button onclick="exportPNG()" class="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-zinc-500/10 text-muted hover:text-indigo-500 transition" title="Save Image"><i class="fas fa-camera text-xs"></i></button>
            </div>
        </div>

        <div id="meta-drawer" class="fixed top-4 right-4 bottom-4 w-80 glass-panel rounded-2xl z-50 transform translate-x-[120%] transition-transform duration-300 flex flex-col shadow-2xl overflow-hidden">
            <div class="p-5 border-b border-zinc-500/10 flex justify-between items-start bg-zinc-500/5">
                <div>
                    <h2 id="meta-title" class="text-lg font-bold text-main break-all leading-snug">Package</h2>
                    <div class="flex items-center gap-2 mt-2">
                        <span id="meta-badge" class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider">ROOT</span>
                        <span id="meta-version" class="font-mono text-xs text-muted bg-zinc-500/10 px-1.5 py-0.5 rounded">v1.0.0</span>
                    </div>
                </div>
                <button onclick="closeDrawer()" class="text-muted hover:text-indigo-500 transition"><i class="fas fa-times"></i></button>
            </div>
            <div class="flex-1 overflow-y-auto p-5 space-y-6">
                <div>
                    <div class="flex items-center justify-between mb-3"><span class="text-[10px] uppercase font-bold text-muted tracking-wider">Used By</span><span id="meta-used-count" class="text-[10px] bg-zinc-500/10 text-muted px-1.5 rounded-full">0</span></div>
                    <ul id="meta-used-list" class="space-y-1"></ul>
                </div>
                <div>
                    <div class="flex items-center justify-between mb-3"><span class="text-[10px] uppercase font-bold text-muted tracking-wider">Dependencies</span><span id="meta-dep-count" class="text-[10px] bg-zinc-500/10 text-muted px-1.5 rounded-full">0</span></div>
                    <ul id="meta-dep-list" class="space-y-1"></ul>
                </div>
            </div>
        </div>

        <div id="ai-drawer" class="fixed top-4 left-4 bottom-4 w-96 glass-panel rounded-2xl z-50 transform -translate-x-[120%] transition-transform duration-300 flex flex-col shadow-2xl overflow-hidden">
             <div class="p-5 border-b border-zinc-500/10 flex justify-between items-center bg-ai-600/10">
                <div class="flex items-center gap-2">
                    <i class="fas fa-robot text-ai-500"></i>
                    <h2 class="text-md font-bold text-main">Conflict Analyst</h2>
                </div>
                <button onclick="toggleAI()" class="text-muted hover:text-ai-500 transition"><i class="fas fa-times"></i></button>
            </div>
            
            <div id="ai-setup-view" class="p-5 flex flex-col gap-4">
                 <div class="bg-zinc-500/5 p-4 rounded-lg border border-zinc-500/10">
                    <p class="text-xs text-muted mb-3">To analyze dependencies, please connect your Google Gemini API Key. It will be stored locally in your browser.</p>
                    <label class="block text-[10px] uppercase font-bold text-muted tracking-wider mb-1">Gemini API Key</label>
                    <div class="flex gap-2">
                        <input type="password" id="ai-api-key-input" placeholder="Paste Key..." 
                            class="flex-1 px-3 py-2 rounded-lg bg-zinc-500/10 border border-zinc-500/20 text-main text-xs focus:border-ai-500 outline-none transition-colors">
                        <button onclick="connectToGemini()" id="btn-connect" class="bg-ai-600 hover:bg-ai-500 text-white font-bold px-4 py-2 rounded-lg text-xs transition-colors">
                            Connect
                        </button>
                    </div>
                    <p id="setup-error" class="text-red-500 text-[10px] mt-2 hidden"></p>
                 </div>
            </div>

            <div id="ai-analysis-view" class="hidden flex flex-col h-full">
                <div class="px-5 pt-4 pb-2 border-b border-zinc-500/10 bg-zinc-500/5">
                    
                    <div class="flex items-center justify-between mb-4 gap-2">
                        <div class="flex-1">
                             <label class="block text-[10px] uppercase font-bold text-muted tracking-wider mb-1">Model</label>
                             <select id="ai-model-select" class="w-full px-2 py-1.5 rounded-lg bg-zinc-500/10 border border-zinc-500/20 text-main text-[10px] focus:border-ai-500 outline-none appearance-none font-mono">
                                <option>gemini-1.5-flash</option>
                             </select>
                        </div>
                        <div class="pt-4">
                            <button onclick="changeApiKey()" class="text-muted hover:text-red-400 text-[10px] underline" title="Change API Key">Change Key</button>
                        </div>
                    </div>

                    <div class="flex items-center justify-between mb-4 bg-zinc-900/50 p-1 rounded-lg border border-zinc-500/20">
                        <button onclick="setSimulationMode(false)" id="btn-mode-static" class="flex-1 py-1.5 text-[10px] font-bold uppercase tracking-wider rounded text-center transition-all bg-zinc-700 text-white shadow-sm">
                            <i class="fas fa-search mr-1"></i> Static Analysis
                        </button>
                        <button onclick="setSimulationMode(true)" id="btn-mode-sim" class="flex-1 py-1.5 text-[10px] font-bold uppercase tracking-wider rounded text-center text-muted hover:text-main transition-all">
                            <i class="fas fa-flask mr-1"></i> UV Playground
                        </button>
                    </div>

                    <div class="flex bg-zinc-500/10 rounded-lg p-1 mb-4">
                        <button onclick="setAIMode('modify')" id="tab-modify" class="flex-1 py-1.5 text-[10px] font-bold uppercase tracking-wider rounded text-center transition-all bg-ai-600 text-white shadow-md">Modify</button>
                        <button onclick="setAIMode('add')" id="tab-add" class="flex-1 py-1.5 text-[10px] font-bold uppercase tracking-wider rounded text-center text-muted hover:text-main transition-all">Add</button>
                        <button onclick="setAIMode('python_ver')" id="tab-python" class="flex-1 py-1.5 text-[10px] font-bold uppercase tracking-wider rounded text-center text-muted hover:text-main transition-all">Python</button>
                    </div>

                    <div id="ai-inputs" class="space-y-3">
                        <div id="input-modify-group">
                            <div class="flex justify-between items-end mb-1">
                                <label class="block text-[10px] uppercase font-bold text-muted tracking-wider">Select Package</label>
                                <span id="lbl-pkg-ver" class="text-[10px] font-mono text-accent-500"></span>
                            </div>
                            <select id="ai-pkg-select" onchange="updatePkgInfo()" class="w-full px-3 py-2 rounded-lg bg-zinc-500/10 border border-zinc-500/20 text-main text-xs focus:border-ai-500 outline-none mb-3 appearance-none">
                                <option>Loading...</option>
                            </select>
                            
                            <label class="block text-[10px] uppercase font-bold text-muted tracking-wider mb-1">Target Version</label>
                            <input type="text" id="ai-target-ver-mod" placeholder="e.g. 2.0.0 or <3.0" 
                                class="w-full px-3 py-2 rounded-lg bg-zinc-500/10 border border-zinc-500/20 text-main text-xs focus:border-ai-500 outline-none">
                        </div>

                        <div id="input-add-group" class="hidden">
                            <label class="block text-[10px] uppercase font-bold text-muted tracking-wider mb-1">New Package Name</label>
                            <input type="text" id="ai-new-pkg-name" placeholder="e.g. pandas" 
                                class="w-full px-3 py-2 rounded-lg bg-zinc-500/10 border border-zinc-500/20 text-main text-xs focus:border-ai-500 outline-none mb-3">
                            
                            <label class="block text-[10px] uppercase font-bold text-muted tracking-wider mb-1">Version</label>
                            <input type="text" id="ai-target-ver-add" placeholder="e.g. 1.5.0" 
                                class="w-full px-3 py-2 rounded-lg bg-zinc-500/10 border border-zinc-500/20 text-main text-xs focus:border-ai-500 outline-none">
                        </div>

                        <div id="input-python-group" class="hidden">
                             <div class="flex justify-between items-end mb-1">
                                <label class="block text-[10px] uppercase font-bold text-muted tracking-wider">New Python Version</label>
                                <span class="text-[10px] text-muted">Current: <span id="lbl-py-ver" class="text-accent-500 font-mono">?</span></span>
                             </div>
                            <input type="text" id="ai-python-ver" placeholder="e.g. 3.12" 
                                class="w-full px-3 py-2 rounded-lg bg-zinc-500/10 border border-zinc-500/20 text-main text-xs focus:border-ai-500 outline-none">
                        </div>
                    </div>

                    <button onclick="runAnalysis()" id="btn-analyze" class="w-full mt-4 bg-ai-600 hover:bg-ai-500 text-white font-bold py-2 rounded-lg text-xs tracking-wide transition-colors flex items-center justify-center gap-2">
                        <i class="fas fa-microchip" id="btn-icon"></i> <span id="btn-text">Analyze Conflicts</span>
                    </button>
                </div>

                <div class="flex-1 overflow-y-auto p-5 pb-20 bg-zinc-500/5 relative">
                    <div id="ai-loading" class="hidden absolute inset-0 flex flex-col items-center justify-center bg-zinc-900/50 backdrop-blur-sm z-10 text-muted gap-3">
                        <i class="fas fa-circle-notch fa-spin text-2xl text-ai-500"></i>
                        <span id="loading-text" class="text-xs animate-pulse">Consulting Gemini API...</span>
                    </div>
                    
                    <div id="ai-history-feed" class="flex flex-col gap-6">
                        <div id="ai-placeholder" class="text-center mt-10 opacity-50 text-xs italic">
                            Select an option and click Analyze to detect potential dependency conflicts.
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div id="toast" class="fixed bottom-24 left-1/2 -translate-x-1/2 glass-panel px-4 py-2 rounded-lg text-sm text-main opacity-0 pointer-events-none transition-all duration-300 transform translate-y-4 z-50 flex items-center gap-2">
            <i class="fas fa-check-circle text-emerald-500"></i><span id="toast-msg">Copied!</span>
        </div>

        <script>
            var cy;
            var currentLayout = 'TB';
            var activeNodeId = null; 
            var edgeWidth = 0.5;
            var edgeOpacity = 1.0;
            var allPackages = []; 
            var currentAiMode = 'modify';
            var currentApiKey = null;
            var isPlaygroundMode = false; // TRACK MODE

            const tooltip = document.getElementById('hover-tooltip');

            // --- INITIALIZATION ---
            var pkgVersions = {}; 
            var projectPyVer = "?"; 
            fetch('/data').then(r => r.json()).then(data => {
                document.getElementById('stat-total').innerText = data.stats.total;
                document.getElementById('stat-direct').innerText = data.stats.direct;
                document.getElementById('stat-trans').innerText = data.stats.transitive;
                
                projectPyVer = data.stats.python_version;
                document.getElementById('lbl-py-ver').innerText = projectPyVer;

                allPackages = [];
                pkgVersions = {};
                data.elements.forEach(e => {
                    if(e.data.type !== 'root' && !e.data.source) {
                        allPackages.push(e.data.id);
                        pkgVersions[e.data.id] = e.data.raw_version;
                    }
                });
                allPackages.sort();
                populatePkgDropdown();

                initGraph(data.elements);
            });

            // --- AI & API KEY LOGIC ---
            
            const storedKey = localStorage.getItem('gemini_api_key');
            if(storedKey) {
                document.getElementById('ai-api-key-input').value = storedKey;
                connectToGemini(storedKey); 
            }

            function toggleAI() {
                const drawer = document.getElementById('ai-drawer');
                const btn = document.getElementById('btn-ai');
                
                if (drawer.classList.contains('-translate-x-[120%]')) {
                    drawer.classList.remove('-translate-x-[120%]');
                    btn.classList.add('text-ai-500', 'bg-ai-500/20');
                } else {
                    drawer.classList.add('-translate-x-[120%]');
                    btn.classList.remove('text-ai-500', 'bg-ai-500/20');
                }
            }

            async function connectToGemini(keyOverride) {
                const key = keyOverride || document.getElementById('ai-api-key-input').value.trim();
                const errElem = document.getElementById('setup-error');
                const btn = document.getElementById('btn-connect');
                
                if(!key) {
                    errElem.innerText = "Please enter a key";
                    errElem.classList.remove('hidden');
                    return;
                }

                btn.innerText = "Connecting...";
                btn.disabled = true;
                errElem.classList.add('hidden');

                try {
                    const response = await fetch('/models', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ api_key: key })
                    });
                    
                    const data = await response.json();

                    if(response.ok) {
                        currentApiKey = key;
                        localStorage.setItem('gemini_api_key', key);
                        populateModelDropdown(data.models);
                        switchView('analysis');
                    } else {
                        throw new Error(data.detail || "Invalid Key");
                    }
                } catch (e) {
                    errElem.innerText = e.message;
                    errElem.classList.remove('hidden');
                    localStorage.removeItem('gemini_api_key'); 
                } finally {
                    btn.innerText = "Connect";
                    btn.disabled = false;
                }
            }

            function changeApiKey() {
                currentApiKey = null;
                localStorage.removeItem('gemini_api_key');
                document.getElementById('ai-api-key-input').value = '';
                switchView('setup');
            }

            function switchView(viewName) {
                const setup = document.getElementById('ai-setup-view');
                const analysis = document.getElementById('ai-analysis-view');
                
                if(viewName === 'analysis') {
                    setup.classList.add('hidden');
                    analysis.classList.remove('hidden');
                } else {
                    setup.classList.remove('hidden');
                    analysis.classList.add('hidden');
                }
            }

            function populateModelDropdown(models) {
                const sel = document.getElementById('ai-model-select');
                sel.innerHTML = '';
                models.forEach(m => {
                    const opt = document.createElement('option');
                    opt.value = m;
                    opt.innerText = m;
                    sel.appendChild(opt);
                });
            }

            // --- NEW: SIMULATION MODE TOGGLE ---
            function setSimulationMode(enabled) {
                isPlaygroundMode = enabled;
                
                const btnStatic = document.getElementById('btn-mode-static');
                const btnSim = document.getElementById('btn-mode-sim');
                const actionBtn = document.getElementById('btn-analyze');
                const actionBtnText = document.getElementById('btn-text');
                const actionBtnIcon = document.getElementById('btn-icon');
                
                if (enabled) {
                    // Active Playground (Green)
                    btnSim.className = "flex-1 py-1.5 text-[10px] font-bold uppercase tracking-wider rounded text-center transition-all bg-uv-600 text-white shadow-sm";
                    btnStatic.className = "flex-1 py-1.5 text-[10px] font-bold uppercase tracking-wider rounded text-center text-muted hover:text-main transition-all";
                    
                    actionBtn.className = "w-full mt-4 bg-uv-600 hover:bg-uv-500 text-white font-bold py-2 rounded-lg text-xs tracking-wide transition-colors flex items-center justify-center gap-2";
                    actionBtnText.innerText = "Run UV Simulation";
                    actionBtnIcon.className = "fas fa-flask";
                } else {
                    // Active Static (Purple/Gray)
                    btnStatic.className = "flex-1 py-1.5 text-[10px] font-bold uppercase tracking-wider rounded text-center transition-all bg-zinc-700 text-white shadow-sm";
                    btnSim.className = "flex-1 py-1.5 text-[10px] font-bold uppercase tracking-wider rounded text-center text-muted hover:text-main transition-all";
                    
                    actionBtn.className = "w-full mt-4 bg-ai-600 hover:bg-ai-500 text-white font-bold py-2 rounded-lg text-xs tracking-wide transition-colors flex items-center justify-center gap-2";
                    actionBtnText.innerText = "Analyze Conflicts";
                    actionBtnIcon.className = "fas fa-microchip";
                }
            }

            function setAIMode(mode) {
                currentAiMode = mode;
                
                ['modify', 'add', 'python'].forEach(m => {
                    const el = document.getElementById('tab-' + m);
                    if (m === mode || (mode === 'python_ver' && m === 'python')) {
                        // Color depends on mode
                        const baseClass = "flex-1 py-1.5 text-[10px] font-bold uppercase tracking-wider rounded text-center transition-all text-white shadow-md ";
                        // We keep the tab selection neutral-ish or matching the theme. Let's stick to AI Purple for tabs to differentiate from main action.
                        el.className = baseClass + "bg-ai-600";
                    } else {
                        el.className = "flex-1 py-1.5 text-[10px] font-bold uppercase tracking-wider rounded text-center text-muted hover:text-main transition-all";
                    }
                });

                document.getElementById('input-modify-group').classList.add('hidden');
                document.getElementById('input-add-group').classList.add('hidden');
                document.getElementById('input-python-group').classList.add('hidden');

                if (mode === 'modify') document.getElementById('input-modify-group').classList.remove('hidden');
                if (mode === 'add') document.getElementById('input-add-group').classList.remove('hidden');
                if (mode === 'python_ver') document.getElementById('input-python-group').classList.remove('hidden');
            }

            function populatePkgDropdown() {
                const sel = document.getElementById('ai-pkg-select');
                sel.innerHTML = '';
                allPackages.forEach(pkg => {
                    const opt = document.createElement('option');
                    opt.value = pkg;
                    opt.innerText = pkg;
                    sel.appendChild(opt);
                });
                updatePkgInfo();
            }

            function updatePkgInfo() {
                const sel = document.getElementById('ai-pkg-select');
                const lbl = document.getElementById('lbl-pkg-ver');
                const val = sel.value;
                if(val && pkgVersions[val]) {
                    lbl.innerText = "Current: v" + pkgVersions[val];
                } else {
                    lbl.innerText = "";
                }
            }

            function addToHistory(mode, summary, content, isError=false) {
                const feed = document.getElementById('ai-history-feed');
                const placeholder = document.getElementById('ai-placeholder');
                if(placeholder) placeholder.remove();

                const item = document.createElement('div');
                item.className = "border-b border-zinc-500/10 pb-6 last:border-0 animation-fade-in";
                
                let badgeBg = "bg-zinc-500/20 text-main";
                if (isError) badgeBg = "bg-red-500/20 text-red-400";
                else if (mode === "SIMULATION") badgeBg = "bg-uv-500/20 text-uv-500"; // Green for Sim
                else if (mode === "STATIC AI") badgeBg = "bg-ai-500/20 text-ai-500"; // Purple for AI

                const contentHtml = marked.parse(content.replace(/^[\\s]+/gm, ''));
                const uniqueId = 'resp-' + Date.now();

                item.innerHTML = `
                    <div class="flex items-center justify-between mb-2">
                        <div class="flex items-center gap-2">
                            <span class="text-[10px] font-bold uppercase px-1.5 py-0.5 rounded ${badgeBg}">${mode}</span>
                            <span class="text-xs font-mono text-muted">${summary}</span>
                        </div>
                        <button onclick="copyContent('${uniqueId}')" class="text-muted hover:text-main transition-colors" title="Copy Analysis">
                            <i class="fas fa-copy text-xs"></i>
                        </button>
                    </div>
                    <div id="${uniqueId}" class="markdown-body text-xs text-main">${contentHtml}</div>
                `;
                feed.insertBefore(item, feed.firstChild);
            }

            async function copyContent(elementId) {
                 const el = document.getElementById(elementId);
                 if(el) {
                     try {
                        await navigator.clipboard.writeText(el.innerText);
                        showToast("Copied!");
                     } catch(err) {
                        showToast("Failed to copy");
                     }
                 }
            }

            async function runAnalysis() {
                if (!currentApiKey) { alert("API Key not set"); return; }
                const selectedModel = document.getElementById('ai-model-select').value;

                let reqData = { 
                    api_key: currentApiKey, 
                    model: selectedModel,
                    mode: currentAiMode, 
                    target_version: "" 
                };

                let summaryText = "";

                if (currentAiMode === 'modify') {
                    reqData.package_name = document.getElementById('ai-pkg-select').value;
                    reqData.target_version = document.getElementById('ai-target-ver-mod').value;
                    summaryText = `${reqData.package_name} -> ${reqData.target_version}`;
                } else if (currentAiMode === 'add') {
                    reqData.package_name = document.getElementById('ai-new-pkg-name').value;
                    reqData.target_version = document.getElementById('ai-target-ver-add').value;
                    summaryText = `+ ${reqData.package_name} ${reqData.target_version}`;
                } else if (currentAiMode === 'python_ver') {
                    reqData.target_version = document.getElementById('ai-python-ver').value;
                    summaryText = `Py -> ${reqData.target_version}`;
                }

                if (!reqData.target_version && currentAiMode !== 'modify') {
                    alert("Please specify a version.");
                    return;
                }

                const loader = document.getElementById('ai-loading');
                const loadingText = document.getElementById('loading-text');
                const btn = document.getElementById('btn-analyze');
                
                loader.classList.remove('hidden');
                loadingText.innerText = isPlaygroundMode ? "Running UV Simulation..." : "Consulting Gemini API...";
                
                btn.disabled = true;
                btn.classList.add('opacity-50', 'cursor-not-allowed');

                // SELECT ENDPOINT
                const endpoint = isPlaygroundMode ? '/playground' : '/analyze';

                try {
                    const response = await fetch(endpoint, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(reqData)
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        // Check logic: Playground API returns "status": "error" if uv failed, but HTTP 200
                        const isLogicalError = (isPlaygroundMode && data.status === 'error');
                        const modeLabel = isPlaygroundMode ? "SIMULATION" : "STATIC AI";
                        
                        addToHistory(modeLabel, summaryText, data.markdown, isLogicalError);
                    } else {
                        let errMsg = data.detail || 'Failed to analyze.';
                        if (response.status === 403 || errMsg.includes("429")) {
                             errMsg += " (Check Quota/Key)";
                        }
                        addToHistory("ERROR", "Request Failed", errMsg, true);
                    }
                } catch (e) {
                    addToHistory("ERROR", "Network Error", e.message, true);
                } finally {
                    loader.classList.add('hidden');
                    btn.disabled = false;
                    btn.classList.remove('opacity-50', 'cursor-not-allowed');
                }
            }


            // --- GRAPH LOGIC (UNCHANGED) ---

            function initGraph(elements) {
                cy = cytoscape({
                    container: document.getElementById('cy'),
                    elements: elements,
                    style: getGraphStyle(),
                    layout: { name: 'dagre', rankDir: 'TB', rankSep: 80, nodeSep: 20, padding: 50 }
                });

                cy.on('mouseover', 'node', function(e){
                    const node = e.target;
                    const ver = node.data('version');
                    tooltip.innerText = ver ? ver : 'unknown';
                    tooltip.style.opacity = '1';
                    const renderedPos = node.renderedPosition();
                    const container = document.getElementById('cy').getBoundingClientRect();
                    tooltip.style.left = (container.left + renderedPos.x) + 'px';
                    tooltip.style.top = (container.top + renderedPos.y - 25) + 'px';
                });

                cy.on('mouseout', 'node', function(e){ tooltip.style.opacity = '0'; });
                cy.on('drag', 'node', function(e){ tooltip.style.opacity = '0'; });

                cy.on('tap', 'node', function(evt){
                    const node = evt.target;
                    const clickedId = node.id();
                    if (activeNodeId === clickedId) { resetSelection(); } 
                    else {
                        activeNodeId = clickedId;
                        highlightNode(node);
                        openDrawer(node.data());
                    }
                });

                cy.on('tap', function(evt){ if(evt.target === cy){ resetSelection(); } });
                
                cy.on('dbltap', 'node', function(evt){
                    const d = evt.target.data();
                    const txt = `${d.id}==${d.raw_version}`;
                    navigator.clipboard.writeText(txt);
                    showToast(`Copied: ${txt}`);
                });
            }

            function getGraphStyle() {
                const isDark = document.documentElement.classList.contains('dark');
                const textColor = isDark ? '#f4f4f5' : '#0f172a';
                const nodeBg = isDark ? '#18181b' : '#ffffff';
                const borderColor = isDark ? '#3f3f46' : '#cbd5e1';
                const edgeColor = isDark ? '#ffffff' : '#000000';

                return [
                    {
                        selector: 'node',
                        style: {
                            'label': function(ele) { return "   " + ele.data('label') + "   "; },
                            'color': textColor,
                            'font-size': '12px', 'font-family': 'Inter', 'font-weight': 600,
                            'text-valign': 'center', 'text-halign': 'center', 'text-wrap': 'none',
                            'background-color': nodeBg,
                            'border-width': 1, 'border-color': borderColor,
                            'shape': 'round-rectangle', 'width': 'label', 'height': '34px', 'padding': '5px'
                        }
                    },
                    { selector: 'node[type="root"]', style: { 'border-color': '#eab308', 'border-width': 2, 'color': isDark ? '#fef08a' : '#854d0e', 'background-color': isDark ? '#422006' : '#fef9c3' } },
                    { selector: 'node[type="direct"]', style: { 'border-color': '#f97316', 'border-width': 1.5, 'color': isDark ? '#fed7aa' : '#9a3412', 'background-color': isDark ? '#431407' : '#ffedd5' } },
                    { selector: 'node[type="transitive"]', style: { 'border-color': '#0ea5e9', 'color': isDark ? '#bae6fd' : '#075985', 'background-color': isDark ? '#082f49' : '#e0f2fe' } },
                    {
                        selector: 'edge',
                        style: {
                            'width': edgeWidth, 
                            'line-color': edgeColor,
                            'opacity': edgeOpacity, 
                            'target-arrow-color': edgeColor, 'target-arrow-shape': 'triangle',
                            'curve-style': 'bezier', 'arrow-scale': 0.8
                        }
                    },
                    { selector: '.dimmed', style: { 'opacity': 0.1, 'filter': 'grayscale(100%)' } },
                    { selector: '.highlighted', style: { 'opacity': 1, 'z-index': 9999, 'border-color': '#6366f1', 'border-width': 2 } },
                    { selector: 'edge.highlighted', style: { 'line-color': '#6366f1', 'target-arrow-color': '#6366f1', 'width': 2.5, 'opacity': 1 } }
                ];
            }

            function toggleSettings() {
                const pop = document.getElementById('settings-popover');
                const btn = document.getElementById('btn-settings');
                
                if (pop.classList.contains('opacity-0')) {
                    pop.classList.remove('opacity-0', 'pointer-events-none', 'translate-y-4');
                    btn.classList.add('text-indigo-500', 'bg-zinc-500/10');
                } else {
                    pop.classList.add('opacity-0', 'pointer-events-none', 'translate-y-4');
                    btn.classList.remove('text-indigo-500', 'bg-zinc-500/10');
                }
            }

            function updateEdgeSettings(type, val) {
                if (type === 'width') {
                    edgeWidth = parseFloat(val);
                    document.getElementById('val-width').innerText = edgeWidth + 'px';
                }
                if (type === 'opacity') {
                    edgeOpacity = parseFloat(val);
                    document.getElementById('val-opacity').innerText = Math.round(edgeOpacity * 100) + '%';
                }
                if(cy) cy.style(getGraphStyle());
            }

            function highlightNode(node) {
                cy.elements().removeClass('dimmed highlighted');
                cy.elements().addClass('dimmed');
                node.removeClass('dimmed').addClass('highlighted');
                node.neighborhood().removeClass('dimmed').addClass('highlighted');
                node.connectedEdges().removeClass('dimmed').addClass('highlighted');
            }

            function resetSelection() {
                activeNodeId = null;
                cy.elements().removeClass('dimmed highlighted');
                cy.edges().removeClass('highlighted');
                closeDrawer();
            }

            function openDrawer(data) {
                document.getElementById('ai-drawer').classList.add('-translate-x-[120%]');
                document.getElementById('btn-ai').classList.remove('text-ai-500', 'bg-ai-500/20');

                const drawer = document.getElementById('meta-drawer');
                drawer.classList.remove('translate-x-[120%]');
                document.getElementById('meta-title').innerText = data.label;
                document.getElementById('meta-version').innerText = data.version || "unknown";
                
                const badge = document.getElementById('meta-badge');
                badge.innerText = data.type;
                if(data.type === 'root') badge.className = "px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-yellow-500/20 text-yellow-600 dark:text-yellow-400";
                else if(data.type === 'direct') badge.className = "px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-orange-500/20 text-orange-600 dark:text-orange-400";
                else badge.className = "px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-sky-500/20 text-sky-600 dark:text-sky-400";

                renderList('meta-dep-list', 'meta-dep-count', data.deps_list);
                renderList('meta-used-list', 'meta-used-count', data.used_by_list);
            }

            function closeDrawer() { document.getElementById('meta-drawer').classList.add('translate-x-[120%]'); }

            function renderList(elemId, countId, listData) {
                const ul = document.getElementById(elemId);
                document.getElementById(countId).innerText = listData ? listData.length : 0;
                ul.innerHTML = '';
                if (listData && listData.length > 0) {
                    listData.forEach(name => {
                        const li = document.createElement('li');
                        li.className = 'group flex items-center justify-between p-2 rounded-lg hover:bg-zinc-500/10 cursor-pointer transition';
                        li.innerHTML = `<span class="text-xs text-main font-mono">${name}</span> <i class="fas fa-arrow-right text-[10px] opacity-0 group-hover:opacity-100 text-indigo-500"></i>`;
                        li.onclick = () => jumpToNode(name);
                        ul.appendChild(li);
                    });
                } else { ul.innerHTML = '<li class="text-[10px] italic text-muted py-1">No connections</li>'; }
            }

            function jumpToNode(id) {
                const node = cy.getElementById(id);
                if(node.length) {
                    cy.animate({ fit: { eles: node, padding: 250 }, duration: 500 });
                    activeNodeId = node.id();
                    highlightNode(node);
                    openDrawer(node.data());
                }
            }

            function search() {
                const q = document.getElementById('search-box').value.toLowerCase();
                if(!q) return;
                const found = cy.nodes().filter(n => n.data('id').includes(q));
                if(found.length){
                    cy.animate({ fit: { eles: found, padding: 150 }, duration: 500 });
                    activeNodeId = found.id();
                    highlightNode(found);
                    openDrawer(found.data());
                }
            }

            function toggleLayout() {
                currentLayout = (currentLayout === 'TB') ? 'LR' : 'TB';
                cy.layout({ name: 'dagre', rankDir: currentLayout, rankSep: 80, nodeSep: 20, padding: 50, animate: true }).run();
            }

            function toggleTheme() {
                const html = document.documentElement;
                const icon = document.getElementById('theme-icon');
                if (html.classList.contains('dark')) {
                    html.classList.remove('dark');
                    icon.className = 'fas fa-moon text-xs';
                } else {
                    html.classList.add('dark');
                    icon.className = 'fas fa-sun text-xs';
                }
                if(cy) cy.style(getGraphStyle());
            }

            function resetView() { cy.animate({ fit: { eles: cy.elements(), padding: 50 }, duration: 500 }); }
            
            function exportPNG() {
                const a = document.createElement("a");
                a.href = cy.png({ full: true, scale: 2, bg: getComputedStyle(document.body).backgroundColor });
                a.download = "dependency-graph.png";
                a.click();
            }

            function showToast(msg) {
                const t = document.getElementById('toast');
                document.getElementById('toast-msg').innerText = msg;
                t.classList.remove('opacity-0', 'translate-y-4');
                setTimeout(() => t.classList.add('opacity-0', 'translate-y-4'), 2500);
            }
        </script>
    </body>
    </html>
    """

def start():
    """
    Entry point for the 'kj-depviz' command.
    """
    parser = argparse.ArgumentParser(description="Dependency Visualizer Tool")
    parser.add_argument("command", nargs="?", default="analysis", help="Command to run (e.g., 'analysis')")
    args = parser.parse_args()

    if args.command == "analysis":
        # Check files in the current directory where the user is running the command
        ensure_uv_files_exist()
        
        print("\n🚀 Starting KJ-DepViz Server...")
        print("👉 Open your browser at: http://127.0.0.1:8000")
        
        # We run uvicorn programmatically
        uvicorn.run(app, host="127.0.0.1", port=8000)
    else:
        print(f"Unknown command: {args.command}")
        print("Usage: kj-depviz analysis")

# This allows you to still test it with 'python -m depviz.main' if needed
if __name__ == "__main__":
    start()