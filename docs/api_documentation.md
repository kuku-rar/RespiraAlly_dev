
# API Documentation

This document provides a detailed description of the REST API for the RespiraAlly backend (`web-app`). The API is versioned under `/api/v1`.

**Authentication:** Most endpoints are protected and require a `Bearer Token` in the `Authorization` header. The token is obtained via the `/auth/login` or `/auth/line/login` endpoints.

---

## 1. Authentication (`/auth`)

Handles user login for both therapists (staff) and patients (LINE users), and patient registration.

### 1.1. Therapist Login

- **Endpoint:** `POST /api/v1/auth/login`
- **Description:** Authenticates a therapist using their account and password.
- **Request Body:**
  ```json
  {
    "account": "admin",
    "password": "admin"
  }
  ```
- **Success Response (200 OK):**
  ```json
  {
    "data": {
      "token": "ey...",
      "expires_in": 3600,
      "user": {
        "id": 1,
        "account": "admin",
        "first_name": "Admin",
        "last_name": "User",
        "is_staff": true,
        "is_admin": true,
        "title": "System Administrator"
      }
    }
  }
  ```

### 1.2. Patient LINE Login

- **Endpoint:** `POST /api/v1/auth/line/login`
- **Description:** Authenticates a registered patient using their `lineUserId` from the LIFF environment.
- **Request Body:**
  ```json
  {
    "lineUserId": "U123456789abcdef..."
  }
  ```
- **Success Response (200 OK):**
  ```json
  {
    "data": {
      "token": "ey...",
      "expires_in": 604800,
      "user": {
        "id": 2,
        "line_user_id": "U123456789abcdef...",
        "first_name": "Mei-Li",
        "last_name": "Chen",
        "health_profile": { ... }
      }
    }
  }
  ```

### 1.3. Patient LINE Registration

- **Endpoint:** `POST /api/v1/auth/line/register`
- **Description:** Registers a new patient using their `lineUserId` and basic profile information.
- **Request Body:**
  ```json
  {
    "lineUserId": "U_new_user_abcdef...",
    "first_name": "美麗",
    "last_name": "陳",
    "gender": "female",
    "phone": "0987654321",
    "height_cm": 160,
    "weight_kg": 55,
    "smoke_status": "never"
  }
  ```
- **Success Response (201 Created):** Returns a new JWT and user information, similar to the login response.

---

## 2. Patients (`/patients`, `/therapist`)

Endpoints for therapists to manage and view their assigned patients.

### 2.1. Get Assigned Patients

- **Endpoint:** `GET /api/v1/therapist/patients`
- **Description:** Retrieves a paginated list of patients assigned to the currently logged-in therapist. Supports filtering and sorting.
- **Permissions:** `staff`
- **Query Parameters:**
  - `page` (int): Page number.
  - `per_page` (int): Items per page.
  - `risk` (string): Filter by risk level (`high`, `medium`, `low`).
  - `sort_by` (string): Field to sort by (e.g., `created_at`).
  - `order` (string): `asc` or `desc`.
- **Success Response (200 OK):**
  ```json
  {
    "data": [
      {
        "user_id": 2,
        "first_name": "Mei-Li",
        "last_name": "Chen",
        "gender": "female",
        "last_login": "2025-10-30T10:00:00Z",
        "risk_level": "medium",
        "last_cat_score": 22,
        "last_mmrc_score": 3
      }
    ],
    "pagination": { ... }
  }
  ```

### 2.2. Get Patient Profile

- **Endpoint:** `GET /api/v1/patients/{patient_id}/profile`
- **Description:** Retrieves the detailed health profile for a specific patient.
- **Permissions:** `staff` (must be the assigned therapist).
- **Success Response (200 OK):**
  ```json
  {
    "data": {
      "user_id": 2,
      "first_name": "Mei-Li",
      "last_name": "Chen",
      "health_profile": {
        "height_cm": 160,
        "weight_kg": 55,
        "smoke_status": "never"
      }
    }
  }
  ```

