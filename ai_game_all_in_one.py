"""
AI 4K/3D Game Generator - ملف واحد شامل
- يولّد أكواد لعبة 3D/4K تلقائيًا
- يتكامل مع GitHub للمستودع مباشرة
- يشتغل كسيرفر API مع FastAPI
"""

import os
import subprocess
from fastapi import FastAPI
from git import Repo
from transformers import pipeline
import uvicorn

# -------------------------------
# 1️⃣ تثبيت المكتبات إذا لم تكن موجودة
# -------------------------------
def install_packages():
    try:
        import fastapi, uvicorn, git, transformers, httpx, sentence_transformers, faiss
    except ImportError:
        print("Installing required packages...")
        subprocess.check_call([ "pip", "install", "--upgrade", "pip" ])
        subprocess.check_call([ "pip", "install", "fastapi", "uvicorn[standard]", "gitpython", "httpx", "transformers", "sentence-transformers", "faiss-cpu" ])
        print("Packages installed successfully.")

install_packages()

# -------------------------------
# 2️⃣ إعداد FastAPI
# -------------------------------
app = FastAPI()
generator = pipeline("text-generation", model="gpt2")

# -------------------------------
# 3️⃣ API لتوليد أكواد اللعبة
# -------------------------------
@app.get("/generate_code")
def generate_code(prompt: str):
    """
    يولّد كود لعبة تلقائيًا بناءً على النص المطلوب
    """
    result = generator(prompt, max_length=700)[0]['generated_text']
    file_path = "game_script.py"
    with open(file_path, "w") as f:
        f.write(result)

    # Commit + Push تلقائي للمستودع
    try:
        repo = Repo(".")
        repo.git.add(file_path)
        repo.index.commit("AI generated 3D/4K game code")
        repo.remote(name="origin").push()
    except Exception as e:
        print("Git operation failed:", e)

    return {"status": "ok", "file": file_path, "preview": result[:200]}

# -------------------------------
# 4️⃣ تشغيل السيرفر
# -------------------------------
if __name__ == "__main__":
    print("Starting AI Game Generator Server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)