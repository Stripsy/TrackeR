# TrackeR

Ce projet est un bot Discord créé avec Python qui permet de suivre et de gérer des colis via l'API de La Poste.


## Fonctionnalités

- Suivre un colis en fournissant son numéro de suivi
- Ajouter un colis à votre liste de suivi avec des notes personnalisées
- Éditer les notes d'un colis de votre liste
- Afficher votre liste de colis avec leur état, date du dernier événement et notes
- Supprimer un colis de votre liste
- Supprimer complètement votre liste de colis


## Commandes


- **!help** : Affiche la liste des commandes disponibles avec leur description.
- **!track <numero>** : Suit le colis avec le numéro de suivi spécifié.
- **!addtrack <numero> [notes]** : Ajoute un colis à votre liste avec des notes facultatives.
- **!editnotes <numero> <notes>** : Modifie les notes d'un colis de votre liste.
- **!listetrack** : Affiche votre liste de colis avec leur état, date du dernier événement et notes.
- **!removetrack <numero>** : Supprime un colis de votre liste.
- **!removeliste** : Supprime complètement votre liste de colis.



## Configuration

Avant d'exécuter le bot, vous devez configurer les variables suivantes :

- `TOKEN` : Votre jeton d'authentification Discord.
- `CHAN` : Votre channel Discord.
- `OKAPI_KEY` : Votre clé d'API Okapi pour accéder à l'API de La Poste.
- `CLUSTER` : L'URI de connexion à votre cluster MongoDB pour stocker les données des utilisateurs.
