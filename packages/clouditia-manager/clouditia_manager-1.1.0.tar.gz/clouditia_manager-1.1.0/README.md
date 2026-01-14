# Clouditia Manager SDK

SDK Python pour gérer les sessions GPU sur la plateforme Clouditia via l'API Computing (`sk_compute_`).

## Installation

```bash
pip install clouditia-manager
```

## Quick Start

```python
from clouditia_manager import GPUManager

# Initialiser avec votre clé API sk_compute_
manager = GPUManager(api_key="sk_compute_xxxxx")

# Créer une session GPU
# Le SDK attend automatiquement que la session soit prête
session = manager.create_session(
    gpu_type="nvidia-rtx-3090",
    vcpu=2,
    ram=4,
    storage=20
)

# Output:
# Creating GPU session with nvidia-rtx-3090...
# Session created: 0e4c713a
# Waiting for session 0e4c713a to be ready... Ready!
#
# ==================================================
#   SESSION READY
# ==================================================
#   Name     : compute-gpu-0e4c713a
#   Short ID : 0e4c713a
#   Status   : running
#   GPU      : nvidia-rtx-3090 x1
#   vCPU     : 2
#   RAM      : 4Gi
#   Storage  : 20Gi
#   URL      : https://clouditia.com/code-editor/...
#   Password : xxxxxxxxxxxx
# ==================================================

print(f"Session prête: {session.name}")
```

## Configuration

```python
from clouditia_manager import GPUManager

# Configuration par défaut (URL: https://clouditia.com/jobs)
manager = GPUManager(api_key="sk_compute_xxxxx")

# Configuration personnalisée (développement local)
manager = GPUManager(
    api_key="sk_compute_xxxxx",
    base_url="http://127.0.0.1:8000/jobs",  # URL locale pour dev
    timeout=120  # Timeout en secondes
)
```

## Fonctionnalités

### 1. Vérifier la clé API

La vérification est automatique à l'initialisation :

```python
manager = GPUManager(api_key="sk_compute_xxxxx")
print(f"Utilisateur: {manager.user['username']}")
print(f"Email: {manager.user['email']}")
```

### 2. Créer une session GPU (Single GPU)

```python
# Création standard (attend automatiquement que la session soit prête)
session = manager.create_session(
    gpu_type="nvidia-rtx-3090",  # Type de GPU
    gpu_count=1,                  # Nombre de GPUs
    vcpu=4,                       # Nombre de vCPUs
    ram=16,                       # RAM en GB
    storage=20                    # Stockage en GB
)

# La session est prête avec un nom automatique: compute-gpu-{short_id}
print(f"Nom: {session.name}")        # compute-gpu-0e4c713a
print(f"ID: {session.short_id}")     # 0e4c713a
print(f"Status: {session.status}")   # running
print(f"URL: {session.url}")
print(f"Password: {session.password}")

# Options avancées
session = manager.create_session(
    gpu_type="nvidia-rtx-3090",
    wait_ready=True,     # Attendre que la session soit prête (défaut: True)
    timeout=180,         # Timeout en secondes (défaut: 180)
    verbose=True         # Afficher les messages de status (défaut: True)
)

# Mode silencieux (sans attente ni messages)
session = manager.create_session(
    gpu_type="nvidia-rtx-3090",
    wait_ready=False,    # Ne pas attendre
    verbose=False        # Pas de messages
)
```

### 3. Créer une session Multi-GPU (plusieurs types de GPU)

```python
# Créer une session avec plusieurs GPUs de types différents
session = manager.create_session(
    gpus=[
        {'type': 'nvidia-rtx-3090', 'count': 1},
        {'type': 'nvidia-rtx-3060ti', 'count': 1}
    ],
    vcpu=4,
    ram=16,
    storage=20
)

# Output:
# Creating GPU session with 1x nvidia-rtx-3090, 1x nvidia-rtx-3060ti...
# Session created: f0b09214
# Waiting for session f0b09214 to be ready... Ready!
#
# ==================================================
#   SESSION READY
# ==================================================
#   Name     : compute-gpu-f0b09214
#   Short ID : f0b09214
#   Status   : running
#   GPUs     : 2 total
#            - nvidia-rtx-3090 x1
#            - nvidia-rtx-3060ti x1
#   vCPU     : 4
#   RAM      : 16Gi
#   Storage  : 20Gi
#   URL      : https://clouditia.com/code-editor/...
#   Password : xxxxxxxxxxxx
# ==================================================

print(f"GPU Count: {session.gpu_count}")  # 2
print(f"GPUs: {session.gpus}")            # Liste des configs GPU
```

### 4. Lister les sessions

```python
# Toutes les sessions
sessions = manager.list_sessions()

# Filtrer par status
running = manager.list_sessions(status="running")
stopped = manager.list_sessions(status="stopped")

for session in sessions:
    print(f"{session.name} ({session.short_id}): {session.status} - {session.gpu_type}")
```

### 5. Obtenir le status d'une session

```python
# Par short ID (8 caractères)
session = manager.get_session("0e4c713a")

print(f"Nom: {session.name}")        # compute-gpu-0e4c713a
print(f"Status: {session.status}")   # running
print(f"GPU: {session.gpu_type}")    # nvidia-rtx-3090
print(f"GPUs: {session.gpus}")       # Liste des GPUs (pour multi-GPU)
print(f"URL: {session.url}")
```

