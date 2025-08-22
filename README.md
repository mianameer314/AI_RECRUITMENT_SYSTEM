
# AI Recruitment System - Comprehensive Documentation

## 1. Project Overview

The AI Recruitment System is a cutting-edge platform designed to revolutionize the hiring process through advanced artificial intelligence, automation, and seamless integration with essential communication tools. This enhanced version provides an end-to-end solution for modern organizations, streamlining everything from intelligent resume analysis to automated interview scheduling and comprehensive dashboard analytics. It aims to significantly reduce recruitment time and effort while improving the quality of hires.

## 2. Key Features

This system offers a robust set of features to support a complete recruitment workflow:

### 2.1. AI-Powered Resume Analysis

Leveraging state-of-the-art Large Language Models (LLMs), the system provides in-depth analysis of candidate resumes. This feature automates the traditionally time-consuming process of resume screening and evaluation.

*   **Google Gemini Integration**: Utilizes Google Gemini for advanced natural language processing, enabling comprehensive evaluation of resume content, including skills, experience, and education.
*   **Multi-Provider Support**: Designed for flexibility, the system supports integration with various LLM providers, including Google Gemini, OpenAI, and a mock service for development and testing purposes. This allows organizations to choose their preferred AI backend.
*   **Intelligent Scoring**: Automatically generates scores across multiple dimensions, providing a quantitative assessment of a candidate's suitability based on predefined criteria such as technical skills, soft skills, years of experience, and educational background.
*   **Job Matching**: Intelligently matches candidate profiles with specific job requirements by analyzing the job description against the resume content, providing a compatibility score and detailed fit assessment.
*   **Asynchronous Processing**: Resume analysis is performed asynchronously using Celery workers, ensuring that the main application remains responsive and scalable, even when processing a large volume of resumes.

### 2.2. Automated Email Notifications

The system automates various communication aspects of the recruitment process, ensuring timely and professional interactions with candidates and recruiters.

*   **Professional Templates**: Comes with a suite of pre-designed HTML email templates for common recruitment scenarios, such as analysis completion notifications, interview invitations, and application status updates.
*   **SMTP Integration**: Supports standard SMTP protocols, allowing integration with popular email services like Gmail, SendGrid, and other custom SMTP providers, offering flexibility in email delivery.
*   **Automated Workflows**: Emails are triggered automatically based on system events (e.g., resume analysis completion) and user actions (e.g., scheduling an interview), reducing manual communication overhead.
*   **Template Management**: Email templates are customizable, allowing organizations to tailor content and branding to their specific needs, with support for dynamic content insertion.
*   **Asynchronous Delivery**: Email sending is handled by Celery workers in the background, preventing delays in the main application and ensuring reliable delivery of notifications.

### 2.3. Zoom Integration

Seamlessly integrates with Zoom to facilitate video interviews, providing a streamlined experience for scheduling and managing virtual meetings.

*   **Meeting Management**: Enables programmatic creation, updating, and cancellation of Zoom meetings directly from the recruitment platform.
*   **Server-to-Server OAuth**: Utilizes Zoom's secure Server-to-Server OAuth 2.0 implementation for robust and secure authentication, ensuring data privacy and integrity.
*   **Interview Scheduling**: Automates the scheduling of video interviews, including generating Zoom meeting links and integrating with calendar services (e.g., Google Calendar) to send invitations to all participants.
*   **Meeting Settings**: Allows configuration of various Zoom meeting settings, such as waiting rooms, recording options, and security features, to ensure a controlled and professional interview environment.
*   **Webhook Support**: Supports real-time updates on meeting status and participant management, providing recruiters with up-to-date information on their scheduled interviews.

### 2.4. Dashboard Analytics

Provides comprehensive insights into the recruitment pipeline through various analytical dashboards, accessible to administrators.

*   **Overview Statistics**: Offers a high-level summary of key recruitment metrics, such as total jobs posted, total applications received, and overall system activity.
*   **Jobs per Location**: Visualizes the distribution of job postings across different geographical locations, helping identify talent hotspots and recruitment needs.
*   **Applications per Job**: Tracks the number of applications received for each job posting, allowing recruiters to identify popular roles and manage application volumes effectively.
*   **Daily Applications**: Displays trends in daily application submissions, providing insights into peak application times and overall recruitment activity over time.
*   **Most Applied Jobs**: Highlights the job postings that have received the most applications, indicating high-demand roles or successful outreach efforts.
*   **Most Active Candidates**: Identifies candidates who are most actively engaging with the platform, potentially indicating high interest or suitability.
*   **Application Status Breakdown**: Provides a breakdown of applications by their current status (e.g., pending, reviewed, interviewed, hired), offering a clear view of the recruitment funnel.
*   **Recent Activity**: Shows a log of recent system activities, including new job postings, resume uploads, and application submissions, keeping administrators informed of ongoing operations.

## 3. Architecture Overview

