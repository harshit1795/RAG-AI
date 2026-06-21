import streamlit as st
import numpy as np
import requests
from pypdf import PdfReader
from google import genai
from google.genai import types

# --------------------------------------------------------
# PAGE CONFIGURATION & ARCHITECTURE METADATA
# --------------------------------------------------------
st.set_page_config(
    page_title="Source of Truth - Governed RAG POC",
    page_icon="🌌",
    layout="wide"
)

# Sidebar - Publisher & Configuration
with st.sidebar:
    st.markdown("### 🌌 Source of Truth")
    
    with st.expander("📖 About Author", expanded=False):
        st.markdown("**Publisher:** Harshit Gola  \n*Author: Source of Truth (SOT)*")
        st.markdown("**Contact:** [LinkedIn](https://www.linkedin.com/in/harshitgola/) | [Website](https://www.harshitgola.com/)")
        st.markdown("Harshit Gola is a data architect focusing on governed RAG pipelines. He builds AI‑enhanced solutions that combine enterprise data governance with large language models.")

    with st.expander("⚙️ Configuration & Settings", expanded=True):
        st.markdown("#### 🔑 Authentication")
        st.markdown("*To obtain a Google Gemini API Key, visit the [Google AI Studio](https://ai.google.dev/) and follow the instructions under **\"Get API key\"**. After creating a project, copy the generated key and paste it below.*")
        api_key = st.text_input("Enter Google Gemini API Key:", type="password")
        
        st.caption("This application processes data through three distinct operational phases:")
        st.info("**1. Bronze Layer:** Raw text extraction from uploaded assets.  \n"
                "**2. Silver Layer:** Deterministic cleaning and semantic chunking.  \n"
                "**3. Gold Layer:** Governed vector storage and trusted context matching.")

# Main Header
st.title("🌌 Governed RAG Architecture Pipeline")
st.subheader("Issue #6 POC: Moving From Raw Ingestion to Controlled Contextual Trust")
st.markdown("---")

# Guardrail for API Key
if not api_key:
    st.warning("⚠️ Please provide a valid Google Gemini API Key in the sidebar to initialize the architecture.")
    st.stop()

# ================================================================
# EMBEDDING SETUP
# Step 0 : Call ListModels to find what the API key CAN access.
# Step 1 : REST probes — discovered models first, then fallbacks.
# Step 2 : google-genai SDK probes as a last resort.
# All logic returns a single  embed_fn(text) -> list[float]
# callable so the rest of the app stays clean.
# ================================================================

_FALLBACK_MODELS = [
    "text-embedding-004",
    "text-embedding-005",
    "gemini-embedding-exp-03-07",
    "embedding-001",
    "gemini-embedding-exp-03-07",
]
_API_VERSIONS = ["v1", "v1beta"]
_PROBE = "embedding probe"


def _list_available_embedding_models(api_key: str):
    """
    Query the ListModels REST endpoint (v1 then v1beta).
    Returns (embed_model_names: list[str], debug_lines: list[str]).
    embed_model_names are bare names without the 'models/' prefix.
    """
    embed_models, debug_lines = [], []
    for api_ver in _API_VERSIONS:
        try:
            url = f"https://generativelanguage.googleapis.com/{api_ver}/models"
            r = requests.get(url, params={"key": api_key, "pageSize": 200}, timeout=20)
            debug_lines.append(f"ListModels/{api_ver} → HTTP {r.status_code}")
            if r.status_code == 200:
                for m in r.json().get("models", []):
                    name = m.get("name", "").replace("models/", "").strip()
                    methods = m.get("supportedGenerationMethods", [])
                    if "embedContent" in methods and name:
                        embed_models.append(name)
                        debug_lines.append(f"  ✅ {name}  |  methods: {methods}")
                    else:
                        debug_lines.append(f"  ℹ️  {name}  |  methods: {methods}")
                if embed_models:
                    return embed_models, debug_lines
            else:
                debug_lines.append(f"  Response: {r.text[:300]}")
        except Exception as exc:
            debug_lines.append(f"ListModels/{api_ver} error: {exc}")
    return embed_models, debug_lines


