# Labo 06 – Orchestrateur Saga et Distributed Tracing

<img src="https://upload.wikimedia.org/wikipedia/commons/2/2a/Ets_quebec_logo.png" width="250">    
ÉTS - LOG430 - Architecture logicielle - Chargé de laboratoire: Gabriel C. Ullmann, Automne 2025.

## 🎯 Objectifs d'apprentissage
- Comprendre le patron Saga et son rôle dans les architectures distribuées
- Comprendre le fonctionnement d'un orchestrateur Saga pour coordonner des transactions distribuées
- Analyser les interactions entre services dans un écosystème de microservices complexe
- Utiliser le distributed tracing avec Jaeger pour observer et déboguer les transactions distribuées

## ⚙️ Setup
Notre magasin a connu une croissance importante, et avec l'augmentation du volume de commandes, nous avons constaté une hausse proportionnelle du nombre d'erreurs. Lorsque le store_manager ou l'API de paiement sont indisponibles ou dysfonctionnels durant l'ajout ou la modification d'une commande, celle-ci peut se retrouver dans un état incohérent (par exemple, la commande est créée sans transaction de paiement associée, ou inversement). Pour résoudre ce type de problème, nous pouvons implémenter le patron Saga orchestré.

Dans ce laboratoire, nous allons implémenter un orchestrateur Saga (`saga_orchestrator`) qui coordonne les transactions distribuées entre les services `store_manager` et `payment_api`. Contrairement aux laboratoires précédents où les services communiquaient directement entre eux, l'orchestrateur Saga centralise la logique de coordination et gère les transactions complexes impliquant plusieurs services.

Pour en savoir plus sur l'architecture et les décisions de conception, veuillez consulter le document d'architecture dans `/docs/arc42/docs.md`.

### Prérequis
- Avoir les dépôts `log430-a25-labo5` et `log430-a25-labo5-paiement` dans votre ordinateur

### 1. Changez de branche du labo 05
Dans le labo 06, nous allons utiliser une version légèrement modifiée du labo 5 qui apporte quelques modifications dans le code et dans la configuration de KrakenD. Dans les dépôts `log430-a25-labo5` et `log430-a25-labo5-paiement`, changez à la branche `feature/labo06`. Pour changer de branche en utilisant votre terminal, vous pouvez exécuter `git checkout nom_du_branch` dans le répertoire de chaque dépôt.

### 2. Clonez le dépôt du labo 06
Créez votre propre dépôt à partir du dépôt gabarit (template). Vous pouvez modifier la visibilité pour le rendre privé si vous voulez.
```bash
git clone https://github.com/[votredepot]/log430-a25-labo6
cd log430-a25-labo6
```

Ensuite, veuillez faire les étapes de setup suivantes pour **tous les dépôts**.

### 3. Créez un fichier .env
Créez un fichier `.env` basé sur `.env.example`. Dans ce labo, nous n'avons pas d'informations d'authentification de base de données dans le fichier `.env`, alors il n'y a rien à cacher. Vous pouvez utiliser les mêmes paramètres du fichier `.env.example` dans le `.env`, et modifier selon le besoin.

### 4. Vérifiez le réseau Docker
Le réseau `labo05-network` créé lors du Labo 05 sera réutilisé parce que nous allons intégrer l'orchestrateur avec le Store Manager. Si vous ne l'avez pas encore créé, exécutez :
```bash
docker network create labo05-network
```

### 5. Préparez l'environnement de développement
Démarrez les conteneurs de TOUS les services. Importez la collection Postman dans `docs/collections`. Suivez les mêmes étapes que pour les derniers laboratoires.
```bash
docker compose build
docker compose up -d
```

## 🧪 Activités pratiques

> ⚠️ ATTENTION : même si nous utiliserons les fonctionnalités des dépôts `log430-a25-labo5` et `log430-a25-labo5-paiement`, nous n'écrirons du nouveau code que dans celui-ci (`labo6-saga-orchestrator`). Alors, les noms de fichiers dans les activités font toujours réference à ce dépôt.

### 1. Analyse du patron Saga
Lisez attentivement le document d'architecture dans `/docs/arc42/docs.md` et examinez l'implémentation déjà présente dans trois fichiers: `src/handlers/create_order_handler.py`, `src/controllers/order_saga_controller.py` et `src/saga_orchestrator.py`.