The enhanced AI Recruitment System is built with a microservices-inspired architecture, promoting modularity, scalability, and maintainability. The core components interact asynchronously to ensure high performance and resilience.

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │   Celery Worker │    │   Redis Queue   │
│                 │    │                 │    │                 │
│ • REST APIs     │◄──►│ • Resume Analysis│◄──►│ • Task Queue    │
│ • Authentication│    │ • Email Sending │    │ • Result Storage│
│ • File Upload   │    │ • Zoom Meetings │    │ • Session Cache │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MongoDB       │    │   File Storage  │    │   External APIs │
│                 │    │                 │    │                 │
│ • User Data     │    │ • Resume PDFs   │    │ • Google Gemini │
│ • Job Postings  │    │ • JSON Results  │    │ • Zoom API      │
│ • Applications  │    │ • Email Templates│    │ • SMTP Servers
 │                                              . OpenAI
                                                 . Google Calender
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 3.1. FastAPI Application

This is the primary interface of the system, handling all incoming API requests. It is built using FastAPI, a modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints.

*   **REST APIs**: Exposes a comprehensive set of RESTful endpoints for managing users, jobs, resumes, applications, notifications, and interviews.
*   **Authentication**: Implements JWT token-based authentication for secure access to API endpoints, ensuring that only authorized users can perform specific actions.
*   **File Upload**: Manages the secure upload of resume files (PDFs) and other related documents.

### 3.2. Celery Worker

Celery is an asynchronous task queue/job queue based on distributed message passing. It is used to offload long-running or resource-intensive tasks from the main FastAPI application, improving responsiveness and scalability.

*   **Resume Analysis**: Executes the AI-powered resume analysis tasks in the background, preventing the API from blocking while LLM processing occurs.
*   **Email Sending**: Handles the asynchronous delivery of all automated email notifications, ensuring that email sending does not impact the user experience.
*   **Zoom Meetings**: Manages the creation, updating, and cancellation of Zoom meetings, integrating with the Zoom API in a non-blocking manner.

### 3.3. Redis Queue

Redis serves as the message broker for Celery, facilitating communication between the FastAPI application and the Celery workers. It also acts as a cache and storage for task results.

*   **Task Queue**: Stores tasks submitted by the FastAPI application, which are then picked up and processed by Celery workers.
*   **Result Storage**: Stores the results of completed Celery tasks, allowing the FastAPI application to retrieve analysis results or meeting details asynchronously.
*   **Session Cache**: Can be used for caching session data or other temporary information to improve application performance.

### 3.4. MongoDB

MongoDB is a NoSQL document database used for persistent storage of application data. Its flexible schema is well-suited for the diverse data types in a recruitment system.

*   **User Data**: Stores user profiles, including candidate and administrator information, authentication credentials (hashed), and roles.
*   **Job Postings**: Persists details of all job vacancies, including titles, descriptions, required skills, salary information, company details, and location.
*   **Applications**: Records all job applications, linking candidates to specific job postings and storing application-related metadata.

### 3.5. File Storage

Dedicated storage for various files generated or uploaded within the system.

*   **Resume PDFs**: Stores the original PDF files uploaded by candidates.
*   **JSON Results**: Stores the structured JSON output of resume analyses and other processed data.
*   **Email Templates**: Houses the HTML templates used for automated email notifications.

### 3.6. External APIs

The system integrates with several external services to provide its core functionalities.

*   **Google Gemini**: The primary LLM service used for advanced resume analysis and intelligent matching.
*   **Zoom API**: Provides programmatic access to Zoom's meeting functionalities for scheduling and managing video interviews.
*   **SMTP Servers**: External email servers (e.g., Gmail, SendGrid) used for sending automated notifications.
*   **Google Calendar API**: Used for creating and managing calendar events for scheduled interviews.

## 4. Installation and Setup

To get the AI Recruitment System up and running, follow these steps:

### 4.1. Prerequisites

Ensure you have the following installed on your system:

*   **Python 3.11+**: The core programming language for the application.
*   **Redis Server**: Required for Celery as a message broker and result backend.
*   **MongoDB**: A NoSQL database for storing application data. While optional for basic setup, it's essential for full functionality.
*   **SMTP Email Account**: An email account (e.g., Gmail, SendGrid) configured for sending emails. You will need its SMTP details.
*   **Zoom Developer Account**: Necessary for integrating with Zoom's API for video interview functionalities.
*   **Google Cloud Project (Optional)**: Required for Google Gemini API key and Google Calendar API if you plan to use these features.

### 4.2. Environment Configuration

Create a `.env` file in the root directory of the project (`AI_REC_SYSTEM/AI_REC_SYSTEM/.env`) and populate it with the following configuration variables. Replace placeholder values with your actual credentials and settings.

```bash
# Database Configuration
MONGO_URI=mongodb://localhost:27017
MONGO_DB=ai_recruitment

# Security
SECRET_KEY=your-super-secret-key-here-make-it-long-and-random
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# AI Services
GOOGLE_API_KEY=your-google-gemini-api-key
OPENAI_API_KEY=your-openai-api-key

# Email Configuration
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=your-email@gmail.com
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_FROM_NAME=AI Recruitment System
MAIL_STARTTLS=True
MAIL_SSL_TLS=False

# Zoom Configuration (Server-to-Server OAuth - Recommended)
ZOOM_ACCOUNT_ID=your-zoom-account-id
ZOOM_CLIENT_ID=your-zoom-client-id
ZOOM_CLIENT_SECRET=your-zoom-client-secret

# Alternative: Zoom JWT (Deprecated - Use Server-to-Server OAuth instead)
# ZOOM_API_KEY=your-zoom-api-key
# ZOOM_API_SECRET=your-zoom-api-secret

# Google Calendar Configuration (Optional)
GOOGLE_CALENDAR_ID=your-google-calendar-id # e.g., primary or a specific calendar ID
GOOGLE_SERVICE_ACCOUNT_INFO='''{"type": "service_account", ...}''' # JSON content of your service account key file
```

