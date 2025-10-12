# Labo 06 – Orchestrateur Saga et Distributed Tracing

<img src="https://upload.wikimedia.org/wikipedia/commons/2/2a/Ets_quebec_logo.png" width="250">    
ÉTS - LOG430 - Architecture logicielle - Chargé de laboratoire: Gabriel C. Ullmann, Automne 2025.

## 🎯 Objectifs d'apprentissage
- Comprendre le fonctionnement d'un orchestrateur Saga pour coordonner des transactions distribuées
- Comprendre le patron Saga et son rôle dans les architectures distribuées
- Analyser les interactions entre services dans un écosystème de microservices complexe
- Utiliser le distributed tracing avec Jaeger pour observer et déboguer les transactions distribuées

## 📖 Contexte

Dans ce laboratoire, nous allons implémenter un orchestrateur Saga qui coordonne les transactions distribuées entre les services `store_manager` et `payment_api`. Contrairement aux laboratoires précédents où les services communiquaient directement entre eux, l'orchestrateur Saga centralise la logique de coordination et gère les transactions complexes impliquant plusieurs services.

Pour en savoir plus sur l'architecture et les décisions de conception, veuillez consulter le document d'architecture dans `/docs/arc42/docs.md`.

## ⚙️ Setup

### Prérequis
- Avoir complété le Labo 05
- Avoir les dépôts `log430-a25-labo5` et `log430-a25-labo5-paiement` fonctionnels

### 1. Clonez le dépôt
Créez votre propre dépôt à partir du dépôt gabarit (template). Vous pouvez modifier la visibilité pour le rendre privé si vous voulez.
```bash
git clone https://github.com/[votredepot]/log430-a25-labo6
cd log430-a25-labo6
```

### 2. Créez un fichier .env
Créez un fichier `.env` basé sur `.env.example`. Dans le fichier `.env`, utilisez les mêmes identifiants que ceux mentionnés dans `docker-compose.yml`. Veuillez suivre la même approche que pour les derniers laboratoires.

### 3. Vérifiez le réseau Docker
Le réseau `labo05-network` créé lors du Labo 05 sera réutilisé parce que nous allons intégrer l'orchestrateur avec le Store Manager. Si vous ne l'avez pas encore créé, exécutez :
```bash
docker network create labo05-network
```

### 4. Préparez l'environnement de développement
Démarrez les conteneurs de TOUS les services. Suivez les mêmes étapes que pour les derniers laboratoires.
```bash
docker compose build
docker compose up -d
```

### 5. Préparez l'environnement de déploiement et le pipeline CI/CD
Utilisez les mêmes approches qui ont été abordées lors des derniers laboratoires.

## 🧪 Activités pratiques

### 1. Analyse du patron Saga
Lisez attentivement le document d'architecture dans `/docs/arc42/docs.md` et examinez l'implémentation déjà présente dans trois fichiers: `src/commands/create_order_command.py`, `src/controllers/order_saga_controller.py` et `src/saga_orchestrator.py`.

> 💡 **Question 1** : Lequel de ces fichiers Python représente la logique de la machine à états décrite dans les diagrammes dans `/docs/arc42/docs.md`? Est-ce que son implémentation est complète ou y a-t-il des éléments qui manquent? Illustrez votre réponse avec des extraits de code.

> 💡 **Question 2** : Lequel de ces fichiers Python déclenche la création ou suppression des commandes? Est-ce qu'il accède à une base de données directement pour le faire? Illustrez votre réponse avec des extraits de code.

> 💡 **Question 3** : Quelle requête dans la collection Postman du Labo 05 correspond à l'endpoint appelé dans `create_order_command.py`? Illustrez votre réponse avec des captures d'écran ou extraits de code.

### 2. Implémentation de la gestion de stock

La première étape (création de la commande) étant déjà implémentée, votre tâche consiste à implémenter les deux étapes suivantes de la saga. Complétez l'implémentation dans `src/commands/decrease_stock_command.py` en vous inspirant de `create_order_command.py`. Voici quelques considérations importantes :
- Les commentaires `TODO` disséminés dans le code vous guideront vers les modifications nécessaires.
- Vous devrez appeler l'endpoint de gestion de stock du service Store Manager **via l'API Gateway (KrakenD)**. 
- Si vous ne connaissez pas l'endpoint exact ou la méthode HTTP à utiliser (POST, GET, etc.), consultez **la collection Postman du Store Manager** pour identifier les bonnes informations. La collection est justement là pour documenter les endpoints et permettre un test rapide.
- Pour tester l'ensemble de la saga, utilisez la **collection Postman de l'Orchestrateur** en appelant l'endpoint `/saga/order`. 
- En cas d'erreurs 500 avec des messages peu explicites, ajoutez des loggers dans les méthodes suspectes. Consultez la section « Astuces de débogage » pour plus de détails sur cette approche.
- N'oubliez pas d'implémenter les deux méthodes: `run()` et `rollback()`. **Chacune de nos actions doit être réversible, et déclencher la compensation des actions précédentes**.

> 💡 **Question 4** : Quel endpoint avez-vous appelé pour modifier le stock? Quelles informations de la commande avez-vous utilisées? Illustrez votre réponse avec des extraits de code.

### 3. Implémentation de la création de paiement

Complétez l'implémentation dans `src/commands/create_payment_command.py` en vous basant sur `create_order_command.py` et `decrease_stock_command.py`. Suivez la même logique que pour l'activité précédente.

> 💡 **Question 5** : Quel endpoint avez-vous appelé pour générer une transaction de paiement? Quelles informations de la commande avez-vous utilisées? Illustrez votre réponse avec des extraits de code.

### 4. Intégration de Jaeger pour le distributed tracing
Ajoutez Jaeger à votre `docker-compose.yml` pour permettre le tracing distribué de vos transactions Saga.

```yaml
  jaeger:
    image: jaegertracing/all-in-one:latest
    container_name: jaeger
    ports:
      - "16686:16686"  # Interface web Jaeger
      - "14268:14268"  # Jaeger collector
      - "6831:6831/udp"  # Jaeger agent
    environment:
      - COLLECTOR_ZIPKIN_HOST_PORT=:9411
    networks:
      - labo05-network
```

Ensuite, configurez votre application pour envoyer les traces à Jaeger. Dans votre code Python, vous devrez :
1. Installer les dépendances nécessaires (`opentelemetry` packages)
2. Configurer l'exportateur de traces vers Jaeger
3. Instrumenter vos commands avec des spans

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
2. Tentez de créer une commande via l'orchestrateur Saga
3. Observez le comportement dans les logs (via Docker Desktop) et dans Jaeger

## 🔍 Astuces de débogage

- **Ajoutez des loggers** : Lorsqu'une erreur n'est pas claire, ajoutez des `print()` ou `logger.info()` dans votre code
- **Déboguez en profondeur** : Si un logger dans un module ne vous aide pas, descendez plus profondément dans le code, dans les fonctions internes. Si ça n'aide pas, remontez dans la call stack (ex. vérifiez la méthode qui appelle votre méthode).
- **Utilisez Postman** : Postman nous permet de vérifier chaque endpoint de manière individuelle et rapide, sans écrire aucun code
- **Utilisez Jaeger** : Utilisez l'interface Jaeger pour visualiser où exactement une transaction échoue

## 📦 Livrables

- Un fichier .zip contenant l'intégralité du code source du projet Labo 06
- Un rapport en .pdf répondant à toutes les questions présentées dans ce document. Il est **obligatoire** d'illustrer vos réponses avec du code et des captures d'écran