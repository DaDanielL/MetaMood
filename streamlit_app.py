"""Minimal Streamlit dashboard shell for MetaMood."""

import streamlit as st

from app import APP_VERSION


def main() -> None:
    st.set_page_config(page_title="MetaMood", layout="wide")

    st.title("MetaMood")
    st.caption(f"Live-ops patch intelligence demo, version {APP_VERSION}")

    st.header("Game Monitor")
    st.write(
        "MetaMood is ready for the foundation flow. Game catalog loading, "
        "cloud configuration status, and analysis controls will be added in "
        "later stories."
    )

    st.info("This shell does not require Steam, Qwen, OSS, RDS, or Knowledge Base credentials.")


if __name__ == "__main__":
    main()
