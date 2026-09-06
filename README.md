# Python App — CI/CD & GitOps

A simple Flask application deployed using Docker, Kubernetes, GitHub Actions, and Argo CD with a GitOps workflow.

## Architecture

```text
Developer
   │
   │ git push
   ▼
GitHub - python-app
   │
   ▼
GitHub Actions
   │
   ├── Run Tests
   │
   ├── Build Docker Image
   │
   └── Push Image to Docker Hub
           │
           ▼
      Docker Hub
           
GitHub Actions
   │
   │ update image tag
   ▼
GitHub - infra-repo
   │
   ▼
   Argo CD
   │
   ▼
Kubernetes
   │
   ├── Deployment
   ├── Pods
   └── Service
        │
        ▼
      Traefik
        │
        ▼
   Python Flask App
```

---

## Project Overview

This project demonstrates a complete DevOps workflow for a Python Flask application.

The application is:

* Written with **Python / Flask**
* Tested with **pytest**
* Packaged into a **Docker image**
* Stored in **Docker Hub**
* Deployed to **Kubernetes**
* Exposed through **Traefik**
* Automatically deployed using **Argo CD**
* Managed using a **GitOps** workflow
* Automated with **GitHub Actions**

---

# Repository Structure

This project uses two Git repositories.

## 1. Application Repository

```text
python-app/
├── src/
│   └── app.py
│
├── test_app.py
├── requirements.txt
├── Dockerfile
└── .github/
    └── workflows/
        └── ci.yml
```

This repository contains the application source code and CI pipeline.

---

## 2. Infrastructure Repository

```text
infra-repo/
├── k8s-manifest/
│   ├── deployment.yml
│   ├── service.yml
│   ├── gateway.yml
│   └── httproute.yml
│
└── argocd/
    └── application.yml
```

This repository contains the Kubernetes desired state.

---

# Application

The Flask application provides two API endpoints.

## `/api/v1/info`

Returns information about the application:

```json
{
  "time": "2026-09-06 20:00:00",
  "hostname": "python-app-xxxxx"
}
```

## `/api/v1/healthz`

Health-check endpoint:

```json
{
  "status": "up"
}
```

---

# Run Locally

Create a Python virtual environment:

```bash
python -m venv venv
```

Activate it on Linux:

```bash
source venv/bin/activate
```

On Windows:

```powershell
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run tests:

```bash
pytest
```

Expected result:

```text
2 passed
```

Run the application:

```bash
python src/app.py
```

The application runs on:

```text
http://localhost:5000
```

Test:

```bash
curl http://localhost:5000/api/v1/info
```

---

# Docker

## Build the Image

```bash
docker build -t mohammadrezabazarjani/python-app:v2 .
```

## Run the Container

```bash
docker run -p 5000:5000 mohammadrezabazarjani/python-app:v2
```

The application is then available at:

```text
http://localhost:5000
```

---

# Docker Image

The application image is published to Docker Hub.

Image:

```text
mohammadrezabazarjani/python-app
```

GitHub Actions creates two tags:

```text
latest
```

and:

```text
<git-sha>
```

For example:

```text
mohammadrezabazarjani/python-app:latest

mohammadrezabazarjani/python-app:8f31a2c...
```

Using the Git SHA makes it possible to identify exactly which source-code commit produced a deployed image.

---

# Kubernetes

The application runs inside Kubernetes using a Deployment.

Example:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: python-app
spec:
  replicas: 3
```

Three Pods are normally running:

```text
python-app
 ├── Pod 1
 ├── Pod 2
 └── Pod 3
```

The Deployment makes sure the desired number of replicas remains available.

---

# Kubernetes Service

The application is exposed internally through a ClusterIP Service.

```text
Service Port: 8080
       │
       ▼
Container Port: 5000
```

The Service configuration:

```yaml
ports:
  - protocol: TCP
    port: 8080
    targetPort: 5000
```

Therefore:

```text
Service :8080
     ↓
Pod :5000
     ↓
Flask
```

---

# Traefik

Traefik is used as the reverse proxy / Gateway implementation.

The request flow is:

```text
Client
  │
  ▼
Traefik
  │
  ▼
Gateway
  │
  ▼
HTTPRoute
  │
  ▼
python-app-service:8080
  │
  ▼
Python Pod:5000
```

The application hostname is:

```text
python-app-test.com
```

---

# GitHub Actions

GitHub Actions provides the CI pipeline.

The workflow contains three main jobs.

```text
test
  ↓
docker
  ↓
update-infra
```

## 1. Test

The first job:

* Checks out the repository
* Installs Python
* Installs dependencies
* Runs pytest

```yaml
pytest
```

If tests fail, the next jobs do not run.

---

## 2. Docker

After successful tests, GitHub Actions:

1. Logs into Docker Hub
2. Builds the Docker image
3. Pushes the image to Docker Hub

The image receives:

```text
latest
```

and:

```text
github.sha
```

tags.

---

## 3. Update Infrastructure

After the Docker image is pushed, GitHub Actions clones `infra-repo`.

It changes:

```yaml
image: mohammadrezabazarjani/python-app:OLD_TAG
```

to:

```yaml
image: mohammadrezabazarjani/python-app:<GIT_SHA>
```

Then it commits and pushes the change to `infra-repo`.

---

# GitOps

GitOps means that Git is the source of truth for the desired infrastructure state.

In this project:

