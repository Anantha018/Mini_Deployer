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

Technologies Used

| Component        | Purpose                 |
| ---------------- | ----------------------- |
| FastAPI          | Deployment API          |
| Docker           | Containerization        |
| Docker Hub       | Image registry          |
| Kubernetes (K3s) | Container orchestration |
| Traefik          | Ingress controller      |
| AWS EC2          | Cloud infrastructure    |


Step 1 — Create an AWS EC2 Instance

Go to AWS Console → EC2 → Launch Instance

Recommended configuration:

| Setting       | Value               |
| ------------- | ------------------- |
| OS            | Ubuntu 22.04        |
| Instance Type | t2.micro / t3.micro |
| Storage       | 20 GB               |
| Key Pair      | Create `.pem` key   |


Step 2 — Configure Security Group

Add inbound rules:

| Type   | Port |
| ------ | ---- |
| SSH    | 22   |
| HTTP   | 80   |
| HTTPS  | 443  |
| Custom | 8000 |

Reason:

| Port | Usage           |
| ---- | --------------- |
| 22   | SSH             |
| 80   | HTTP traffic    |
| 443  | HTTPS           |
| 8000 | FastAPI backend |


Step 3 — Assign Elastic IP

AWS public IPs change after restart.

Elastic IP ensures:

• Stable DNS
• Stable HTTPS certificates
• Permanent public endpoint

Go to:

EC2 → Elastic IPs → Allocate → Associate with instance


Step 4 — Connect to EC2

ssh -i "your-key.pem" ubuntu@<elastic-ip>


Step 5 — Install Docker

sudo apt update
sudo apt install docker.io -y

sudo systemctl enable docker
sudo systemctl start docker

sudo usermod -aG docker ubuntu

logout

Verify:

docker ps


Step 6 — Install Kubernetes (K3s)

Install lightweight Kubernetes:

curl -sfL https://get.k3s.io | sh -

Verify installation:

sudo kubectl get nodes

Expected output:

Ready control-plane


Step 7 — Configure kubectl

Copy kubeconfig:

sudo mkdir -p ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown ubuntu:ubuntu ~/.kube/config

Set environment variable:

export KUBECONFIG=/home/ubuntu/.kube/config

Verify:

kubectl get nodes


Step 8 — Install Python Environment

sudo apt install python3 python3-pip python3-venv -y

Clone repository:

git clone https://github.com/YOUR_USERNAME/mini_deployment_platform
cd mini_deployment_platform

Create virtual environment:

python3 -m venv env
source env/bin/activate

Install dependencies:

pip install -r requirements.txt


Step 9 — Docker Hub Login

Login to Docker Hub:

docker login

Why a Docker registry is required:

When Kubernetes deploys applications it must pull images from a registry.

Flow:

Code → Docker image → Registry → Kubernetes pulls image

Without a registry Kubernetes cannot fetch the container image.


Step 10 — Run the Deployment API

Run:

uvicorn app.main:app --host 0.0.0.0 --port 8000

Access API:

http://<elastic-ip>:8000/docs


Step 11 — Configure Domain

Buy a free domain from:

• Namecheap
• Freenom
• Cloudflare

Example domain:

mydeployplatform.dev


Step 12 — Configure DNS

In DNS settings add:

A record

| Type | Value          |
| ---- | -------------- |
| Host | @              |
| IP   | EC2 Elastic IP |

Example:

mydeployplatform.dev → 54.xx.xx.xx


Step 13 — HTTPS (Optional)

If HTTPS certificate is not configured you may need:

export KUBECONFIG=/home/ubuntu/.kube/config

This ensures Kubernetes commands work correctly.

Traefik can automatically issue certificates via Let's Encrypt.



Deployment Flow

User sends request:

POST /deploy
{
 "github_url":"https://github.com/user/app"
}


Platform executes:

1. Clone repo
2. Build Docker image
3. Push image to Docker Hub
4. Generate Kubernetes YAML
5. Deploy container
6. Create service
7. Expose application



Repository Structure Required for Deployment

Repositories must include a Dockerfile.

Example structure:

my-app/
│
├── Dockerfile
├── requirements.txt
├── main.py
│
├── app/
│   └── main.py
│
└── README.md


Example Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn","main:app","--host","0.0.0.0","--port","8000"]



Important Deployment Rules

Applications must:

✔ include a Dockerfile
✔ expose port 8000
✔ bind to 0.0.0.0

Example:

uvicorn main:app --host 0.0.0.0 --port 8000



Debugging Errors

No Server Available Error

If the cluster runs out of resources, old deployments may block scheduling.

Delete previous deployments:

kubectl get deployments

Then remove unused apps:

kubectl delete deployment <deployment-name>

Example:

kubectl delete deployment testapp


Kubernetes Commands Not Working

Run:

export KUBECONFIG=/home/ubuntu/.kube/config



Docker Permission Error

Fix permissions:

sudo usermod -aG docker ubuntu

Log out and log back in.


SSH Host Key Changed

Run:

ssh-keygen -R <ec2-host>