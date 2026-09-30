# Image Processing System

A cloud-based, asynchronous image-processing backend built using **Python, FastAPI, PostgreSQL, AWS S3, AWS SQS, Docker and Kubernetes**. The project demonstrates how to build, deploy and maintain a backend application using a distributed processing architecture.

## Overview

This application allows clients to upload images through a REST API. Images are stored in Amazon S3, while their metadata and processing status are maintained in PostgreSQL. Amazon SQS decouples image uploads from background processing, allowing a separate worker to process images asynchronously.

The application is containerized using Docker, deployed on Kubernetes running on AWS EC2, and automatically deployed through GitHub Actions.

## Live Deployment

* **API documentation:** http://13.62.240.127:30080/docs
* **GitHub repository:** https://github.com/ashokarika7/image-processing

> The application currently uses HTTP. HTTPS and a custom domain have not been configured.

## Architecture

```mermaid
flowchart TD
    A[Client] --> B[FastAPI]
    B --> C[(PostgreSQL / RDS)]
    B --> D[Amazon S3]
    D --> E[Amazon SQS]
    E --> F[Background Worker]
    F --> G[Download Image from S3]
    G --> H[Process Image]
    H --> C
    F --> I[Delete SQS Message]
    J[GitHub Repository] --> K[GitHub Actions]
    K --> L[Build Docker Image]
    L --> M[Docker Hub]
    K --> N[AWS SSM]
    N --> O[EC2 / k3s]
    M --> O
```

### Image upload workflow

1. The client sends an image upload request to the FastAPI application.
2. The application uploads the image to Amazon S3.
3. Image metadata and its initial processing status are stored in PostgreSQL.
4. Amazon S3 sends an object-created event to Amazon SQS.
5. The background worker polls the SQS queue and receives the event.
6. The worker downloads the image from S3 and processes it.
7. The worker updates the image's processing status in PostgreSQL.
8. After successful processing, the worker deletes the SQS message.

### Deployment workflow

1. A developer pushes code to the `main` branch.
2. GitHub Actions checks out the source code.
3. Docker Buildx builds the application image.
4. The image is pushed to Docker Hub with a commit SHA tag.
5. GitHub Actions authenticates with AWS using OpenID Connect (OIDC).
6. AWS Systems Manager (SSM) sends deployment commands to EC2.
7. The commands update the Kubernetes API and worker deployments.
8. Kubernetes rollout status and an HTTP health check are verified.
9. If a detected failure occurs, the workflow attempts to roll back the deployments.

## Technology Stack

| Category                 | Technology           |
| ------------------------ | -------------------- |
| Programming language     | Python               |
| Backend framework        | FastAPI              |
| API documentation        | Swagger UI / OpenAPI |
| Database                 | PostgreSQL           |
| Database hosting         | Amazon RDS           |
| Object storage           | Amazon S3            |
| Message queue            | Amazon SQS           |
| Background processing    | Python worker        |
| Containerization         | Docker               |
| Container orchestration  | Kubernetes (k3s)     |
| Cloud provider           | AWS                  |
| Compute                  | Amazon EC2           |
| CI/CD                    | GitHub Actions       |
| Container registry       | Docker Hub           |
| Deployment management    | AWS Systems Manager  |
| Authentication for CI/CD | AWS IAM and OIDC     |

## Key Features

### 1. REST API

* Built with FastAPI.
* Provides an HTTP interface for image uploads.
* Automatically generates interactive API documentation.
* Uses Pydantic schemas for request and response validation.

### 2. Image storage

* Stores uploaded images in Amazon S3.
* Uses S3 object keys to identify stored images.
* Keeps image metadata separately in PostgreSQL.
* Uses S3 event notifications to initiate asynchronous processing.

### 3. Asynchronous processing

* Uses Amazon SQS to decouple image uploads from processing.
* A separate worker polls the queue for messages.
* The worker downloads images from S3 before processing.
* Updates image processing status in PostgreSQL.
* Deletes successfully processed SQS messages.

### 4. Database management

* Uses PostgreSQL to persist image metadata.
* Tracks image processing states such as `pending` and `processed`.
* Stores image identifiers, filenames, S3 keys and timestamps.
* Uses SQLAlchemy for database operations.

### 5. Containerization

* Uses Docker to package the API and worker.
* Provides a consistent runtime environment.
* Uses Docker Compose for local development and service integration.

### 6. Kubernetes deployment

* Deploys the API and worker as separate Kubernetes Deployments.
* Uses Kubernetes Services to expose the API.
* Runs on k3s on an AWS EC2 instance.
* Supports rolling updates of application deployments.

### 7. CI/CD automation

* Uses GitHub Actions to automate builds and deployments.
* Builds and pushes Docker images to Docker Hub.
* Uses OIDC to authenticate GitHub Actions with AWS.
* Uses SSM instead of SSH for remote deployment commands.
* Updates Kubernetes deployments with commit-specific image tags.
* Checks rollout status and performs an HTTP health check.
* Attempts automatic rollback when a deployment failure is detected.

## Database Design

The image metadata table contains the following fields:

| Column         | Description                           |
| -------------- | ------------------------------------- |
| `id`           | Unique image identifier               |
| `filename`     | Original image filename               |
| `s3_key`       | Unique S3 object key                  |
| `status`       | Current processing status             |
| `description`  | Image description                     |
| `category`     | Image category                        |
| `created_at`   | Image creation timestamp              |
| `processed_at` | Image processing completion timestamp |

### Processing states

