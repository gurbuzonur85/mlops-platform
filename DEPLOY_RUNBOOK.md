# Canlıya Alma Runbook'u — `gurbuzonur85/mlops-platform`

Bu repo için **kişiselleştirilmiş** dağıtım adımları. Docker Desktop'ta
Kubernetes'in etkin olduğu bir makinede sırayla çalıştır. Tüm komutlar
`ghcr.io/gurbuzonur85/mlops-platform` imajını ve senin repo'nu kullanır.

> Gereksinim: Docker Desktop (Kubernetes **enabled**), `kubectl`, `helm`, `git`.
> Kurumsal makinede kurulamıyorsa: ev bilgisayarı, kişisel laptop veya bir
> bulut VM (ör. bir Linux sunucuda `kind`/`k3s`) kullan.

---

## 0) Ön koşullar (bir kez)

```bash
kubectl config use-context docker-desktop
kubectl get nodes            # docker-desktop  Ready  control-plane
```

WSL2/Docker Desktop DNS düzeltmesi (ArgoCD github.com'u çözebilsin diye) —
README Step 0'daki CoreDNS ConfigMap bloğunu uygula.

---

## 1) CI/CD imajını hazır et (GitHub tarafı)

`main`'e push yaptığında GitHub Actions imajı otomatik üretir. İki ayarı
**bir kez** yap:

1. **Repo → Settings → Actions → General → Workflow permissions**
   → *Read and write permissions* → Save.
2. İlk build bittikten sonra: **Profil → Packages → `ml-prediction`
   → Package settings → Change visibility → Public.**
   (Aksi halde Kubernetes `ImagePullBackOff` verir.)

Actions sekmesinde `lint → build-and-push → update-manifest` üçü de yeşil
olmalı. `update-manifest`, `k8s/ml-prediction-deployment.yaml` içindeki
imaj tag'ini gerçek SHA'ya çevirip geri commit'ler.

---

## 2) ArgoCD kur

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl -n argocd wait --for=condition=available --timeout=180s deployment/argocd-server

# NodePort ile dışarı aç
kubectl -n argocd patch svc argocd-server -p '{"spec":{"type":"NodePort","ports":[{"port":80,"nodePort":30084},{"port":443,"nodePort":30081}]}}'

# Admin parolası
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d ; echo
```

UI: <https://localhost:30081>  (kullanıcı: `admin`)

---

## 3) Prometheus + Grafana kur (ArgoCD app'ten ÖNCE)

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
kubectl create namespace monitoring

helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --set grafana.adminPassword=admin \
  --set nodeExporter.enabled=false \
  --set prometheus-node-exporter.enabled=false \
  --set grafana.service.type=NodePort --set grafana.service.nodePort=30082 \
  --set prometheus.service.type=NodePort --set prometheus.service.nodePort=30083

kubectl -n monitoring wait --for=condition=ready pod \
  --selector=app.kubernetes.io/name=grafana --timeout=300s
kubectl get crd servicemonitors.monitoring.coreos.com   # kayıtlı olmalı
```

- Grafana → <http://localhost:30082>  (admin / admin)
- Prometheus → <http://localhost:30083>

---

## 4) Uygulamayı GitOps ile yayınla

```bash
kubectl apply -n argocd -f argocd/ml-prediction-app.yaml
```

ArgoCD UI'da `ml-prediction` kartı çıkar → **SYNC**. Sonra:

```bash
kubectl wait --for=condition=ready pod -l app=postgres      --timeout=180s
kubectl wait --for=condition=ready pod -l app=ml-prediction --timeout=180s
kubectl get pods
```

---

## 5) (Opsiyonel) LLM anahtarı — /llm/chat için

```bash
cp .env.example .env     # LLM_PROVIDER + API anahtarını yaz
kubectl create secret generic app-secret --from-env-file=.env
kubectl rollout restart deployment ml-prediction-deployment
```

iris ve advertising uçları anahtarsız da çalışır.

---

## 6) Test et + trafik üret

```bash
# iris tahmini
curl -X POST http://localhost:30080/prediction/iris \
  -H 'Content-Type: application/json' \
  -d '{"SepalLengthCm":5.1,"SepalWidthCm":3.5,"PetalLengthCm":1.4,"PetalWidthCm":0.2}'

# advertising tahmini
curl -X POST http://localhost:30080/prediction/advertising \
  -H 'Content-Type: application/json' \
  -d '{"TV":230.1,"Radio":37.8,"Newspaper":69.2}'

# Swagger arayüzü: http://localhost:30080/docs
# Metrikler:      http://localhost:30080/metrics

# Grafana'da panel dolsun diye sürekli trafik:
while true; do
  curl -s -X POST http://localhost:30080/prediction/iris \
    -H 'Content-Type: application/json' \
    -d '{"SepalLengthCm":5.1,"SepalWidthCm":3.5,"PetalLengthCm":1.4,"PetalWidthCm":0.2}' > /dev/null
  sleep 0.2
done
```

Prometheus → Status → Targets → `serviceMonitor/default/ml-prediction/0` yeşil olmalı.

Grafana panelleri (Add visualization → Prometheus data source):

| Panel | PromQL |
|---|---|
| İstek hızı | `sum by (handler) (rate(http_requests_total{job="ml-prediction"}[1m]))` |
| p95 gecikme | `histogram_quantile(0.95, sum by (le,handler) (rate(http_request_duration_seconds_bucket{job="ml-prediction"}[5m])))` |
| 5xx hata | `sum(rate(http_requests_total{job="ml-prediction",status=~"5.."}[1m]))` |

---

## 7) Sunum için ekran görüntüsü listesi

Aşağıdakileri yakala (sunumdaki placeholder slaytlara koy):

1. **GitHub Actions** — 3 job yeşil (Actions sekmesi)
2. **ArgoCD** — `ml-prediction` kartı *Synced / Healthy*
3. **kubectl get pods** — postgres + 3 ml-prediction pod'u Running
4. **Swagger /docs** veya curl çıktısı — başarılı tahmin cevabı
5. **Grafana** — istek hızı / latency paneli veri gösterirken