> 💡 **Question 1** : Lequel de ces fichiers Python représente la logique de la machine à états décrite dans les diagrammes du document arc42? Est-ce que son implémentation est complète ou y a-t-il des éléments qui manquent? Illustrez votre réponse avec des extraits de code.

> 💡 **Question 2** : Lequel de ces fichiers Python déclenche la création ou suppression des commandes? Est-ce qu'il accède à une base de données directement pour le faire? Illustrez votre réponse avec des extraits de code.

> 💡 **Question 3** : Quelle requête dans la collection Postman du Labo 05 correspond à l'endpoint appelé dans `create_order_handler.py`? Illustrez votre réponse avec des captures d'écran ou extraits de code.

### 2. Implémentation de la gestion de stock

La première étape (création de la commande) étant déjà implémentée, votre tâche consiste à implémenter les deux étapes suivantes de la saga. Complétez l'implémentation dans `src/handlers/decrease_stock_handler.py` en vous inspirant de `create_order_handler.py`. Voici quelques considérations importantes :
- Les commentaires `TODO` disséminés dans le code vous guideront vers les modifications nécessaires. Si vous utilisez VS Code, cliquez sur l'icône en forme de loupe ou appuyez sur CTRL + SHIFT + F pour effectuer une recherche dans l'ensemble du projet.
- Vous devrez appeler l'endpoint de gestion de stock du service Store Manager **via l'API Gateway (KrakenD)**. 
- Si vous ne connaissez pas l'endpoint exact ou la méthode HTTP à utiliser (POST, GET, etc.), consultez **la collection Postman du Store Manager** pour identifier les bonnes informations. La collection est justement là pour documenter les endpoints et permettre un test rapide.
- Pour tester l'ensemble de la saga, utilisez la **collection Postman de l'Orchestrateur (pas la collection du Store Manager)** en appelant l'endpoint `/saga/order`. 
- En cas d'erreurs 500 avec des messages peu explicites, ajoutez des loggers dans les méthodes suspectes. Consultez la section « Astuces de débogage » pour plus de détails sur cette approche.
- N'oubliez pas d'implémenter les deux méthodes: `run()` et `rollback()`. **Chacune de nos actions doit être réversible, et déclencher la compensation des actions précédentes**.

> 💡 **Question 4** : Quel endpoint avez-vous appelé pour modifier le stock? Quelles informations de la commande avez-vous utilisées? Illustrez votre réponse avec des extraits de code.

### 3. Implémentation de la création de paiement

Complétez l'implémentation dans `src/handlers/create_payment_handler.py` en vous basant sur `create_order_handler.py` et `decrease_stock_handler.py`. Suivez la même logique que pour l'activité précédente.

> 💡 **Question 5** : Quel endpoint avez-vous appelé pour générer une transaction de paiement? Quelles informations de la commande avez-vous utilisées? Illustrez votre réponse avec des extraits de code.

### 4. Intégration de Jaeger pour le distributed tracing
Ajoutez Jaeger à votre `docker-compose.yml` pour permettre le tracing distribué de vos transactions Saga.

```yaml
  jaeger:
    image: jaegertracing/all-in-one:latest
    container_name: jaeger
    ports:
      - "16686:16686"      # Jaeger UI
      - "14268:14268"      # Jaeger collector HTTP
      - "14250:14250"      # Jaeger collector gRPC (legacy)
      - "4317:4317"        # OTLP gRPC receiver
      - "4318:4318"        # OTLP HTTP receiver
      - "6831:6831/udp"    # Jaeger agent (legacy)
    environment:
      - COLLECTOR_ZIPKIN_HOST_PORT=:9411
      - COLLECTOR_OTLP_ENABLED=true
    networks:
      - labo05-network
```

Ensuite, configurez **tous vos microservices** pour envoyer les traces à Jaeger. Dans votre code Python, vous devrez :
#### 4.1. Ajoutez les dépendances nécessaires à votre requirements.txt
```txt
opentelemetry-api
opentelemetry-sdk
opentelemetry-exporter-otlp-proto-grpc
opentelemetry-instrumentation-flask
opentelemetry-instrumentation-requests
```

