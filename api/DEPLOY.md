# Deploying to GCP Cloud Run

Cloud Run is the right fit here: it runs a container directly, scales to zero when
idle (so an unused demo costs nothing), and gives you managed HTTPS with no VM or
cluster to maintain. GKE would be overkill for a single stateless API.

All commands below run from the `api/` directory.

---

## 0. Prerequisites (one time)

1. **Install the gcloud CLI** — https://cloud.google.com/sdk/docs/install
   (Windows: download the installer, then reopen your terminal.)

2. **Log in and pick a project:**

   ```bash
   gcloud auth login
   ```

   ```bash
   gcloud projects create attrition-api-demo --name="Attrition API"
   ```

   Skip the create step if you already have a project you want to use.

   ```bash
   gcloud config set project attrition-api-demo
   ```

3. **Enable billing** on the project in the Cloud Console. Cloud Run has a free
   monthly tier, but the project still needs a billing account attached.

4. **Enable the APIs you'll use:**

   ```bash
   gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com
   ```

---

## 1. Deploy

Two paths. **Path A is fewer steps and recommended for the first deploy.**

### Path A — let Cloud Build build it for you

Google builds the image from your `Dockerfile` in the cloud and deploys it in one
command. No local Docker push needed.

```bash
gcloud run deploy employee-attrition-api --source . --region asia-southeast2 --allow-unauthenticated --memory 1Gi
```

First run will ask to create an Artifact Registry repo — answer yes.

### Path B — push the image you already tested locally

Slower to type, but what you verified locally is byte-for-byte what runs in
production. Replace `PROJECT_ID` with your actual project id.

```bash
gcloud artifacts repositories create ml-apis --repository-format=docker --location=asia-southeast2
```

```bash
gcloud auth configure-docker asia-southeast2-docker.pkg.dev
```

```bash
docker tag employee-attrition-api asia-southeast2-docker.pkg.dev/PROJECT_ID/ml-apis/employee-attrition-api:v1
```

```bash
docker push asia-southeast2-docker.pkg.dev/PROJECT_ID/ml-apis/employee-attrition-api:v1
```

```bash
gcloud run deploy employee-attrition-api --image asia-southeast2-docker.pkg.dev/PROJECT_ID/ml-apis/employee-attrition-api:v1 --region asia-southeast2 --allow-unauthenticated --memory 1Gi
```

---

## 2. Test it

The deploy prints a **Service URL** like
`https://employee-attrition-api-xxxxxxxxxx.asia-southeast2.run.app`.

```bash
curl https://YOUR-SERVICE-URL/health
```

Then point Postman at `POST https://YOUR-SERVICE-URL/predict` with the same JSON
body you used locally, or just open `https://YOUR-SERVICE-URL/docs` in a browser
for the Swagger UI.

---

## Why these flags

| Flag | Reason |
|---|---|
| `--region asia-southeast2` | Jakarta — lowest latency if your users are in Indonesia. Any region works. |
| `--memory 1Gi` | pandas + scikit-learn + scipy import to roughly 400–500 MB before serving a request. The 512 Mi default is too tight and will cause startup crashes. |
| `--allow-unauthenticated` | Makes the URL **public**. See the security note below. |
| *(no `--port` flag)* | The container reads the `PORT` env var Cloud Run injects, so this is handled automatically. |

---

## Security note: `--allow-unauthenticated`

That flag puts the endpoint on the public internet with no key, no login, and no
rate limit. For a portfolio piece that's usually what you want — anyone can click
your link.

If this ever handles real employee records, drop it and deploy privately instead:

```bash
gcloud run deploy employee-attrition-api --source . --region asia-southeast2 --no-allow-unauthenticated --memory 1Gi
```

Then callers need a token:

```bash
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" https://YOUR-SERVICE-URL/health
```

---

## Cost control

The service scales to zero by default — no traffic means no charge, at the cost of
a cold start (a few seconds) on the first request after idling.

To eliminate cold starts you can keep one instance warm, **but this bills 24/7 and
is not free-tier eligible**:

```bash
gcloud run services update employee-attrition-api --region asia-southeast2 --min-instances 1
```

Leave it at the default `0` unless a slow first request is actually a problem.

---

## Updating after a code change

Re-run the same deploy command. Cloud Run creates a new revision and shifts
traffic to it, with no downtime.

To roll back:

```bash
gcloud run revisions list --service employee-attrition-api --region asia-southeast2
```

```bash
gcloud run services update-traffic employee-attrition-api --region asia-southeast2 --to-revisions REVISION_NAME=100
```
