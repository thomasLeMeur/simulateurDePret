# Simulateur de prêt #

Ce simulateur permet de réaliser cinq simulations différentes sous Python3.


## Simulation de la capacité maximale de remboursement ##

En France, le remboursement d'un prêt immobilier ne peut dépasser 33% de ses revenus nets avant impôts.

Cette simulation prend donc en compte :
- le salaire mensuel net avant impôts
- le nombre de mensualités par an (mois de salaire)
- le nombre d'années de remboursement du prêt
- l'apport fourni

Formules :
- capacité = (revenusMensuel * 33 / 100) * nombreDeMensualités * nbAnnées + apport

Sortie :
- La capacité maximale de remboursement


## Simulation du nombre d'années nécessaire pour acheter un bien suivant un salaire mensuel donné et un taux fixe renseigné ##

Les mensualités de remboursement (valeur fixe) comprennent le capital initial désiré, les intérêts à verser à la banque (taux), le coût de l'assurance emprunteur (décès-invalidité), le coût de la garantie, le coût de gestion du prêt (frais et tenue du dossier) et les frais de notaire.

a) Les intérêts du prêt sont calculés chaque mois suivant le capital restant à rembourser. Ainsi, plus le taux est élevé, plus la part des intérêts par mois est grande, moins le capital à rembourser diminue vite, plus le prêt sera long et la somme des inétrêts versés sera grande.

b) Le coût de l'assurance emprunteur (0.5% en moyenne), qui dépend du risque que représente l'emprunteur auprès de l'organisme assureur (âge, maladie, etc...) peut se calculer de deux manières :
- De manière dégressive, comme les intérêts du prêt vu précédemment, suivant le capital restant à rembourser (la somme totale à payer sera lissée pour que chaque mensualité soit fixe)
- De manière fixe, moins intéressant, se basant uniquement sur le capital initial

c) Le coût de la garantie du prêt (0.7% en moyenne) correspond à un montant à verser à la signature du prêt. Généralement, 75% de cette somme peut être restituée à échéance. Il existe trois types de garantie : la caution, l'hypothèque et l'IPPD. On s'intéressera ici à la caution car c'est l'option la plus courante et donc avec les taux les plus bas.

d) Le coût de gestion du compte (1000€ en moyenne) correspond à une somme à versée à la banque pour couvrir leurs frais de gestion du prêt (ouverture/analyse du dossier + gestion dans la durée). Comme ce sont de faux frais, ceux-ci sont tout à fait négociables et souvent offerts aux emprunteurs ayant un compte dans la banque prêteuse.

e) Enfin, ce que l'on nomme les frais de notaire (7.8% en moyenne sur les biens bâtis dans l'ancien) sont un ensemble de taxes prélevées par l'état (7%) auxquelles s'ajoute la commission réelle du notaire (0.8%). Si l'achat se fait dans du neuf, ces frais seront plutôt de l'ordre de 3-4%. Il faut savoir que fournir un apport couvrant les frais de notaire "rassurent" les banques voire est nécessaire pour l'obtention d'un prêt.

Cette simulation prend donc en compte :
- le salaire mensuel net avant impôts
- le nombre de mensualités par an (mois de salaire)
- l'apport fourni
- le prix du bien
- le taux du prêt
- le taux de l'assurance emprunteur
- le fait que l'assurance emprunteur soit dégressive ou non
- le taux de garantie
- le coût de gestion
- le taux de frais de notaire

Formules :
- capitalEmprunté = (prixDuBien + prixDeLaGarantie + coutDeGestion + fraisDeNotaire) - apport
- tauxPeriodique = tauxAnnuel / 100 / nbPériodesParAn
- nbMensualités = nbAnnées * nbPériodesParAn
- mensualiteInterets = capitalRestantARembourse * tauxPeriodique
- mensualiteAssurance =
  - si fixe : capitalInitial * tauxPeriodique 
  - si dégressive : sommeDeToutesLesMensualitésCalculées / nbMensualités
- mensualitéFixe = ((capitalEmprunte * tauxPeriodique) / (1 - ((1 + tauxPeriodique) ** -nbMensualites))) + mensualiteAssurance

Sortie :
- Le détail de chaque mensualité
- Le total des intérêts versés à la banque
- Le coût total des frais de notaire
- Le coût total de l'assurance emprunteur
- Le coût de la garantie
- Le nombre d'années nécessaire


## Simulation proche de la précédente mais qui se base sur un nombre d'années donné pour calculer la mensualité nécessaire ##

Cette simulation prend donc en compte :
- le salaire mensuel net avant impôts
- le nombre de mensualités par an (mois de salaire)
- l'apport fourni
- le prix du bien
- le taux du prêt
- le taux de l'assurance emprunteur
- le fait que l'assurance emprunteur soit dégressive ou non
- le taux de garantie
- le coût de gestion
- le taux de frais de notaire
- le nombre d'années désiré

Sortie :
- Si le salaire est suffisant, sortie similaire à la simulation précédente
- Si le salaire est insuffisant, on indique le salaire minimum pour que le nombre d'années soit respecté et le nombre d'années nécessaire pour le salaire donné


## Simulation du nombre d'années nécessaire pour acheter un bien suivant une dépense mensuelle donnée et un taux fixe renseigné ##

Cette simulation se calcule comme la deuxième à la différence que la dépense mensuelle doit couvrir les dépenses annexes liées à la porpriété.

