from typing import Any, cast
from src.annees import MensualiteSuivantNbAnneesEtSalaireSimulator
from src.models import BaseMensualiteSuivantNbAnneesEtSalaireModel, MaxCapacityModel
from src.utils import BaseSimulator, SuccesSimulator


class MaxCapacitySimulator(BaseSimulator[MaxCapacityModel], SuccesSimulator):
    @staticmethod
    def get_model():
        return MaxCapacityModel

    def __init__(self, config_as_dict: dict[str, Any]):
        super().__init__(config_as_dict)

        self.mensualite_max = self.config.salaire * self.config.taux_endettement / 100
        self.capacite_remboursement = (
            self.mensualite_max * 12 * self.config.nb_annees + self.config.apport
        )

    def debrief(self):
        print(f"Emprunt sur {self.config.nb_annees} ans")
        print(f"Salaire mensuel net avant impôts : {self.config.salaire}€ sur 12 mois")
        print(
            f"\tSoit une mensualité maximale de {self.mensualite_max}€ (pour un endettement de {self.config.taux_endettement}%)"
        )
        print(f"Apport : {self.config.apport}€")
        print(f"Capacité maximale de remboursement : {self.capacite_remboursement}€")


class MaxPretCapacitySimulator(
    BaseSimulator[BaseMensualiteSuivantNbAnneesEtSalaireModel]
):
    @staticmethod
    def get_model():
        return BaseMensualiteSuivantNbAnneesEtSalaireModel

    def succeed(self):
        return self.last_success is not None

    def has_better(self):
        return False

    def __init__(self, config_as_dict: dict[str, Any]):
        super().__init__(config_as_dict)

        mini = 0
        maxi = MaxCapacitySimulator(config_as_dict).capacite_remboursement
        self.last_success = None
        while abs(mini - maxi) > 1:
            prix_du_bien = round(mini + (maxi - mini) / 2, 2)
            simulation = MensualiteSuivantNbAnneesEtSalaireSimulator(
                {**self.config.model_dump(), "prix_du_bien": prix_du_bien}
            )
            if simulation.succeed():
                mini = prix_du_bien
                self.last_success = simulation
            else:
                maxi = prix_du_bien

    def debrief(self):
        if not self.succeed():
            print("Vous ne pouvez rien acheter avec ce salaire")
        else:
            last_success = cast(
                MensualiteSuivantNbAnneesEtSalaireSimulator, self.last_success
            )
            print(f"Vous pouvez acheter un bien à {last_success.config.prix_du_bien}")
            print("Voici le détail:")
            last_success.debrief()