### 6. Renommer une session

```python
# Chaque session a un nom par défaut: compute-gpu-{short_id}
session = manager.create_session(gpu_type="nvidia-rtx-3090")
print(f"Nom par défaut: {session.name}")  # compute-gpu-0e4c713a

# Renommer la session
session = manager.rename_session("0e4c713a", "mon-projet-ml-v1")
print(f"Nouveau nom: {session.name}")  # mon-projet-ml-v1
```

### 7. Arrêter une session

```python
# Arrêt standard (attend automatiquement la suppression du pod)
session = manager.stop_session("0e4c713a")

# Output:
# Stopping session 0e4c713a...
# Waiting for pod termination... Done!
#
# ==================================================
#   SESSION STOPPED
# ==================================================
#   Name     : mon-projet-ml-v1
#   Short ID : 0e4c713a
#   Status   : stopped
#   GPU      : nvidia-rtx-3090 (released)
# ==================================================

print(f"Session arrêtée: {session.name}")
print(f"Status: {session.status}")

# Options avancées
session = manager.stop_session(
    "0e4c713a",
    wait_stopped=True,   # Attendre la suppression complète (défaut: True)
    timeout=120,         # Timeout en secondes (défaut: 120)
    verbose=True         # Afficher les messages (défaut: True)
)

# Mode silencieux
session = manager.stop_session("0e4c713a", wait_stopped=False, verbose=False)
```

### 8. Consulter l'inventaire GPU

```python
inventory = manager.get_inventory()

for gpu in inventory:
    print(f"{gpu.gpu_name}: {gpu.available}/{gpu.total} disponibles")
    print(f"  Prix: {gpu.price_per_hour}EUR/h")
```

### 9. Générer une clé SDK (sk_live_)

```python
# Générer une clé pour utiliser le SDK clouditia
sdk_key = manager.generate_sdk_key("0e4c713a", name="Ma clé SDK")
print(f"Clé SDK: {sdk_key}")  # sk_live_xxxxx...

# Utiliser avec le SDK clouditia
from clouditia import GPUSession
gpu = GPUSession(api_key=sdk_key)
result = gpu.run("print('Hello GPU!')")
```

## Types de GPU disponibles

| GPU | Slug | Prix/h |
|-----|------|--------|
| NVIDIA RTX 3060 Ti | `nvidia-rtx-3060ti` | 0.50 EUR |
| NVIDIA RTX 3080 Ti | `nvidia-rtx-3080ti` | 0.90 EUR |
| NVIDIA RTX 3090 | `nvidia-rtx-3090` | 1.00 EUR |
| NVIDIA RTX 4090 | `nvidia-rtx-4090` | 1.50 EUR |

## Gestion des erreurs

```python
from clouditia_manager import (
    GPUManager,
    AuthenticationError,
    SessionNotFoundError,
    InsufficientResourcesError,
    APIError
)

try:
    manager = GPUManager(api_key="sk_compute_xxxxx")
    session = manager.create_session(gpu_type="nvidia-rtx-4090")
except AuthenticationError:
    print("Clé API invalide")
except InsufficientResourcesError:
    print("Aucun GPU disponible")
except SessionNotFoundError:
    print("Session non trouvée")
except APIError as e:
    print(f"Erreur API: {e}")
```

## Référence API

| Méthode | Description |
|---------|-------------|
| `GPUManager(api_key, base_url, timeout)` | Initialise le SDK |
| `create_session(gpu_type, gpu_count, gpus, vcpu, ram, storage, wait_ready, timeout, verbose)` | Crée une session GPU |
| `stop_session(session_id, wait_stopped, timeout, verbose)` | Arrête une session |
| `get_session(session_id)` | Récupère les détails d'une session |
| `list_sessions(status)` | Liste les sessions (filtre optionnel) |
| `rename_session(session_id, new_name)` | Renomme une session |
| `get_inventory()` | Récupère l'inventaire GPU |
| `generate_sdk_key(session_id, name)` | Génère une clé sk_live_ |

## Attributs GPUSession

| Attribut | Type | Description |
|----------|------|-------------|
| `id` | str | UUID complet de la session |
| `short_id` | str | ID court (8 caractères) |
| `name` | str | Nom de la session |
| `status` | str | running, stopped, pending, failed |
| `gpu_type` | str | Type(s) de GPU (séparés par virgule si multi-GPU) |
| `gpu_count` | int | Nombre total de GPUs |
| `gpus` | list | Liste des configurations GPU (pour multi-GPU) |
| `vcpu` | int | Nombre de vCPUs |
| `ram` | str | RAM allouée |
| `storage` | str | Stockage alloué |
| `url` | str | URL d'accès |
| `password` | str | Mot de passe |

## Attributs GPUInventory

| Attribut | Type | Description |
|----------|------|-------------|
| `gpu_type` | str | Slug du GPU |
| `gpu_name` | str | Nom complet du GPU |
| `total` | int | Stock total |
| `available` | int | Stock disponible |
| `in_use` | int | Stock en utilisation |
| `price_per_hour` | float | Prix par heure (EUR) |

## License

MIT License
