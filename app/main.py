import os, uuid
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from app.deployer import deploy_project  
from fastapi.responses import StreamingResponse
from app.deployer import generate_k8_yaml
from app.deployer import stream_cmd


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI()

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

DOCKER_USERNAME = "DOCKER_USERNAME" # replace with your docker hub username
DOMAIN = "YOUR_DOMAIN" # replace with your domain

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

class DeployRequest(BaseModel):
    github_url: str
    project_name: str


@app.post("/deploy")
def deploy(request: DeployRequest):

    def generator():
        unique_id = str(uuid.uuid4())[:6]
        deployment_name = f"{request.project_name}-{unique_id}"
        project_path = os.path.join(BASE_DIR, deployment_name)
        image_name = f"docker.io/{DOCKER_USERNAME}/mini-platform:{deployment_name}"

        yield "Cloning repository...\n"
        yield from stream_cmd(f"git clone {request.github_url} {project_path}")

        yield "\nBuilding Docker image...\n"
        yield from stream_cmd(f"docker build -t {image_name} {project_path}")

        yield "\nPushing Docker image...\n"
        yield from stream_cmd(f"docker push {image_name}")

        yield "\nGenerating Kubernetes YAML...\n"

        yaml_content = generate_k8_yaml(deployment_name, image_name, DOMAIN)
        yaml_file = os.path.join(BASE_DIR, f"{deployment_name}.yaml")

        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        yield "\nDeploying to Kubernetes...\n"
        yield from stream_cmd(f"kubectl apply -f {yaml_file}")

        yield "\n✅ Deployment complete!\n"
        yield f"🌍 URL: https://{deployment_name}.{DOMAIN}\n"

    return StreamingResponse(generator(), media_type="text/plain")