Ces dépenses correspondent à :
- les charges de copropriété (montant annuel payé à la copropriété pour le bon fonctionnement de cette dernière (entretien, etc...))
- la taxe d'habitation (taxe annuelle payée à la commune que l'on soit propriétaire ou locataire)
	- pour savoir si vous en êtes éxonérés : https://www.impots.gouv.fr/portail/particulier/questions/suis-je-concerne-par-la-reforme-de-la-taxe-dhabitation
- la contribution à l'audiovisuel public (taxe annuelle payée à l'état)
	- pour savoir sa valeur actuelle ou si vous en êtes éxonérés : https://www.service-public.fr/particuliers/vosdroits/F88
- les impôts fonciers (taxes annuelles payées à la commune, département, etc... si l'on est propriétaire) :
	- la taxe foncière communale
	- la taxe foncière départementale
	- la taxe d'enlèvement d'ordures ménagères (en tant que locataire, elle est souvent ajoutée au prix locatif réel)
	- d'autres taxes existent mais sont minimes (une dizaine d'euros par an) et donc négligeables
Ces dernières sont calculées suivant la valeur locative cadastrale du bien. Elles correspondent donc à un impôt à payer sur le revenu que pourrait vous rappoter votre bien si vous le mettiez en location (et ce, même si vous ne le faites pas). Pour information, cette valeur locative cadastrale correspond souvent à la moitié du prix de location réel d'un bien (elle augmentera généralement de 1% par an mais ce n'est pas ici pris en compte car cela rentrerai en contradiction avec une mensualité fixe).

Cette simulation prend donc en compte :
- le salaire mensuel net avant impôts
- le nombre de mensualités par an (mois de salaire)
- l'apport fourni
- le prix du bien
- le taux du prêt
- le taux de l'assurance emprunteur
- le fait que l'assurance emprunteur soit dégressive ou non
- le taux de garantie
- le coût de gestion
- le taux de frais de notaire
- les charges de copropriété
- la redevance télé (138€ à ce jour)
- le code postal du bien (pour calculer les autres dépenses additionnelles)
- le prix locatif mensuel estimé (pour en déduire la valeur locative cadastrale annuelle)
- la mensualité maximale désirée

Formules :
- Taxe d'habitation (TH) : valeur locative cadastrale annuelle * taux communal (lu dans un fichier de ressource)
- Taxe foncière communale (TFC) : valeur locative cadastrale annuelle / 2 * taux communal (lu dans un fichier de ressource)
- Taxe foncière départementale (TFD) : valeur locative cadastrale anuelle / 2 * taux départemental (lu dans un fichier de ressource)
- Taxe d'enlèvement d'ordures ménagères (TEOM) : valeur locative cadastrale annuelle / 2 * taux communal (lu dans un fichier de ressource)

Sortie :
- Le détail de chaque mensualité
- Le total des intérêts versés à la banque
- Le coût total des frais de notaire
- Le coût total de l'assurance emprunteur
- Le coût de la garantie
- Le montant annuel de la redevance télé
- Le montant annuel de la taxe d'habitation
- Le montant cumulé annuel des impôts fonciers
- Le montant annuel des charges de copropriété
- Le montant cumulé annuel de toutes les dépenses additionnelles
- Le nombre d'années nécessaire
- L'économie mensuelle achat/location (taxes de propriétaires vs taxes de locataires)
- Le nombre d'années à partir duquel on peut considérer que l'achat du bien est remboursé par les économies réalisées)


## Simulation proche de la précédente mais qui se base sur un nombre d'années donné pour calculer la mensualité nécessaire ##

Cette simulation prend donc en compte :
- le salaire mensuel net avant impôts
- le nombre de mensualités par an (mois de salaire)
- l'apport fourni
- le prix du bien
- le taux du prêt
- le taux de l'assurance emprunteur
- le fait que l'assurance emprunteur soit dégressive ou non
- le taux de garantie
- le coût de gestion
- le taux de frais de notaire
- les charges de copropriété
- la redevance télé
- le code postal du bien
- le prix locatif mensuel estimé
- le nombre d'années désiré

Sortie :
- Si le salaire est suffisant, sortie similaire à la simulation précédente
- Si le salaire est insuffisant, on indique le salaire minimum pour que le nombre d'années soit respecté et le nombre d'années nécessaire pour le salaire donné


### Liens utiles concernant les taxes ##

- Fichier La Poste associant code postal et code INSEE : 
	- https://www.data.gouv.fr/fr/datasets/base-officielle-des-codes-postaux/

- Fichier gouvernemental recensant, entre autres, les derniers (2018) taux votés rendus public concernant les taxes évoquées plus haut :
	- https://www.data.gouv.fr/fr/datasets/impots-locaux-fichier-de-recensement-des-elements-dimposition-a-la-fiscalite-directe-locale-rei-3/#_
	- La TH est à la colonne H12
	- La TEOM est à la colonne F22
	- La TFPB1 est à la colonne E12
	- La TFPB2 est à la colonne E42


### Fichier de configuration ###

Le fichier config.txt respecte le format Json.

Avant de lancer le programme, il faut configurer le fichier config.txt pour, au moins, y renseigner les champs nécessaires à la simulation désirée.
Si certains champs ne sont pas nécessaires, ils peuvent être laissés.


### Lancement du programme ###

Il suffit de double cliquer sur le fichier simulation.py ou de lancer une commande similaire à 'python3 simulation.py' suivant l'environnement de travail.

