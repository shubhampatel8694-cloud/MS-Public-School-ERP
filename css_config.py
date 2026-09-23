import streamlit as st

def apply_custom_css():
    page_bg_css = """
    <style>
    /* 🌟 CLEAN HEADER & MENU BUTTON FIX 🌟 */
    #MainMenu { display: none !important; }
    footer { display: none !important; }
    [data-testid="stDecoration"] { display: none !important; }
    
    /* Strict rules to hide all top-right icons */
    [data-testid="stToolbar"], 
    [data-testid="stActionElements"], 
    .stAppToolbar { 
        display: none !important; 
        visibility: hidden !important; 
        opacity: 0 !important;
    }

    /* Header ko background color se match kar diya taaki black patti na dikhe */
    [data-testid="stHeader"] { 
        background-color: #0b214a !important; 
    }

    /* Menu Button ko White aur visible karna */
    [data-testid="collapsedControl"], [data-testid="collapsedControl"] svg, button[kind="header"] svg {
        color: #ffffff !important;
        fill: #ffffff !important;
        visibility: visible !important;
        display: flex !important;
    }

    /* Sidebar Theme */
    [data-testid="stSidebar"] {
        background-color: #0b214a !important;
        border-right: 1px solid rgba(255,255,255,0.1) !important;
    }

    /* 🌟 UNIFIED APP BACKGROUND (Dark Blue) 🌟 */
    .stApp { background-color: #0b214a !important; }
    .block-container { max-width: 1350px; padding-top: 2rem !important; padding-left: 2rem; padding-right: 2rem; }

    /* Force General Text to White */
    .stApp, .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp span, .stApp label, .stApp div { color: #f8fafc; }

    /* Navbar Area */
    .nav-links { display: flex; gap: 30px; font-weight: 600; font-size: 16px; margin-top: 25px; justify-content: center;}
    .nav-links span { cursor: pointer; transition: all 0.3s; opacity: 0.9; color: white; padding-bottom: 5px;}
    .nav-links span:hover { color: #0ea5e9; opacity: 1; transform: translateY(-2px);}

    /* 🌟 STANDARD BUTTONS 🌟 */
    div[data-testid="stButton"] button, 
    div[data-testid="stFormSubmitButton"] button {
        background: linear-gradient(45deg, #e11d48, #be123c) !important; color: #ffffff !important; 
        border: 1px solid rgba(255,255,255,0.2) !important; border-radius: 8px !important; 
        font-weight: 700 !important; padding: 0.6rem 1.5rem !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4) !important; transition: all 0.3s ease !important; margin-top: 10px; 
    }
    div[data-testid="stButton"] button:hover, 
    div[data-testid="stFormSubmitButton"] button:hover {
        transform: translateY(-4px) !important; 
        box-shadow: 0 10px 25px rgba(225, 29, 72, 0.7) !important;
        background: linear-gradient(45deg, #be123c, #9f1239) !important; border-color: #ff4d6d !important;
    }

    /* 🌟 FIXED INPUT FIELDS 🌟 */
    .stTextInput input, .stNumberInput input, .stDateInput input, .stTextArea textarea, div[data-baseweb="select"] > div {
        background-color: #ffffff !important; 
        border: 2px solid rgba(255, 255, 255, 0.3) !important; 
        border-radius: 8px !important; color: #000000 !important; font-weight: 800 !important; 
        padding: 10px !important;
    }
    .stTextInput input:focus, .stNumberInput input:focus, div[data-baseweb="select"] > div:focus-within {
        border-color: #0ea5e9 !important; box-shadow: 0 0 15px rgba(14, 165, 233, 0.8) !important;
    }

    /* 🌟 FORMS & CARDS 🌟 */
    [data-testid="stForm"], .content-box, .dash-card, [data-testid="stDataFrame"] {
        background-color: rgba(255, 255, 255, 0.05) !important; border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 12px !important; padding: 30px !important; box-shadow: 0 6px 15px rgba(0, 0, 0, 0.4) !important; 
        backdrop-filter: blur(10px); transition: all 0.4s ease !important; margin-bottom: 25px !important;
    }
    [data-testid="stForm"]:hover, .content-box:hover, .dash-card:hover {
        transform: translateY(-8px) !important; box-shadow: 0 15px 35px rgba(14, 165, 233, 0.45) !important; border-color: #0ea5e9 !important; 
    }
    [data-testid="stForm"] { border-top: 4px solid #e11d48 !important; margin-top: 15px !important; }

    /* Typography */
    .hero-title { font-size: 50px; font-weight: 800; margin: 0; line-height: 1.2; color: #ffffff !important;}
    .hero-subtitle { font-size: 24px; margin: 15px 0 20px 0; font-weight: 600; color: #0ea5e9 !important;}
    .side-card-header h3 { color: #ffffff !important; margin:0; font-size: 20px; font-weight: 800; border-bottom: 2px solid rgba(255,255,255,0.1); padding-bottom: 12px;}

    /* Sidebar & Radio Buttons */
    div[role="radiogroup"] { justify-content: center; margin-bottom: 20px; margin-top: 10px; gap: 15px; }
    div[role="radiogroup"] label {
        background-color: rgba(255,255,255,0.05) !important; border: 1px solid rgba(255,255,255,0.2) !important;
        padding: 12px 25px !important; border-radius: 8px !important; cursor: pointer !important;
    }
    .main div[role="radiogroup"] label:has(input:checked) {
        background: linear-gradient(45deg, #e11d48, #be123c) !important; border-color: #ff4d6d !important; transform: translateY(-4px) !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
        background: linear-gradient(45deg, #0ea5e9, #0284c7) !important; border-color: #38bdf8 !important;
    }
    div[role="radiogroup"] label:has(input:checked) p { color: #ffffff !important; font-weight: 800 !important;}

    /* DATE TEXT FIX */
    div[data-baseweb="input"] *, div[data-baseweb="base-input"] *, div[data-baseweb="calendar"] *, div[data-testid="stDateInput"] input { color: #000000 !important; -webkit-text-fill-color: #000000 !important; font-weight: 900 !important; }

    /* TABLE FIX */
    [data-testid="stDataFrame"] { padding: 0px !important; background: transparent !important; border: none !important; box-shadow: none !important; margin-bottom: 25px !important;}
    [data-testid="stDataFrame"] > div { border-radius: 8px !important; overflow: hidden !important; border: 1px solid #94a3b8 !important; filter: invert(0.95) hue-rotate(180deg) brightness(1.05) !important;}
    [data-testid="stElementToolbar"] { filter: invert(0.95) hue-rotate(180deg) brightness(1.05) !important;}
    </style>
    """
    st.markdown(page_bg_css, unsafe_allow_html=True)