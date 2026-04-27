"""
Groww FactFinder: Obsidian Glass (Dark High-Tech)
- Theme: Black / Dark Grey / Groww Green
- Aesthetic: Glassmorphism / Neon Accents
- Persona: Fin-Bot (State-Aware)
"""
import streamlit as st
import os
import sys
import time
import re

# Add paths
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(base_path, "Phase 1"))
sys.path.append(os.path.join(base_path, "Phase 2"))
sys.path.append(os.path.join(base_path, "Phase 3"))

from rag_engine import get_assistant_answer
from guardrails import apply_guardrails
from retention import (
    record_query, get_context_bridge, save_insight, remove_insight,
    get_vault, get_vault_count, is_high_value_response,
    get_retention_hook, get_past_interests_summary
)

# --- Page Setup ---
st.set_page_config(
    page_title="Groww FactFinder",
    page_icon="💹",
    layout="centered"
)

# --- Obsidian Glass CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&family=Inter:wght@400;500&display=swap');

    /* 1. Global Dark Tech Base */
    .stApp {
        background: radial-gradient(circle at top right, #121212, #000000 70%);
        font-family: 'Inter', sans-serif;
        color: #F3F4F6;
    }

    h1, h2, h3, .header-title {
        font-family: 'Outfit', sans-serif;
    }

    /* 2. Glass Mascot & Header */
    .header-stack {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 4rem 1rem 2rem 1rem;
        text-align: center;
    }

    .finbot-avatar-container {
        position: relative;
        width: 80px;
        height: 80px;
        margin-bottom: 2rem;
    }

    .finbot-avatar {
        width: 80px;
        height: 80px;
        background-color: #00D09C;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        box-shadow: 0 0 40px rgba(0, 208, 156, 0.4);
        border: 2px solid rgba(255, 255, 255, 0.1);
        z-index: 2;
    }

    .finbot-eyes {
        display: flex;
        gap: 10px;
    }

    .eye {
        width: 12px;
        height: 12px;
        background-color: white;
        border-radius: 50%;
        transition: all 0.3s ease;
        box-shadow: 0 0 10px rgba(255,255,255,0.8);
    }

    .eye.amber { background-color: #FBB03B !important; box-shadow: 0 0 15px #FBB03B; }
    .eye.spinning { 
        animation: spin 1s infinite linear;
        border: 2px solid white;
        border-top: 2px solid transparent;
        background-color: transparent !important;
        box-shadow: none;
    }

    @keyframes spin { 100% { transform: rotate(360deg); } }

    .rupee-symbol {
        position: absolute;
        top: 10px;
        font-size: 12px;
        font-weight: 700;
        color: rgba(255, 255, 255, 0.9);
    }

    .status-dot {
        position: absolute;
        bottom: 5px;
        right: 5px;
        width: 15px;
        height: 15px;
        background-color: #00D09C;
        border: 3px solid #000000;
        border-radius: 50%;
        animation: pulse 2s infinite;
        z-index: 3;
    }

    @keyframes pulse {
        0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(0, 208, 156, 0.4); }
        70% { transform: scale(1.1); box-shadow: 0 0 0 10px rgba(0, 208, 156, 0); }
        100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(0, 208, 156, 0); }
    }

    .header-title {
        font-size: 24px !important;
        font-weight: 700 !important;
        color: #FFFFFF !important;
        background: linear-gradient(to right, #FFFFFF, #9CA3AF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2px;
    }

    .header-sublabel {
        font-size: 14px !important;
        color: #00D09C !important;
        font-weight: 500;
        letter-spacing: 1px;
        text-transform: uppercase;
        opacity: 0.8;
    }

    /* 3. Obsidian Fact Cards */
    [data-testid="stChatMessage"] {
        background: transparent !important;
        border: none !important;
    }

    .fact-card {
        background: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(24px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 20px !important;
        padding: 1.5rem !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5) !important;
        margin-top: 10px;
    }

    .bot-body {
        font-size: 15px !important;
        line-height: 1.7;
        color: #E2E8F0;
    }

    .verified-badge {
        font-size: 11px;
        font-weight: 700;
        color: #00D09C;
        margin-bottom: 10px;
        display: block;
        letter-spacing: 1px;
    }

    /* 4. Uniform Quick-Action Grid */
    .stButton {
        width: 100% !important;
    }
    
    .stButton button {
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        background: rgba(255, 255, 255, 0.04) !important;
        color: #F3F4F6 !important;
        padding: 1.5rem 1rem !important;
        width: 100% !important;
        min-height: 120px !important; /* Uniform height */
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.3s ease !important;
        font-weight: 600 !important;
        text-align: center !important;
        line-height: 1.4 !important;
    }

    .stButton button:hover {
        background: rgba(0, 208, 156, 0.08) !important;
        border-color: #00D09C !important;
        transform: translateY(-4px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }

    /* Back Button — Fixed Bottom Left (Side of Input) */
    .back-nav-left-side {
        position: fixed;
        bottom: 92px; /* Aligned with the bottom input area */
        left: 2rem;
        z-index: 100000;
    }

    .back-nav-left-side button {
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(0, 208, 156, 0.3) !important;
        color: #00D09C !important;
        width: 36px !important;
        height: 36px !important;
        border-radius: 10px !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 18px !important;
        min-height: 36px !important;
        line-height: 1 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5) !important;
    }

    .back-nav-left-side button:hover {
        background: #00D09C !important;
        color: #000000 !important;
        border-color: #00D09C !important;
        transform: scale(1.1);
    }



    /* PDF Action Button (Dual Line) */
    .pdf-button {
        display: inline-flex;
        flex-direction: column;
        align-items: flex-start;
        background: rgba(0, 208, 156, 0.08) !important;
        border: 1px solid rgba(0, 208, 156, 0.25) !important;
        border-radius: 14px;
        padding: 12px 24px;
        color: #00D09C !important;
        text-decoration: none !important;
        margin-top: 15px;
        transition: all 0.3s ease;
        line-height: 1.4;
    }

    .pdf-button:hover {
        background: #00D09C !important;
        color: #000000 !important;
        box-shadow: 0 0 15px #00D09C;
    }

    /* 5. Chat Input & Disclaimer (Remove White Band) */
    div[data-testid="stBottom"] {
        background-color: transparent !important;
        background-image: none !important;
        border: none !important;
    }
    
    div[data-testid="stBottom"] > div {
        background-color: transparent !important;
        background-image: none !important;
        border: none !important;
    }

    [data-testid="stChatInput"] {
        background: #0A0A0A !important; /* Pure Black Box */
        border: 1px solid rgba(0, 208, 156, 0.2) !important;
        border-radius: 20px !important;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.8) !important;
        margin-bottom: 20px !important;
    }

    [data-testid="stChatInput"]:focus-within {
        border-color: #00D09C !important;
        box-shadow: 0 0 15px rgba(0, 208, 156, 0.2) !important;
    }

    .disclaimer-text {
        font-size: 11px !important;
        color: #4B5563 !important;
        text-align: center;
        margin-top: 15px;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }

    /* Hide default elements */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    .stChatInputContainer {
        padding-bottom: 70px !important;
    }

    /* Retention Layer — Context Bridge Banner */
    .context-bridge {
        background: rgba(0, 208, 156, 0.06);
        border-left: 3px solid #00D09C;
        border-radius: 0 12px 12px 0;
        padding: 10px 16px;
        margin-bottom: 12px;
        font-size: 13px;
        color: #9CA3AF;
    }
    .context-bridge strong { color: #00D09C; }

    /* Retention Hook */
    .retention-hook {
        background: rgba(83, 103, 245, 0.06);
        border: 1px solid rgba(83, 103, 245, 0.15);
        border-radius: 14px;
        padding: 12px 16px;
        margin-top: 14px;
        font-size: 13px;
        color: #9CA3AF;
    }
    .retention-hook strong { color: #FFFFFF; }

    /* Save-to-Vault Ribbon (Targeting the Column Block) */
    div[data-testid="stHorizontalBlock"]:has(button[key*="save"]) {
        background: rgba(0, 208, 156, 0.05) !important;
        border: 1px solid rgba(0, 208, 156, 0.15) !important;
        border-left: 4px solid #00D09C !important;
        border-radius: 12px !important;
        padding: 4px 12px !important;
        margin-top: 15px !important;
        margin-bottom: 25px !important;
        align-items: center !important;
    }

    div[data-testid="stHorizontalBlock"]:has(button[key*="save"]) button {
        background: #00D09C !important;
        border: none !important;
        color: #000000 !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        padding: 4px 14px !important;
        border-radius: 8px !important;
        min-height: auto !important;
        height: auto !important;
        width: fit-content !important;
        box-shadow: 0 4px 12px rgba(0, 208, 156, 0.3) !important;
        transition: all 0.2s ease !important;
        float: right !important;
    }

    div[data-testid="stHorizontalBlock"]:has(button[key*="save"]) button:hover {
        background: #FFFFFF !important;
        transform: translateY(-1px);
        box-shadow: 0 6px 15px rgba(0, 208, 156, 0.4) !important;
    }

    /* Sidebar Vault Styling */
    section[data-testid="stSidebar"] {
        background: #0A0A0A !important;
        border-right: 1px solid rgba(255,255,255,0.06);
    }
    .vault-entry {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 8px;
        font-size: 12px;
        color: #9CA3AF;
    }
    .vault-entry strong { color: #FFFFFF; font-size: 13px; }

    /* Vault Removal Button */
    .vault-remove-btn button {
        background: transparent !important;
        border: none !important;
        color: #ff4b4b !important;
        padding: 0 !important;
        font-size: 10px !important;
        line-height: 1 !important;
        min-height: auto !important;
        height: auto !important;
        width: auto !important;
        margin-top: -15px !important;
        opacity: 0.6;
        transition: opacity 0.2s ease;
    }
    .vault-remove-btn button:hover {
        opacity: 1;
        background: transparent !important;
    }
    /* Bulletproof Uniform Button Logic */
    #faq-box-fix button {
        height: 110px !important;
        min-height: 110px !important;
        width: 100% !important;
        max-width: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 10px 15px !important;
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 18px !important;
        margin: 0 !important;
    }

    #faq-box-fix button p {
        font-size: 14px !important;
        font-weight: 500 !important;
        line-height: 1.3 !important;
        color: #FFFFFF !important;
        text-align: center !important;
        margin: 0 !important;
    }

    #faq-box-fix button:hover {
        border-color: #00D09C !important;
        background: rgba(0, 208, 156, 0.08) !important;
        box-shadow: 0 5px 20px rgba(0, 208, 156, 0.15) !important;
    }

    #faq-box-fix div[data-testid="column"] {
        display: flex !important;
        align-items: stretch !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Groww Brand Card Helper ---
