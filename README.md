# 4D-SynthForge 🎬 → 🧬 → 🎲

**Vibe Coding for Robots. Turn real-world videos into physics-accurate simulations.**

![Architecture](https://img.shields.io/badge/Stack-Gemini%20%7C%20Isaac%20Sim%20%7C%20USD-blue)
![Python](https://img.shields.io/badge/Python-3.10%2B-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🌟 What is 4D-SynthForge?

**4D-SynthForge** is the first **"Vibe Coding" IDE for Physical AI**. 

Instead of writing complex simulation code line-by-line, you simply provide the **"vibe"**—a real-world video of a physics interaction. Our AI analyzes the video's physical essence (mass, friction, velocity) and instantly generates a Digital Twin in **NVIDIA Isaac Sim**.

### The Problem
Building 3D simulations manually is slow, rigid, and hard. You have to guess friction coefficients and write URDF files. It has no flow.

### The Solution: Vibe Coding
You provide the intent (video). The AI provides the implementation (USD/PhysX code).

1. **Analyze 📹** - Gemini extracts physics parameters ("the vibe") from your video.
2. **Recreate 🔧** - Automatically generates USD scenes in Isaac Sim.
3. **Multiply 🎲** - Creates 100+ variations using Domain Randomization.
4. **Train 🤖** - Exports synthetic datasets for AI training.

---

## 💎 Hybrid High-Fidelity Workflow (Pro Mode)

**"But wait, does it just make spheres and cubes?"**

For rapid prototyping? Yes. 
**For professional training? No.**

The true power of 4D-SynthForge is the **Hybrid Workflow**. You can bring your own high-quality assets (Photogrammetry, Gaussian Splats, 3D Models) and letting 4D-SynthForge inject the **real-world physics** from your video into them.

**Real World Physics + Cinema Quality Visuals = The Ultimate Training Data**

1.  **Input**: Record your video (e.g., "Ball hitting cup").
2.  **Analysis**: `python main.py video.mp4` (Gemini extracts real physics).
3.  **Visuals**: Create a stunning, photorealistic scene in Isaac Sim.
4.  **Fusion**: 
    ```bash
    python main.py video.mp4 --base_usd my_photorealistic_scene.usd
    ```
    **Result**: Your cinema-quality scene is now "alive" with the exact physics from the real-world video, plus 100 domain-randomized variations.

---

## 🏗️ Architecture

```
┌─────────────────┐
│  Real-World     │
│  Video Input    │  (The "Vibe")
└────────┬────────┘
         │
         ▼
┌──────────────────────────────────┐
│  Gemini 3.0 Flash                │
│  Physics Extraction Engine       │
│  • Estimates Mass & Friction     │
│  • Captures "Physical Priors"    │
│  → JSON Output                   │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  Code Generator                  │
│  (Gemini 3.0 OR Ollama)          │
│  JSON → USD/PhysX Scripts        │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  NVIDIA Isaac Sim                │
│  Physics Simulation              │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  Domain Randomization            │
│  (Omniverse Replicator)          │
│  → 100+ Variations               │
└────────┬─────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
1.  **Python 3.10+**
2.  **Gemini API Key** ([Google AI Studio](https://aistudio.google.com))
3.  **Nvidia Isaac Sim** (Optional for rendering, required for full pipeline)

### Installation

```bash
git clone https://github.com/mromerocastro/4D-SynthForge.git
cd 4D-SynthForge
pip install -r requirements.txt
```

### Configuration
```bash
export GEMINI_API_KEY="your-key"
```

### Basic Usage

#### 1. Analyze a Video (Get the Physics Vibe)
```bash
python video_analyzer.py examples/ball_cup.mp4
```
**Output**: `output/ball_cup_analysis.json`

#### 2. Generate Variations (Scale the Vibe)
```bash
python domain_randomizer.py output/ball_cup_analysis.json 9
```

#### 3. Run Full Pipeline
```bash
python main.py examples/ball_cup.mp4 --count 100 --render
```


### 🔧 Troubleshooting: USD Generation

If you run `main.py` in a standard Python environment (without Isaac Sim libraries), it cannot directly create the `.usd` file. Instead, it generates a builder script.

**To finish generating the variants:**

```bash
# Run the generated builder script using Isaac Sim's python
~/.local/share/ov/pkg/isaac_sim-*/python.sh output/usd_scenes/build_variants.py
```

This will produce the final `master_scene_variants.usd` with all your physics variations packed inside.

---

## 🧩 Ecosystem Fit

| Component | Tool | Role | 4D-SynthForge's Contribution |
|-----------|------|------|------------------------------|
| **The Brain** 🧠 | **LeRobot** (Hugging Face) | Training Policies | **Data Factory**: Provides the synthetic examples LeRobot needs to learn. |
| **The Eyes** 👀 | **Rerun.io** | Visualization | **Simulation Source**: Generates the 3D visual data to visualize. |
| **The Forge** ⚒️ | **4D-SynthForge** | **Vibe Coding** | **Video → Physics → Data**. |

---

## 📧 Contact
**Built by**: Marlon Romero Castro