### 2.3. Get Patient KPIs

- **Endpoint:** `GET /api/v1/patients/{patient_id}/kpis`
- **Description:** Retrieves key performance indicators for a single patient over a specified period.
- **Permissions:** `staff` (must be the assigned therapist).
- **Query Parameters:**
  - `days` (int): Calculation period in days (default: 7).
- **Success Response (200 OK):**
  ```json
  {
    "data": {
      "risk_level": "medium",
      "latest_cat_score": 22,
      "latest_mmrc_score": 3,
      "medication_adherence": 0.85,
      "avg_exercise_min": 25
    }
  }
  ```

---

## 3. Health Data & Questionnaires

Endpoints for submitting and retrieving patient health data, including daily metrics and standardized questionnaires (CAT, mMRC).

### 3.1. Get Daily Metrics

- **Endpoint:** `GET /api/v1/patients/{patient_id}/daily_metrics`
- **Description:** Retrieves a patient's daily health logs within a date range.
- **Permissions:** `staff` or the patient themselves.
- **Query Parameters:** `start_date`, `end_date`, `page`, `per_page`.
- **Success Response (200 OK):**
  ```json
  {
    "data": [
      {
        "log_id": 1,
        "created_at": "2025-10-30T08:00:00Z",
        "water_cc": 2000,
        "medication": true,
        "exercise_min": 30,
        "cigarettes": 0
      }
    ],
    "pagination": { ... }
  }
  ```

### 3.2. Add Daily Metric

- **Endpoint:** `POST /api/v1/patients/{patient_id}/daily_metrics`
- **Description:** Adds a new daily health log for the patient. A patient can only add a log for themselves.
- **Permissions:** The patient themselves.
- **Request Body:**
  ```json
  {
    "water_cc": 2000,
    "medication": true,
    "exercise_min": 30,
    "cigarettes": 0
  }
  ```
- **Success Response (201 Created):** Returns the newly created log entry.

### 3.3. Get CAT History

- **Endpoint:** `GET /api/v1/patients/{patient_id}/questionnaires/cat`
- **Description:** Retrieves a patient's historical CAT questionnaire scores.
- **Permissions:** `staff` or the patient themselves.
- **Success Response (200 OK):**
  ```json
  {
    "data": [
      {
        "record_id": 1,
        "record_date": "2025-10-01",
        "total_score": 22,
        "scores": { ... }
      }
    ],
    "pagination": { ... }
  }
  ```

### 3.4. Submit CAT Questionnaire

- **Endpoint:** `POST /api/v1/patients/{patient_id}/questionnaires/cat`
- **Description:** Submits a new CAT questionnaire for the patient. Limited to one submission per month.
- **Permissions:** The patient themselves.
- **Request Body:**
  ```json
  {
    "record_date": "2025-10-31",
    "cough_score": 3,
    "phlegm_score": 2,
    "chest_score": 3,
    "breath_score": 4,
    "limit_score": 3,
    "confidence_score": 2,
    "sleep_score": 3,
    "energy_score": 2
  }
  ```
- **Success Response (201 Created):**
  ```json
  {
    "data": {
      "record_id": 2,
      "total_score": 22,
      "message": "CAT questionnaire submitted successfully."
    }
  }
  ```

*(Similar endpoints exist for `mMRC` questionnaires: `GET` and `POST` on `/api/v1/patients/{patient_id}/questionnaires/mmrc`)*

---

## 4. Voice Interaction (`/voice`)

Endpoints for handling voice input and output, integrating the STT -> LLM -> TTS pipeline.

### 4.1. Voice Chat

- **Endpoint:** `POST /api/v1/voice/chat`
- **Description:** A complete voice-in, voice-out chat interaction. The user uploads an audio file, and the system returns a transcribed version of the user's speech, the AI's text response, and a URL to the AI's synthesized audio response.
- **Request (multipart/form-data):**
  - `audio`: The audio file.
  - `patient_id` (string, optional): The patient's ID.
  - `conversation_id` (string, optional): To maintain conversation context.
