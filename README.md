
# Secure Distributed Dico

Ce projet implémente un protocole client-serveur personnalisé en Python, permettant de manipuler des dictionnaires de données distants de manière sécurisée. Il repose sur une architecture TCP chiffrée (SSL/TLS), un multiplexage des connexions et une hiérarchie de serveurs (délégation vers un serveur maître).

## Fonctionnalités Principales

* **Protocole personnalisé** : Communication par requêtes/réponses textuelles (encodage UTF-8) avec gestion standardisée des codes de retour (`OK` / `ERR`).
* **Sécurité SSL/TLS** : L'intégralité des échanges entre les clients, l'administrateur et les serveurs est chiffrée.
* **Architecture Distribuée** : Si un serveur ne possède pas le dictionnaire demandé, il délègue automatiquement la requête à un serveur maître.
* **Accès Administrateur** : Authentification par vérification d'empreinte SHA-256 permettant les opérations de modification et de suppression.
* **Multiplexage** : Le serveur utilise `select` pour gérer de multiples connexions TCP simultanées sans bloquer le processus principal.

## Configuration et Prérequis

Avant de lancer les serveurs et les clients, l'environnement de sécurité doit être initialisé (certificats TLS et mot de passe administrateur).


### 1. Génération des certificats SSL/TLS

Le projet repose sur une véritable architecture PKI (Public Key Infrastructure). Il est nécessaire de créer une Autorité de Certification (CA) locale, de générer une demande de signature pour le serveur (CSR), puis de signer le certificat final du serveur.

Exécutez la séquence de commandes suivante depuis la racine du projet :

```bash
mkdir tls
cd tls

# 1. Générer une clé et un certificat CA (Autorité de Certification) :
openssl genrsa -out ca.key 4096
openssl req -new -x509 -days 365 -key ca.key -out ca.pem

# 2. Générer la clé du serveur et la demande de signature (CSR) :
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr

# 3. Générer le certificat du serveur signé par le CA :
openssl x509 -req -in server.csr -CA ca.pem -CAkey ca.key -CAcreateserial -out server.pem -days 365

cd ..
```

### 2. Configuration du mot de passe Administrateur

Le serveur vérifie l'identité de l'administrateur en comparant le hash de sa saisie avec un hash stocké localement. Pour configurer le mot de passe `adminMDP2025` :

```bash
mkdir mdp
python3 -c "import hashlib; print(hashlib.sha256(b'adminMDP2025').hexdigest())" > mdp/mdp_admin.txt

```

## Utilisation

Les fichiers de données (au format JSON) doivent être placés dans un répertoire `data/` à la racine de l'exécution du serveur.

### 1. Lancement de l'infrastructure

Il est recommandé de lancer le serveur maître avant les serveurs noeuds.

**Serveur Maître :**

```bash
cd master
./master.py 8888

```

**Serveur Local :**
Le serveur se connecte au maître sur `localhost:8888` et écoute les requêtes clientes sur le port `7777`.

```bash
./dico_server.py localhost:8888 7777

```

### 2. Requêtes Client (Lecture seule)

Le script client permet d'effectuer des requêtes ponctuelles et se ferme immédiatement après la réponse du serveur.

```bash
# Récupération d'une valeur exacte
./dico_client.py localhost 7777 mois_duree.json get "janvier"

# Recherche par préfixe
./dico_client.py localhost 7777 mois_duree.json pref "j"

# Requêtes sur un dictionnaire différent
./dico_client.py localhost 7777 punchlines.json get "Mike Tyson"
./dico_client.py localhost 7777 punchlines.json pref "J"

```

### 3. Session Administrateur (Lecture et Écriture)

L'administrateur s'authentifie lors du lancement du script, puis accède à un shell interactif lui permettant d'enchaîner les commandes (ajout, modification, suppression) sans refermer la socket.

**Connexion :**

```bash
./dico_admin.py localhost 7777 login "adminMDP2025"

```

**Exemple de session interactive (`===>` représente l'invite de commande) :**

```text
===> mois_duree.json get "février"
===> mois_duree.json pref "d"
===> punchlines.json pref "J"
===> mois_duree.json set "février" "30"
===> mois_duree.json get "février"
===> mois_duree.json del "janvier"
===> mois_duree.json set "janvier" "31"
===> exit

```

## Documentation

Pour une description détaillée de la syntaxe des messages, des codes d'erreurs et des règles de communication, veuillez vous référer au fichier `protocol_dico.md`.

```

---

**Points vérifiés lors de l'analyse de votre code :**
* Le script `dico_admin.py` boucle bien sur un `input("===> ")` après la connexion initiale, ce qui justifie la présentation sous forme de session interactive.
* La gestion des quotes (`"..."`) est correctement traitée côté serveur grâce à `shlex.split`, ce qui rend vos exemples de commandes parfaitement fonctionnels.
* Les chemins relatifs vers `./tls/ca.pem` et `./data/` sont stricts dans votre code, les instructions de configuration reflètent donc exactement cette structure de dossiers.

```