def _try_rest_embed(api_key: str, model: str, api_ver: str, text: str):
    """Direct REST call to embedContent. Returns vector list or raises."""
    url = f"https://generativelanguage.googleapis.com/{api_ver}/models/{model}:embedContent"
    payload = {"content": {"parts": [{"text": text}]}}
    r = requests.post(url, json=payload, params={"key": api_key}, timeout=20)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:300]}")
    return r.json()["embedding"]["values"]


@st.cache_resource
def build_embed_fn(api_key: str):
    """
    Returns (embed_fn, label, gen_client, list_debug) on success,
    or       (None, errors_list, None, list_debug) on failure.
    """
    errors = []

    # Step 0: discover what models this key can actually access
    available, list_debug = _list_available_embedding_models(api_key)
    # Try discovered models first, then hardcoded fallbacks
    probe_order = available + [m for m in _FALLBACK_MODELS if m not in available]

    # Step 1: REST API (most reliable — bypasses SDK routing)
    for api_ver in _API_VERSIONS:
        for model in probe_order:
            label = f"REST/{api_ver}/{model}"
            try:
                vec = _try_rest_embed(api_key, model, api_ver, _PROBE)
                if vec:
                    def make_rest_fn(m=model, v=api_ver, k=api_key):
                        def fn(text): return _try_rest_embed(k, m, v, text)
                        return fn
                    return make_rest_fn(), label, genai.Client(api_key=api_key), list_debug
            except Exception as exc:
                errors.append(f"{label}: {exc}")

    # Step 2: google-genai SDK fallback
    for ver_label, http_opts in [
        ("sdk/v1",    types.HttpOptions(api_version="v1")),
        ("sdk/v1beta",types.HttpOptions(api_version="v1beta")),
        ("sdk/default", None),
    ]:
        for model in probe_order:
            label = f"{ver_label}/{model}"
            try:
                c = (genai.Client(api_key=api_key, http_options=http_opts)
                     if http_opts else genai.Client(api_key=api_key))
                vec = list(c.models.embed_content(model=model, contents=_PROBE).embeddings[0].values)
                if vec:
                    def make_sdk_fn(client=c, m=model):
                        def fn(text):
                            return list(client.models.embed_content(model=m, contents=text).embeddings[0].values)
                        return fn
                    return make_sdk_fn(), label, c, list_debug
            except Exception as exc:
                errors.append(f"{label}: {exc}")

    return None, errors, None, list_debug


# ── Sidebar re-detect button (clears cache) ──────────────────────────────
if st.sidebar.button("🔄 Re-detect embedding model"):
    build_embed_fn.clear()
    st.rerun()

with st.spinner("🔍 Detecting available embedding models for your API key..."):
    embed_fn, embed_label, gen_client, list_debug = build_embed_fn(api_key)

if embed_fn is None:
    st.error("❌ No working embedding model found for this API key.")
    col1, col2 = st.columns(2)
    with col1:
        with st.expander("📋 Models available for your API key", expanded=True):
            if list_debug:
                st.code("\n".join(list_debug), language="")
            else:
                st.warning("Could not retrieve model list (network error or invalid key).")
    with col2:
        with st.expander("🔎 All probe errors", expanded=True):
            for err in embed_label:
                st.code(err, language="")
    st.markdown("""
**Most common fixes:**
- Your key must be from **[Google AI Studio](https://aistudio.google.com/apikey)** — not a Vertex AI service-account key.
- Enable the **[Generative Language API](https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com)**
  for your Google Cloud project.
- In AI Studio, click **Create API key** in a project that has billing enabled (free tier is sufficient).
- If the key was recently created, wait 1–2 minutes then click **🔄 Re-detect embedding model** in the sidebar.
""")
    st.stop()

st.sidebar.success(f"✅ Embedding via `{embed_label}`")


