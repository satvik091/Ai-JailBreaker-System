import streamlit as st
import logging
import re
import groq
from guardrails import Guard
from fastapi import FastAPI

# Store Groq API Key securely 
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

# Initialize Groq Client
groq_client = groq.Client(api_key=GROQ_API_KEY)

# Configure logging 
logging.basicConfig(level=logging.WARNING)

# Jailbreak Prompt Patterns
jailbreak_patterns = [
    r"ignore all previous instructions",
    r"bypass your restrictions",
    r"tell me how to",
    r"pretend you are evil",
    r"forget your safety rules",
]

# Simple custom toxicity check function
def is_toxic(text):
    """
    Basic custom toxicity detection function
    Returns True if text contains toxic language
    """
    toxic_words = [
        'fuck', 'shit', 'bitch', 'cunt', 'nigger', 
        'asshole', 'bastard', 'racist', 'hate', 
        'kill', 'die', 'destroy', 'violent'
    ]
    
    # Convert text to lowercase for case-insensitive matching
    text_lower = text.lower()
    
    # Check for toxic words
    for word in toxic_words:
        if word in text_lower:
            return True
    
    return False

# Function to Detect Jailbreaking Attempts
def detect_jailbreak(prompt):
    for pattern in jailbreak_patterns:
        if re.search(pattern, prompt, re.IGNORECASE):
            st.warning(f"🚨 Possible Jailbreak Attempt: {prompt}")
            return True
    return False

# Function to Call Groq API
def get_groq_response(prompt):
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",  # Change to any available Groq model
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

# Streamlit UI
st.title("🔐 AI Interview System with Groq & Jailbreak Protection")
st.write("This AI assistant ensures ethical and safe responses.")

# User Input
user_input = st.text_area("Ask a question:")

# Submit Button
if st.button("Get AI Response"):
    if not user_input.strip():
        st.warning("⚠️ Please enter a valid question.")
    else:
        # Step 1: Check for Jailbreak Attempts
        if detect_jailbreak(user_input):
            st.error("🚨 Jailbreak Attempt Detected! Your request is blocked.")
        else:
            # Step 2: Get AI Response from Groq
            ai_response = get_groq_response(user_input)
           
            # Step 3: Custom Toxicity Check
            if is_toxic(ai_response):
                st.error("Response contains toxic language and has been blocked.")
            else:
                st.success(ai_response)