- **Success Response (200 OK):**
  ```json
  {
    "user_transcription": "Hello, how are you?",
    "ai_response_text": "I am doing well, thank you for asking. How can I help you today?",
    "ai_audio_url": "https://minio.example.com/audio-bucket/...",
    "conversation_id": "...",
    "duration": 4500
  }
  ```

### 4.2. Request Upload URL

- **Endpoint:** `POST /audio/request-url`
- **Description:** Requests a pre-signed URL to upload a large audio file directly to object storage (MinIO). This is useful for bypassing the web server's file size limits.
- **Request Body:**
  ```json
  {
    "filename": "my-long-recording.wav"
  }
  ```
- **Success Response (200 OK):**
  ```json
  {
    "url": "https://minio.example.com/audio-uploads/...?...",
    "object_name": "..."
  }
  ```

---

## 5. Therapist Dashboard (`/overview`)

Endpoints that provide aggregated data for the therapist's dashboard.

### 5.1. Get KPIs

- **Endpoint:** `GET /api/v1/overview/kpis`
- **Description:** Retrieves high-level Key Performance Indicators for the therapist's patient cohort.
- **Permissions:** `staff`
- **Success Response (200 OK):**
  ```json
  {
    "data": {
      "total_patients": 50,
      "high_risk_patients": 5,
      "average_adherence": 0.82,
      "active_today": 35
    }
  }
  ```

### 5.2. Get Trends

- **Endpoint:** `GET /api/v1/overview/trends`
- **Description:** Retrieves time-series data for key metrics (CAT, mMRC, daily logs) for trend analysis.
- **Permissions:** `staff`
- **Query Parameters:** `days` (int, default: 30).
- **Success Response (200 OK):**
  ```json
  {
    "data": {
      "cat_trends": [ { "date": "2025-10-01", "avg_score": 21.5 }, ... ],
      "mmrc_trends": [ { "date": "2025-10-01", "avg_score": 2.8 }, ... ],
      "daily_trends": [ ... ]
    }
  }
  ```

*(Other overview endpoints include `/adherence` and `/usage`.)*

---

## 6. Education (`/education`)

Endpoints for managing and retrieving COPD educational materials.

### 6.1. Get Education Resources

- **Endpoint:** `GET /api/v1/education`
- **Description:** Retrieves a list of educational articles/Q&A.
- **Permissions:** `jwt_required`
- **Query Parameters:** `category`, `q` (search query), `limit`.
- **Success Response (200 OK):**
  ```json
  {
    "data": [
      {
        "id": "1",
        "category": "Disease Knowledge",
        "question": "What is COPD?",
        "answer": "COPD stands for Chronic Obstructive Pulmonary Disease..."
      }
    ],
    "total": 1
  }
  ```

*(This module also includes `POST`, `PUT`, `DELETE` for managing resources and `POST /batch` for bulk import.)*

---

## 7. AI Alerts (`/alerts`)

Endpoints for therapists to view AI-generated alerts about their patients.

### 7.1. Get Alerts

- **Endpoint:** `GET /api/v1/alerts`
- **Description:** Retrieves a list of alerts for the logged-in therapist.
- **Permissions:** `staff`
- **Query Parameters:** `page`, `per_page`, `level`, `category`, `unread_only`.
- **Success Response (200 OK):**
  ```json
  {
    "data": [
        {
            "id": 1,
            "patient_name": "Mei-Li Chen",
            "level": "warning",
            "category": "adherence",
            "message": "Patient has missed medication for 3 consecutive days.",
            "is_read": false,
            "created_at": "2025-10-31T10:30:00Z"
        }
    ],
    "pagination": { ... },
    "summary": { "unread_count": 1 }
  }
  ```

*(This module also includes `PUT /alerts/{id}/read` and `PUT /alerts/batch/read` to mark alerts as read.)*

