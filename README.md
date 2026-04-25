# 🌐 LogiSense: AI Global Supply Chain Simulator (Web-Based)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3-lightgrey)](https://flask.palletsprojects.com/)
[![JavaScript](https://img.shields.io/badge/JavaScript-ES6-yellow)](https://developer.mozilla.org/)

> **A fully functional web application** that integrates 6 AI algorithms to solve real-world logistics problems – accessible through a browser-based dashboard.

---

## 📖 Project Overview

**LogiSense** is a **web‑based AI simulation platform** for global supply chain management.  
It runs on a **Flask backend** (Python) and a **responsive frontend** (HTML/CSS/JS).  
Users interact with six independent AI modules via a clean dashboard – **no local installation of AI libraries needed** (just a browser).

---

---

## ⚙️ AI Modules (6 Algorithms)

| Module | Algorithm | What the Web UI Does |
|--------|-----------|----------------------|
| Route Optimization | BFS, DFS, A* | Select start/end city & algorithm → shows path & distance |
| Fleet Scheduling | Genetic Algorithm | Click button → displays vehicle routes & total distance |
| Drone Frequency | Graph Coloring | Assigns frequencies to zones, shows conflict‑free assignment |
| Contract Bidding | Minimax + Alpha‑Beta | Enters contract value, budget → recommends best bid |
| Warehouse Management | Backtracking | Places items in zones (avoids hazardous adjacency) |
| Risk Prediction | Bayesian Network | Checks risk factors → shows delay probability & advice |

All results are rendered in the browser with **loading animations and error handling**.

---

## 🏗 System Architecture
Browser (HTML/CSS/JS)
│
│ HTTP POST / GET (JSON)
▼
Flask Server (Python)
│
├── /api/find_route → BFS/DFS/A*
├── /api/schedule_fleet → Genetic Algorithm
├── /api/drone_frequency → Graph Coloring
├── /api/bid_contract → Minimax
├── /api/warehouse_placement → Backtracking
└── /api/predict_risk → Bayesian Network
│
▼
Algorithm Engine (Pure Python)

text

- **Frontend:** Vanilla JS, no frameworks.  
- **Backend:** Flask, CORS enabled.  
- **Communication:** JSON over HTTP.

---

## 💻 Technology Stack

| Layer | Technologies |
|-------|--------------|
| Frontend | HTML5, CSS3 (custom dark theme), ES6 JavaScript |
| Backend  | Python 3, Flask, Flask‑CORS |
| Algorithms | Implemented manually (BFS, DFS, A*, GA, Graph Coloring, Minimax, Backtracking, Bayesian) |
| Graph Library | NetworkX (only for A* shortest path) |

---

## 🛠 How to Run (Local Web Server)

1. **Clone the repository**
   ```bash
   https://github.com/RounakRaju/Logisense
Install dependencies

bash
pip install flask flask-cors networkx
Start the Flask web server

bash
python app.py
Open your browser and go to:

text
http://127.0.0.1:5000
The dashboard will load. You can now interact with all six modules.

📁 Project Structure
text
LogiSense-AI-Supply-Chain/
│
├── app.py               # Flask backend & AI implementations
├── index.html           # Main web page (dashboard)
├── script.js            # Frontend logic (fetch API, UI updates)
├── static/              # CSS, images
│   └── style.css
├── templates/           # (if any additional HTML)
└── README.md            # This file
No node_modules or __pycache__ are included in the repo.

📊 Example Web Interaction
Route Optimization: Select Dhaka → Khulna, choose BFS, click Find Route.
→ The page shows: Path: Dhaka → Rajshahi → Khulna (489 km)

Fleet Scheduling: Click Generate Optimal Schedule.
→ Output: Vehicle 1: Warehouse → Rajshahi → Dhaka → Warehouse (total distance 61 units)

Risk Prediction: Check High Demand + Port Congestion, click Predict Risk.
→ Output: Delay Probability: 55%, Risk Level: Medium.

All responses appear immediately without page refresh.

Rounak Hasan Raju	232002242
Course: CSE 316 – Artificial Intelligence Lab, Spring 2026
Section: 232_D7
Instructor: Md. Sabbir Hosen Mamun
Institution: Green University of Bangladesh
