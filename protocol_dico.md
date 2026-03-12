# Projet

## But

- L’objectif du protocole est de permettre à un client de manipuler un dictionnaire a distance hébergé dans un serveur.
- Il permet aux clients normaux de récupérer une valeur du dictionnaire avec une clé et pour les administrateur de récupérer, modifier, d’ajouter et supprimer des valeur du  dictionnaire.
- Il peut y avoir plusieurs clients et le protocoles est base de requêtes réponses.

## Communication

### client-serveur:

- C’est le client qui initie la connexion TCP.
- Il envoie une requête, le serveur répond et ferme la connexion.

### administrateur-serveur:

- L’administrateur initie la connexion TCP.
- il envoie une requête de connexion avec un mot de passe.
- Après authentification, il envoie les requêtes qu’il veut, le serveur répond et c’est à l’administrateur de fermer la connexion.

### serveur-serveur :
- après la communication client-serveur ou administrateur-serveur si le client fait une commande get ou pref et que le serveur n'as pas la réponse il renvoie la requête au serveur maitre.
- Le protocole entre le serveur et le serveur maitre marche de la même manière que client-serveur.

## Format

- texte.
- **Encodage :** `utf-8` .
- Chaque message(requête ou réponse) se termine par un retour à la ligne `\n`.
- La clé ou valeur sont entre guillemets(“ ”).
- Les clés ou valeur peuvent avoir des guillement mais doivent être préceder d'un `\` comme dans le shell exemple: `"Mike \"Tyson\""` 
- Ils peuvent aussi avoir des retour à la lignes vu qu'il sont toujours dans des guillemets.


## Commandes

La seul commande disponible pour les clients normaux est :

- `get` :  suivie d’une clé permet d’obtenir sa valeur.
- `pref` : suivie d'un préfixe permet d'obtenir une liste contenant les clés qui ont ce préfixe et leur valeurs.

Pour les administrateurs `get` et `pref` mais aussi:

- `login` : suivie d’un mot de passe permet de se connecter en tant qu’admin.
- `set` : suivie d’une clé et d’une valeur permet de modifier la valeur de la clé si celle-ci existe et sinon de l’ajouter au dictionnaire.
- `del` : permet de supprimer une clé.
- `exit` : quand l’admin compte quitter, elle permet de fermer la connexion.

## Structure

### Requête Client:

La requête est de la forme suivantes pour la commandes `set` :

`<dictionnaire> <commandes> "<clé>" "<valeur>"` .

- `<dictionnaire>`: le serveur pourrait héberger plusieurs dictionnaires donc ce champ est obligatoire pour toutes les commandes sauf pour la commande `login`.
- `<commandes>` : il existe plusieurs commandes donc il faut spécifier cependant pour un client normal la seul commande est `get` .
- `"<clé>"` : elle permet de retrouver la valeur et elle doit être entre guillemets.
- `"<valeur>"` : l’administrateur peut ajouter des valeurs à une clé, toujours entre guillemets.

Pour la commande `get`, `pref` et `del` la requête est de la forme : 

`<dictionnaire> <commandes> "<clé>"` 

Pour la commande `login` la forme de la requête est :

`login <mot de passe>` 

- `<mot de passe>` : permet à l’administrateur de se connecter il est connue par le serveur.

### Réponse serveur :

La réponse du serveur est de la forme : `<code d'erreur> <longueur de la reponse>\n <réponses>` .

`<code d'erreur>` : il permet d’obtenir plus d’informations sur la réponse.
`<longueur de la reponse>` : la longueur de la reponse du serveur.

`<réponses>` : la réponses du serveur.

## Code d’erreur

Le serveur répond au client en lui envoyant d’abord un code avec la réponse on 2 codes :

`OK` : pour dire que tout s’est bien passé.

`ERR` : suivie d’un message d’erreur si un problème se produit.

Exemple pour chaque commande : 

`get <clé>` :

- `OK <longueur>`
- `<valeur>`

- `ERR 19`
- `La clé n’existe pas`

`pref <prefix>` :

- `OK <longueur>`
- `Les clés-valeur dont la clé a pour préfixe <prefix> : <clé1> <valeur> , <clé2> <valeur>... `

- `ERR <longueur>`
- `il y'as pas de clé contenant ce préfixe.`

`del <clé>` :

- `OK <longueur>`
- `clé supprimer`

- `ERR <longueur>`
- `La clé n’existe pas`

`set <clé> <valeur>` :

- `OK <longueur>`
- `La clé a été modifier.`

- `OK <longueur>`
- `La clé à été ajouté avec sa valeur.`

- `ERR <longueur>`
- `une erreur est survenue`

`login <mot de passe>` :

- `OK 15`
- `bienvenue admin`

- `ERR 20`
- `mot de passe incorrecte`

`dget <valeur>` :

- `ERR 16`
- `commande incorrecte`

## Exemple de chat

exemple entre client normal(user) et serveur :

**serveur :** 

`./dico_serveur.py 7777`

**user** :

`./dico_client.py [localhost](http://localhost) 7777 mois_durée.json get "janvier"` 

**serveur** :

`OK 2`
`31` 

exemple entre admin :

**serveur :** 

`./dico_serveur.py 7777`

**user** :

`./dico_client.py [localhost](http://localhost) 7777 login motdepasse1` 

**serveur** :

`OK 15`
`bienvenue admin`

**user** :

`mois_durée.json get "janvier"` 

**serveur** :

`OK 2`
`bienvenue admin`