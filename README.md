# Hand Sentinel: Computer Vision Engine ✋🤖

<p align="left">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white" />
  <img src="https://img.shields.io/badge/MediaPipe-00C0A8?style=for-the-badge&logo=google&logoColor=white" />
  <img src="https://img.shields.io/badge/Neural_Network-Deep_Learning-FF6F00?style=for-the-badge" />
</p>

**Hand Sentinel** is an advanced Computer Vision and Neural Network engine developed in Python. It utilizes robust Deep Learning models to dynamically map 21 articular nodes on both the **left and right hands** in real-time. By accurately classifying complete physical signs and complex gestures, the neural network acts as an automated trigger to execute and control media (video playback) without physical interfaces.

## ✨ Core Features & Architecture

* **Bilateral Node Tracking:** Precise, real-time spatial mapping of 42 total articular nodes (21 per hand) utilizing advanced neural network architectures.
* **Gesture-Triggered Automation:** Translates specific, complete physical signs into executable binary commands to instantly trigger and manage video playback.
* **Low Latency Processing:** Highly optimized for real-time execution and zero-lag rendering via OpenCV frame processing.
* **Modular Engineering:** Clean, scalable architecture strictly separated into `core` (AI engine), `ui` (interface), and `assets` (media and data) for seamless future integrations.

## 🗂️ Project Structure

The engine is built with a highly modular approach to ensure clean code and scalability:

```text
hand-sentinel/
├── assets/       # Media files and output data
├── config/       # Global configurations and parameters
├── core/         # AI engine, node tracking, and neural network logic
├── ui/           # User interface components and visual OpenCV overlays
├── utils/        # Helper functions and isolated auxiliary scripts
├── main.py       # Main execution script
└── requirements.txt

🛠 Technologies Used
- Core Language: Python 3.x
- Computer Vision: OpenCV, MediaPipe (Hand Tracking Solutions)
- Machine Learning / AI: Integrated Neural Network logic for gesture classification
- Architecture: Modular component isolation and real-time data streaming.

🚀 Installation & Setup
To deploy the Hand Sentinel engine locally on a Windows environment:

1. Clone the repository:
```bash
git clone git clone https://github.com/jp-software-dev/hand-sentinel.git

2. Navigate into the project directory:
cd hand-sentinel

3. Install the required dependencies:
pip install -r requirements.txt

4. Run the main engine:
python main.py

🎮 Usage: The "Scuba" Trigger
Once the engine is running and your webcam is active, Hand Sentinel will map your hand nodes in real-time.

To trigger the automated media response (Scuba Cat meme):

- Bring both hands into the camera frame.
- Place your hands over your mouth and raise one in the air, simulating a scuba mask.
- The neural network will instantly classify this physical sign and execute the video playback command without needing to touch the keyboard or mouse.
