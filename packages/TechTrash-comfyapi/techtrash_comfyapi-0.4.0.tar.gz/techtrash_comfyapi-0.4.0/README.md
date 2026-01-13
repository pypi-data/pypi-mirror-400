## TechTrash ComfyAPI

TechTrash ComfyAPI est une petite librairie Python qui permet de piloter facilement plusieurs instances ComfyUI en parallèle, en utilisant automatiquement toutes les GPU disponibles, et en gérant les modèles / LoRAs et la récupération des images générées.

### Installation

- **Prérequis** :
  - Python **3.11+**
  - `pynvml` installé sur la machine avec les GPU
  - Accès à un stockage S3 compatible OVH (endpoint, bucket, clés, etc.)
  - ComfyUI installé sur la machine, avec une instance par GPU si possible

- **Depuis `pip` (wheel déjà générée)** :

```bash
pip install techtrash-comfyapi
```

ou directement depuis le projet :

```bash
pip install .
```

### Idée générale

- **Détection GPU** : `ComfyAPI` détecte le nombre et le type de GPU via `pynvml`.
- **Lancement des instances ComfyUI** : pour chaque GPU, la classe lance un process ComfyUI sur un port dédié (`subprocess.Popen(...)`).
- **Gestion des modèles / LoRAs** :
  - vérifie que les modèles demandés existent dans `models_path`,
  - télécharge les LoRAs manquants depuis une URL vers `models_path/loras`.
- **Répartition des réglages** :
  - certains paramètres sont **divisés par le nombre de GPU** (ex: `batch_size`),
  - d’autres restent **fixes par GPU** (ex: `steps`).
- **Exécution du workflow** :
  - envoie le workflow JSON à chaque instance ComfyUI,
  - attend la fin du traitement,
  - retourne la liste complète des chemins des images générées.

### Utilisation rapide

Exemple minimal pour lancer un workflow (pseudo-code simplifié) :

```python
import asyncio
from comfyapi.main import ComfyAPI

api = ComfyAPI(
    api_key="TON_API_KEY",
    s3_endpoint="https://s3.gra.io.cloud.ovh.net",
    s3_bucket="ton-bucket",
    s3_region="gra",
    s3_key_id="TON_KEY_ID",
    s3_secret="TON_SECRET",
    absolute_paths_comfyui=[
        "/chemin/vers/comfyui/gpu0",
        "/chemin/vers/comfyui/gpu1",
    ],
    models_path="/chemin/vers/models",
    ports=[3050, 3051],
)

workflow_json = {...}  # workflow ComfyUI complet
models = [
    {"type": "checkpoints", "name": "model.safetensors"},
]
loras = [
    {"name": "lora.safetensors", "url": "https://.../lora.safetensors"},
]
settings_scaled_by_gpu_count = [
    {"title": "KSampler", "value": 8},   # ex : batch_size
]
settings_fixed_per_gpu = [
    {"title": "KSampler", "value": 20},  # ex : steps
]

async def main():
    images = await api.execute_workflow_TtI(
        workflow_json=workflow_json,
        models=models,
        loras=loras,
        settings_scaled_by_gpu_count=settings_scaled_by_gpu_count,
        settings_fixed_per_gpu=settings_fixed_per_gpu,
    )
    print("Images générées :", images)

asyncio.run(main())
```

### Paramètres principaux

- **`ComfyAPI`** :
  - `api_key` : clé API pour sécuriser l’accès (si utilisée par tes instances).
  - `s3_*` : paramètres S3 OVH (endpoint, bucket, région, clés).
  - `absolute_paths_comfyui` : liste des chemins vers chaque installation ComfyUI.
  - `models_path` : chemin racine où sont stockés les modèles et LoRAs.
  - `ports` : ports HTTP de chaque instance ComfyUI.

- **`execute_workflow_TtI(...)`** :
  - `workflow_json` : workflow ComfyUI complet.
  - `models` : liste de modèles à vérifier dans `models_path`.
  - `loras` : LoRAs à télécharger / vérifier.
  - `settings_scaled_by_gpu_count` : paramètres divisés par le nombre de GPU.
  - `settings_fixed_per_gpu` : paramètres identiques sur chaque GPU.

### Comment tester rapidement

- **1. Vérifier l’installation** :

```bash
python -c "import comfyapi; print('Ok')"
```

- **2. Lancer un petit script** avec un workflow simple (même machine que ComfyUI).
- **3. Surveiller les logs** : tu verras l’initialisation des GPU, le lancement des instances ComfyUI et la liste des images générées.

Ce README reste volontairement bref : il donne une vue d’ensemble de la librairie, comment l’installer, l’utiliser rapidement, et quels sont les paramètres importants. Tu peux me demander une version plus détaillée ou orientée prod si besoin.


