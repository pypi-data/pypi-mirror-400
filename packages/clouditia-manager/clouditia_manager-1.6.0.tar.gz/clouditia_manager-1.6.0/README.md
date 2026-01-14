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

# Configuration avec timeout personnalisé
manager = GPUManager(
    api_key="sk_compute_xxxxx",
    base_url="https://clouditia.com/jobs",
    timeout=120  # Timeout en secondes (défaut: 60)
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

### 4. Gestion de la disponibilité GPU (allow_partial)

Le SDK vérifie automatiquement la disponibilité des GPUs demandés avant de créer la session.

```python
# Si certains GPUs ne sont pas disponibles, le SDK affiche:
# ==================================================
#   GPU AVAILABILITY CHECK
# ==================================================
#   Unavailable GPUs:
#     - nvidia-rtx-4090
#   Available GPUs:
#     - nvidia-rtx-3090
# ==================================================
# Continue with 1 available GPU(s)? [y/N]:

# Mode interactif (par défaut): demande confirmation
session = manager.create_session(
    gpus=[
        {'type': 'nvidia-rtx-3090', 'count': 1},
        {'type': 'nvidia-rtx-4090', 'count': 1}
    ],
    vcpu=4,
    ram=16,
    storage=20
)

# Mode automatique: continue avec les GPUs disponibles
session = manager.create_session(
    gpus=[
        {'type': 'nvidia-rtx-3090', 'count': 1},
        {'type': 'nvidia-rtx-4090', 'count': 1}
    ],
    vcpu=4,
    ram=16,
    storage=20,
    allow_partial=True  # Continue avec les GPUs disponibles uniquement
)
```

### 5. Lister les sessions

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

### 8. Consulter les GPUs disponibles

```python
inventory = manager.get_inventory()

if not inventory:
    print("Aucun GPU disponible actuellement")
else:
    for gpu in inventory:
        print(f"{gpu.gpu_name}: {gpu.available} disponible(s)")
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

### 10. Consulter le solde de crédits

```python
# Obtenir le solde de crédits disponible
balance = manager.get_balance()
print(f"Solde: {balance['balance']} {balance['currency']}")
# Output: Solde: 150.50 EUR
```

### 11. Coût et durée d'une session

```python
# Obtenir le coût et la durée d'une session spécifique
cost_info = manager.get_session_cost("0e4c713a")

print(f"Session: {cost_info['name']}")
print(f"Coût actuel: {cost_info['cost']} EUR")
print(f"Taux horaire: {cost_info['hourly_rate']} EUR/h")
print(f"Durée: {cost_info['duration_display']}")
# Output:
# Session: compute-gpu-0e4c713a
# Coût actuel: 2.45 EUR
# Taux horaire: 0.98 EUR/h
# Durée: 2h 30m 15s

# Obtenir uniquement la durée
duration = manager.get_session_duration("0e4c713a")
print(f"Durée: {duration['duration_display']}")
print(f"En heures: {duration['duration_hours']}")
```

### 12. Coût de plusieurs sessions

```python
# Obtenir le coût de plusieurs sessions spécifiques
costs = manager.get_sessions_cost(["0e4c713a", "f0b09214"])

print(f"Nombre de sessions: {costs['session_count']}")
print(f"Coût total: {costs['total_cost']} EUR")
print(f"Durée totale: {costs['total_duration_display']}")

for session in costs['sessions']:
    print(f"  - {session['name']}: {session['cost']} EUR ({session['duration_display']})")
```

### 13. Coût de toutes les sessions actives

```python
# Obtenir le coût de toutes les sessions en cours d'exécution
active_costs = manager.get_active_sessions_cost()

print(f"Sessions actives: {active_costs['session_count']}")
print(f"Coût total: {active_costs['total_cost']} EUR")
print(f"Durée totale: {active_costs['total_duration_display']}")

if active_costs['session_count'] == 0:
    print("Aucune session active")
else:
    for session in active_costs['sessions']:
        print(f"  - {session['name']}: {session['cost']} EUR")
```

### 14. File d'attente (Queue) pour création de session

Si les GPUs ne sont pas disponibles, vous pouvez ajouter votre demande à une file d'attente au lieu de recevoir une erreur.

```python
# Créer une session avec fallback sur la queue si indisponible
result = manager.create_session(
    gpu_type="nvidia-rtx-4090",
    vcpu=4,
    ram=16,
    storage=20,
    queue_if_unavailable=True  # Ajouter à la queue si indisponible
)

# Si la session est créée immédiatement
if isinstance(result, GPUSession):
    print(f"Session créée: {result.name}")
# Si ajouté à la queue
elif isinstance(result, dict) and result.get('queued'):
    print(f"Demande ajoutée à la queue!")
    print(f"Queue ID: {result['queue_id']}")
    print(f"Position: #{result['position']}")

# Output si mis en queue:
# ==================================================
#   REQUEST QUEUED
# ==================================================
#   Queue ID  : a1b2c3d4...
#   Position  : #3
#   Message   : Aucun GPU disponible. Votre demande a été ajoutée à la queue.
#   Unavailable GPUs: nvidia-rtx-4090
# ==================================================
#
# Use manager.get_queue_job('a1b2c3d4') to check status
# Use manager.cancel_queue_job('a1b2c3d4') to cancel
```

### 15. Lister les jobs en queue

```python
# Lister tous vos jobs en queue
queue_jobs = manager.list_queue_jobs()

for job in queue_jobs:
    print(f"Position #{job.position}: {job.status_display}")
    print(f"  GPU Config: {job.gpu_config}")
    print(f"  Tentatives: {job.attempt_count}")
    if job.last_attempt_at:
        print(f"  Dernière tentative: {job.last_attempt_at}")

# Filtrer par status
pending_jobs = manager.list_queue_jobs(status="pending")
completed_jobs = manager.list_queue_jobs(status="completed")
```

### 16. Voir les détails d'un job en queue

```python
# Obtenir les détails d'un job avec l'historique des tentatives
result = manager.get_queue_job("a1b2c3d4", verbose=True)

job = result['job']
attempts = result['attempts']

print(f"Position: #{job.position}")
print(f"Status: {job.status_display}")
print(f"Tentatives: {job.attempt_count}")

# Afficher l'historique des tentatives
for attempt in attempts:
    status = "Succès" if attempt.success else "Échec"
    print(f"  [{status}] {attempt.attempted_at}")
    if attempt.error_message:
        print(f"    Erreur: {attempt.error_message}")
    if attempt.unavailable_gpus:
        print(f"    GPUs indisponibles: {', '.join(attempt.unavailable_gpus)}")
```

### 17. Annuler un job en queue

```python
# Annuler un job en attente
manager.cancel_queue_job("a1b2c3d4")
# Output: Queue job a1b2c3d4... cancelled successfully
```

### 18. Limites automatiques (Auto-stop)

Définissez des limites de coût ou de durée pour arrêter automatiquement une session.

```python
# Limite de coût: auto-stop quand le coût atteint 5 EUR
session = manager.create_session(
    gpu_type="nvidia-rtx-3090",
    vcpu=4,
    ram=16,
    cost_limit=5.0  # Max 5 EUR
)

# Limite de durée: auto-stop après 2 heures (7200 secondes)
session = manager.create_session(
    gpu_type="nvidia-rtx-3090",
    vcpu=4,
    ram=16,
    duration_limit=7200  # Max 2 heures
)

# Les deux limites ensemble: arrêt dès que l'une est atteinte
session = manager.create_session(
    gpu_type="nvidia-rtx-3090",
    vcpu=4,
    ram=16,
    cost_limit=10.0,      # Max 10 EUR
    duration_limit=3600   # OU max 1 heure
)

# Output avec limites:
# ==================================================
#   SESSION READY
# ==================================================
#   Name     : compute-gpu-0e4c713a
#   Short ID : 0e4c713a
#   Status   : running
#   GPU      : nvidia-rtx-3090 x1
#   vCPU     : 4
#   RAM      : 16Gi
#   Storage  : 20Gi
#   ----------------------------------------------
#   AUTO-STOP ENABLED
#   Cost Limit     : 10.0 EUR
#   Duration Limit : 1h 0m (3600s)
#   ----------------------------------------------
#   URL      : https://clouditia.com/code-editor/...
#   Password : xxxxxxxxxxxx
# ==================================================

# Vérifier les limites d'une session
print(f"Auto-stop activé: {session.auto_stop_enabled}")
print(f"Limite coût: {session.cost_limit} EUR")
print(f"Limite durée: {session.duration_limit} secondes")
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
| `create_session(gpu_type, gpu_count, gpus, vcpu, ram, storage, wait_ready, timeout, verbose, allow_partial, queue_if_unavailable)` | Crée une session GPU |
| `stop_session(session_id, wait_stopped, timeout, verbose)` | Arrête une session |
| `get_session(session_id)` | Récupère les détails d'une session |
| `list_sessions(status)` | Liste les sessions (filtre optionnel) |
| `rename_session(session_id, new_name)` | Renomme une session |
| `get_inventory()` | Récupère les GPUs disponibles |
| `generate_sdk_key(session_id, name)` | Génère une clé sk_live_ |
| `get_balance()` | Récupère le solde de crédits |
| `get_session_cost(session_id)` | Récupère le coût et la durée d'une session |
| `get_session_duration(session_id)` | Récupère la durée d'une session |
| `get_sessions_cost(session_ids)` | Récupère le coût de plusieurs sessions |
| `get_active_sessions_cost()` | Récupère le coût de toutes les sessions actives |
| `list_queue_jobs(status)` | Liste les jobs en queue (filtre optionnel) |
| `get_queue_job(queue_id, verbose)` | Récupère les détails d'un job en queue avec historique |
| `cancel_queue_job(queue_id, verbose)` | Annule un job en queue |

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
| `available` | int | Nombre de GPUs disponibles |
| `price_per_hour` | float | Prix par heure (EUR) |

## Attributs QueueJob

| Attribut | Type | Description |
|----------|------|-------------|
| `queue_id` | str | UUID du job en queue |
| `position` | int | Position dans la queue |
| `status` | str | pending, processing, completed, failed, cancelled |
| `status_display` | str | Libellé du status (traduit) |
| `gpu_config` | dict | Configuration GPU demandée |
| `vcpu` | int | Nombre de vCPUs demandés |
| `ram` | int | RAM demandée (GB) |
| `storage` | int | Stockage demandé (GB) |
| `allow_partial` | bool | Autoriser création partielle |
| `attempt_count` | int | Nombre de tentatives |
| `last_attempt_at` | datetime | Date de la dernière tentative |
| `last_error` | str | Dernière erreur rencontrée |
| `created_at` | datetime | Date de création |
| `created_session_id` | str | ID de la session créée (si succès) |

## Attributs QueueAttempt

| Attribut | Type | Description |
|----------|------|-------------|
| `attempt_id` | str | UUID de la tentative |
| `success` | bool | Succès ou échec |
| `error_message` | str | Message d'erreur |
| `available_gpus` | list | GPUs disponibles au moment de la tentative |
| `unavailable_gpus` | list | GPUs indisponibles au moment de la tentative |
| `attempted_at` | datetime | Date et heure de la tentative |

## License

MIT License