**Important Notes on Environment Variables:**

*   **`SECRET_KEY`**: Generate a strong, random string for this. It's crucial for the security of your JWT tokens.
*   **`MAIL_PASSWORD`**: If using Gmail, you'll need to generate an App Password, especially if you have 2-Factor Authentication enabled. Regular Gmail passwords will not work for SMTP.
*   **`GOOGLE_SERVICE_ACCOUNT_INFO`**: This should be the entire JSON content of your Google service account key file, escaped appropriately for a single-line environment variable. For Docker, it's often better to mount the file directly.

### 4.3. Installation Steps

Follow these steps to install and run the application locally:

1.  **Navigate to Project Directory**
    ```bash
    cd AI_REC_SYSTEM/AI_REC_SYSTEM
    ```

2.  **Install Python Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Start Redis Server**
    If you have Redis installed locally, start it. For most Linux distributions, you can use:
    ```bash
    redis-server --daemonize yes
    ```
    Verify it's running: `redis-cli ping` (should return `PONG`)

4.  **Start MongoDB (if not already running)**
    Ensure your MongoDB instance is running. If you're using Docker, you can start it via `docker-compose up -d mongo` (see Docker section).

5.  **Start Celery Worker**
    This will run the background tasks for resume analysis, email sending, and Zoom integrations.
    ```bash
    celery -A app.workers.celery_worker worker --loglevel=info --detach
    ```
    To view logs, remove `--detach` or check Celery's log file.

6.  **Start FastAPI Application**
    This will launch the main web API.
    ```bash
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ```
    The `--reload` flag is useful for development as it automatically restarts the server on code changes. For production, remove this flag.

    The API will be accessible at `http://localhost:8000`.
    The interactive API documentation (Swagger UI) will be available at `http://localhost:8000/docs`.

## 5. API Documentation

The AI Recruitment System provides a comprehensive set of RESTful APIs for interacting with its various functionalities. The API is self-documenting using FastAPI's built-in Swagger UI, accessible at `/docs` endpoint when the application is running.

### 5.1. Authentication Endpoints

*   **`POST /api/v1/auth/register`**: Register a new user (candidate or admin).
    *   **Request Body**: `UserCreate` schema (username, email, password, role).
    *   **Response**: Success message upon registration.
*   **`POST /api/v1/auth/login`**: Authenticate a user and receive a JWT access token.
    *   **Request Body**: `UserLogin` schema (username, password).
    *   **Response**: `access_token` and `token_type`.

### 5.2. Job Management Endpoints

*   **`POST /api/v1/jobs/`**: Post a new job listing (admin only).
    *   **Request Body**: `JobCreate` schema (title, description, skills, salary, company, location, tags).
    *   **Response**: Details of the created job.
*   **`GET /api/v1/jobs/`**: List available job postings.
    *   **Query Parameters**: `keyword` (search by title/description), `location` (filter by location), `limit`, `skip`.
    *   **Response**: List of `PublicJobOut` schemas.
*   **`POST /api/v1/jobs/apply`**: Apply to a job with a processed resume (candidate only).
    *   **Request Body**: `JobApplication` schema (job_id, resume_id).
    *   **Response**: Success message for application.
*   **`GET /api/v1/jobs/{job_id}/applications`**: Get all applicants for a specific job (admin only).
    *   **Response**: List of applications for the job.
*   **`PUT /api/v1/jobs/{job_id}`**: Update an existing job listing (admin only).
    *   **Request Body**: `JobUpdate` schema.
    *   **Response**: Updated job details.
*   **`DELETE /api/v1/jobs/{job_id}`**: Delete a job listing (admin only).
    *   **Response**: Success message for deletion.
*   **`POST /api/v1/jobs/seed`**: Seed sample jobs into the database (admin only).
    *   **Response**: Confirmation of seeded jobs.

### 5.3. Resume Processing Endpoints

*   **`POST /api/v1/resumes/upload`**: Upload a resume file (PDF only).
    *   **Request Body**: `file` (UploadFile).
    *   **Response**: `file_name` and `resume_id`.
*   **`POST /api/v1/resumes/analyze/{resume_id}`**: Trigger AI analysis for a specific resume (admin only).
    *   **Path Parameter**: `resume_id`.
    *   **Request Body**: `AnalysisRequest` schema (optional `job_description`, `provider` - `gemini`, `openai`, `mock`).
    *   **Response**: `task_id` for asynchronous analysis tracking.
*   **`GET /api/v1/resumes/analysis/{resume_id}`**: Retrieve the AI analysis results for a resume (admin only).
    *   **Path Parameter**: `resume_id`.
    *   **Response**: Detailed analysis data.
