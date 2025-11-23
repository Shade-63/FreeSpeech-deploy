# 🛡️ FreeSpeech — AI-Powered Toxicity Detection & Classroom Safety Platform

FreeSpeech is a lightweight, real-time AI moderation system designed for **online classrooms, communities, and group chats**.  
It detects toxic messages instantly, categorizes severity, logs harmful content, and provides each user with a **personal analytics dashboard**.

Built with **Flask**, **HuggingFace (Toxic-BERT)**, and **Plotly**, it’s fast, privacy-friendly, and easy to deploy anywhere.

---

## 🚀 Features

### 🔍 Real-Time Toxicity Detection
- Powered by **unitary/toxic-bert**
- Detects:
  - Toxic
  - Severe Toxic
  - Obscene
  - Threat
  - Insult
  - Identity Hate

### 👤 User Authentication
- Secure **Login / Signup**
- Password hashing
- Individual user message tracking

### 📊 Personal Analytics Dashboard
Includes:
- Total messages  
- Toxic vs Safe distribution  
- Toxic label breakdown  
- Toxicity score timeline  
- Recent toxic message table  

Charts built with **Plotly**.

### 🗄️ Data Logging
Each message stores:
- User ID  
- Message  
- Label  
- Score  
- Severity  
- Timestamp  

(using **SQLite + SQLAlchemy**)

### 🎨 Modern UI
- Clean, responsive design  
- Bootstrap-based  
- Smooth and intuitive chat interface  

---

## 🛠️ Tech Stack

**Frontend:**  
HTML, CSS, Bootstrap, Plotly, JavaScript

**Backend:**  
Python, Flask, Flask-Login, SQLAlchemy

**AI Model:**  
HuggingFace `unitary/toxic-bert` using Transformers pipeline

---