# Initialize session state for architectural vector database (Gold Layer)
if "gold_layer_db" not in st.session_state:
    st.session_state.gold_layer_db = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "processed_files" not in st.session_state:
    st.session_state.processed_files = set()
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

def reset_session():
    st.session_state.gold_layer_db = []
    st.session_state.chat_history = []
    st.session_state.processed_files = set()
    st.session_state.uploader_key += 1

st.sidebar.markdown("---")
st.sidebar.button("🗑️ Start New Session", on_click=reset_session, key="btn_sidebar", use_container_width=True)

# Helper: Cosine Similarity for Vector Search
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# --------------------------------------------------------
# DATA INGESTION PIPELINE (BRONZE -> SILVER -> GOLD)
# --------------------------------------------------------
st.header("📥 1. Contextual Ingestion Pipeline")

st.button("🗑️ Start New Session", on_click=reset_session, key="btn_main", type="secondary")

uploaded_files = st.file_uploader(
    "Upload organizational documentation (PDF or TXT format)", 
    type=["pdf", "txt"], 
    accept_multiple_files=True,
    key=f"uploader_{st.session_state.uploader_key}"
)

if uploaded_files:
    if st.button("🚀 Process & Govern Assets"):
        with st.status("Executing data maturity pipeline...", expanded=True) as status:
            
            raw_chunks = []
            
            # --- PHASE 1: BRONZE LAYER (Extraction) ---
            status.update(label="Extracting raw metrics (Bronze Layer)...")
            for uploaded_file in uploaded_files:
                if uploaded_file.name in st.session_state.processed_files:
                    continue  # Already processed in this session
                
                if uploaded_file.name.endswith(".pdf"):
                    try:
                        pdf_reader = PdfReader(uploaded_file)
                        for page_num, page in enumerate(pdf_reader.pages):
                            text = page.extract_text()
                            if text and text.strip():
                                raw_chunks.append({"source": f"{uploaded_file.name} (Pg {page_num+1})", "text": text})
                        st.session_state.processed_files.add(uploaded_file.name)
                    except Exception as pdf_err:
                        st.error(f"❌ Failed to read PDF **{uploaded_file.name}**: {pdf_err}")
                        continue
                elif uploaded_file.name.endswith(".txt"):
                    text = uploaded_file.read().decode("utf-8")
                    raw_chunks.append({"source": uploaded_file.name, "text": text})
                    st.session_state.processed_files.add(uploaded_file.name)
            
            if not raw_chunks:
                st.write("✅ All selected files have already been processed.")
                status.update(label="System Ready.", state="complete")
            else:
                st.write(f"✅ **Bronze Layer Completed:** Extracted {len(raw_chunks)} raw asset segments.")
                
                # --- PHASE 2: SILVER LAYER (Semantic Chunking & Cleaning) ---
                status.update(label="Refining data alignment (Silver Layer)...")
                refined_chunks = []
                # Simple windowed chunking for stability and clean semantic grouping
                for chunk in raw_chunks:
                    text_content = chunk["text"].replace("\n", " ").strip()
                    words = text_content.split(" ")
                    chunk_size = 150
                    for i in range(0, len(words), chunk_size):
                        slice_words = words[i:i+chunk_size]
                        joined_text = " ".join(slice_words)
                        if len(joined_text) > 50:
                            refined_chunks.append({"source": chunk["source"], "text": joined_text})
                
                st.write(f"✅ **Silver Layer Completed:** Normalized data into {len(refined_chunks)} standardized chunks.")
                
                # --- PHASE 3: GOLD LAYER (Vector Transformations & Governance) ---
                status.update(label="Vectorizing and validating context (Gold Layer)...")
                gold_layer_cache = []
                
                failed_chunks = []
                for index, item in enumerate(refined_chunks):
                    try:
                        embedding = embed_fn(item["text"])
                        gold_layer_cache.append({
                            "source": item["source"],
                            "text": item["text"],
                            "embedding": embedding
                        })
                    except Exception as ex:
                        failed_chunks.append(index)
                        st.warning(f"⚠️ Skipped chunk {index} ({item['source']}): {ex}")
                        continue  # non-fatal — skip bad chunk, keep processing
    
                if failed_chunks:
                    st.warning(f"⚠️ {len(failed_chunks)} chunk(s) could not be embedded and were skipped.")
                        
                st.session_state.gold_layer_db.extend(gold_layer_cache)
                st.write(f"✅ **Gold Layer Active:** Added {len(gold_layer_cache)} verified entities to system memory.")
                status.update(label="Pipeline verification successful. System Ready.", state="complete")

