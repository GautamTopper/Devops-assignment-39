# Devops-assignment-39

Lightweight Python/Flask web app with Docker, Kubernetes manifests, and a Jenkins pipeline for CI/CD.

This repository contains:

- `app.py` — the Flask application entry point.
- `requirements.txt` — Python dependencies.
- `Dockerfile` — image build instructions.
- `Jenkinsfile` — pipeline definition for CI/CD.
- `k8s/deployment.yaml`, `k8s/service.yaml` — Kubernetes manifests for deployment and service.
- `templates/` — HTML templates used by the web app.
- `static/` — static assets (CSS, images, etc.).

## Quick start (local)

Prerequisites

- Python 3.8+ (or appropriate 3.x version)
- pip

Create a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate   # or `venv\\Scripts\\activate` on Windows
pip install -r requirements.txt
```

Run the app locally (exact command used by this project):

```bash
python app.py
```

The application starts with Flask's built-in server and binds to `0.0.0.0:5000` by default (see `app.py`).

Open http://localhost:5000/ in your browser.

Health endpoint (useful for smoke tests and k8s probes):

```
GET /health  -> returns JSON {"status":"running","timestamp":...}
```

If you prefer to control port or environment, set `PORT`, `FLASK_ENV`, or other environment variables as required and update `app.py` or Dockerfile accordingly.

## Docker

Build the Docker image:

```bash
docker build -t devops-assignment-39:latest .
```

Run the container (map ports as needed):

```bash
docker run --rm -p 5000:5000 devops-assignment-39:latest
```

The app should be reachable at http://localhost:5000/.

## Minimal smoke test (included)

I added a small smoke-test script at `scripts/smoke.sh` that calls the `/health` endpoint and fails if the service doesn't return HTTP 200. Make it executable and run:

```bash
chmod +x scripts/smoke.sh
./scripts/smoke.sh            # defaults to http://localhost:5000/health
# or: URL=http://my-host:5000/health ./scripts/smoke.sh
```

This script is suitable for a quick local smoke check and can be added as a Jenkins pipeline stage after deployment.

## Kubernetes

Apply the manifests in the `k8s/` folder:

```bash
kubectl apply -f k8s/
```

This repository's `k8s/deployment.yaml` uses port `5000`. I also added recommended liveness/readiness probes to the deployment that hit `/health`. Example probe configuration is already added to the deployment manifest; they use `initialDelaySeconds` and reasonable timeouts.

Inspect and forward ports if you need local access:

```bash
kubectl get deployments,svc
# For local testing: kubectl port-forward svc/<service-name> 5000:5000
```

Replace `<service-name>` with the actual name defined in `k8s/service.yaml`.

### Suggested k8s probe snippet

If you need to replicate or tune the probe settings, here is the snippet used in `k8s/deployment.yaml`:

```yaml
livenessProbe:
	httpGet:
		path: /health
		port: 5000
	initialDelaySeconds: 10
	periodSeconds: 15
	timeoutSeconds: 3
	failureThreshold: 3
readinessProbe:
	httpGet:
		path: /health
		port: 5000
	initialDelaySeconds: 5
	periodSeconds: 10
	timeoutSeconds: 3
	failureThreshold: 3
```

## Jenkins (CI/CD)

This repository includes a `Jenkinsfile` showing a pipeline. Typical pipeline steps:

- Checkout
- Build Python dependencies
- Build Docker image and push to registry (configure credentials)
- Deploy / update Kubernetes manifests (kubectl)
- Run smoke test (use `scripts/smoke.sh` against deployed app)

You will need to configure credentials and pipeline agents in Jenkins to match your environment.

## Security notes

- `app.py` currently sets `app.secret_key` inline. For production, move secrets into environment variables or a secret manager. Example pattern:

```bash
export APP_SECRET="$(generate-or-retrieve-secret)"
```

and in Python:

```python
app.secret_key = os.environ.get("APP_SECRET")
```

- `debug=True` is set in `app.py` for development. Disable it in production to avoid exposing the Werkzeug debugger.

## Project structure

```
.
├─ app.py
├─ Dockerfile
├─ Jenkinsfile
├─ requirements.txt
├─ k8s/
│  ├─ deployment.yaml
│  └─ service.yaml
├─ scripts/
│  └─ smoke.sh
├─ static/
└─ templates/
```

## Next steps (suggested)

- Add a Jenkins pipeline stage that runs `scripts/smoke.sh` after deploy and fails if it doesn't pass.
- Add a small unit/smoke test in Python (pytest) and run it in CI.
- Replace hard-coded secrets and disable debug mode for production builds.

## License

This project does not include a license file. Add a LICENSE if you intend to publish or share the code.

---

If you'd like, I can also convert the smoke check into a small Python-based test or add the Jenkins pipeline stage. Tell me which and I'll implement it.
