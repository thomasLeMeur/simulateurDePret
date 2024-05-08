from src.annees import BaseAnneesSimulator
from src.utils import AnneesSuccesSimulator, BaseSimulator, SuccesSimulator
from .models import (
    NbAnneesSuivantSalaireEtDepensesModel,
    MensualiteSuivantNbAnneesEtSalaireEtDepensesModel,
)
from typing import TypeVar, cast
import math
import csv
from typing import Any, Callable, TextIO


DepensesT = TypeVar("DepensesT", bound=NbAnneesSuivantSalaireEtDepensesModel)


class BaseDepensesSimulator(BaseAnneesSimulator[DepensesT]):
    @staticmethod
    def open_file_and_apply(filename: str, func_to_apply: Callable[[TextIO], Any]):
        try:
            with open(filename, encoding="utf-8") as file:
                return func_to_apply(file)
        except:
            print(f"Le fichier {filename} est manquant ou mal formaté")
            raise

    # On renvoie (le nom de la ville (str), le numéro INSEE du département (str car on peut avoir 2A par exmeple), le numéro de commune INSEE (int))
    @staticmethod
    def get_infos_de_la_poste(
        code_postal: int,
    ) -> tuple[str, str, int] | tuple[None, None, None]:
        def func(file: TextIO):
            reader = csv.reader(file)
            reader.__next__()  # On passe la ligne des headers
            line = next(
                (
                    (codeINSEE, nom)
                    for codeINSEE, nom, code in reader
                    if int(code) == code_postal
                ),
                None,
            )
            if line != None:
                return line[1], line[0][:2], int(line[0][2:])
            else:
                return None, None, None

        return BaseDepensesSimulator.open_file_and_apply(
            "datas/laposte_hexasmal_simplified.csv", func
        )

    # On renvoie les taux de (TFC, TFD, TEOM, TH)
    @staticmethod
    def get_infos_taxes(
        departement: str, code_commune: int
    ) -> tuple[float, float, float] | tuple[None, None, None]:
        def func(file: TextIO):
            reader = csv.reader(file)
            reader.__next__()  # On passe la ligne des headers
            line = next(
                (
                    (t1, t2, t3)
                    for dpt, index, _, t1, t2, t3, _ in reader
                    if dpt == departement and int(index) == code_commune
                ),
                None,
            )
            if line != None:
                return float(line[0]), float(line[1]), float(line[2])
            else:
                return None, None, None

        return BaseDepensesSimulator.open_file_and_apply(
            "datas/REI_2018_simplified.csv", func
        )

    # Les villes avec arrondissements ont un code INSEE différent dans les fichiers de données
    @staticmethod
    def check_ville_avec_code_postal_particulier(
        nom_ville: str,
    ) -> tuple[float, float, float] | tuple[None, None, None]:
        if "PARIS" in nom_ville:
            return BaseDepensesSimulator.get_infos_taxes("75", 56)
        elif "MARSEILLE" in nom_ville:
            return BaseDepensesSimulator.get_infos_taxes("13", 55)
        else:
            return None, None, None

    def mensualite_acceptable(self, mensualite: float):
        return (
            mensualite > self.mensualite_max - self.depenses_additionnelles_mensuelles
        )

    def __init__(self, config_as_dict: dict[str, Any]):
        BaseSimulator.__init__(self, config_as_dict)

        nom_ville, dpt, code = self.get_infos_de_la_poste(self.config.code_postal)
        if (nom_ville, dpt, code) == (None, None, None):
            raise Exception(
                f"Le code postal {self.config.code_postal} ne fait pas partie des données La Poste"
            )
        self.nom_ville = cast(str, nom_ville)

        TFC, TFD, TEOM = self.get_infos_taxes(cast(str, dpt), cast(int, code))
        if (TFC, TFD, TEOM) == (None, None, None):
            TFC, TFD, TEOM = self.check_ville_avec_code_postal_particulier(
                self.nom_ville
            )
        if (TFC, TFD, TEOM) == (None, None, None):
            raise Exception(
                f"Le code postal {self.config.code_postal} ne correspond à aucune donnée fournie par l'État"
            )
        TFC, TFD, TEOM = cast(tuple[float, float, float], (TFC, TFD, TEOM))

        TFC_annuelle = self.config.prix_locatif_mensuel / 2.0 / 2.0 * 12.0 * TFC / 100.0
        TFD_annuelle = self.config.prix_locatif_mensuel / 2.0 / 2.0 * 12.0 * TFD / 100.0
        TEOM_annuelle = (
            self.config.prix_locatif_mensuel / 2.0 / 2.0 * 12.0 * TEOM / 100.0
        )
        depenses_additionnelles_annuelles = (
            TFC_annuelle + TFD_annuelle + TEOM_annuelle + self.config.charges_copro
        )
        self.depenses_additionnelles_mensuelles = (
            depenses_additionnelles_annuelles / 12.0
        )
        depenses_locataire_annuelles = self.config.prix_locatif_mensuel * 12
        enomomies_annuelles_propriete = (
            depenses_locataire_annuelles - depenses_additionnelles_annuelles
        )
        enomomies_mensuelles_propriete = enomomies_annuelles_propriete / 12.0

        BaseAnneesSimulator.__init__(self, config_as_dict)

        self.nb_annees_pour_remboursement_pret = math.ceil(
            self.prix_total / enomomies_annuelles_propriete
        )
        self.taxe_fonciere = round(TFC_annuelle + TFD_annuelle + TEOM_annuelle, 2)
        self.TFC = round(cast(float, TFC), 2)
        self.TFD = round(cast(float, TFD), 2)
        self.TEOM = round(cast(float, TEOM), 2)
        self.depenses_additionnelles_annuelles = round(
            depenses_additionnelles_annuelles, 2
        )
        self.depenses_locataire_annuelles = round(depenses_locataire_annuelles, 2)
        self.depenses_additionnelles_mensuelles = round(
            self.depenses_additionnelles_mensuelles, 2
        )
        self.enomomies_annuelles_propriete = round(enomomies_annuelles_propriete, 2)
        self.enomomies_mensuelles_propriete = round(enomomies_mensuelles_propriete, 2)

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
            f"\tSoit une mensualité maximale de {self.mensualite_max}€ (pour un endettement de {round(self.config.taux_endettement, 2)}%) face à un désir de {self.mensualite_max}€"
        )
        print(f"Taux annuel du prêt : {round(self.config.taux_annuel_pret, 2)}%")
        print(
            f"Taux annuel de l'assurance dégressive: {round(self.config.taux_annuel_assurance, 2)}%"
        )

        print(
            f"Le bien, d'une valeur locative mensuelle estimée à {self.config.prix_locatif_mensuel}€, se situe à {self.nom_ville} ({self.config.code_postal})"
        )
        print(f"\tCharges annuelles de copropriété : {self.config.charges_copro}€")
        print(
            f"\tMontant annuel des taxes foncières : {self.taxe_fonciere}€ (TFC:{self.TFC}% + TFD:{self.TFD}% + TEOM:{self.TEOM}%)"
        )
        print(
            f"\tMontant annuel cumulé des dépenses additionnelles de propriété : {self.depenses_additionnelles_annuelles}€, soit {self.depenses_additionnelles_mensuelles}€ par mois"
        )
        print(
            f"\tMontant annuel cumulé des dépenses additionnelles de location : {self.depenses_locataire_annuelles}€, soit {round(self.depenses_locataire_annuelles / 12, 2)}€ par mois"
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

            if self.mensualite_max <= self.depenses_additionnelles_mensuelles:
                print(
                    "La mensualité maximale désirée ne peut donc pas couvrir les dépenses additionnelles et le remboursement du prêt"
                )
            else:
                print(
                    f"Avec une mensualité de {self.mensualite + self.depenses_additionnelles_mensuelles}€, le prêt sera remboursé en {self.nb_annees} ans, soit {len(self.detail_mensualites)} mensualités"
                )
                print(
                    f"Avec une mensualité hors assurance et dépenses additionnelles de {self.mensualite_hors_assurance}€, le total des intérêts s'élève à {self.total_interets}€"
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

                if self.enomomies_annuelles_propriete < 0:
                    print(
                        f"Les charges annuelles de propriété sont plus importantes que les charges de location ({self.depenses_additionnelles_mensuelles}€ contre {self.depenses_locataire_annuelles}€)"
                    )
                    print(
                        f"Ce bien coûtera donc {-self.enomomies_mensuelles_propriete}€ de plus par mois si l'achat est réalisé"
                    )
                elif self.enomomies_annuelles_propriete > 0:
                    print(
                        f"Les charges annuelles de propriété sont moins importantes que les charges de location ({self.depenses_additionnelles_mensuelles}€ contre {self.depenses_locataire_annuelles}€)"
                    )
                    print(
                        f"Ce bien fera donc 'économiser' {self.enomomies_mensuelles_propriete}€ par mois si l'achat est réalisé"
                    )
                    print(
                        f"En cumulant ces économies, on peut considérer que le prêt sera amorti au bout de {self.nb_annees_pour_remboursement_pret} ans après la signature"
                    )


class NbAnneesSuivantSalaireEtDepensesSimulator(
    BaseDepensesSimulator[NbAnneesSuivantSalaireEtDepensesModel], SuccesSimulator
):
    @staticmethod
    def get_model():
        return NbAnneesSuivantSalaireEtDepensesModel


class MensualiteSuivantNbAnneesEtSalaireEtDepensesSimulator(
    BaseDepensesSimulator[MensualiteSuivantNbAnneesEtSalaireEtDepensesModel],
    AnneesSuccesSimulator[MensualiteSuivantNbAnneesEtSalaireEtDepensesModel],
):
    @staticmethod
    def get_model():
        return MensualiteSuivantNbAnneesEtSalaireEtDepensesModel
