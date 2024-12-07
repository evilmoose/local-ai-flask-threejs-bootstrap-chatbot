
# Local Flask + Three.js + Bootstrap AI Chat Application

This project is a Local Flask-based web application that combines Bootstrap for styling and Three.js for 3D rendering. It provides a basic chat interface with the potential to integrate AI chatbot features and 3D visualizations.

![image](https://github.com/user-attachments/assets/a4caee3d-fe83-4f5a-a0e2-8ae9b68b5116)

---

## **Features**
- Flask backend for serving API and web content.
- Bootstrap-based UI for responsive and professional design.
- Three.js integration for future 3D content rendering.
- Dynamic chat functionality with `llama3.2` via Ollama.

---

## **Getting Started**

Follow these steps to set up the project locally:

---

### **Prerequisites**
- Python 3.8 or higher installed
- Virtual environment tool (`venv`) or `pipenv`
- Git installed on your system
- [Ollama](https://github.com/ollama/ollama) installed and set up on your machine
- `llama3.2` model downloaded via Ollama

---

### **1. Clone the Repository**
Use the following command to clone the project repository:

```bash
git clone <repository-url>
```

Replace `<repository-url>` with the actual GitHub repository URL.

---

### **2. Navigate to the Project Directory**
Change into the project folder:

```bash
cd flask_threejs_project
```

---

### **3. Set Up a Virtual Environment**
Create and activate a Python virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

---

### **4. Install Python Dependencies**
Install all required Python packages using `pip`:

```bash
pip install -r requirements.txt
```

---

### **5. Install and Configure Ollama**
1. Follow the [official Ollama installation guide](https://github.com/ollama/ollama) to set up Ollama on your machine.
2. Download the `llama3.2` model by running:
   ```bash
   ollama install llama3.2
   ```
   Ensure that Ollama is running and properly configured on your system.

---

### **6. Run the Application**
Start the Flask development server:

```bash
python run.py
```

By default, the server runs on `http://127.0.0.1:5000`.

---

### **7. Open the Application in a Browser**
Visit the following URL in your web browser:

```
http://127.0.0.1:5000
```

You should see the chat application with a Bootstrap-styled UI and a placeholder for Three.js content.

---

## **Project Structure**
```
flask_threejs_project/
├── app/
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css         # Bootstrap-based CSS file
│   │   ├── js/
│   │   │   └── app.js            # Frontend logic for chat
│   ├── templates/
│   │   └── index.html            # Main HTML template
│   ├── __init__.py               # App initialization
│   ├── app.py                    # Flask routes
├── run.py                        # Entry point to run the app
├── requirements.txt              # Python dependencies
└── README.md                     # Project documentation
```

---

## **Customization**
- **Styling**: Update the `styles.css` file in `app/static/css/` to customize the appearance.
- **Three.js Integration**: Add Three.js logic in `app/static/js/app.js` for rendering 3D objects.
- **Chatbot Backend**: Replace the dummy chatbot logic in `app.py` with your AI model or external API.

---

## **Contributing**
Feel free to fork this repository and submit pull requests with improvements or new features. Contributions are welcome!

---

## **License**
This project is licensed under the MIT License. See the `LICENSE` file for details.