#### 4.2 Configurer l'exportateur de traces vers Jaeger
```python
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

app = Flask(__name__)

# TODO: Indiquez un nom pertinent à votre service
resource = Resource.create({
   "service.name": "nom-de-votre-service",
   "service.version": "1.0.0"
})

trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

# Indiquez l'endpoint Jaeger (hostname dans Docker)
otlp_exporter = OTLPSpanExporter(
   endpoint="http://jaeger:4317",
   insecure=True
)
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)


# Automatic Flask instrumentation
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

# Ensuite, le code pour vos endpoints Flask, etc...
``` 

#### 4.3. Modifiez votre configuration KrakenD pour reconnaître la spécification OpenTelemetry (utilisé par Jaeger)
```yml
 "port": 8080,
 "extra_config": {
   "telemetry/opentelemetry": {
     "service_name": "krakend-gateway",
     "service_version": "1.0.0",
     "exporters": {
       "otlp": [
         {
           "name": "jaeger",
           "host": "jaeger",
           "port": 4317,
           "use_http": false
         }
       ]
     }
   }
 }
```

#### 4.4. Modifiez chacun de vos endpoints KrakenD pour laisser passer les traces à Jaeger dans les headers HTTP
Par exemple:
```yml
    {
      "endpoint": "/store-manager-api/orders",
      "method": "POST",
      "input_headers": ["*"], # ajoutez cette ligne à chacun des endpoints pertinents
    }
```

#### 4.5. Instrumenter vos endpoints avec des [spans](https://logit.io/docs/application-performance-monitoring/jaeger/span-types/#python-example)

```python
with tracer.start_as_current_span("nom-de-votre-endpoint"):
	# some code ...
  return {'data': 'les-donées-que-vous-voulez-returner'}
```

Par example, vous pour tracer le début de la saga, vous pouvez ajouter l'objet `tracer` à l'endpoint `POST /saga/order` dans l'orchestrateur et, ensuite, dans l'endpoint `POST /orders` du Store Manager. N'oubliez pas de faire le setup à Jaeger dans **chaque** application oú vous voulez utiliser Jaeger.

**Reconstruisez et redémarrez** tous les conteneurs Docker.

Accédez à l'interface Jaeger à `http://localhost:16686` et observez les traces de vos transactions distribuées.

### 5. Test de la transaction Saga complète
Utilisez Postman pour tester votre orchestrateur Saga :
1. Importez la nouvelle collection Postman disponible dans `docs/collections`
2. Créez une transaction complète via l'orchestrateur Saga
3. En utilisant Postman, vérifiez dans chaque service (Store Manager et Payment API) que les données ont été correctement créées
4. Observez la trace complète dans Jaeger

> 💡 **Question 6** : Quelle est la différence entre appeler l'orchestrateur Saga et appeler directement les endpoints des services individuels? Quels sont les avantages et inconvénients de chaque approche? Illustrez votre réponse avec des captures d'écran ou extraits de code.

### 6. Gestion des échecs et compensation
Testez le comportement de votre orchestrateur Saga en cas d'échec :
1. Arrêtez le service Payment API
2. Essayez de créer une commande via l'orchestrateur Saga
3. Observez le comportement dans les logs (via Docker Desktop) et dans Jaeger

## 🔍 Astuces de débogage

- **Ajoutez des loggers** : Lorsqu'une erreur n'est pas claire, ajoutez `logger.debug()` dans votre code
- **Déboguez en profondeur** : Si un logger dans un module ne vous aide pas, descendez plus profondément dans le code, dans les fonctions internes. Si ça n'aide pas, remontez dans la call stack (ex. vérifiez la méthode qui appelle votre méthode, et ainsi de suite).
- **Utilisez Postman** : Postman nous permet de vérifier chaque endpoint de manière individuelle et rapide, sans écrire aucun code. N'oubliez pas de faire les requêtes seulement à `localhost` à partir de Postman, parce qu'il est hors Docker (il ne connaît pas les hostnames). 
- **Utilisez Jaeger** : Utilisez l'interface Jaeger pour visualiser où exactement une transaction échoue.

## 📦 Livrables

- Un fichier .zip contenant l'intégralité du code source du projet Labo 06
- Un rapport en .pdf répondant à toutes les questions présentées dans ce document. Il est **obligatoire** d'illustrer vos réponses avec du code et des captures d'écran
