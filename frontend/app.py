import streamlit as st
import requests

st.set_page_config(page_title="PlatformIQ", layout="wide")

# 🎨 Sidebar
st.sidebar.title("🚀 PlatformIQ")
st.sidebar.markdown("### AI Platform Portal")

page = st.sidebar.radio(
    "Navigation",
    ["🏠 Dashboard", "🤖 AI Assistant", "🐙 GitHub", "☁️ AWS"]
)

st.sidebar.markdown("---")
st.sidebar.info("AI-Powered Platform Engineering Portal")

# =======================
# 🏠 Dashboard
# =======================
if page == "🏠 Dashboard":
    st.title("📊 Platform Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric("💰 Cloud Cost", "$420", "+5%")
    col2.metric("⚠️ Active Incidents", "1", "-1")
    col3.metric("🧠 AI Insights", "3", "+2")

    st.markdown("---")

    st.subheader("📌 Recent Activity")
    st.write("• Deployment v2.1.3 completed")
    st.write("• GitHub workflow succeeded")
    st.write("• CPU spike detected in checkout service")

# =======================
# 🤖 AI Assistant
# =======================
elif page == "🤖 AI Assistant":
    st.title("🤖 AI Assistant")

    query = st.text_input("Ask anything about your platform:")

    if st.button("Ask AI"):
        if not query:
            st.warning("Please enter a question")
        else:
            with st.spinner("Thinking..."):
                try:
                    response = requests.post(
                        "http://127.0.0.1:8000/query",
                        json={"question": query},
                        timeout=10
                    )

                    result = response.json()

                    st.success("Response received!")
                    st.markdown("### 🧠 AI Response")
                    st.write(result.get("response", "No response"))

                except Exception as e:
                    st.error(f"Error: {e}")

# =======================
# 🐙 GitHub Page
# =======================
elif page == "🐙 GitHub":
    st.title("🐙 GitHub Insights")

    if st.button("Fetch GitHub Data"):
        try:
            response = requests.post(
                "http://127.0.0.1:8000/query",
                json={"question": "show github status"},
            )

            data = response.json()

            st.subheader("📌 Latest Insights")
            st.write(data.get("response"))

        except Exception as e:
            st.error(f"Error: {e}")

# =======================
# ☁️ AWS Page
# =======================
elif page == "☁️ AWS":
    st.title("☁️ AWS Insights")

    if st.button("Fetch AWS Data"):
        try:
            response = requests.post(
                "http://127.0.0.1:8000/query",
                json={"question": "aws cost"},
            )

            data = response.json()

            st.subheader("💰 Cost Summary")
            st.write(data.get("response"))

        except Exception as e:
            st.error(f"Error: {e}")