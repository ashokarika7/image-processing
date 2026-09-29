# Image Processing System

A backend image-processing application built with **Python, FastAPI, PostgreSQL, AWS S3, AWS SQS, Docker, and Kubernetes**.

The application provides presigned URLs for image uploads, stores image metadata in PostgreSQL, and processes uploaded images asynchronously using an SQS worker.

## Live Demo

* **API Documentation (Swagger):** http://13.62.240.127:30080/docs
* **GitHub Repository:** https://github.com/ashokarika7/image-processing

> The live URL uses the EC2 public IP and may change if the instance is stopped and started.

## Architecture

```text
                 Client
                   |
                   v
             FastAPI Backend
                   |
          +--------+--------+
          |                 |
          v                 v
      PostgreSQL          S3 Bucket
     (Image metadata)    (Image files)
                            |
                            v
                       S3 Event
                            |
                            v
                       SQS Queue
                            |
                            v
                     Python Worker
                            |
                            v
                       PostgreSQL
                  (Update image status)
```

## Features

* REST APIs built with FastAPI.
* Image uploads using S3 presigned URLs.
* Image metadata stored in PostgreSQL.
* Asynchronous image processing using AWS SQS.
* Background worker for processing uploaded images.
* Docker containerization.
* Docker Compose for local development.
* Kubernetes deployments for the API and worker.
* AWS EC2 deployment using k3s.

## Technology Stack

| Technology       | Purpose                         |
| ---------------- | ------------------------------- |
| Python           | Backend programming             |
| FastAPI          | REST API framework              |
| PostgreSQL       | Image metadata storage          |
| AWS S3           | Image storage                   |
| AWS SQS          | Asynchronous message processing |
| Docker           | Application containerization    |
| Docker Compose   | Local multi-container setup     |
| Kubernetes (k3s) | Application orchestration       |
| AWS EC2          | Application hosting             |
| AWS RDS          | Managed PostgreSQL database     |

## Project Structure

```text
.
├── database/
│   └── db.py
├── k8s/
│   ├── api-deployment.yaml
│   ├── api-service.yaml
│   └── worker-deployment.yaml
├── model_handler/
│   └── image_model_handler.py
├── models/
│   └── image.py
├── routes/
│   ├── images.py
│   └── images_schema.py
├── services/
│   ├── s3.py
│   └── sqs_worker.py
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yaml
├── main.py
└── requirements.txt
```

## Prerequisites

* Python 3.12
* Docker and Docker Compose
* An AWS account
* An S3 bucket and SQS queue
* A PostgreSQL database

## Environment Variables

Create a `.env` file in the project root using `.env.example` as a template.

```env
DATABASE_URL=postgresql://username:password@localhost:5432/image_db
QUEUE_URL=your-sqs-queue-url
AWS_DEFAULT_REGION=eu-north-1
BUCKET_NAME=your-s3-bucket-name
```

Configure AWS credentials using an IAM role or the AWS credential chain. Do not commit real credentials or `.env` files.

## Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/ashokarika7/image-processing.git
cd image-processing
```

### 2. Configure environment variables

Create a `.env` file and provide your database, SQS, S3 and AWS configuration.

### 3. Start the application

```bash
docker compose up -d --build
```

This starts the FastAPI application and the background worker.

### 4. Access the API

Open:

```text
http://localhost:8000/docs
```

## Kubernetes Deployment

The project contains Kubernetes manifests for the API, worker and API service.

Apply the manifests after configuring the required Kubernetes Secret and container image:

```bash
kubectl apply -f k8s/
```

Check the deployments:

```bash
kubectl get deployments
kubectl get pods
kubectl get services
```

## AWS Deployment

The application is deployed on an AWS EC2 instance using k3s.

The deployment uses:

* EC2 to host the Kubernetes cluster.
* S3 to store uploaded images.
* SQS to deliver image-upload events to the worker.
* RDS PostgreSQL to store image metadata.
* Docker Hub to host the application image.

The EC2 instance accesses AWS services using its configured AWS permissions.

## API Documentation

Swagger UI is available at:

http://13.62.240.127:30080/docs

Use the interactive documentation to explore and test the available API endpoints.

## Future Improvements

* Add AI-based semantic image search.
* Add face grouping.
* Improve observability with metrics and logging.
* Configure HTTPS and a custom domain.
* Implement automatic scaling based on workload.

## License

This project is intended for learning and demonstration purposes.