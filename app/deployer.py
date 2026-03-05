import os
import subprocess
import uuid
from app.k8s_templates import generate_k8_yaml

DOCKER_USERNAME = "DOCKER_USERNAME" # replace with your docker hub username
DOMAIN = "YOUR_DOMAIN" # replace with your domain
DOCKER_REPO = "YOUR_DOCKER_HUB_REPO" # replace with your docker hub repo name

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def stream_cmd(cmd):
    process = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    for line in process.stdout:
        yield line

    process.wait()

    if process.returncode != 0:
        yield f"\n❌ Command failed: {cmd}\n"

def deploy_project(github_url, project_name):
    unique_id = str(uuid.uuid4())[:6]
    deployment_name = f"{project_name}-{unique_id}"
    project_path = os.path.join(BASE_DIR, deployment_name)

    image_name = f"docker.io/{DOCKER_USERNAME}/{DOCKER_REPO}:{deployment_name}"

    # Clone
    run(f"git clone {github_url} {project_path}")

    # Build
    run(f"docker build -t {image_name} {project_path}")
    
    # Push
    run(f"docker push {image_name}")

    # YAML
    yaml_content = generate_k8_yaml(deployment_name, image_name, DOMAIN)
    yaml_file = os.path.join(BASE_DIR, f"{deployment_name}.yaml")

    with open(yaml_file, "w") as f:
        f.write(yaml_content)

    run(f"kubectl apply -f {yaml_file}")

    return f"https://{deployment_name}.{DOMAIN}"