"""Streamlit UI for the Caesar cipher and Playfair cipher assignment.

All cryptography lives in caesar_cipher.py and playfair_cipher.py; this file only
handles layout, session state and user feedback.
"""

from __future__ import annotations

import streamlit as st

import caesar_cipher as caesar
import playfair_cipher as playfair

st.set_page_config(page_title="Cryptography Project", page_icon="🔐", layout="centered")

THEME_CSS = """
<style>
:root {
    --navy: #0a1628;
    --panel: #0f2038;
    --field: #0c1b31;
    --line: #1d3a5c;
    --text: #d5e3f4;
    --muted: #8aa3c2;
    --cyan: #22d3ee;
    --blue: #3b82f6;
}
.stApp { background: var(--navy); color: var(--text); }
[data-testid="stHeader"] { background: transparent; }
.block-container { max-width: 860px; padding-top: 2.5rem; }
h1, h2, h3, h4 { color: #eaf4ff; letter-spacing: -0.01em; }
p, label, li, span { color: var(--text); }
[data-testid="stCaptionContainer"], small { color: var(--muted) !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 0.25rem; border-bottom: 1px solid var(--line); }
.stTabs [data-baseweb="tab"] { color: var(--muted); padding: 0.6rem 1.1rem; }
.stTabs [aria-selected="true"] { color: var(--cyan); }
.stTabs [data-baseweb="tab-highlight"] { background-color: var(--cyan); }

/* Inputs */
textarea, input {
    background: var(--field) !important;
    color: var(--text) !important;
    caret-color: var(--cyan);
}
[data-baseweb="textarea"], [data-baseweb="base-input"] {
    background: var(--field) !important;
    border-color: var(--line) !important;
}
[data-baseweb="textarea"]:focus-within, [data-baseweb="base-input"]:focus-within {
    border-color: var(--cyan) !important;
}
textarea:disabled { -webkit-text-fill-color: var(--text) !important; opacity: 1 !important; }

/* Buttons */
.stButton > button, .stDownloadButton > button {
    background: var(--panel);
    color: var(--cyan);
    border: 1px solid var(--line);
    border-radius: 8px;
    font-weight: 600;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    border-color: var(--cyan);
    color: #fff;
    background: #123055;
}
.stButton > button[kind="primary"], .stButton > button[data-testid="stBaseButton-primary"] {
    background: linear-gradient(135deg, var(--cyan), var(--blue));
    color: #04101f;
    border: none;
}
.stButton > button[kind="primary"]:hover, .stButton > button[data-testid="stBaseButton-primary"]:hover {
    color: #04101f;
    filter: brightness(1.1);
}

/* Code blocks and expanders */
[data-testid="stCode"], .stCodeBlock, pre {
    background: var(--field) !important;
    border: 1px solid var(--line);
    border-radius: 8px;
}
[data-testid="stExpander"] { border: 1px solid var(--line); border-radius: 8px; background: var(--panel); }
[data-testid="stExpander"] summary { color: var(--cyan); }

@media (max-width: 640px) {
    .block-container { padding-left: 1rem; padding-right: 1rem; }
}
</style>
"""
st.markdown(THEME_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session state defaults (keys persist across reruns, including the RSA pair)
# ---------------------------------------------------------------------------
DEFAULTS = {
    "caesar_text": "",
    "caesar_shift": 3,
    "caesar_result": None,  # dict with mode/text/shift/output, or {"error": ...}
    "playfair_text": "",
    "playfair_key": "MONARCHY",
    "playfair_result": None,
}
for _key, _value in DEFAULTS.items():
    st.session_state.setdefault(_key, _value)


# ---------------------------------------------------------------------------
# Caesar callbacks
# ---------------------------------------------------------------------------
def run_caesar(mode: str) -> None:
    """Encrypt or decrypt the current input and store the outcome."""
    text = st.session_state.caesar_text
    shift = st.session_state.caesar_shift
    if not text:
        st.session_state.caesar_result = {"error": "Enter some text first."}
        return
    try:
        operation = caesar.caesar_encrypt if mode == "encrypt" else caesar.caesar_decrypt
        output = operation(text, shift)
    except ValueError as exc:
        st.session_state.caesar_result = {"error": str(exc)}
        return
    st.session_state.caesar_result = {
        "mode": mode,
        "text": text,
        "shift": int(shift),
        "output": output,
    }


def reset_caesar() -> None:
    st.session_state.caesar_text = DEFAULTS["caesar_text"]
    st.session_state.caesar_shift = DEFAULTS["caesar_shift"]
    st.session_state.caesar_result = None


# ---------------------------------------------------------------------------
# Playfair callbacks
# ---------------------------------------------------------------------------
def run_playfair(mode: str) -> None:
    """Encrypt or decrypt using Playfair cipher and store the outcome."""
    text = st.session_state.playfair_text
    key = st.session_state.playfair_key
    if not text:
        st.session_state.playfair_result = {"error": "Enter some text first."}
        return
    if not key:
        st.session_state.playfair_result = {"error": "Enter a secret key phrase."}
        return
    try:
        outcome = playfair.playfair_process(text, key, mode)
    except ValueError as exc:
        st.session_state.playfair_result = {"error": str(exc)}
        return
    st.session_state.playfair_result = outcome


def reset_playfair() -> None:
    st.session_state.playfair_text = DEFAULTS["playfair_text"]
    st.session_state.playfair_key = DEFAULTS["playfair_key"]
    st.session_state.playfair_result = None


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------
st.title("Cryptography Project")
st.caption("Cryptography & Network Security: Caesar cipher and Playfair cipher")

caesar_tab, playfair_tab = st.tabs(["Caesar Cipher", "Playfair Cipher"])

# ----------------------------- Caesar tab ----------------------------------
with caesar_tab:
    st.subheader("Caesar Cipher")
    st.text_area("Input text", key="caesar_text", height=130, placeholder="HELLO WORLD")
    st.number_input(
        "Shift key",
        key="caesar_shift",
        min_value=-1_000_000_000,
        max_value=1_000_000_000,
        step=1,
        format="%d",
        help="Any whole number. Negative and large values wrap around the 26-letter alphabet.",
    )

    enc_col, dec_col, reset_col = st.columns(3)
    enc_col.button(
        "Encrypt", key="caesar_encrypt_btn", type="primary", use_container_width=True,
        on_click=run_caesar, args=("encrypt",),
    )
    dec_col.button(
        "Decrypt", key="caesar_decrypt_btn", use_container_width=True,
        on_click=run_caesar, args=("decrypt",),
    )
    reset_col.button(
        "Reset", key="caesar_reset_btn", use_container_width=True, on_click=reset_caesar
    )

    result = st.session_state.caesar_result
    if result:
        if "error" in result:
            st.error(result["error"])
        else:
            verb = "Encrypted" if result["mode"] == "encrypt" else "Decrypted"
            st.success(f"{verb} successfully.")
            st.markdown("**Entered text**")
            st.code(result["text"], language=None)
            st.markdown("**Shift key**")
            st.code(str(result["shift"]), language=None)
            st.markdown(f"**{verb} output**")
            st.code(result["output"], language=None)  # code blocks include a copy button
            report = (
                f"Mode: {result['mode']}\n"
                f"Shift key: {result['shift']}\n"
                f"Input: {result['text']}\n"
                f"Output: {result['output']}\n"
            )
            st.download_button(
                "Download result",
                data=report,
                file_name=f"caesar_{result['mode']}.txt",
                mime="text/plain",
                key="caesar_download_btn",
            )

# ---------------------------- Playfair tab ---------------------------------
with playfair_tab:
    st.subheader("Playfair Cipher")
    st.caption("5x5 polyalphabetic matrix cipher. 'I' and 'J' share a single cell; 'X' (or 'Z') is used as filler.")

    st.text_area("Input text", key="playfair_text", height=130, placeholder="INSTRUMENTS")
    st.text_input(
        "Secret key",
        key="playfair_key",
        placeholder="MONARCHY",
        help="Letters only. Duplicates are removed and 'J' is mapped to 'I'.",
    )

    # Live key matrix preview
    current_key = st.session_state.playfair_key
    if current_key and any(ch.isalpha() for ch in current_key):
        try:
            preview_matrix = playfair.generate_key_matrix(current_key)
            with st.expander("5x5 Key Matrix preview", expanded=False):
                st.code(playfair.format_matrix(preview_matrix), language=None)
        except Exception:
            pass

    enc_col, dec_col, reset_col = st.columns(3)
    enc_col.button(
        "Encrypt", key="playfair_encrypt_btn", type="primary", use_container_width=True,
        on_click=run_playfair, args=("encrypt",),
    )
    dec_col.button(
        "Decrypt", key="playfair_decrypt_btn", use_container_width=True,
        on_click=run_playfair, args=("decrypt",),
    )
    reset_col.button(
        "Reset", key="playfair_reset_btn", use_container_width=True, on_click=reset_playfair
    )

    pf_result = st.session_state.playfair_result
    if pf_result:
        if "error" in pf_result:
            st.error(pf_result["error"])
        else:
            verb = "Encrypted" if pf_result["mode"] == "encrypt" else "Decrypted"
            st.success(f"{verb} successfully.")

            st.markdown("**5x5 Key Matrix**")
            st.code(pf_result["matrix_str"], language=None)

            st.markdown("**Input digraph pairs**")
            st.code(pf_result["formatted_digraphs_in"], language=None)

            st.markdown(f"**{verb} digraph pairs**")
            st.code(pf_result["formatted_digraphs_out"], language=None)

            st.markdown(f"**{verb} output**")
            st.code(pf_result["output"], language=None)

            report = (
                f"Mode: {pf_result['mode']}\n"
                f"Key: {pf_result['key']} (Cleaned: {pf_result['cleaned_key']})\n\n"
                f"5x5 Key Matrix:\n{pf_result['matrix_str']}\n\n"
                f"Input Text: {pf_result['input_text']}\n"
                f"Input Digraphs: {pf_result['formatted_digraphs_in']}\n"
                f"Output Digraphs: {pf_result['formatted_digraphs_out']}\n"
                f"Output: {pf_result['output']}\n"
            )
            st.download_button(
                "Download result",
                data=report,
                file_name=f"playfair_{pf_result['mode']}.txt",
                mime="text/plain",
                key="playfair_download_btn",
            )