st.markdown("---")

# --------------------------------------------------------
# GOVERNED REASONING & CHAT INTERFACE
# --------------------------------------------------------
st.header("🤖 2. Governed Reasoning Interface")

# Display current architecture status
if st.session_state.gold_layer_db:
    st.success(f"🔒 **System Status:** Active Knowledge Base contains {len(st.session_state.gold_layer_db)} validated references.")
else:
    st.info("💡 **System Status:** Operating on foundational model intelligence. Upload documents above to anchor reasoning in a trusted data layer.")

# Chat History Container
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Query Processing
if user_query := st.chat_input("Submit inquiry across your organizational data architecture..."):
    with st.chat_message("user"):
        st.markdown(user_query)
    st.session_state.chat_history.append({"role": "user", "content": user_query})
    
    # Process Retrieval Context
    context_retrieved = ""
    sources_used = []
    
    if st.session_state.gold_layer_db:
        try:
            query_vector = embed_fn(user_query)
            
            # Calculate mathematical proximity (Similarity Search)
            scored_chunks = []
            for item in st.session_state.gold_layer_db:
                score = cosine_similarity(query_vector, item["embedding"])
                scored_chunks.append((score, item))
                
            # Sort and select top 3 highest-scoring vectors (Top-K)
            scored_chunks.sort(key=lambda x: x[0], reverse=True)
            top_chunks = scored_chunks[:3]
            
            # Build trust layer boundary
            context_segments = []
            for score, item in top_chunks:
                if score > 0.3:  # Structural confidence threshold
                    context_segments.append(f"[Source: {item['source']}] {item['text']}")
                    sources_used.append(item["source"])
            
            if context_segments:
                context_retrieved = "\n\n".join(context_segments)
        except Exception as embed_err:
            st.error(f"Error during context retrieval: {embed_err}")

    # Execute Governed Generation Task
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        
        # System instructions enforcing the "Controlled Contextual Trust" design pattern
        governance_prompt = (
            "You are an advanced enterprise intelligence assistant operating inside a Governed RAG system architecture. "
            "Your domain space includes Accounting, Finance, Risk Management, and IT Audit. "
            "You must synthesize answers based STRICTLY on the validated context provided below. "
            "If the retrieved context does not contain sufficient factual substance to support an accurate answer, "
            "state clearly that the required context is missing from the validated organizational memory layer. "
            "Do not hallucinate or speculate.\n\n"
            f"--- VALIDATED GOLD-LAYER CONTEXT ---\n{context_retrieved or 'No validated context provided.'}\n---"
        )
        
        try:
            response = gen_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=user_query,
                config=types.GenerateContentConfig(
                    system_instruction=governance_prompt,
                    temperature=0.2  # Kept low to prioritize deterministic accuracy over creativity
                )
            )
            
            output_text = response.text
            
            # Append verified sources to the UI if utilized
            if sources_used:
                unique_sources = list(set(sources_used))
                output_text += f"\n\n**🛡️ Verified Context Sources:** {', '.join(unique_sources)}"
            else:
                if st.session_state.gold_layer_db:
                    output_text += "\n\n*⚠️ Warning: No context matched our confidence thresholds. This output is generated strictly from foundational weights.*"
            
            response_placeholder.markdown(output_text)
            st.session_state.chat_history.append({"role": "assistant", "content": output_text})
            
        except Exception as gen_err:
            st.error(f"Execution Error: {gen_err}")