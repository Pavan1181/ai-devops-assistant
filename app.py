import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# Get Groq API key
api_key = os.getenv("GROQ_API_KEY")

# Check API key
if not api_key:
    st.error("GROQ_API_KEY not found. Check your .env file.")
    st.stop()

# Create Groq client
client = Groq(api_key=api_key)

# Page configuration
st.set_page_config(
    page_title="AI DevOps Assistant",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 AI DevOps Assistant")
st.write("Ask me about Linux, AWS, DevOps and troubleshooting.")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
prompt = st.chat_input("Ask a DevOps question...")

if prompt:
    # Show user message
    st.chat_message("user").markdown(prompt)

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    # AI instructions
    system_message = """
You are an AI DevOps Assistant specializing in Linux, AWS and DevOps.

For Linux-related questions:
1. Give the exact Linux command.
2. Explain what the command does.
3. Explain the important options/flags.
4. Give a realistic example.
5. If the command can be dangerous, clearly warn the user before suggesting it.

For AWS-related questions:
1. Explain the AWS service simply.
2. Give relevant AWS CLI commands when useful.
3. Explain the command.
4. Give troubleshooting steps.

For DevOps questions:
1. Identify the likely problem.
2. Give step-by-step troubleshooting.
3. Provide commands when appropriate.
4. Explain each command.

Important:
- Keep answers beginner-friendly.
- Never claim that you executed a command.
- Never claim that you changed an AWS resource or server.
- Ask for the error message or logs when necessary.
"""


    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system",
                    "content": system_message
                },
                *st.session_state.messages
            ],
            temperature=0.3,
            max_completion_tokens=1024
        )

        answer = response.choices[0].message.content

        # Display AI response
        with st.chat_message("assistant"):
            st.markdown(answer)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })

    except Exception as e:
        st.error(f"Error: {e}")
        st.divider()

st.subheader("📋 DevOps Log Analyzer")

log_text = st.text_area(
    "Paste your Linux / AWS / Docker logs here:",
    height=200,
    placeholder="Example:\nERROR: Connection refused\nFailed to start nginx.service"
)

if st.button("🔍 Analyze Logs"):
    if not log_text.strip():
        st.warning("Please paste some logs first.")
    else:
        with st.spinner("Analyzing logs..."):
            try:
                log_response = client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=[
                        {
                            "role": "system",
                            "content": """
You are a DevOps log analysis expert.

Analyze the provided logs and return:

1. 🔴 Errors detected
2. 🔎 Likely root cause
3. 🛠️ Step-by-step solution
4. 💻 Useful Linux/AWS/Docker commands
5. ⚠️ Important warnings

Keep the explanation beginner-friendly.
Do not claim that you executed any command.
"""
                        },
                        {
                            "role": "user",
                            "content": log_text
                        }
                    ],
                    temperature=0.2,
                    max_completion_tokens=1500
                )

                log_answer = log_response.choices[0].message.content

                st.success("Log analysis completed!")
                st.markdown(log_answer)

            except Exception as e:
                st.error(f"Log analysis error: {e}")
                # ---------------- Docker Troubleshooter ----------------

st.divider()
st.subheader("🐳 Docker Troubleshooter")

docker_error = st.text_area(
    "Paste your Docker error here:",
    height=180,
    placeholder="""Example:
docker: Error response from daemon:
Conflict. The container name is already in use.
The container name "/myapp" is already in use."""
)

if st.button("🐳 Troubleshoot Docker"):
    if not docker_error.strip():
        st.warning("Please paste a Docker error first.")
    else:
        with st.spinner("Analyzing Docker error..."):
            try:
                docker_response = client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=[
                        {
                            "role": "system",
                            "content": """
You are an expert Docker and DevOps troubleshooting assistant.

Analyze the Docker error provided by the user.

Return the answer in this structure:

## 🔴 Problem
Clearly identify the Docker problem.

## 🔎 Root Cause
Explain why the error is happening.

## 🛠️ Step-by-Step Solution
Give beginner-friendly steps to fix it.

## 💻 Commands
Provide the exact Docker/Linux commands when appropriate.
Explain what each command does.

## ⚠️ Warning
Before any destructive command such as:
docker rm
docker rmi
docker system prune
docker volume prune
or similar commands, clearly warn the user that data or resources may be deleted.

Important:
- Never claim that you executed a command.
- Never claim that you changed a Docker container or server.
- Do not invent command output.
- Ask for additional logs if the error is insufficient.
"""
                        },
                        {
                            "role": "user",
                            "content": docker_error
                        }
                    ],
                    temperature=0.2,
                    max_completion_tokens=1500
                )

                docker_answer = docker_response.choices[0].message.content

                st.success("Docker troubleshooting completed!")
                st.markdown(docker_answer)

            except Exception as e:
                st.error(f"Docker troubleshooting error: {e}")