def render_finbot(state="success"):
    st.markdown(f"""
    <style>
        @keyframes border-glow {{
            0% {{ box-shadow: 0 0 15px rgba(83, 103, 245, 0.3), inset 0 0 5px rgba(83, 103, 245, 0.2); border-color: rgba(83, 103, 245, 0.5); }}
            50% {{ box-shadow: 0 0 35px rgba(0, 208, 156, 0.6), inset 0 0 15px rgba(0, 208, 156, 0.3); border-color: rgba(0, 208, 156, 0.8); }}
            100% {{ box-shadow: 0 0 15px rgba(83, 103, 245, 0.3), inset 0 0 5px rgba(83, 103, 245, 0.2); border-color: rgba(83, 103, 245, 0.5); }}
        }}
        @keyframes breathe {{
            0% {{ transform: scale(1); }}
            50% {{ transform: scale(1.08); }}
            100% {{ transform: scale(1); }}
        }}
        .brand-card-container {{
            display: flex;
            justify-content: center;
            margin-bottom: 4rem;
        }}
        .brand-card {{
            width: 750px;
            padding: 1.5rem 2rem;
            background: rgba(10, 10, 10, 0.8) !important;
            backdrop-filter: blur(30px) !important;
            border: 2px solid rgba(83, 103, 245, 0.4);
            border-radius: 28px;
            display: flex;
            flex-direction: column;
            align-items: center;
            animation: border-glow 4s infinite ease-in-out;
            position: relative;
            overflow: visible;
        }}
        .logo-wrap {{
            width: 100px;
            height: 100px;
            border-radius: 50%;
            overflow: hidden;
            background: #5367F5;
            display: flex;
            align-items: center;
            justify-content: center;
            animation: breathe 5s infinite ease-in-out;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.8);
        }}
        .logo-wrap svg {{
            width: 100%;
            height: 100%;
        }}
    </style>
    <div class="brand-card-container">
        <div class="brand-card">
            <div class="logo-wrap">
                <svg viewBox="0 0 100 100" preserveAspectRatio="none">
                    <path d="M0,70 Q25,30 50,70 T100,70 V100 H0 Z" fill="#00D09C" />
                </svg>
            </div>
            <div style="margin-top: 1rem; text-align: center;">
                <div style="font-weight: 700; font-size: 28px; color: #FFFFFF; font-family: 'Outfit'; letter-spacing: 2px; text-shadow: 0 4px 15px rgba(0,0,0,0.8);">GROWW FACTFINDER</div>
                <div style="color: #00D09C; font-size: 13px; font-weight: 700; letter-spacing: 3px; opacity: 0.9; margin-top: 5px; text-transform: uppercase;">SECURE HDFC DATA ENGINE</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- Persistent Header (Top of Every Page) ---
def render_persistent_header():
    st.markdown(f"""
    <div style="display: flex; align-items: center; justify-content: center; padding: 1.5rem 0; margin-top: -1rem; border-bottom: 1px solid rgba(255,255,255,0.06); margin-bottom: 2rem;">
        <div style="display: flex; align-items: center; gap: 12px;">
            <div style="background: #00D09C; width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; color: #000000; font-size: 12px; box-shadow: 0 0 10px rgba(0,208,156,0.3);">₹</div>
            <span style="font-weight: 700; font-size: 14px; color: #FFFFFF; font-family: 'Outfit'; letter-spacing: 1px; text-transform: uppercase;">Groww FactFinder</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Session State for Messages and Topic
if "messages" not in st.session_state:
    st.session_state.messages = []
if "topic_selected" not in st.session_state:
    st.session_state.topic_selected = False
if "selected_topic" not in st.session_state:
    st.session_state.selected_topic = None

# Render Persistent Header at the top
render_persistent_header()

# Landing State
if not st.session_state.topic_selected and not st.session_state.messages:
    render_finbot()
    st.markdown("<p style='text-align: center; color: #4B5563; font-size: 14px; margin-top: -1.5rem; margin-bottom: 2.5rem;'>Choose a category below to see common FAQs or ask anything manually.</p>", unsafe_allow_html=True)
    
    # Uniform Grid for Categories
    c1, c2, c3 = st.columns(3, gap="large")
    if c1.button("📊 Exit Load\nCheck Conditions"):
        st.session_state.topic_selected = True
        st.session_state.selected_topic = "Exit Load"
        st.rerun()
    if c2.button("🔒 Lock-in\nELSS Duration"):
        st.session_state.topic_selected = True
        st.session_state.selected_topic = "ELSS Lock-in"
        st.rerun()
    if c3.button("📑 SIP Limits\nMinimum Amount"):
        st.session_state.topic_selected = True
        st.session_state.selected_topic = "SIP Minimum"
        st.rerun()

elif st.session_state.topic_selected and not st.session_state.messages:
    
    # 4 FAQ Buttons in a 2x2 Grid with Bulletproof Fix
    st.markdown('<div id="faq-box-fix">', unsafe_allow_html=True)
    faq_col1, faq_col2 = st.columns(2)
    selected_faq = None
    
    topic = st.session_state.selected_topic
    
    if topic == "SIP Minimum":
        with faq_col1:
            if st.button("💰 What is the lowest amount I can invest via SIP?"):
                selected_faq = "What is the lowest amount I can invest via SIP in HDFC Funds?"
            if st.button("⚖️ Is minimum SIP same for all categories?"):
                selected_faq = "Is the minimum SIP amount the same for all HDFC mutual fund categories?"
        with faq_col2:
            if st.button("📈 Can I change my SIP amount after starting?"):
                selected_faq = "Can I increase or decrease my SIP amount after starting my HDFC SIP?"
            if st.button("❌ What if I miss an SIP payment?"):
                selected_faq = "What happens if I miss an HDFC SIP payment due to low bank balance?"
            
    elif topic == "Exit Load":
        with faq_col1:
            if st.button("🧮 How is the Exit Load calculated?"):
                selected_faq = "How exactly is the Exit Load calculated?"
            if st.button("🚫 Which funds have Zero Exit Load?"):
                selected_faq = "Which types of HDFC funds generally have Zero Exit Load?"
        with faq_col2:
            if st.button("⏳ Does 1-year rule apply to SIPs differently?"):
                selected_faq = "Does the 1-year Exit Load rule apply to SIPs differently?"
            if st.button("🔄 Is Load charged if I 'Switch' my funds?"):
                selected_faq = "Will I be charged an Exit Load if I 'Switch' my HDFC funds?"
            
    elif topic == "ELSS Lock-in":
        with faq_col1:
            if st.button("🆘 Can I withdraw ELSS early for emergency?"):
                selected_faq = "Can I withdraw HDFC ELSS funds early in case of an emergency?"
            if st.button("📑 Tax implications once lock-in ends?"):
                selected_faq = "What are the tax implications once the HDFC ELSS lock-in ends?"
        with faq_col2:
            if st.button("📅 How does Rolling Lock-in work for SIPs?"):
                selected_faq = "How does the 'Rolling Lock-in' work for HDFC ELSS SIPs?"
            if st.button("🔓 What to do once units are unlocked?"):
                selected_faq = "What should I do once my HDFC ELSS units are unlocked?"

    st.markdown('</div>', unsafe_allow_html=True)

    if selected_faq:
        st.session_state.messages.append({"role": "user", "content": selected_faq})
        st.rerun()



# PII Redaction Logic
def detect_pii(text):
    pan_pattern = r'[A-Z]{5}[0-9]{4}[A-Z]{1}'
    aadhaar_pattern = r'[0-9]{4}\s?[0-9]{4}\s?[0-9]{4}'
    if re.search(pan_pattern, text.upper()) or re.search(aadhaar_pattern, text):
        return True
    return False

# Response Processor
def process_query(user_query):
    # Step 1: Slot Filling Logic (Handling Ambiguity after security check)
    funds_in_scope = ["HDFC Top 100", "HDFC Flexi Cap", "HDFC Mid-Cap Opportunities", "HDFC ELSS Tax Saver"]
    found_fund = None
    for f in funds_in_scope:
        if f.lower() in user_query.lower():
            found_fund = f
            break
    
    # If broad query detected (Exit Load, SIP, etc.) WITHOUT fund name
    broad_keywords = ["exit load", "nav", "sip", "expense", "lock-in", "objective"]
    is_broad = any(k in user_query.lower() for k in broad_keywords)

    if is_broad and not found_fund:
        with st.chat_message("assistant", avatar="💹"):
            st.markdown(f"""
            <div class="fact-card">
                <div class="verified-badge">ℹ️ CLARIFICATION REQUIRED</div>
                <div class="bot-body">
                    I can certainly provide those details for you. However, I need to know which specific <b>HDFC Fund</b> you are referring to.
                </div>
                <p style="font-size: 13px; color: #9CA3AF; font-style: italic; margin-top: 10px;">
                    Please note that exit loads may vary based on the duration of your investment.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Identify the missing slot (Exit Load, etc.)
            intent = next((k for k in broad_keywords if k in user_query.lower()), "Information")
            
            # Interactive Choice Buttons
            st.markdown("<p style='font-size: 13px; font-weight: 600; margin-bottom: 5px; color: #9CA3AF;'>CHOOSE FUND TO CONFIRM:</p>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            
            if c1.button("Top 100", key=f"f1_{intent}"):
                st.session_state.messages.append({"role": "assistant", "content": "Clarification required.", "source": None})
                st.session_state.messages.append({"role": "user", "content": f"{intent} for HDFC Top 100 Fund"})
                st.rerun()
            if c2.button("Flexi Cap", key=f"f2_{intent}"):
                st.session_state.messages.append({"role": "assistant", "content": "Clarification required.", "source": None})
                st.session_state.messages.append({"role": "user", "content": f"{intent} for HDFC Flexi Cap Fund"})
                st.rerun()
            if c3.button("Mid-Cap", key=f"f3_{intent}"):
                st.session_state.messages.append({"role": "assistant", "content": "Clarification required.", "source": None})
                st.session_state.messages.append({"role": "user", "content": f"{intent} for HDFC Mid-Cap Opportunities Fund"})
                st.rerun()
        return

    # Step 3: Record query for cross-session memory
    record_query(user_query)

    # Step 4: Response Engine Execution
    with st.chat_message("assistant", avatar="💹"):
        with st.status("Reading Vault...", expanded=False) as status:
            full_res = get_assistant_answer(user_query)
            status.update(label="Retrieval Complete", state="complete", expanded=False)
        
        # Parse result and metadata
        parts = full_res.split("\nSource: ")
        answer_text = parts[0]
        metadata_part = parts[1] if len(parts) > 1 else ""
        source_url = metadata_part.split(" | ")[0].strip() if metadata_part else None

        # --- Aggressive Live URL Mapping (HDFC 2025/2026 Migration) ---
        if source_url:
            # 1. Standardize Directory
            for old_path in ["/product-solutions/overview/", "/product/"]:
                source_url = source_url.replace(old_path, "/explore/mutual-funds/")
            
            # 2. Hard-Map Fund Names to Verified Slugs (Absolute Fail-Safe)
            fund_redirects = {
                "top-100": "hdfc-large-cap-fund/direct",
                "large-cap": "hdfc-large-cap-fund/direct",
                "flexi-cap": "hdfc-flexi-cap-fund/direct",
                "tax": "hdfc-elss-tax-saver/direct",
                "elss": "hdfc-elss-tax-saver/direct",
                "mid-cap": "hdfc-mid-cap-fund/direct",
                "opportunities": "hdfc-mid-cap-fund/direct"
            }
            matched_fund = False
            for key, target_slug in fund_redirects.items():
                if key in source_url.lower():
                    source_url = f"https://www.hdfcfund.com/explore/mutual-funds/{target_slug}"
                    matched_fund = True
                    break
            
            # 3. Service / Account Statement URL fix (non-fund queries)
            if not matched_fund:
                service_keywords = ["statement", "account", "download", "cas", "service", "investor"]
                query_lower = user_query.lower()
                if any(kw in query_lower for kw in service_keywords):
                    source_url = "https://www.hdfcfund.com/investor-services"
        
        # --- Context Bridge (Cross-Session Continuity) ---
        bridge = get_context_bridge(user_query)
        if bridge:
            st.markdown(f'<div class="context-bridge">{bridge}</div>', unsafe_allow_html=True)

        # Render the Fact Card with explicit metadata
        st.markdown(f"""
        <div class="fact-card">
            <span class="verified-badge">VERIFIED SOURCE</span>
            <div class="bot-body">{answer_text}</div>
            <div style="margin-top: 15px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.05);">
                <span class="disclaimer-text" style="text-align: left; margin: 0; padding: 0;">
                    LAST UPDATED: MARCH 2026
                </span>
            </div>
            {f'''<a href="{source_url}" class="pdf-button" target="_blank"><span style="font-size: 15px; font-weight: 700;">📄 View factsheet</span><span style="font-size: 11px; font-weight: 400; opacity: 0.8;">source link</span></a>''' if source_url and source_url.startswith("http") else f'<div class="disclaimer-text">SOURCE: {source_url if source_url else "AMFI Investor Education"}</div>'}
        </div>
        """, unsafe_allow_html=True)

        # --- Retention Hook (Forward-Looking Data Hook) ---
        hook = get_retention_hook(user_query)
        if hook:
            st.markdown(f'<div class="retention-hook">{hook}</div>', unsafe_allow_html=True)


        
        # We place the button overlay or right next to it. 
        # Since I can't put st.button inside the raw HTML div and keep the flex layout easily,
        # I'll use columns but style the container of the columns.
        # Wait, I can just use st.columns and style the wrapper.
        
        save_key = f"save_{len(st.session_state.messages)}"
        col_nudge, col_btn = st.columns([5, 1])
        with col_nudge:
            st.markdown('<div style="line-height: 32px; color: #9CA3AF; font-size: 14px;">💡 Found this useful? Save it for quick access later.</div>', unsafe_allow_html=True)
        with col_btn:
            if st.button("💾 Save", key=save_key):
                save_insight(user_query, answer_text)
                st.toast("✅ Saved to your Personal Insight Vault!", icon="💾")
            
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer_text,
        "source": source_url if source_url else "AMFI Investor Education"
    })
    st.rerun()

# --- Render History with Explicit Metadata ---
for idx, msg in enumerate(st.session_state.messages):
    if msg["role"] == "user":
        with st.chat_message("user", avatar="👤"):
            st.markdown(f"**{msg['content']}**")
    else:
        with st.chat_message("assistant", avatar="💹"):
            source_content = msg.get("source")
            is_url = source_content and source_content.startswith("http")

            # --- Aggressive Live URL Mapping for History ---
            mapped_src = source_content.strip() if source_content else None
            if is_url and mapped_src:
                for old_path in ["/product-solutions/overview/", "/product/"]:
                    mapped_src = mapped_src.replace(old_path, "/explore/mutual-funds/")
                
                fund_redirects = {
                    "top-100": "hdfc-large-cap-fund/direct",
                    "large-cap": "hdfc-large-cap-fund/direct",
                    "flexi-cap": "hdfc-flexi-cap-fund/direct",
                    "tax": "hdfc-elss-tax-saver/direct",
                    "elss": "hdfc-elss-tax-saver/direct",
                    "mid-cap": "hdfc-mid-cap-fund/direct",
                    "opportunities": "hdfc-mid-cap-fund/direct"
                }
                for key, target_slug in fund_redirects.items():
                    if key in mapped_src.lower():
                        mapped_src = f"https://www.hdfcfund.com/explore/mutual-funds/{target_slug}"
                        break
            
            source_content = mapped_src
            
            st.markdown(f"""
            <div class="fact-card">
                <span class="verified-badge">VERIFIED SOURCE</span>
                <div class="bot-body">{msg['content']}</div>
                <div style="margin-top: 15px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.05);">
                    <span class="disclaimer-text" style="text-align: left; margin: 0; padding: 0;">
                        LAST UPDATED: MARCH 2026
                    </span>
                </div>
                {f'''<a href="{source_content}" class="pdf-button" target="_blank"><span style="font-size: 15px; font-weight: 700;">📄 View factsheet</span><span style="font-size: 11px; font-weight: 400; opacity: 0.8;">source link</span></a>''' if is_url else f'<div class="disclaimer-text">SOURCE: {source_content if source_content else "AMFI Investor Education"}</div>'}
            </div>
            """, unsafe_allow_html=True)

            # Save to Vault Ribbon (history rendering)
            save_key = f"save_hist_{idx}"
            col_nudge, col_btn = st.columns([5, 1])
            with col_nudge:
                st.markdown('<div style="line-height: 32px; color: #9CA3AF; font-size: 14px;">💡 Found this useful? Save it for quick access later.</div>', unsafe_allow_html=True)
            with col_btn:
                if st.button("💾 Save", key=save_key):
                    save_insight(msg.get('content', ''), msg.get('content', ''))
                    st.toast("✅ Saved to your Personal Insight Vault!", icon="💾")

# Execution (Moved up to ensure new responses render in history flow before navigation)
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user" and st.session_state.messages[-1]["content"] != "Security Redacted Query":
    process_query(st.session_state.messages[-1]["content"])

# --- Back Button (Fixed at Bottom Left - Visible except on Home) ---
if st.session_state.messages or st.session_state.topic_selected:
    st.markdown('<div class="back-nav-left-side">', unsafe_allow_html=True)
    if st.button("←", key="home_nav", help="Return to Home"):
        st.session_state.messages = []
        st.session_state.topic_selected = False
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# User Zone
prompt = st.chat_input("Ask about HDFC exit loads, SIP, T&Cs...")

if prompt:
    if detect_pii(prompt):
        st.session_state.messages.append({"role": "user", "content": "Security Redacted Query"})
        st.error("FIN-BOT ALERT: PII detected. Request blocked for security.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

# Clean Disclaimer below the input
st.markdown("""
    <div class="disclaimer-text">
        FACTUAL ANALYTICS ONLY. NO INVESTMENT ADVICE. DATA BASELINE: MARCH 2026.
    </div>
""", unsafe_allow_html=True)



# ================================================================
# SIDEBAR — Personal Insight Vault & Profile
# ================================================================
with st.sidebar:
    st.markdown("""<div style="text-align:center; padding: 1.5rem 0 1rem 0;">
        <span style="font-size: 26px;">💾</span>
        <div style="font-weight: 700; font-size: 16px; color: #FFFFFF; font-family: 'Outfit'; margin-top: 8px;">INSIGHT VAULT</div>
        <div style="font-size: 11px; color: #4B5563; letter-spacing: 1px; margin-top: 4px;">YOUR PERSONAL ARCHIVE</div>
    </div>""", unsafe_allow_html=True)

    # Profile Summary
    interests = get_past_interests_summary()
    if interests:
        st.markdown(f"""
        <div style="background: rgba(0,208,156,0.06); border: 1px solid rgba(0,208,156,0.15);
                    border-radius: 12px; padding: 12px; margin-bottom: 16px; font-size: 12px;">
            <span style="color: #00D09C; font-weight: 700; letter-spacing: 1px; font-size: 10px;">YOUR RESEARCH PROFILE</span><br>
            <span style="color: #9CA3AF;">{interests}</span>
        </div>
        """, unsafe_allow_html=True)

    vault_items = get_vault()
    vault_count = len(vault_items)
    st.caption(f"{vault_count} insight{'s' if vault_count != 1 else ''} saved")

    if vault_items:
        # We need the actual indices from the original vault_items to remove them correctly.
        full_vault = vault_items 
        count = len(full_vault)
        for i in range(count - 1, max(-1, count - 11), -1):
            item = full_vault[i]
            ts = item.get("timestamp", "")[:10]
            
            # Use two columns for Side-by-Side Remove Button
            v_col, r_col = st.columns([5, 1])
            
            with v_col:
                st.markdown(f"""
                <div class="vault-entry" style="margin-right: -10px;">
                    <strong>{item.get('query', 'Saved Insight')[:80]}</strong><br>
                    <span style="font-size: 11px;">{item.get('insight', '')[:150]}…</span><br>
                    <span style="font-size: 10px; color: #4B5563;">📌 {ts}</span>
                </div>
                """, unsafe_allow_html=True)
            
            with r_col:
                st.markdown('<div class="vault-remove-btn" style="margin-top: 20px;">', unsafe_allow_html=True)
                if st.button("✖", key=f"rm_{i}", help="Delete from vault"):
                    remove_insight(i)
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<p style="color: #4B5563; font-size: 12px; text-align: center; margin-top: 2rem;">No insights saved yet.<br>Ask questions and hit 💾 to build your vault.</p>', unsafe_allow_html=True)