*   **`GET /api/v1/resumes/list`**: List all uploaded resumes.
    *   **Response**: List of resume metadata (parsed, analyzed status).

### 5.4. Notification Endpoints

*   **`POST /api/v1/notifications/send-email`**: Send a custom email using a template.
    *   **Request Body**: `EmailRequest` schema (recipients, subject, template_name, template_data).
    *   **Response**: `task_id` for email sending.
*   **`POST /api/v1/notifications/test-email`**: Send a test email to verify configuration.
    *   **Request Body**: `TestEmailRequest` schema (recipient, subject).
    *   **Response**: `task_id` for test email.
*   **`POST /api/v1/notifications/analysis-notification`**: Send a notification about completed resume analysis.
    *   **Request Body**: `AnalysisNotificationRequest` schema.
    *   **Response**: `task_id` for notification.
*   **`POST /api/v1/notifications/interview-invitation`**: Send an interview invitation email.
    *   **Request Body**: `InterviewInvitationRequest` schema.
    *   **Response**: `task_id` for invitation.
*   **`POST /api/v1/notifications/status-update`**: Send an application status update email.
    *   **Request Body**: `StatusUpdateRequest` schema.
    *   **Response**: `task_id` for status update.
*   **`GET /api/v1/notifications/templates`**: List available email templates.
    *   **Response**: List of template filenames.
*   **`GET /api/v1/notifications/config`**: Get email configuration status (non-sensitive).
    *   **Response**: Configuration details.

### 5.5. Interview and Zoom Integration Endpoints

*   **`POST /api/v1/interviews/schedule`**: Schedule an interview, including Zoom meeting creation and calendar event.
    *   **Request Body**: `InterviewScheduleRequest` schema (candidate_name, candidate_email, interviewer_name, job_title, start_time, duration, timezone, send_email, calendar_id).
    *   **Response**: Meeting details, calendar link, and email task ID.
*   **`PATCH /api/v1/interviews/meetings/{meeting_id}`**: Update an existing Zoom meeting.
    *   **Path Parameter**: `meeting_id`.
    *   **Request Body**: `MeetingUpdateRequest` schema (topic, start_time, duration, settings).
    *   **Response**: `task_id` for update.
*   **`DELETE /api/v1/interviews/meetings/{meeting_id}`**: Cancel/delete a Zoom meeting.
    *   **Path Parameter**: `meeting_id`.
    *   **Response**: `task_id` for cancellation.
*   **`GET /api/v1/interviews/meetings`**: List all scheduled Zoom meetings.
    *   **Response**: List of meeting details.
*   **`GET /api/v1/interviews/config`**: Get Zoom configuration status (non-sensitive).
    *   **Response**: Configuration details.
*   **`POST /api/v1/interviews/test-meeting`**: Create a test Zoom meeting to verify integration.
    *   **Response**: Details of the created test meeting.
*   **`GET /api/v1/interviews/stored-meetings`**: List all stored meeting details from local files.
    *   **Response**: List of stored meeting data.

### 5.6. Dashboard Analytics Endpoints (Admin Only)

*   **`GET /api/v1/dashboard/stats/overview`**: Get overall recruitment statistics.
*   **`GET /api/v1/dashboard/stats/jobs-per-location`**: Get job distribution by location.
*   **`GET /api/v1/dashboard/stats/applications-per-job`**: Get application count per job.
*   **`GET /api/v1/dashboard/stats/daily-applications`**: Get daily application trends.
*   **`GET /api/v1/dashboard/stats/most-applied-jobs`**: Get a list of most applied jobs.
*   **`GET /api/v1/dashboard/stats/most-active-candidates`**: Get a list of most active candidates.
*   **`GET /api/v1/dashboard/stats/application-status-breakdown`**: Get breakdown of application statuses.
*   **`GET /api/v1/dashboard/stats/recent-activity`**: Get recent system activities.

## 6. Configuration Guide

This section provides detailed instructions on how to configure the various external services required by the AI Recruitment System.

### 6.1. AI Service Configuration

#### 6.1.1. Google Gemini Setup

