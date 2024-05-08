from pydantic import BaseModel, PositiveInt, NonNegativeFloat, PositiveFloat


class BaseSimulationModel(BaseModel):
    apport: NonNegativeFloat
    salaire: PositiveFloat
    taux_endettement: PositiveFloat


class MaxCapacityModel(BaseSimulationModel):
    nb_annees: PositiveInt


class BaseNbAnneesSuivantSalaireModel(BaseSimulationModel):
    taux_garantie: NonNegativeFloat
    frais_gestion: NonNegativeFloat
    frais_notaire: NonNegativeFloat
    taux_annuel_pret: PositiveFloat
    taux_annuel_assurance: NonNegativeFloat


class NbAnneesSuivantSalaireModel(BaseNbAnneesSuivantSalaireModel):
    prix_du_bien: PositiveFloat


class BaseMensualiteSuivantNbAnneesEtSalaireModel(
    BaseNbAnneesSuivantSalaireModel, MaxCapacityModel
):
    pass


class MensualiteSuivantNbAnneesEtSalaireModel(
    NbAnneesSuivantSalaireModel, MaxCapacityModel
):
    pass


class NbAnneesSuivantSalaireEtDepensesModel(NbAnneesSuivantSalaireModel):
    code_postal: PositiveInt
    charges_copro: NonNegativeFloat
    mensualite_max: PositiveFloat
    prix_locatif_mensuel: PositiveFloat


class MensualiteSuivantNbAnneesEtSalaireEtDepensesModel(
    NbAnneesSuivantSalaireEtDepensesModel, MaxCapacityModel
):
    pass
