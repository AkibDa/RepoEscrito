import google.generativeai as genai
import sys
import os
import json
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini API
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

def read_file_if_exists(filepath, max_chars=4000):
  """Read file contents safely with size limit."""
  if os.path.exists(filepath):
    try:
      with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
        if len(content) > max_chars:
          content = content[:max_chars] + "\n... [truncated]"
        return f"\n--- {os.path.basename(filepath)} ---\n{content}\n"
    except Exception as e:
      return f"\n--- {os.path.basename(filepath)} (error reading: {e}) ---\n"
  return ""

def parse_package_json(filepath):
  """Parse project name, description, dependencies from package.json."""
  if os.path.exists(filepath):
    try:
      with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        name = data.get("name")
        desc = data.get("description")
        deps = data.get("dependencies", {})
        dev_deps = data.get("devDependencies", {})
        return name, desc, f"\nDependencies: {deps}\nDevDependencies: {dev_deps}\n"
    except json.JSONDecodeError:
      return None, None, read_file_if_exists(filepath)
  return None, None, ""

def collect_project_context(root):
  """Walk project directory and collect important file contents."""
  context = ""
  include_exts = {".py", ".js", ".ts", ".json", ".toml", ".yml", ".yaml", ".md"}
  important_files = {"requirements.txt", "Dockerfile", "package.json", "setup.py", "pyproject.toml"}

  found_files = set()

  for dirpath, _, filenames in os.walk(root):
    for filename in filenames:
      filepath = os.path.join(dirpath, filename)
      ext = os.path.splitext(filename)[1]

      if filename in important_files or ext in include_exts:
        found_files.add(filename)
        context += read_file_if_exists(filepath)

  # Parse package.json separately
  pkg_name, pkg_desc, pkg_info = parse_package_json(os.path.join(root, "package.json"))
  context += pkg_info

  return context, pkg_name, pkg_desc, found_files

def generate_readme(root):
  context, pkg_name, pkg_desc, found_files = collect_project_context(root)

  # Auto-detect project name & description with placeholders
  project_name = pkg_name or "[ADD PROJECT NAME HERE]"
  description = pkg_desc or "[ADD PROJECT DESCRIPTION HERE]"

  # Decide installation placeholder vs actual
  if any(f in found_files for f in ["requirements.txt", "package.json", "Dockerfile", "setup.py", "pyproject.toml"]):
    installation_note = "Derive from provided files (requirements.txt / package.json / Dockerfile)."
  else:
    installation_note = "[ADD INSTALLATION INSTRUCTIONS HERE]"

  # Usage always starts as placeholder
  usage_note = "[ADD USAGE EXAMPLES HERE]"

  # Features placeholder
  features_note = "[ADD FEATURES HERE]"

  prompt = f"""
  Generate a professional GitHub README.md for a project named "{project_name}".
  Description: {description}.

  Here are the project files for context:
  {context}

  README must include:
  - Title & tagline
  - Project overview
  - Features ({features_note} if not inferable)
  - Installation ({installation_note})
  - Usage examples ({usage_note})
  - Tech stack
  - Contributing guidelines
  - License (leave as [ADD LICENSE INFO HERE] if not available)
  """

  response = model.generate_content(prompt)
  return response.text or ""

def main():
  if len(sys.argv) < 2:
    print("Usage: python prompt.py <project_directory>")
    sys.exit(1)

  project_dir = sys.argv[1]
  if not os.path.isdir(project_dir):
    print(f"❌ Error: {project_dir} is not a directory.")
    sys.exit(1)

  readme = generate_readme(project_dir)

  output_path = os.path.join(project_dir, "README.md")
  with open(output_path, "w", encoding="utf-8") as f:
    f.write(readme)

  print(f"✅ README.md generated successfully at {output_path}")

if __name__ == "__main__":
  main()
