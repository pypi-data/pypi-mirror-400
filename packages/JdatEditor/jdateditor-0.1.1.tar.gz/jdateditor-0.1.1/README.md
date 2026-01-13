# jdateditor
## a quoi il sert
Il permet de gérer et utiliser les données du nouveau language jdat 
## c'est quoi jdat
JDAT est un format de stockage de données structuré, lisible et chiffrable, conçu pour stocker des informations ou du texte long (comme du code ou de la documentation) sans jamais exécuter quoi que ce soit.
Chaque bloc est délimité par () et contient :
meta (n, l, t) → informations descriptives
data {…} → données ou texte stocké
Les blocs peuvent être chiffrés, mais le format reste lisible et modifiable via des outils externes (shell, éditeur, module Python).
JDAT n’est pas un langage de programmation : aucun code à l’intérieur n’est exécuté.
JDAT = format de données sûr, structuré et modulable, destiné à être lu, édité et chiffré via des outils, pas exécuté.
## comment s'en servir ?
### 1.l'import
on écrit:
import JdatEditor as jdat
### utiliser
with jdat.action("C:/Users/exemple/Desktop/compte.jdat") as a:  
    a("read")  # ou "edit"
