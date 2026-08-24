import streamlit as st
import os
import requests
import pandas as pd
from supabase import create_client, Client

# Optional integrations (wrapped in try/except to avoid build-time failures)
try:
    from langchain_groq import ChatGroq
except Exception:
    ChatGroq = None

try:
    from langchain_community.tools import DuckDuckGoSearchRun
except Exception:
    DuckDuckGoSearchRun = None

# Page Configuration & Modern UI Styles
st.set_page_config(
    page_title="Mohit Agentic AI & BharatGpilot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main .block-container { max-width: 1200px; padding-top: 2rem; }
    div.stButton > button:first-child {
        background-color: #ff4b4b; color: white; border-radius: 8px; width: 100%; border: none;
    }
    div.stButton > button:first-child:hover { background-color: #ff3333; border: none; }
    .stTextInput>div>div>input { border-radius: 8px; }
    .chat-bubble { padding: 1rem; border-radius: 12px; margin-bottom: 1rem; line-height: 1.5; }
    .user-bubble { background-color: #2e3136; border-left: 5px solid #00bcff; color: #fff }
    .ai-bubble { background-color: #23272a; border-left: 5px solid #ff4b4b; color: #fff }
    .metric-card { background-color: #1e1e24; border: 1px solid #333; padding: 1.5rem; border-radius: 10px; text-align: center; color: #fff }
    </style>
""", unsafe_allow_html=True)

# Database & Auth Environment Connection (Supabase)
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "mohit@admin.local") # Default fallback admin email

supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Supabase Connection Failed: {e}")

# Session Engine Initialization
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "active_mode" not in st.session_state:
    st.session_state.active_mode = "🤖 Mohit Agentic AI"
if "current_view" not in st.session_state:
    st.session_state.current_view = "Chat Interface"

# Authentication User Interface Component
def render_auth_interface():
    st.title("🔒 Unified Access Control Portal")
    st.subheader("Mohit Agentic AI & BharatGpilot Enterprise Pipeline")
    
    if not supabase:
        st.warning("⚠️ Cloud Deployment Notice: Set your SUPABASE_URL and SUPABASE_KEY variables to unlock user registration.")
        if st.button("Proceed via Sandbox Developer Bypass"):
            st.session_state.authenticated = True
            st.session_state.user_email = "developer@sandbox.local"
            st.session_state.user_id = "00000000-0000-0000-0000-000000000000"
            st.rerun()
        return

    tab1, tab2 = st.tabs(["🔑 Sign In", "📝 Create Free Account"])
    
    with tab1:
        with st.form("signin_form"):
            email = st.text_input("Registered Email Address")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Authenticate Instance")
            
            if submitted:
                try:
                    res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    st.session_state.authenticated = True
                    # supabase-py may return different shapes; guard access
                    try:
                        st.session_state.user_email = res.user.email
                        st.session_state.user_id = res.user.id
                    except Exception:
                        st.session_state.user_email = email
                        st.session_state.user_id = getattr(res, "data", {}).get("user", {}).get("id", None)

                    st.success("Access Granted. Booting nodes...")
                    st.rerun()
                except Exception as err:
                    st.error(f"Authentication Failure: {err}")

    with tab2:
        with st.form("signup_form"):
            new_email = st.text_input("Target Email Address")
            new_password = st.text_input("Set Password (Min 6 chars)", type="password")
            submitted_signup = st.form_submit_button("Provision New Account Identity")
            
            if submitted_signup:
                try:
                    res = supabase.auth.sign_up({"email": new_email, "password": new_password})
                    st.info("Registration request issued! Check email inbox for confirmation link.")
                except Exception as err:
                    st.error(f"Provisioning Failure: {err}")

# Load User Logs From Database
def load_db_history():
    if supabase and st.session_state.user_id:
        try:
            res = supabase.table("chat_logs").select("*").eq("user_id", st.session_state.user_id).order("created_at", desc=False).execute()
            data = getattr(res, "data", None) or res.get("data") if isinstance(res, dict) else None
            if data:
                st.session_state.chat_history = [{"role": row["role"], "content": row["content"], "engine": row.get("engine", "Unknown")} for row in data]
        except Exception:
            pass 

# Save Single Conversation Turn Into Database Row
def save_log_to_db(role, content, engine):
    if supabase and st.session_state.user_id:
        try:
            supabase.table("chat_logs").insert({
                "user_id": st.session_state.user_id,
                "role": role,
                "content": content,
                "engine": engine
            }).execute()
        except Exception:
            pass

# Renders Admin View Metrics (Strictly Secured)
def render_admin_dashboard():
    st.title("📊 Platform Admin Analytics Panel")
    st.caption("Secure real-time diagnostic reporting across system servers.")
    st.write("---")
    
    if not supabase:
        st.error("Admin view requires an active Supabase database context link.")
        return

    try:
        res = supabase.table("chat_logs").select("id, role, engine, created_at, user_id").execute()
        data = getattr(res, "data", None) or res.get("data") if isinstance(res, dict) else None
        logs_df = pd.DataFrame(data) if data else pd.DataFrame()
        
        if logs_df.empty:
            st.info("Database initialized successfully. No interaction logs captured yet.")
            return

        # Top Metric Summaries
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="metric-card"><h3>📈 Total Request Logs</h3><h2>{len(logs_df)}</h2></div>', unsafe_allow_html=True)
        with col2:
            unique_users = logs_df["user_id"].nunique()
            st.markdown(f'<div class="metric-card"><h3>👥 Active User Nodes</h3><h2>{unique_users}</h2></div>', unsafe_allow_html=True)
        with col3:
            engine_counts = logs_df["engine"].value_counts()
            favorite_engine = engine_counts.index[0] if not engine_counts.empty else "None"
            st.markdown(f'<div class="metric-card"><h3>🔥 Most Used Module</h3><h2>{favorite_engine}</h2></div>', unsafe_allow_html=True)
            
        st.write("### 🕒 Recent Infrastructure Operations Logging")
        st.dataframe(logs_df[["created_at", "engine", "role", "id"]].tail(20), use_container_width=True)
        
        st.write("### 📊 Module Usage Distribution Graph")
        st.bar_chart(logs_df["engine"].value_counts())
        
    except Exception as e:
        st.error(f"Failed to aggregate cloud logs layout: {e}")
        st.info("💡 Security Tip: To allow the Admin view to read global metrics across all users, confirm your Supabase security policies grant read access to your designated Admin Email identity.")

# Core helpers: simple web search and groq chat wrapper (safe fallbacks)
def web_search(query: str) -> str:
    if DuckDuckGoSearchRun is None:
        return f"(DuckDuckGoSearchRun not installed) Placeholder results for: {query}"
    try:
        search = DuckDuckGoSearchRun()
        results = search.run(query)
        return results
    except Exception as e:
        return f"(search failed: {e})"


def groq_chat(prompt: str) -> str:
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key or ChatGroq is None:
        return f"(ChatGroq not configured) echo: {prompt[:200]}"
    try:
        client = ChatGroq(api_key=api_key)
        resp = client.chat(prompt)
        return getattr(resp, "text", str(resp))
    except Exception as e:
        return f"(groq error: {e})"

# Main Platform View Layout Workspace
def render_main_workspace():
    is_admin = (st.session_state.user_email == ADMIN_EMAIL)
    
    with st.sidebar:
        st.title("🌐 System Control")
        st.info(f"Active Identity:\n{st.session_state.user_email}")
        
        if is_admin:
            st.warning("⚡ ADMIN SECURITY ACCREDITED")
            st.session_state.current_view = st.radio("Navigation View:", ["Chat Interface", "Admin Dashboard"])
        else:
            st.session_state.current_view = "Chat Interface"
            
        st.write("---")
        
        if st.session_state.current_view == "Chat Interface":
            mode = st.radio(
                "Engine Routing Mode:",
                ["🤖 Mohit Agentic AI", "💻 BharatGpilot"],
                index=0 if st.session_state.active_mode == "🤖 Mohit Agentic AI" else 1
            )
            st.session_state.active_mode = mode
            
            if mode == "🤖 Mohit Agentic AI":
                st.caption("🎯 **Context Flow:** Autonomous web lookup capabilities, search tools, and agent logic reasoning.")
            else:
                st.caption("⚡ **Context Flow:** Optimized for code output emission, software architecture scripts, and debugging queries.")
        
        st.write("---")
        if st.button("Terminate Session (Log Out)"):
            if supabase:
                try: supabase.auth.sign_out()
                except: pass
            st.session_state.authenticated = False
            st.session_state.user_email = None
            st.session_state.user_id = None
            st.session_state.chat_history = []
            st.session_state.current_view = "Chat Interface"
            st.rerun()

    # Route output screen based on sidebar choice
    if st.session_state.current_view == "Admin Dashboard" and is_admin:
        render_admin_dashboard()
        return

    st.title("⚡ Enterprise Scaled Multi-Agent Infrastructure")
    st.subheader(f"Current Matrix Pipeline: {st.session_state.active_mode}")
    
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
    if not GROQ_API_KEY and ChatGroq is not None:
        st.info("🔑 If you intend to use Groq, set 'GROQ_API_KEY' in Space secrets. The UI will still function without it.")

    if len(st.session_state.chat_history) == 0:
        load_db_history()

    # Chat history display
    for msg in st.session_state.chat_history:
        bubble_class = "user-bubble" if msg["role"] == "user" else "ai-bubble"
        with st.container():
            st.markdown(f'<div class="chat-bubble {bubble_class}"><strong>{msg.get("engine","")} — {msg["role"].upper()}:</strong><br/>{msg["content"]}</div>', unsafe_allow_html=True)

    st.write("---")
    st.markdown("#### New Message")
    user_input = st.text_area("", height=160, placeholder="Ask Mohit Agentic AI to orchestrate tools, or ask BharatGpilot to emit code precisely...")
    col1, col2 = st.columns([1, 4])
    with col1:
        send = st.button("Send")
    with col2:
        tone = st.selectbox("Output Style", ["Concise", "Detailed", "Explain like I'm 5"], index=0)

    if send and user_input.strip():
        # Append user message
        st.session_state.chat_history.append({"role": "user", "content": user_input, "engine": st.session_state.active_mode})
        save_log_to_db("user", user_input, st.session_state.active_mode)

        # Decide execution path
        if st.session_state.active_mode.startswith("🤖 Mohit"):
            # Orchestration: run web search then call groq (if available)
            search_results = web_search(user_input)
            prompt = f"Web search summary:\n{search_results}\n\nUser request:\n{user_input}\n\nRespond as an assistant with next steps and, if asked for code, call BharatGpilot."
            response_text = groq_chat(prompt)
            engine_label = "Mohit Agentic AI"
        else:
            # BharatGpilot: deterministic code emission
            prompt = f"Mode: bharatGpilot (temperature=0)\nUser request:\n{user_input}\nReturn only the code or precise instructions."
            response_text = groq_chat(prompt)
            engine_label = "BharatGpilot"

        st.session_state.chat_history.append({"role": "assistant", "content": response_text, "engine": engine_label})
        save_log_to_db("assistant", response_text, engine_label)
        st.experimental_rerun()


# APP ENTRY
st.sidebar.title("Welcome")
if not st.session_state.authenticated:
    render_auth_interface()
else:
    render_main_workspace()


# Footer / Notes
st.markdown("---")
st.caption("Mohit Agentic AI (web/tool orchestration)  •  BharatGpilot (zero-temperature code emission). Replace placeholders with your LLM/search integrations and secrets in Space settings.")
