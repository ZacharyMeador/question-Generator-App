# Question Generator App

A Python desktop application designed to streamline the creation of practice problems for high school Probability and Statistics courses. Built by educator Zachary Meador to support teachers and students with dynamic, printable question generation.

## 🚀 Features

- Generate random questions for key statistical topics (mean, median, and more coming soon)
- Export problems and solutions to LaTeX and generate polished PDFs
- GUI interface for easy use with no coding required
- Toggle visibility of solutions in PDF exports
- Customize headers and generate multiple problems per worksheet (planned)

## 🧱 Project Structure
Question Generator App/
├── generators/ # Logic for generating problems (mean, median, etc.)
│ └── mean_generator.py
│ └── median_generator.py
├── ui/ # PyQt5 interface components
│ └── main_window.py
├── exports/ # LaTeX export engine
│ └── latex_exporter.py
├── main.py # Entry point for the app
├── README.md # Project documentation
├── requirements.txt # Python dependencies

## 📦 Installation

1. Clone this repository:

```bash
git clone https://github.com/ZacharyMeador/question-Generator-App.git
cd question-Generator-App

python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows

pip install -r requirements.txt
python main.py
