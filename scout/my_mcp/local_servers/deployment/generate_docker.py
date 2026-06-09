from pathlib import Path


def generate_docker(
    project_path: str,
    framework: str
):

    project = Path(project_path)

    dockerfile = project / "Dockerfile"
    dockerignore = project / ".dockerignore"

    if dockerfile.exists():
        return {
            "success": True,
            "message": "Dockerfile already exists"
        }

    docker_templates = {

        "FastAPI": """
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
""",

        "Flask": """
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
""",

        "React": """
FROM node:20

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
"""
    }

    if framework not in docker_templates:

        return {
            "success": False,
            "message": f"Unsupported framework: {framework}"
        }

    dockerfile.write_text(
        docker_templates[framework]
    )

    dockerignore.write_text(
        """
__pycache__
*.pyc
.env
.git
.gitignore
node_modules
venv
.venv
"""
    )

    return {
        "success": True,
        "framework": framework,
        "dockerfile": str(dockerfile),
        "dockerignore": str(dockerignore)
    }