1.  Visit [Google AI Studio](https://makersuite.google.com/app/apikey).
2.  Create a new API key for your project.
3.  Add the generated API key to your `.env` file as `GOOGLE_API_KEY`.

#### 6.1.2. OpenAI Setup

1.  Visit [OpenAI API Keys](https://platform.openai.com/api-keys).
2.  Create a new secret API key.
3.  Add the generated API key to your `.env` file as `OPENAI_API_KEY`.

### 6.2. Email Configuration

#### 6.2.1. Gmail SMTP Setup

To use Gmail for sending emails, you need to generate an App Password, especially if you have 2-Factor Authentication (2FA) enabled on your Google account.

1.  **Enable 2-Factor Authentication**: If not already enabled, go to your Google Account settings -> Security -> 2-Step Verification and follow the steps.
2.  **Generate an App Password**:
    *   Go to your Google Account settings.
    *   Navigate to `Security` -> `2-Step Verification` -> `App passwords`.
    *   Select `Mail` for the app and `Other (Custom name)` for the device. Give it a name like 


"AI Recruitment System" and click `Generate`.
    *   Copy the generated 16-character password.
3.  Use this generated app password in your `.env` file for `MAIL_PASSWORD`.

#### 6.2.2. SendGrid Setup

1.  Create a SendGrid account and verify your sender identity.
2.  Generate an API key with Mail Send permissions.
3.  Configure your `.env` file with the following SMTP settings:
    ```bash
    MAIL_SERVER=smtp.sendgrid.net
    MAIL_PORT=587
    MAIL_USERNAME=apikey
    MAIL_PASSWORD=your-sendgrid-api-key
    ```

### 6.3. Zoom Integration Setup

#### 6.3.1. Server-to-Server OAuth (Recommended)

This is the most secure and recommended method for Zoom integration.

1.  Visit the [Zoom App Marketplace](https://marketplace.zoom.us/).
2.  Log in and navigate to `Develop` -> `Build App`.
3.  Choose `Server-to-Server OAuth` as the app type and click `Create`.
4.  Provide a name for your app and click `Create`.
5.  On the `App Credentials` page, you will find your `Account ID`, `Client ID`, and `Client Secret`.
6.  Add these credentials to your `.env` file:
    ```bash
    ZOOM_ACCOUNT_ID=your-zoom-account-id
    ZOOM_CLIENT_ID=your-zoom-client-id
    ZOOM_CLIENT_SECRET=your-zoom-client-secret
    ```
7.  On the `Information` page, fill in the basic information and add the necessary `Scopes` for your app (e.g., `meeting:write`, `meeting:read`, `user:read`).
8.  Enable your app by clicking `Activate your app`.

#### 6.3.2. JWT App (Deprecated)

While still functional, JWT apps are deprecated by Zoom. Server-to-Server OAuth is preferred.

1.  Create a JWT app in the [Zoom App Marketplace](https://marketplace.zoom.us/).
2.  Obtain your `API Key` and `API Secret`.
3.  Add them to your `.env` file:
    ```bash
    ZOOM_API_KEY=your-zoom-api-key
    ZOOM_API_SECRET=your-zoom-api-secret
    ```

### 6.4. Google Calendar Integration Setup

To enable automated Google Calendar event creation for interviews, you need to set up a Google Service Account.

1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Select or create a new project.
3.  Enable the `Google Calendar API` for your project.
4.  Create a Service Account:
    *   Navigate to `IAM & Admin` -> `Service Accounts`.
    *   Click `+ CREATE SERVICE ACCOUNT`.
    *   Follow the steps to create the account.
5.  Generate a new JSON key for the service account:
    *   Click on the newly created service account.
    *   Go to the `Keys` tab.
    *   Click `ADD KEY` -> `Create new key` -> `JSON` -> `Create`.
    *   A JSON file will be downloaded. This file contains your service account credentials.
6.  Share your Google Calendar with the Service Account:
    *   Go to [Google Calendar](https://calendar.google.com/).
    *   Find the calendar you want to use for scheduling (e.g., your primary calendar or a dedicated 


calendar). 
    *   Click the three dots next to the calendar name -> `Settings and sharing`.
    *   Scroll down to `Share with specific people` and click `Add people`.
    *   Paste the service account email address (from the JSON key file, it ends with `@<project-id>.iam.gserviceaccount.com`).
    *   Set `Permissions` to `Make changes to events` or `Make changes and manage sharing`.
    *   Click `Send`.
7.  Copy the entire content of the downloaded JSON key file and paste it as the value for `GOOGLE_SERVICE_ACCOUNT_INFO` in your `.env` file. Ensure it's a single line and properly escaped if necessary.
8.  Optionally, set `GOOGLE_CALENDAR_ID` in your `.env` file to the ID of the calendar you shared (e.g., `primary` for your main calendar).

## 7. Deployment Guide

This section outlines various methods for deploying the AI Recruitment System to different environments.

### 7.1. Production Deployment with Docker

Docker provides a consistent and isolated environment for deploying the application.

#### 7.1.1. Using Dockerfile

Create a `Dockerfile` in the root of your project:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

To build and run the Docker image:

```bash
# Build the Docker image
docker build -t ai-recruitment-system .

# Run the Docker container
docker run -p 8000:8000 --env-file .env ai-recruitment-system
```

#### 7.1.2. Using Docker Compose

Docker Compose allows you to define and run multi-container Docker applications. This project includes a `docker-compose.yml` file to orchestrate the FastAPI app, Celery worker, Redis, and MongoDB.

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379/0
      - MONGO_URI=mongodb://mongo:27017
    depends_on:
      - redis
      - mongo
      - celery
    # Mount .env file for environment variables (recommended for development)
    env_file:
      - .env

  celery:
    build: .
    command: celery -A app.workers.celery_worker worker --loglevel=info
    environment:
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
    env_file:
      - .env

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"

  mongo:
    image: mongo:latest
    ports:
      - "27017:27017"
    # Optional: Persist MongoDB data
    volumes:
      - mongo_data:/data/db

volumes:
  mongo_data:
```

To start the entire stack:

```bash
# Build and start all services in detached mode
docker-compose up --build -d

# Stop all services
docker-compose down
```

### 7.2. Cloud Deployment

#### 7.2.1. AWS Deployment

Deploying to AWS involves setting up EC2 instances, managed database services, and load balancing.

1.  **EC2 Instance Setup**:
    *   Launch an Ubuntu 22.04 EC2 instance.
    *   Install Docker and Docker Compose on the instance.
    *   Configure security groups to allow inbound traffic on ports 8000 (for FastAPI), 6379 (for Redis), and 27017 (for MongoDB, if self-hosted).
2.  **RDS for MongoDB (or MongoDB Atlas)**:
    *   For a production-grade MongoDB, consider using MongoDB Atlas (a fully managed cloud database) or AWS DocumentDB (MongoDB-compatible service).
    *   Update the `MONGO_URI` in your environment variables to point to your managed database instance.
3.  **ElastiCache for Redis**:
    *   Create a Redis cluster using AWS ElastiCache.
    *   Update the `REDIS_URL` in your environment variables to point to your ElastiCache endpoint.
4.  **Load Balancer (Application Load Balancer - ALB)**:
    *   Configure an Application Load Balancer to distribute traffic to your FastAPI instances.
    *   Set up SSL certificates (e.g., using AWS Certificate Manager) for HTTPS.
    *   Configure health checks to ensure only healthy instances receive traffic.

#### 7.2.2. Heroku Deployment

Heroku provides a platform-as-a-service (PaaS) that simplifies deployment.

1.  **Install Heroku CLI**:
    If you haven't already, install the Heroku Command Line Interface.
2.  **Create Heroku App**:
    ```bash
    heroku create ai-recruitment-system
    ```
3.  **Add Add-ons (Redis and MongoDB)**:
    ```bash
    heroku addons:create heroku-redis:hobby-dev
    heroku addons:create mongolab:sandbox # Or another MongoDB add-on
    ```
4.  **Set Environment Variables**:
    Configure all necessary environment variables (e.g., `GOOGLE_API_KEY`, `MAIL_USERNAME`, `ZOOM_CLIENT_ID`, etc.) using Heroku config vars.
    ```bash
    heroku config:set GOOGLE_API_KEY=your-key
    heroku config:set MAIL_USERNAME=your-email
    # ... set other environment variables as per your .env file
    ```
5.  **Deploy**:
    ```bash
    git push heroku main
    ```

## 8. Testing Guide

This section covers how to test the AI Recruitment System.

### 8.1. Unit Testing

The project includes unit tests written with `pytest` to ensure individual components function correctly.

*   **Run all tests**:
    ```bash
    pytest
    ```
*   **Run specific test file**:
    ```bash
    pytest tests/test_llm_service.py
    ```
*   **Run with coverage (requires `pytest-cov`)**:
    ```bash
    pytest --cov=app tests/
    ```

### 8.2. API Testing

You can use `curl` or tools like Postman/Insomnia to test the API endpoints.

*   **Test resume analysis (using mock provider for quick testing)**:
    ```bash
    curl -X POST "http://localhost:8000/api/v1/resumes/analyze/resume_id" \
      -H "Content-Type: application/json" \
      -d '{"provider": "mock"}'
    ```
*   **Test email configuration**:
    ```bash
    curl "http://localhost:8000/api/v1/notifications/config"
    ```
*   **Test Zoom integration (creates a test meeting)**:
    ```bash
    curl -X POST "http://localhost:8000/api/v1/interviews/test-meeting"
    ```

### 8.3. Load Testing

Load testing helps assess the system's performance under heavy traffic. `Locust` is a popular tool for this.

1.  **Install Locust**:
    ```bash
    pip install locust
    ```
2.  **Create `locustfile.py`** (example):
    ```python
    from locust import HttpUser, task, between

    class RecruitmentUser(HttpUser):
        wait_time = between(1, 2) # Simulate user waiting between tasks

        @task
        def test_resume_list(self):
            self.client.get("/api/v1/resumes/list")
        
        @task
        def test_analysis(self):
            # Replace 'test_resume' with an actual resume_id for real testing
            self.client.post("/api/v1/resumes/analyze/test_resume", 
                            json={"job_description": "Software Engineer", "provider": "mock"})

        @task
        def test_login(self):
            # Assuming a login endpoint exists and returns a token
            self.client.post("/api/v1/auth/login", json={"username": "testuser", "password": "testpassword"})

    ```
3.  **Run load test**:
    ```bash
    locust -f locustfile.py --host=http://localhost:8000
    ```
    Open your browser to `http://localhost:8089` to access the Locust web UI and start the test.

## 9. Monitoring and Logging

Effective monitoring and logging are crucial for maintaining the health and performance of the system in production.

### 9.1. Application Monitoring

Basic request logging can be added to your FastAPI `main.py` to monitor API performance.

```python
# Add to app/main.py
import logging
from fastapi import Request
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"Request: {request.method} {request.url} | Status: {response.status_code} | Time: {process_time:.2f}s")
    return response
```

For more advanced monitoring, consider integrating with tools like Prometheus and Grafana.

### 9.2. Celery Monitoring

Monitor your Celery workers and tasks to ensure background processes are running smoothly.

*   **Monitor Celery workers**:
    ```bash
    celery -A app.workers.celery_worker inspect active
    celery -A app.workers.celery_worker inspect registered
    celery -A app.workers.celery_worker inspect scheduled
    ```
*   **Celery Flower (Web UI)**:
    Flower is a web-based tool for monitoring Celery clusters.
    1.  Install Flower:
        ```bash
        pip install flower
        ```
    2.  Run Flower:
        ```bash
        celery -A app.workers.celery_worker flower --port=5555
        ```
        Access Flower at `http://localhost:5555`.

### 9.3. Health Checks

Implement health check endpoints to verify the status of your application and its dependencies.

```python
# Add to app/main.py or a dedicated health check module
from datetime import datetime
from app.db.mongo import db
from app.workers.celery_worker import celery_app

async def check_redis_connection():
    try:
        # Celery will use Redis, so checking Celery's broker connection is a good proxy
        # Or directly use redis-py client if you have it configured
        i = celery_app.control.inspect()
        return i.ping() is not None
    except Exception:
        return False

async def check_mongo_connection():
    try:
        await db.command('ping')
        return True
    except Exception:
        return False

async def check_celery_workers():
    try:
        i = celery_app.control.inspect()
        return i.active() is not None # Checks if any workers are active
    except Exception:
        return False

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "redis": await check_redis_connection(),
            "mongodb": await check_mongo_connection(),
            "celery": await check_celery_workers()
        }
    }
```

## 10. Security Considerations

Security is paramount for any production system. This project incorporates several security best practices.

### 10.1. Authentication and Authorization

*   **JWT token-based authentication**: Securely verifies user identity for API access.
*   **Role-based access control (RBAC)**: Ensures users can only access resources and perform actions authorized by their assigned roles (e.g., `admin`, `candidate`).
*   **API rate limiting**: (To be implemented or configured via a proxy) Prevents abuse and protects against brute-force attacks.
*   **Input validation and sanitization**: Protects against injection attacks (e.g., SQL injection, XSS) by validating and sanitizing all user inputs.

### 10.2. Data Protection

*   **Encrypt sensitive data at rest**: Sensitive information in the database (e.g., user passwords, API keys) should be encrypted.
*   **Use HTTPS for all communications**: Ensures data in transit is encrypted and protected from eavesdropping.
*   **Implement proper session management**: Securely manages user sessions to prevent session hijacking.
*   **Regular security audits**: Periodically review code and configurations for vulnerabilities.

### 10.3. API Security Example (Rate Limiting Middleware)

While not fully implemented in the provided code, a rate-limiting middleware can be added to `app/main.py`.

```python
from fastapi import Security, HTTPException, Request
from fastapi.security import HTTPBearer

security = HTTPBearer()

# This is a placeholder. A real rate limiter would use Redis or similar.
# from collections import defaultdict
# from time import time
# request_counts = defaultdict(lambda: {'count': 0, 'last_reset': time()})

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Example: Simple IP-based rate limiting (not production ready)
    # client_ip = request.client.host
    # current_time = time()
    # if current_time - request_counts[client_ip]['last_reset'] > 60: # Reset every 60 seconds
    #     request_counts[client_ip]['count'] = 0
    #     request_counts[client_ip]['last_reset'] = current_time
    #
    # request_counts[client_ip]['count'] += 1
    # if request_counts[client_ip]['count'] > 100: # Max 100 requests per minute
    #     raise HTTPException(status_code=429, detail="Too Many Requests")

    response = await call_next(request)
    return response
```

## 11. Troubleshooting

This section provides solutions to common issues you might encounter.

### 11.1. Common Issues

#### 11.1.1. Celery Worker Not Starting

*   **Check Redis connection**:
    Ensure your Redis server is running and accessible.
    ```bash
    redis-cli ping
    ```
    Expected output: `PONG`
*   **Check Celery configuration**:
    Verify that Celery can connect to its broker and backend.
    ```bash
    celery -A app.workers.celery_worker inspect ping
    ```
    Expected output: `{<worker_name>: True}`
*   **Restart worker**:
    Sometimes, a simple restart can resolve issues.
    ```bash
    pkill -f celery # Kills all Celery processes
    celery -A app.workers.celery_worker worker --loglevel=info
    ```

#### 11.1.2. Email Not Sending

*   **Test SMTP connection**:
    Use a simple Python script to test your SMTP server connection.
    ```bash
    python -c "\
import smtplib, ssl;\
from email.mime.text import MIMEText;\
from email.header import Header;\

SMTP_SERVER = 'smtp.gmail.com';\
SMTP_PORT = 587;\
EMAIL_ADDRESS = 'your-email@gmail.com';\
EMAIL_PASSWORD = 'your-app-password';\
RECIPIENT_EMAIL = 'test-recipient@example.com';\

msg = MIMEText('This is a test email from the AI Recruitment System.', 'plain', 'utf-8');\
msg['Subject'] = Header('SMTP Test Email', 'utf-8');\
msg['From'] = EMAIL_ADDRESS;\
msg['To'] = RECIPIENT_EMAIL;\

context = ssl.create_default_context();\

try:\
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:\
        server.starttls(context=context);\
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD);\
        server.sendmail(EMAIL_ADDRESS, RECIPIENT_EMAIL, msg.as_string());\
        print('SMTP connection and email sending successful');\
except Exception as e:\
    print(f'SMTP connection or email sending failed: {e}');\
"
    ```
    Replace `your-email@gmail.com`, `your-app-password`, and `test-recipient@example.com` with your actual details.
*   **Check environment variables**: Ensure `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_SERVER`, `MAIL_PORT` are correctly set in your `.env` file.

#### 11.1.3. Zoom API Errors

*   **Test Zoom credentials**:
    Verify your Zoom API credentials by attempting to get an access token.
    ```bash
    curl -X POST "https://zoom.us/oauth/token" \
      -H "Authorization: Basic $(echo -n 'your_client_id:your_client_secret' | base64)" \
      -d "grant_type=account_credentials&account_id=your_account_id"
    ```
    Replace `your_client_id`, `your_client_secret`, and `your_account_id` with your actual Zoom Server-to-Server OAuth credentials.
*   **Check scopes**: Ensure your Zoom app has the necessary scopes enabled (e.g., `meeting:write`, `meeting:read`).

### 11.2. Performance Optimization

#### 11.2.1. Database Optimization

*   **Index frequently queried fields**: Add indexes to fields commonly used in queries (e.g., `job_id`, `user_id`, `resume_id`) to speed up database operations.
*   **Use connection pooling**: Configure your MongoDB client to use connection pooling to efficiently manage database connections.
*   **Implement caching strategies**: Cache frequently accessed data (e.g., job listings, dashboard statistics) in Redis to reduce database load.

#### 11.2.2. Celery Optimization

Optimize Celery settings for better performance and resource utilization.

```python
# In app/workers/celery_worker.py or a dedicated Celery config file
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    worker_prefetch_multiplier=1, # Adjust based on task nature
    task_acks_late=True, # Acknowledge task only after it's done
    broker_connection_retry_on_startup=True # Important for Docker/Compose setups
)
```

## 12. Contributing

We welcome contributions to the AI Recruitment System! Please follow these guidelines.

### 12.1. Development Setup

1.  **Fork the repository** on GitHub.
2.  **Clone your forked repository** to your local machine.
3.  **Create a new feature branch** for your changes:
    ```bash
    git checkout -b feature/your-feature-name
    ```
4.  **Install development dependencies**:
    ```bash
    pip install -r requirements-dev.txt
    ```
    (Ensure `requirements-dev.txt` exists and lists development-specific packages like `pytest`, `locust`, `flake8`, `black`, etc.)
5.  **Run tests before committing**: Ensure all existing tests pass and add new tests for your features.
6.  **Submit a pull request** to the `main` branch of the original repository.

### 12.2. Code Style

*   **Follow PEP 8 guidelines**: Adhere to Python's official style guide.
*   **Use type hints**: Improve code readability and maintainability.
*   **Write comprehensive docstrings**: Document functions, classes, and modules clearly.
*   **Maintain test coverage above 80%**: Ensure new features are well-tested.
*   **Use a linter and formatter**: Consider using `flake8` for linting and `black` for code formatting to maintain consistency.

## 13. License

This project is licensed under the MIT License. See the `LICENSE` file in the root of the repository for full details.

## 14. Support

For technical support, questions, or to report issues, please use the following resources:

*   **Email**: support@ai-recruitment-system.com
*   **Documentation**: https://docs.ai-recruitment-system.com (Placeholder - to be developed)
*   **Issues**: https://github.com/your-org/ai-recruitment-system/issues (Placeholder - replace with actual GitHub issues link)

---

**Author**: Manus AI  
**Version**: 2.0.0  
**Last Updated**: August 2024




## 15. Project File Structure

```
AI_REC_SYSTEM/
├── Dockerfile
├── README_ENHANCED.md
├── README_IMPROVED.md
├── celerybeat-schedule
├── docker-compose.yml
├── pytest.ini
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── applications.py
│   │       ├── auth.py
│   │       ├── dashboard.py
│   │       ├── interviews.py
│   │       ├── jobs.py
│   │       ├── notifications.py
│   │       ├── resumes.py
│   │       └── users.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── jwt.py
│   ├── db/
│   │   ├── __init__.py
│   │   └── mongo.py
│   ├── dependencies/
│   │   ├── __init__.py
│   │   └── roles.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── job.py
│   │   └── user.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── job.py
│   │   └── user.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── dashboard_service.py
│   │   ├── email_service.py
│   │   ├── google_calender_service.py
│   │   ├── job_service.py
│   │   ├── llm_service.py
│   │   ├── resume_service.py
│   │   └── zoom_service.py
│   ├── templates/
│   │   └── email/
│   │       ├── analysis_notification.html
│   │       ├── base.html
│   │       ├── interview_invitation.html
│   │       └── status_update.html
│   ├── uploads/
│   │   ├── json/
│   │   └── resumes/
│   └── utils/
│       ├── __init__.py
│       ├── hashing.py
│       └── service_account.json
│   └── workers/
│       ├── __init__.py
│       ├── celery_worker.py
│       └── tasks.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_auth.py
    ├── test_dashboard.py
    ├── test_jobs.py
    └── test_resumes.py
```