```text
infra-repo
     │
     │ desired state
     ▼
  Argo CD
     │
     │ reconciliation
     ▼
 Kubernetes
```

For example, if Git contains:

```yaml
replicas: 3
```

Argo CD makes sure Kubernetes eventually has:

```text
3 Pods
```

---

# Argo CD

Argo CD continuously watches the infrastructure repository.

The Application points to:

```text
https://github.com/mohammadrezabazarjani/infra-repo.git
```

and:

```text
k8s-manifest
```

Argo CD compares:

```text
Git Desired State
       │
       │ compare
       ▼
Kubernetes Actual State
```

If they are different, Argo CD synchronizes Kubernetes with Git.

---

# Automated Deployment Flow

The complete deployment process is:

```text
Developer changes code
        │
        ▼
git push
        │
        ▼
GitHub
        │
        ▼
GitHub Actions
        │
        ├──────────────┐
        ▼              │
     pytest            │
        │              │
        ▼              │
      PASS             │
        │              │
        ▼              │
 Build Docker Image    │
        │              │
        ▼              │
   Docker Hub          │
        │              │
        └──────┐       │
               ▼       │
         Update infra-repo
               │
               ▼
            Argo CD
               │
               ▼
          Kubernetes
               │
               ▼
          New Version
```

---

# CI vs CD vs GitOps

## CI — Continuous Integration

GitHub Actions checks the application:

```text
Code
 ↓
Test
 ↓
Build
 ↓
Docker Image
```

---

## CD — Continuous Deployment

The new version is automatically deployed to Kubernetes.

```text
New Image
   ↓
Infrastructure Update
   ↓
Argo CD
   ↓
Kubernetes
```

---

## GitOps

GitOps controls deployment through Git:

```text
Git Repository
      ↓
   Argo CD
      ↓
 Kubernetes
```

Git contains the desired state.

---

# Important Concepts

## Image vs Container

### Image

A Docker image is a packaged template containing:

* Application code
* Python
* Dependencies
* Runtime configuration

### Container

A container is a running instance of an image.

```text
Image
  │
  ├── Container 1
  ├── Container 2
  └── Container 3
```

---

## Deployment vs Pod

### Pod

The Pod is where the application container runs.

### Deployment

The Deployment manages Pods and ensures the desired number of replicas exists.

```text
Deployment
    │
    ├── Pod
    ├── Pod
    └── Pod
```

---

## Service

A Service provides a stable network endpoint for Pods.

```text
Service
   │
   ├── Pod
   ├── Pod
   └── Pod
```

---

# Useful Kubernetes Commands

Check Pods:

```bash
kubectl get pods
```

Check Deployment:

```bash
kubectl get deployment python-app
```

Check Service:

```bash
kubectl get svc python-app-service
```

Check Gateway:

```bash
kubectl get gateway
```

Check HTTPRoute:

```bash
kubectl get httproute
```

Check Argo CD Application:

```bash
kubectl get application python-app -n argocd
```

Check detailed Argo CD status:

```bash
kubectl describe application python-app -n argocd
```

---

# GitOps Test

A useful test for this project is changing the number of replicas in:

```text
infra-repo/k8s-manifest/deployment.yml
```

For example:

```yaml
replicas: 3
```

Change it to:

```yaml
replicas: 5
```

Commit and push:

```bash
git add .
git commit -m "scale python app"
git push origin main
```

Do **not** run:

```bash
kubectl apply
```

Argo CD should detect the Git change and update Kubernetes.

Check:

```bash
kubectl get deployment python-app
```

and:

```bash
kubectl get pods
```

This demonstrates the GitOps principle.

---

# Project Technologies

| Technology     | Purpose                      |
| -------------- | ---------------------------- |
| Python         | Application                  |
| Flask          | Web API                      |
| pytest         | Testing                      |
| Git            | Version control              |
| GitHub         | Source code hosting          |
| GitHub Actions | CI automation                |
| Docker         | Containerization             |
| Docker Hub     | Container registry           |
| Kubernetes     | Container orchestration      |
| Minikube       | Local Kubernetes cluster     |
| Traefik        | Reverse proxy / Gateway      |
| Gateway API    | Traffic routing              |
| Argo CD        | GitOps / Continuous Delivery |

---

# Final Architecture

```text
                    ┌─────────────────┐
                    │    Developer    │
                    └────────┬────────┘
                             │
                         git push
                             │
                             ▼
                    ┌─────────────────┐
                    │     GitHub      │
                    │   python-app    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ GitHub Actions  │
                    └────────┬────────┘
                             │
                   ┌─────────┴─────────┐
                   │                   │
                   ▼                   ▼
                pytest              Docker
                   │                   │
                   │                   ▼
                   │              Docker Hub
                   │                   │
                   └─────────┬─────────┘
                             ▼
                    ┌─────────────────┐
                    │   infra-repo     │
                    │ Kubernetes YAML  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │     Argo CD     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   Kubernetes    │
                    │    Minikube     │
                    └────────┬────────┘
                             │
                             ▼
                       ┌───────────┐
                       │ Traefik   │
                       └─────┬─────┘
                             │
                             ▼
                       ┌───────────┐
                       │ Flask API │
                       └───────────┘
```

## Goal

The main goal of this project is to demonstrate a practical DevOps pipeline:

```text
Code
 ↓
Test
 ↓
Build
 ↓
Docker
 ↓
Registry
 ↓
GitOps
 ↓
Argo CD
 ↓
Kubernetes
 ↓
Application
```
