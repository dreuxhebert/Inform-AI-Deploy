# Inform QA Backend

This repository contains the **backend** of the Inform QA built using **FastAPI**.  
It manages call data, performs AI-based transcription and summarization using the **Elevate API**,  
and exposes RESTful endpoints for the frontend to interact with.

The backend is **hosted on Render**, providing automatic deployment, scalability, and reliability.

---

## Tech Stack

- **Framework:** FastAPI  
- **Database:** MongoDB (via PyMongo)  
- **AI Integration:** Elevate AI API  
- **Deployment:** Render  
- **Language:** Python 3.13  

---


## Folder Breakdown

### 1. `main.py`
The entry point of the FastAPI application.

- Initializes the FastAPI app  
- Configures CORS and routing  
- Connects to the database  
- Mounts all API routers from the `Routs` directory  

---

### 2. `Routs/`
This folder contains **route definitions (API endpoints)**.  
Each file represents a logical module (for example, `CallsRouts.py` manages all call-related routes).

**Why it’s used:**  
- Keeps the code modular and easy to maintain.  
- Each route handles specific functionalities such as uploading a call file, fetching call data, or generating summaries.  
- Routes delegate business logic to the controllers for better separation of concerns.

---

### 3. `controllers/`
This folder contains the **core business logic** of the application.

**Why it’s used:**  
- Keeps route handlers lightweight and readable.  
- Handles interaction with external services like the Elevate API.  
- Processes responses and performs validation before returning data to the frontend.

Example tasks performed by controllers:
- Sending the uploaded call file to Elevate AI for transcription.
- Fetching the transcription summary.
- Updating MongoDB with the generated results.

---

### 4. `models.py`
Defines the **data models and schemas** using **Pydantic**.

**Why it’s used:**  
- Ensures consistent structure for data stored in MongoDB.  
- Automatically validates request and response data.  
- Provides clear typing and documentation for each model.  

Example models:
- `Call` – stores details about each recorded call.  
- `Transcript` – stores text transcriptions and AI summaries.  
- `Evaluation` – contains quality metrics or AI evaluation results.  
- `Dispatcher` – stores dispatcher metadata.

---

### 5. `db_connect.py`
Handles the MongoDB connection using **PyMongo**.  
All database operations across controllers and routes rely on this connection.

**Why it’s used:**  
- Keeps the connection logic centralized.  
- Simplifies database management and reusability.

---

## Elevate AI Integration

The backend uses **Elevate AI’s transcription and summarization APIs** to process audio recordings.

**Workflow:**
1. A call recording is uploaded via the `/upload` endpoint.  
2. The controller sends the file to the Elevate AI API.  
3. Elevate AI returns:
   - A **transcription** (complete call text).  
   - A **summary** of the call content.  
4. The backend stores this data in MongoDB under the `transcripts` and `call_summaries` collections.

---

## Deployment on Render

The backend is deployed on [Render](https://render.com), which automatically builds and runs the FastAPI app from the GitHub repository.

**Typical Render setup:**
- **Start command:**  
  ```bash
  uvicorn main:app --host 0.0.0.0 --port 8001

## Environment variable structure
ELEVATEAI_API_TOKEN = Elevate AI api token
ELEVATEAI_BASE_URL = Elevate AI base url (https://api.elevateai.com/v1)
HUGGINGFACE_TOKEN = hugging face api token
MONGODB_URI = mongo db connection url
ORIGINS = allowed origins for resource sharing (CORS) (link1, link2, link3)


