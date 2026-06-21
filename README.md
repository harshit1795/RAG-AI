# RAG Architecture (Source of Truth) – Governed RAG POC

## Overview
This repository contains a **Streamlit** application that demonstrates a governed Retrieval‑Augmented Generation (RAG) pipeline with three layers:

1. **Bronze Layer** – Raw text extraction from PDF/TXT assets.
2. **Silver Layer** – Deterministic cleaning and semantic chunking.
3. **Gold Layer** – Vector embeddings (Google Gemini `text-embedding-004`) with trust‑based retrieval.

The UI includes a left‑hand sidebar where you can:
- See the publisher/author information.
- Access your LinkedIn profile and personal website.
- Get quick instructions on how to obtain a **Google Gemini API Key**.

## Prerequisites
- **Python 3.10+** (the project was tested on 3.10/3.11).
- `pip` (or `uv` if you prefer) installed and available in your PATH.
- A **Google Gemini API Key** – see the *Google Gemini Key* section below.

## Installation
```bash
# Clone the repo and cd into the project folder
git clone https://github.com/harshit1795/RAG-AI.git
cd RAG-AI

# (Optional) Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # on macOS/Linux
# .venv\Scripts\activate   # on Windows

# Install dependencies
pip install -r requirement.txt
```
If you prefer the modern `uv` package manager, you can run:
```bash
uv pip install -r requirement.txt
```

## Obtaining a Google Gemini API Key
1. Open the **Google AI Studio**: <a href="https://ai.google.dev/" target="_blank">https://ai.google.dev/</a>
2. Click **Get API key** and follow the on‑screen prompts to create a new project (or select an existing one).
3. Copy the generated key.
4. In the Streamlit app’s left sidebar, paste the key into the **Authentication** field.

## Running the App locally
```bash
streamlit run App.py
```
The app will start and display URLs such as:
- `http://localhost:8501` (or another port if 8501 is taken)
- `http://<your‑LAN‑IP>:8501` (accessible from other devices on the same network)

## Deployment Options
### Render (Classic) – Static Site & Web Service
1. Sign up at <a href="https://render.com" target="_blank">https://render.com</a> and create a **New Web Service**.
2. Connect your GitHub repository (or push the current folder to a new repo).
3. Set the **Build Command** to `pip install -r requirement.txt`.
4. Set the **Start Command** to `streamlit run App.py --server.port $PORT`.
5. Add an **Environment Variable** named `GEMINI_API_KEY` with your key – the app will read it automatically if you modify `App.py` to use `os.getenv("GEMINI_API_KEY")` instead of the sidebar input (optional).

### Vercel / Netlify (via Render static hosting)
- Build the Streamlit app into a static HTML bundle using `streamlit export` (requires Streamlit >= 1.31). Deploy the generated files as a static site.
- Remember to store the Gemini key as a Vercel/Netlify environment variable.

## License & Credits
- This project is provided under the **Google Gemini Free Usage License**.
- Author: **Harshit Gola** – Data architect specializing in governed RAG pipelines.
- LinkedIn: <a href="https://www.linkedin.com/in/harshitgola/" target="_blank">https://www.linkedin.com/in/harshitgola/</a>
- Website: <a href="https://www.harshitgola.com/" target="_blank">https://www.harshitgola.com/</a>
- Newsletter: <a href="https://www.linkedin.com/newsletters/source-of-truth-sot-7437687249598763008/" target="_blank">Source of Truth (SOT)</a>

---
*Happy hacking! 🚀*
