#!/bin/sh
# Setup AI 4K/3D Game Project on GitHub with Copilot automation
set -e

# 1️⃣ Clone your repo (تأكد من استبدال USERNAME و REPO_NAME)
git clone https://github.com/USERNAME/REPO_NAME.git
cd REPO_NAME

# 2️⃣ Add Copilot as collaborator with Write access
gh repo add-collaborator COPILOT_USERNAME --permission write

# 3️⃣ Fix permissions for the project folder
chmod -R u+w .

# 4️⃣ Create dependencies file
cat > requirements.txt <<'EOF'
fastapi
uvicorn[standard]
gitpython
httpx
transformers
sentence-transformers
faiss-cpu
EOF

# 5️⃣ Create README safely
echo "# AI 4K/3D Game Project" > README.md

# 6️⃣ Create AI Agent
cat > ai_agent.py <<'EOF'
import os
from fastapi import FastAPI
from git import Repo
from transformers import pipeline

app = FastAPI()
generator = pipeline("text-generation", model="gpt2")

@app.get("/generate_code")
def generate_code(prompt: str):
    result = generator(prompt, max_length=700)[0]['generated_text']
    file_path = "game_script.py"
    with open(file_path, "w") as f:
        f.write(result)
    # Commit + Push automatic
    repo = Repo(".")
    repo.git.add(file_path)
    repo.index.commit("AI generated 3D/4K game code")
    repo.remote(name="origin").push()
    return {"status": "ok", "file": file_path}
EOF

# 7️⃣ Setup GitHub Action to run AI automatically
mkdir -p .github/workflows
cat > .github/workflows/ai_build.yml <<'EOF'
name: AI 4K/3D Game Build

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Run AI Agent
      run: python ai_agent.py
EOF

# 8️⃣ Commit & push all setup
git add .
git commit -m "Initial AI 4K/3D Game Setup + Copilot automation"
git push origin main