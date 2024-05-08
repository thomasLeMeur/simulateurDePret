from typing import Any, TypeVar
import math

from src.models import (
    MensualiteSuivantNbAnneesEtSalaireModel,
    NbAnneesSuivantSalaireModel,
)

from src.utils import AnneesSuccesSimulator, BaseSimulator, SuccesSimulator


AnneesT = TypeVar("AnneesT", bound=NbAnneesSuivantSalaireModel)


class BaseAnneesSimulator(BaseSimulator[AnneesT]):
    @staticmethod
    def get_taux_periodique(taux_annuel: float) -> float:
        return taux_annuel / 100 / 12

    @staticmethod
    def get_nombre_mensualites(nb_annees: int) -> int:
        return nb_annees * 12

    @staticmethod
    def get_total_interets(
        capital_emprunte: float, nb_annees: int, mensualite: float
    ) -> float:
        return nb_annees * 12 * mensualite - capital_emprunte

    @staticmethod
    def get_interet_rembourses(
        capital_restant_a_rembourser: float, taux_annuel: float
    ) -> float:
        taux_periodique = BaseAnneesSimulator.get_taux_periodique(taux_annuel)
        return capital_restant_a_rembourser * taux_periodique

    @staticmethod
    def get_mensualite(
        capital_emprunte: float, taux_annuel: float, nb_annees: int
    ) -> float:
        taux_periodique = BaseAnneesSimulator.get_taux_periodique(taux_annuel)
        nb_mensualites = BaseAnneesSimulator.get_nombre_mensualites(nb_annees)
        return (
            (capital_emprunte * taux_periodique)
            / (1 - ((1 + taux_periodique) ** -nb_mensualites))
            if nb_mensualites
            else 0
        )

    def mensualite_acceptable(self, mensualite: float):
        return mensualite > self.mensualite_max

    def __init__(self, config_as_dict: dict[str, Any]):
        super().__init__(config_as_dict)

        cout_notaire = self.config.prix_du_bien * self.config.frais_notaire / 100.0
        cout_garantie = self.config.prix_du_bien * self.config.taux_garantie / 100.0
        self.mensualite_max = self.config.salaire * self.config.taux_endettement / 100.0
        capital_emprunte = max(
            0,
            (
                self.config.prix_du_bien
                + cout_garantie
                + self.config.frais_gestion
                + cout_notaire
            )
            - self.config.apport,
        )

        self.nb_annees = 0
        mensualite = self.mensualite_max + 1
        while capital_emprunte and self.mensualite_acceptable(mensualite):
            if self.nb_annees > 1000:
                raise Exception("1000 ans ne suffirait pas à rembourser ce prêt")

            self.nb_annees += 1
            cout_total_assurance = 0
            nb_mensualites = self.nb_annees * 12
            capital_restant = capital_emprunte
            mensualite_hors_assurance = self.get_mensualite(
                capital_emprunte, self.config.taux_annuel_pret, self.nb_annees
            )
            while capital_restant > 0:
                cout_total_assurance += self.get_interet_rembourses(
                    capital_restant, self.config.taux_annuel_assurance
                )
                interets_courants = self.get_interet_rembourses(
                    capital_restant, self.config.taux_annuel_pret
                )
                capital_rembourse = mensualite_hors_assurance - interets_courants
                capital_restant -= capital_rembourse
            mensualite_assurance_lissee = cout_total_assurance / nb_mensualites
            mensualite = mensualite_hors_assurance + mensualite_assurance_lissee

        self.detail_mensualites = []
        cout_total_assurance = 0
        nb_mensualites = self.get_nombre_mensualites(self.nb_annees)
        mensualite_hors_assurance = self.get_mensualite(
            capital_emprunte, self.config.taux_annuel_pret, self.nb_annees
        )

        id_mensualite = 0
        capital_restant = capital_emprunte
        while capital_restant > 0:
            cout_total_assurance += self.get_interet_rembourses(
                capital_restant, self.config.taux_annuel_assurance
            )
            interets_courants = self.get_interet_rembourses(
                capital_restant, self.config.taux_annuel_pret
            )
            capital_rembourse = mensualite_hors_assurance - interets_courants
            capital_restant -= capital_rembourse
            id_mensualite += 1

            self.detail_mensualites.append(
                (id_mensualite, interets_courants, capital_rembourse, capital_restant)
            )

        mensualite_assurance_lissee = (
            cout_total_assurance / nb_mensualites if nb_mensualites else 0
        )
        mensualite = mensualite_hors_assurance + mensualite_assurance_lissee

        self.cout_notaire = round(cout_notaire, 2)
        self.cout_garantie = round(cout_garantie, 2)
        self.mensualite_max = round(self.mensualite_max, 2)
        self.capital_emprunte = round(capital_emprunte, 2)
        self.cout_total_assurance = round(cout_total_assurance, 2)
        self.mensualite_assurance_lissee = round(mensualite_assurance_lissee, 2)
        self.mensualite_hors_assurance = round(mensualite_hors_assurance, 2)
        self.mensualite = round(mensualite, 2)
        self.total_interets = round(
            self.get_total_interets(
                capital_emprunte, self.nb_annees, mensualite_hors_assurance
            ),
            2,
        )
        self.prix_total = round(self.mensualite * nb_mensualites, 2)

    def debrief(self):
        print(f"Prix du bien : {round(self.config.prix_du_bien, 2)}€")
        print(f"Frais de gestion : {round(self.config.frais_gestion, 2)}€")
        print(
            f"Coût de la garantie : {self.cout_garantie}€ ({round(self.config.taux_garantie, 2)}%), avec un remboursement à échéance possible de {round(self.cout_garantie * 0.75, 2)}€"
        )
        print(
            f"Frais de notaire : {self.cout_notaire}€ ({round(self.config.frais_notaire, 2)}%)"
        )
        print(f"Apport : {round(self.config.apport, 2)}€")
        print(f"Capital emprunté : {self.capital_emprunte}€")
        print(
            f"Salaire mensuel net avant impôts : {round(self.config.salaire)}€ sur 12 mois"
        )
        print(
            f"\tSoit une mensualité maximale de {self.mensualite_max}€ (pour un endettement de {round(self.config.taux_endettement, 2)}%)"
        )
        print(f"Taux annuel du prêt : {round(self.config.taux_annuel_pret, 2)}%")
        print(
            f"Taux annuel de l'assurance dégressive: {round(self.config.taux_annuel_assurance, 2)}%"
        )

        if self.has_better() or not self.succeed():
            print(
                f"Pour un tel prêt, la mensualité nécessaire est de {self.mensualite}€"
            )
            print(
                f"Avec la mensualité maximale actuelle, il faudrait {self.nb_annees} ans pour remboursé ce prêt"
            )
        else:
            print(f"Détails des {len(self.detail_mensualites)} mensualités :")
            for (
                id_mensualite,
                interets_courants,
                capital_rembourse,
                capital_restant,
            ) in self.detail_mensualites:
                print(
                    "Mensualité {: >3} : part des intérêts {: >7.2f}€, part du capital {: >7.2f}€, part de l'assurance {: >7.2f}€, capital restant {: >10.2f}€".format(
                        id_mensualite,
                        interets_courants,
                        capital_rembourse,
                        self.mensualite_assurance_lissee,
                        capital_restant,
                    )
                )
            print("")

            print(
                f"Avec une mensualité de {self.mensualite}€, le prêt sera remboursé en {self.nb_annees} ans, soit {len(self.detail_mensualites)} mensualités"
            )
            print(
                f"Avec une mensualité hors assurance de {self.mensualite_hors_assurance}€, le total des intérêts s'élève à {self.total_interets}€"
            )
            print(
                f"Avec une assurance mensuelle lissée de {self.mensualite_assurance_lissee}€, le coût total de l'assurance s'élève à {self.cout_total_assurance}€"
            )
            print(
                f"Avec un coût du prêt de {round(self.total_interets + self.cout_total_assurance, 2)}€, on a un donc un remboursement de {self.prix_total}€"
            )
            print(
                f"Il faut donc attendre la mensualité {math.ceil((self.total_interets + self.cout_total_assurance) / self.mensualite if self.mensualite else 0)} avant de ne pas revendre le bien à perte"
            )


class NbAnneesSuivantSalaireSimulator(
    BaseAnneesSimulator[NbAnneesSuivantSalaireModel], SuccesSimulator
):
    @staticmethod
    def get_model():
        return NbAnneesSuivantSalaireModel


class MensualiteSuivantNbAnneesEtSalaireSimulator(
    AnneesSuccesSimulator[MensualiteSuivantNbAnneesEtSalaireModel],
    BaseAnneesSimulator[MensualiteSuivantNbAnneesEtSalaireModel],
):
    @staticmethod
    def get_model():
        return MensualiteSuivantNbAnneesEtSalaireModel
