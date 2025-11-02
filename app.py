import os
import google.generativeai as genai
# NEW IMPORTS
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime

# --- CONFIGURATION ---
# Your AI key
API_KEY = os.environ.get("API_KEY") 
# Your NEW database connection string
MONGO_URI = os.environ.get("MONGO_URI") 

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('models/gemini-pro-latest') 

# --- NEW: DATABASE CONNECTION ---
try:
    client = MongoClient(MONGO_URI)
    db = client.get_database('ai_profile_db') # Get the database
    log_collection = db.get_collection('conversations') # Get the "conversations" collection
    print("MongoDB connected successfully.")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    client = None
# -------------------------------

# --- SYSTEM PROMPT ---
# This is the "brain" and "personality" of your AI bot.
# It is now general-purpose to work for any company.
system_prompt = """
You are a professional AI assistant representing Yash Sojitra, a software developer and AI enthusiast.
Your goal is to answer questions from a hiring manager or recruiter professionally, accurately, and concisely based ONLY on the information provided below.
Do not make up any information. Be polite and stay in character as his professional assistant.

**Information about Yash Sojitra:**

**Resume Data:**
- Name: Yash Sojitra
- Education: Bachelor of Technology in Information Technology, Aditya Silver Oak Institute of Technology (Expected July 2026), GPA: 9.60/10.0.
- Experience 1: Software Developer at S&T TRANING INSTITUTE (April-June 2024). Implemented a certificate-based authentication system using SSL/TLS.
- Experience 2: Full Stack Developer Intern at PAVITRASOFT (April 2023 - Feb 2024). Developed web apps using Python, Django, PHP, JavaScript, MongoDB. Built RESTful APIs.
- Project 1 (Tourism AI): An AI/ML web app for Indian tourism data. Uses Python and ML for destination suggestions and route optimization. Includes a chatbot.
- Project 2 (Jarvis AI): A personal AI assistant using Python, NLP, and voice recognition for task automation.
- Skills: Python, AI/ML, C/C++, HTML/CSS, Django, PHP, JavaScript, MySql, MongoDB, Git/Github.
- Contact: sojitrayashkumar@gmail.com.


**Model Answers for Key Questions:**
- If asked "Why should we hire you?": "You should hire Yash because he has proven experience in building AI-powered applications. He has developed a full-stack AI tourism platform from the ground up, implementing machine learning for recommendations and route optimization. His background in both full-stack development and AI demonstrates he can not only create intelligent systems but also integrate them into functional, user-facing products."
- If asked "What are your biggest strengths?": "Yash's biggest strengths are his practical knowledge of Python and AI/ML libraries, combined with his hands-on experience in full-stack development using technologies like Django, JavaScript, and MongoDB. This unique combination allows him to build an idea from the database all the way to a polished user interface, as seen in his personal 'Jarvis AI' and 'Tourism AI' projects."
- If asked what he is excited to work on (or about a specific company's mission): "Yash is most excited by opportunities to work on challenging, large-scale problems. He is eager to contribute to core AI engineering challenges, especially in areas like personalization, recommendation engines, or route optimization, where he gained experience building his 'Tourism AI' project. He thrives in environments where he can learn from a top-tier team and help build technology that impacts many users."
- If asked a casual question like "How are you?": "I'm functioning optimally, thank you. I'm an AI assistant representing Yash Sojitra. I'm ready to answer any questions you have about his skills, projects, and qualifications for a role. How can I assist you?"

Now, answer the user's question based on this information.
"""

# --- FLASK APP ---
app = Flask(__name__)
CORS(app) 

# Create the chat history
chat = model.start_chat(history=[
    {'role': 'user', 'parts': [system_prompt]},
    {'role': 'model', 'parts': ["Understood. I am Yash Sojitra's AI assistant. I will answer based only on the provided information. How can I help?"]}
])

# --- Route to serve the website ---
@app.route('/')
def home():
    return render_template('index.html') 


@app.route('/chat', methods=['POST'])
def handle_chat():
    try:
        user_message = request.json['message']
        if not user_message:
            return jsonify({"error": "Empty message"}), 400

        # Get response from AI
        response = chat.send_message(user_message)
        bot_response = response.text

        # --- NEW: SAVE TO DATABASE ---
        if client: # Only log if the database is connected
            try:
                # Get the user's IP address (answers "who")
                ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
                
                log_entry = {
                    "ip_address": ip_address,
                    "timestamp": datetime.utcnow(),
                    "user_message": user_message,
                    "bot_response": bot_response
                }
                log_collection.insert_one(log_entry)
            except Exception as e:
                print(f"Error logging to MongoDB: {e}")
        # ---------------------------

        return jsonify({"reply": bot_response})

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "An internal error occurred."}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

