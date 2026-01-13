"""Custom CSS styles for PyLive UI."""

import streamlit as st


def apply_custom_styles():
    """Apply custom CSS styles to the app."""
    st.markdown("""
    <style>
    /* Dark theme base */
    .stApp {
        background-color: #09090b;
    }

    /* Text colors */
    .stMarkdown, .stText, p, span, label {
        color: #fafafa !important;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #fafafa !important;
    }

    /* Remove Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Reduce spacing */
    div[data-testid="stVerticalBlock"] {
        gap: 0.5rem;
    }

    /* Input styling */
    .stTextInput > div > div > input {
        background-color: #18181b;
        border: 1px solid #27272a;
        color: #fafafa;
        border-radius: 0.5rem;
    }

    .stTextInput > div > div > input:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
    }

    /* Text area styling */
    .stTextArea > div > div > textarea {
        background-color: #18181b;
        border: 1px solid #27272a;
        color: #fafafa;
        border-radius: 0.5rem;
    }

    /* Button styling */
    .stButton > button {
        background-color: #3b82f6;
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: background-color 0.2s;
    }

    .stButton > button:hover {
        background-color: #2563eb;
    }

    /* Container styling */
    div[data-testid="stHorizontalBlock"] {
        align-items: center;
    }

    /* Divider */
    hr {
        border-color: #27272a;
        margin: 1rem 0;
    }

    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: #18181b;
    }

    ::-webkit-scrollbar-thumb {
        background: #3f3f46;
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #52525b;
    }

    /* Card-like containers */
    .element-container {
        background: transparent;
    }

    /* Success/Error/Warning messages */
    .stSuccess {
        background-color: rgba(34, 197, 94, 0.1);
        border: 1px solid #22c55e;
    }

    .stError {
        background-color: rgba(239, 68, 68, 0.1);
        border: 1px solid #ef4444;
    }

    .stWarning {
        background-color: rgba(234, 179, 8, 0.1);
        border: 1px solid #eab308;
    }

    .stInfo {
        background-color: rgba(59, 130, 246, 0.1);
        border: 1px solid #3b82f6;
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: #27272a;
        border-radius: 0.5rem;
        color: #a1a1aa;
        padding: 0.5rem 1rem;
    }

    .stTabs [aria-selected="true"] {
        background-color: #3b82f6;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)
