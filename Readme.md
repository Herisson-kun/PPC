# PPC
PPC project game : Hanabis

Le jeu se lance très simplement, sur système Unix/Linux.
Il faut peut être installer sysv_ipc si ce n'est pas déjà fait.

 - Installer sysv_ipc si pas déjà sur le PC : pip install sysv_ipc.
 - Lancer game.py dans un terminal : "python3 game.py". 
 - Ecrire le nombre de joueur souhaité.
 - Lancer pour chaque joueur un nouveau terminal et lancer player.py : "python3 player.py"

 Have fun !

Disclaimer !! si le jeu est interrompu, il peut y avoir des erreurs au redémarrage.
Si vous avez besoin de fermer le jeu avec ctrl+C, merci de fermer d'abord TOUS les clients.

To fix issues : - fermer le terminal du serveur/vscode
                - fermer les message queues en faisant toutes les commandes: "ipcrm -Q x" pour x allant de 1 à nombre_de_joueur.

