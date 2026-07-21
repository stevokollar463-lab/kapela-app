import streamlit as st
from config import KAPELA_FOTO_URL


def apply_style():
    st.markdown(f"""
        <style>
        .stApp {{
            background: linear-gradient(rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0.75)),
                        url("{KAPELA_FOTO_URL}");
            background-size: cover;
            background-position: center center;
            background-attachment: fixed;
            image-rendering: -webkit-optimize-contrast;
            color: #ffffff;
        }}

        [data-testid="collapsedSidebarNoOverlay"],
        [data-testid="stSidebar"],
        button[data-testid="stSidebarCollapseButton"] {{
            display: none !important;
        }}

        [data-testid="stToolbar"] {{
            display: none !important;
        }}

        .stDeployButton {{
            display: none !important;
        }}

        h1, h2, h3, h4 {{ color: #d4af37 !important; font-family: 'Playfair Display', serif; text-shadow: 4px 4px 8px #000000; text-align: center; }}

        .info-box {{
            background: rgba(212, 175, 55, 0.15);
            border: 1px solid #d4af37;
            padding: 15px;
            border-radius: 15px;
            text-align: center;
            margin: 10px 0;
        }}

        .cennik-container {{
            background: rgba(0, 0, 0, 0.85);
            border: 2px solid #d4af37;
            padding: 25px;
            border-radius: 20px;
            box-shadow: 0 0 25px rgba(212, 175, 55, 0.25);
            margin-bottom: 25px;
        }}

        .expandable-section {{
            background: rgba(0, 0, 0, 0.9);
            border: 2px solid #d4af37;
            border-radius: 15px;
            padding: 25px;
            margin-top: 20px;
            margin-bottom: 20px;
            box-shadow: 0 0 30px rgba(212, 175, 55, 0.3);
            animation: slideDown 0.3s ease-out;
        }}

        @keyframes slideDown {{
            from {{
                opacity: 0;
                transform: translateY(-20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        .section-title {{
            color: #d4af37;
            font-size: 1.5rem;
            font-weight: bold;
            text-align: center;
            margin-bottom: 20px;
            border-bottom: 2px solid #d4af37;
            padding-bottom: 10px;
        }}

        .faq-item {{
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 1px solid rgba(212, 175, 55, 0.3);
        }}

        .faq-item:last-child {{
            border-bottom: none;
        }}

        .faq-otazka {{
            font-weight: bold;
            color: #d4af37;
            margin-bottom: 8px;
            font-size: 1rem;
        }}

        .faq-odpoved {{
            color: #ccc;
            line-height: 1.5;
            font-size: 0.95rem;
        }}

        .kontakt-info {{
            text-align: center;
            margin: 15px 0;
            padding: 12px;
            background: rgba(212, 175, 55, 0.1);
            border-left: 4px solid #d4af37;
            border-radius: 8px;
        }}

        .kontakt-label {{
            color: #d4af37;
            font-weight: bold;
            font-size: 1rem;
        }}

        .kontakt-value {{
            color: #fff;
            font-size: 1rem;
            margin-top: 5px;
        }}

        .o-nas-box {{
            background: rgba(0, 0, 0, 0.85);
            border: 2px solid #d4af37;
            padding: 25px;
            border-radius: 15px;
            margin: 20px 0;
        }}

        .o-nas-text {{
            color: #ccc;
            line-height: 1.8;
            font-size: 1rem;
        }}

        .clenovia-box {{
            background: rgba(212, 175, 55, 0.1);
            border-left: 4px solid #d4af37;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
        }}

        .stForm {{ background-color: rgba(0, 0, 0, 0.8) !important; border: 2px solid #d4af37 !important; border-radius: 20px; padding: 30px; }}
        .stButton>button {{ background-color: #d4af37 !important; color: black !important; border-radius: 12px !important; font-weight: bold !important; width: 100%; transition: 0.3s; }}

        .admin-detail-box {{
            background-color: rgba(0, 100, 255, 0.15);
            border-left: 5px solid #0064ff;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
            font-size: 0.95rem;
        }}

        div[data-testid="stRadio"] {{
            background: transparent !important;
            padding: 10px 0 !important;
        }}
        div[data-testid="stRadio"] > div[role="radiogroup"] {{
            display: flex !important;
            flex-direction: row !important;
            justify-content: center !important;
            flex-wrap: wrap !important;
            gap: 12px !important;
        }}
        div[data-testid="stRadio"] div[role="radiogroup"] > label > div:first-child {{
            display: none !important;
        }}
        div[data-testid="stRadio"] div[role="radiogroup"] > label {{
            background-color: rgba(0, 0, 0, 0.75) !important;
            border: 2px solid #d4af37 !important;
            color: #ffffff !important;
            padding: 12px 24px !important;
            border-radius: 30px !important;
            cursor: pointer !important;
            transition: all 0.3s ease !important;
            font-weight: bold !important;
            text-align: center !important;
            box-shadow: 0 4px 10px rgba(0,0,0,0.5) !important;
            min-width: 140px !important;
        }}
        div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {{
            background-color: rgba(212, 175, 55, 0.25) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 15px rgba(212, 175, 55, 0.3) !important;
        }}
        div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] {{
            background-color: #d4af37 !important;
            color: #000000 !important;
            box-shadow: 0 0 18px #d4af37 !important;
            border-color: #ffffff !important;
        }}
        </style>
    """, unsafe_allow_html=True)
