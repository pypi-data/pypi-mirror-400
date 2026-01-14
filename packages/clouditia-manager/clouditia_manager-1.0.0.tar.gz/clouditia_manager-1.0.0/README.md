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

# Configuration par défaut (production)
manager = GPUManager(api_key="sk_compute_xxxxx")

# Configuration personnalisée (développement local)
manager = GPUManager(
    api_key="sk_compute_xxxxx",
    base_url="http://127.0.0.1:8000/jobs",  # URL de base de l'API
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

### 2. Créer une session GPU

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

### 3. Lister les sessions

```python
# Toutes les sessions
sessions = manager.list_sessions()

# Filtrer par status
running = manager.list_sessions(status="running")
stopped = manager.list_sessions(status="stopped")

for session in sessions:
    print(f"{session.name} ({session.short_id}): {session.status} - {session.gpu_type}")
```

### 4. Obtenir le status d'une session

```python
# Par short ID (8 caractères)
session = manager.get_session("0e4c713a")

print(f"Nom: {session.name}")        # compute-gpu-0e4c713a
print(f"Status: {session.status}")   # running
print(f"GPU: {session.gpu_type}")    # nvidia-rtx-3090
print(f"URL: {session.url}")
```

### 5. Renommer une session

```python
# Chaque session a un nom par défaut: compute-gpu-{short_id}
session = manager.create_session(gpu_type="nvidia-rtx-3090")
print(f"Nom par défaut: {session.name}")  # compute-gpu-0e4c713a

# Renommer la session
session = manager.rename_session("0e4c713a", "mon-projet-ml-v1")
print(f"Nouveau nom: {session.name}")  # mon-projet-ml-v1
```

### 6. Arrêter une session

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

### 7. Consulter l'inventaire GPU

```python
inventory = manager.get_inventory()

for gpu in inventory:
    print(f"{gpu.gpu_name}: {gpu.available}/{gpu.total} disponibles")
    print(f"  Prix: {gpu.price_per_hour}€/h")
```

### 8. Générer une clé SDK (sk_live_)

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

| GPU | Slug |
|-----|------|
| NVIDIA RTX 3060 Ti | `nvidia-rtx-3060ti` |
| NVIDIA RTX 3080 Ti | `nvidia-rtx-3080ti` |
| NVIDIA RTX 3090 | `nvidia-rtx-3090` |
| NVIDIA RTX 4090 | `nvidia-rtx-4090` |

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
| `create_session(gpu_type, gpu_count, vcpu, ram, storage, wait_ready, timeout, verbose)` | Crée une session GPU |
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
| `gpu_type` | str | Type de GPU |
| `gpu_count` | int | Nombre de GPUs |
| `vcpu` | int | Nombre de vCPUs |
| `ram` | str | RAM allouée |
| `storage` | str | Stockage alloué |
| `url` | str | URL d'accès |
| `password` | str | Mot de passe |

## License

MIT License
