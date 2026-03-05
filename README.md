Mini Deployment Platform 🚀

A lightweight Platform-as-a-Service that deploys GitHub applications automatically using Docker and Kubernetes.

This project builds a mini Heroku-style platform where users can submit a GitHub repository and the platform will automatically:

Clone the repository

Build a Docker image

Push the image to Docker Hub

Deploy the container to Kubernetes

Expose the application publicly via HTTP/HTTPS

The platform is designed to demonstrate DevOps and Platform Engineering concepts.

Architecture

                USER
                 │
                 │ submit repo
                 ▼
        FastAPI Deployment API
                 │
                 ▼
              GitHub
                 │
                 ▼
            Docker Build
                 │
                 ▼
            Docker Hub
                 │
                 ▼
            Kubernetes (K3s)
                 │
                 ▼
               Traefik
                 │
                 ▼
             Public URL