| Status      | Meaning                                           |
| ----------- | ------------------------------------------------- |
| `pending`   | Image has been created and is awaiting processing |
| `processed` | Image processing has completed successfully       |

Additional failure states and retry tracking can be introduced as the application evolves.

## Project Structure

```text
proj_image_processing/
├── database/
│   └── db.py
├── k8s/
│   ├── backend-deployment.yaml
│   └── ...
├── model_handler/
│   └── image_model_handler.py
├── models/
│   └── ...
├── services/
│   ├── s3.py
│   └── sqs_worker.py
├── tests/
│   └── ...
├── worker/
│   └── ...
├── .github/
│   └── workflows/
│       └── deploy.yml
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yaml
├── main.py
├── requirements.txt
└── README.md
```

> Some filenames and directories may change as the project evolves.

## Local Development

### Prerequisites

* Python
* Docker and Docker Compose
* AWS account with permissions for S3, SQS and RDS
* Git

### 1. Clone the repository

```bash
git clone https://github.com/ashokarika7/image-processing.git
cd image-processing
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file using the example:

```bash
cp .env.example .env
```

Update the values for your environment.

```dotenv
DATABASE_URL=postgresql://username:password@localhost:5432/image_db
QUEUE_URL=https://sqs.eu-north-1.amazonaws.com/ACCOUNT_ID/image-processing-queue
AWS_DEFAULT_REGION=eu-north-1
BUCKET_NAME=your-s3-bucket-name
```

Do not commit `.env` files or AWS credentials to Git.

### 5. Run the API

```bash
uvicorn main:app --reload
```

Open the interactive API documentation at:

```text
http://127.0.0.1:8000/docs
```

### 6. Run the worker

From the project root, run:

```bash
python -m services.sqs_worker
```

The worker requires valid AWS credentials and access to the configured SQS queue, S3 bucket and PostgreSQL database.

### 7. Run with Docker Compose

```bash
docker compose up --build
```

To stop the services:

```bash
docker compose down
```

The Compose configuration may require environment variables and accessible AWS resources, depending on the selected configuration.

## AWS Infrastructure

The deployed application uses the following AWS resources:

| Resource       | Purpose                                         |
| -------------- | ----------------------------------------------- |
| EC2            | Hosts the Kubernetes cluster                    |
| k3s            | Runs the API and worker containers              |
| RDS PostgreSQL | Stores image metadata                           |
| S3             | Stores uploaded image objects                   |
| SQS            | Buffers image-processing events                 |
| IAM            | Controls access to AWS resources                |
| SSM            | Executes deployment commands remotely           |
| CloudWatch     | Provides AWS and SSM operational logs           |
| Elastic IP     | Provides a stable public IP for the application |

The application is deployed in the `eu-north-1` region.

## CI/CD Pipeline

The deployment workflow is defined in:

```text
.github/workflows/deploy.yml
```

The pipeline runs when code is pushed to `main` and can also be triggered manually.

### Pipeline stages

| Stage          | Action                                                   |
| -------------- | -------------------------------------------------------- |
| Source         | Check out the repository                                 |
| Build          | Build the Docker image using Docker Buildx               |
| Publish        | Push the image to Docker Hub                             |
| Authentication | Assume an AWS IAM role using OIDC                        |
| Deployment     | Send commands to EC2 through SSM                         |
| Update         | Update the API and worker Kubernetes deployments         |
| Verification   | Check Kubernetes rollout status                          |
| Health check   | Verify that the API responds                             |
| Recovery       | Attempt rollback if a detected deployment failure occurs |

Images are tagged with the Git commit SHA, which makes each build identifiable.

## Security Considerations

* AWS permissions are managed using IAM roles and policies.
* GitHub Actions uses OIDC instead of long-lived AWS access keys.
* Deployment commands are executed through AWS Systems Manager.
* Application configuration is provided through environment variables.
* Sensitive local configuration is excluded through `.gitignore` and `.dockerignore`.

The current public HTTP endpoint does not provide HTTPS encryption. A domain and TLS configuration remain future improvements.

## Testing

The project includes a `tests/` directory for automated testing.

Run the tests using:

```bash
pytest
```

AWS services should be mocked in unit tests where practical to avoid requiring live AWS resources and incurring unnecessary charges.

## Planned Enhancements

The following features are planned and should not be considered implemented yet.

* Image format and file-size validation.
* Thumbnail generation and image resizing.
* Image processing retry and reprocessing APIs.
* Dead-letter queue recovery workflows.
* Paginated image listing and filtering.
* JWT-based authentication and user ownership.
* More comprehensive readiness and dependency health checks.
* Structured logging and processing metrics.
* AI-based image search and image grouping.
* HTTPS with a custom domain.
* Improved deployment rollback and recovery testing.

## Learning Outcomes

This project provides practical experience with:

* Designing REST APIs using FastAPI.
* Integrating PostgreSQL with a Python backend.
* Building asynchronous, event-driven processing workflows.
* Using S3 and SQS together.
* Developing and running Docker containers.
* Deploying applications with Kubernetes.
* Managing cloud infrastructure on AWS.
* Automating deployments using GitHub Actions.
* Using IAM OIDC and SSM for secure deployment workflows.
* Implementing deployment verification and basic rollback logic.

## Future Direction

The next development phase focuses on making the application more complete as an image-processing product, with validation, transformations, retries, pagination and authentication. AI-based image search can be introduced after the core features are in place.

---

**Author:** Ashok Arika
**Repository:** https://github.com/ashokarika7/image-processing
**Deployment:** http://13.62.240.127:30080/docs