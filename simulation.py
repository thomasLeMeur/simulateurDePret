#!/usr/bin/python3

import json
from src import (
    MaxCapacitySimulator,
    NbAnneesSuivantSalaireSimulator,
    MensualiteSuivantNbAnneesEtSalaireSimulator,
    MaxPretCapacitySimulator,
    NbAnneesSuivantSalaireEtDepensesSimulator,
    MensualiteSuivantNbAnneesEtSalaireEtDepensesSimulator,
)


def main():
    ret = None
    while ret is None or not (1 <= ret <= 6):
        msgs = []
        msgs.append("Quelle type de simulation voulez-vous lancer ? :")
        msgs.append("1- Capacité maximale de remboursement")
        msgs.append("2- Nombre d'années nécessaire suivant un salaire")
        msgs.append("3- Mensualité nécessaire suivant un nombre d'années et un salaire")
        msgs.append(
            "4- Nombre d'années nécessaire suivant un salaire et des dépenses additionnelles"
        )
        msgs.append(
            "5- Mensualité nécessaire suivant un nombre d'années, un salaire et des dépenses additionnelles"
        )
        msgs.append(
            "6- Prix maximal d'un bien achetable suivant un salaire, un nombre d'années et un coût de prêt (intérêts, etc.)"
        )
        msgs.append("")
        ret = input("\n".join(msgs))

        try:
            ret = int(ret)
        except:
            ret = None

    match ret:
        case 1:
            simulator_cls = MaxCapacitySimulator
        case 2:
            simulator_cls = NbAnneesSuivantSalaireSimulator
        case 3:
            simulator_cls = MensualiteSuivantNbAnneesEtSalaireSimulator
        case 4:
            simulator_cls = NbAnneesSuivantSalaireEtDepensesSimulator
        case 5:
            simulator_cls = MensualiteSuivantNbAnneesEtSalaireEtDepensesSimulator
        case 6:
            simulator_cls = MaxPretCapacitySimulator
        case _:
            raise Exception("Impossible")

    with open("config.txt") as config_file:
        simulator_cls(json.load(config_file)).debrief()


if __name__ == "__main__":
    main()
    input()
