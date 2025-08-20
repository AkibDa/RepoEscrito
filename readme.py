import os
import json
import tomllib
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Model
model = genai.GenerativeModel("gemini-1.5-flash")

def extract_project_info():
  """
  Extracts project info from pyproject.toml, package.json, or requirements.txt
  """
  info = {
    "name": None,
    "description": None,
    "dependencies": [],
    "features": None,
    "usage": None,
    "license": None
  }

  # pyproject.toml
  if os.path.exists("pyproject.toml"):
    with open("pyproject.toml", "rb") as f:
      data = tomllib.load(f)
      project = data.get("project", {})
      info["name"] = project.get("name")
      info["description"] = project.get("description")
      info["dependencies"].extend(project.get("dependencies", []))

  # package.json
  elif os.path.exists("package.json"):
    with open("package.json", "r", encoding="utf-8") as f:
      data = json.load(f)
      info["name"] = data.get("name")
      info["description"] = data.get("description")
      deps = data.get("dependencies", {})
      info["dependencies"].extend(list(deps.keys()))

  # requirements.txt
  elif os.path.exists("requirements.txt"):
    with open("requirements.txt", "r", encoding="utf-8") as f:
      deps = f.read().splitlines()
      info["dependencies"].extend(deps)

  return info

def interactive_fill(info):
  """
  Ask the user for missing details interactively
  """
  if not info["name"]:
    info["name"] = input("📌 Enter project name: ").strip()

  if not info["description"]:
    info["description"] = input("📝 Enter project description: ").strip()

  if not info["features"]:
    features = input("✨ List main features (comma separated, or press Enter to skip): ").strip()
    if features:
      info["features"] = [f.strip() for f in features.split(",")]

  if not info["usage"]:
    usage = input("▶️ Provide usage examples (or press Enter to skip): ").strip()
    if usage:
      info["usage"] = usage

  if not info["license"]:
    license_choice = input("📄 Enter license type (e.g., MIT, Apache-2.0, GPL, or press Enter for None): ").strip()
    if license_choice:
      info["license"] = license_choice

  return info

def generate_readme(info: dict) -> str:
  """
  Generates a README.md content based on project info
  """
  prompt = f"""
  You are an expert open-source maintainer. Write a professional, clear, and well-structured README.md.

  Project Info:
  - Name: {info.get("name", "Unknown Project")}
  - Description: {info.get("description", "No description provided")}
  - Features: {", ".join(info.get("features", [])) if info.get("features") else "Not provided"}
  - Usage Examples: {info.get("usage", "Not provided")}
  - Dependencies/Technologies: {", ".join(info.get("dependencies", []))}
  - License: {info.get("license", "Not specified")}

  Requirements for README:
  - Project Title
  - Description
  - Features
  - Installation Instructions
  - Usage Examples
  - Technologies Used
  - Contributing Guidelines
  - License
  """

  response = model.generate_content(prompt)
  return response.text.strip()

if __name__ == "__main__":
  print("🚀 RepoEscrito - README Generator (Gemini API)\n")

  # Extract auto info
  project_info = extract_project_info()

  # Fill missing details interactively
  project_info = interactive_fill(project_info)

  print("\n📝 Generating README.md...\n")
  readme_content = generate_readme(project_info)

  # Save to README.md
  with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme_content)

  print("✅ README.md generated successfully! Check the file in your project directory.\n")
