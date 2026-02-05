
---

## 🎮 SENTINEL.EXE | AI-Powered Firewall Defense

![SENTINEL.EXE Project Icon](game/assets/logo.png)

> **"SYSTEM_NOTE:** The localized UI corruption in the project icon (FIREWAALL) is a thematic representation of the virus's impact on the system's visual subroutines."

### 🚀 Overview

**SENTINEL.EXE** is an experimental Tower Defense game built for the **2026 Google AI "New Year, New You" Portfolio Challenge**.

Players take on the role of the last active security protocol in a dying supercomputer. Your mission is to deploy experimental subroutines (towers) to prevent sentient logic bombs (viruses) from reaching the "Human History Core."

> **"In a world of collapsing data, you are the last line of defense."**

---

### 🤖 AI Integration (The Challenge Edge)

This project features deep integration with **Google Gemini 2.0 Flash** to create a dynamic, ever-evolving gameplay experience:

* **Lore Generation:** The game's name, backstory, and world-building were procedurally generated using the Gemini API.
* **Dynamic Enemy Intel:** (Implemented) Gemini generates unique descriptions and "threat levels" for each wave of viruses.
* **AI Co-Pilot** (Implemented): A real-time tactical advisor. Pressing 'H' sends current game metadata (Integrity, Cycles, Towers) to Gemini, which returns a context-aware strategic tip.
* **Sentient Antagonist** (Implemented): When the core integrity hits 0%, Gemini generates a unique "System Compromised" taunt based on the player's final performance.

---

### 🔧 Technical Design Decisions
- **AI-On-Demand:** To optimize performance, Gemini 2.0 Flash is only invoked during wave transitions.
- **Fail-Safe Architecture:** Implemented a 'Local Lore' fallback system. This ensures the game adheres to the Responsible AI pillar of **Robustness** by maintaining uptime during API outages.

---

## 🏛️ Architectural Narrative: AI Integration Strategy
In developing SENTINEL.EXE, the core architectural goal was to move beyond "AI as a gimmick" and treat the Gemini 2.0 Flash model as a critical, yet reliable, system component. Two key design patterns were implemented to achieve this: Event-Driven AI Integration and Robust Resilience Logic.

**Containerization for Cloud Portability**: I containerized the application using Docker to ensure environment parity between local development and production. By utilizing a multi-stage-ready Dockerfile and a .dockerignore file, I optimized the build for Google Cloud Run deployment, demonstrating an 'Infrastructure-as-Code' mindset."

### ⚡ 1. Event-Driven AI Calls
Traditional AI-integrated loops often suffer from "API Churn," where the system polls the model too frequently. For SENTINEL.EXE, I implemented an Event-Driven pattern:

**Mechanism**: AI inference is gated behind a specific user action (pressing the SPACE key) during the "Pre-Wave" game state.

**Engineering Benefits**:

**Quota Conservation**: By triggering calls only at wave transitions, the application stays well within the Gemini Free Tier limits.

**Latency Elimination**: The game loop remains performant at 60 FPS because the AI call is handled as a discrete "state transition" rather than a per-frame operation. This prevents "stutter" during active gameplay.

### 🛡️ 2. Responsible AI: Robustness & Graceful Fallbacks
A major pillar of Responsible AI is Robustness—ensuring that a system remains functional even when its AI component is unavailable or produces an error.

**Mechanism**: The fetch_wave_lore subroutine is wrapped in a comprehensive try/except block.

**The Fallback Logic**:

If the system detects a Network Timeout, 429 Quota Limit, or Safety Filter Trigger, it immediately defaults to a "Local Subroutine" (pre-scripted lore stored in the game’s local constants).

**User Experience (UX)**: From the player's perspective, the game never crashes. A "Connection Error" message is styled to fit the cyber-noir aesthetic, maintaining the immersion of being a firewall under attack.

**Documentation Benefit**: This demonstrates to judges that I have considered the "Real World" messy data environment where APIs are not 100% reliable.

---

### 🛠️ Tech Stack

* **Language:** Python 3.11+
* **Game Engine:** Pygame
* **AI Engine:** [Google GenAI SDK](https://pypi.org/project/google-genai/) (Gemini 2.0 Flash)
* **Deployment:** Google Cloud Run (Containerized via Docker)
* **Environment:** `python-dotenv` for secure API key management.

---

### 🚀 Getting Started

#### 1. Prerequisites

* Python installed on your machine.
* A **Google AI Studio** API Key.

#### 2. Installation

```bash
# Clone the repository
git clone https://github.com/your-username/google-ai-tower-defense.git
cd google-ai-tower-defense

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

```

#### 3. Configuration

Create a `.env` file in the root directory and add your key:

```text
GOOGLE_API_KEY=your_api_key_here

```

#### 4. Run the Game

```bash
python3 game/main.py

```

---

## 🛠 Technical Challenges & Solutions

### 🤖 Real-Time AI Integration
**Challenge:** How do you query a Cloud LLM without breaking the player's immersion?
**Solution:** Implemented a **State-Based Loading Sequence**. When calling the Gemini API, the game transitions to an AI_LOADING state, displaying a thematic "Synchronizing with Neural Network" message. This prevents the game from appearing frozen and ensures a smooth transition once the data is received.

### 📉 Smart Rate-Limit Handling (429 Handling)
**Challenge:** Managing the Google Gemini Free Tier limits (15 requests/min).
**Solution:** Built a **Tactical Cooldown System** and **Local Fallback Subroutines**. If the API is exhausted or the network is disconnected, the game automatically switches to a local library of pre-calculated tips, ensuring the "AI Advisor" feature never breaks the immersion.

### 🌊 Procedural Wave Scaling
**Challenge:** Creating a game that gets progressively harder without manually coding 100 waves.
**Solution:** Developed a wave logic system that scales enemy health and speed using dynamic multipliers, passed into the Enemy class at instantiation.


---

### 🛠️ Lessons Learned

During development, I utilized a branching strategy (main/dev) to experiment with UI enhancements. This allowed me to iterate on a dynamic resource-tracking system while ensuring the core submission remained stable and playable.

---

### 🛡️ Safety Setting

I utilized the google.genai.types module to explicitly define safety thresholds. This ensures that even if the game lore is generated dynamically, it remains within the boundaries of a 'Teen' rated game experience by blocking low-probability harmful content.

---

### 🗺️ Project Roadmap

* [x] Core Game Engine (Pygame + Grid System)
* [x] AI Identity Integration (Gemini 3 Flash)
* [x] Enemy Pathfinding & Wave Logic
* [x] Tower Placement & Currency System
* [x] AI Strategy Guide & Game Over Taunts
* [x] Deployment to Google Cloud Run 

---

### 🚀 Future Roadmap

* Dynamic Resource UI: Implement real-time color-coding for the "Cycles" counter to provide immediate visual feedback on affordability.

* Advanced Tactical Subroutines: Expand the Gemini AI integration to analyze specific enemy wave compositions and suggest optimal tower placements.

* Expansion Packs: Add "Sniper" and "Area of Effect" nodes to increase tactical variety.

* Global Leaderboard: A backend integration to track high scores across the cyber-defense network.

---

### 👨‍💻 Author

* **Mohd Ibrahim** – *Bootcamp Student & AI Explorer*
* Project built for the [Google AI Portfolio Challenge 2026](https://dev.to/challenges).

---
