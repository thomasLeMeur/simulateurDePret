import json
import FileUtilities

class ConfigLoader :
	def __init__(self) :
		self.apport = None
		self.salaire = None
		self.nbAnnees = None
		self.codePostal = None
		self.prixDuBien = None
		self.fraisGestion = None
		self.fraisNotaire = None
		self.tauxGarantie = None
		self.chargesCopro = None
		self.mensualiteMax = None
		self.redevanceTele = None
		self.tauxAnnuelPret = None
		self.tauxEndettement = None
		self.nbMensualitesParAn = None
		self.prixLocatifMensuel = None
		self.tauxAnnuelAssurance = None
		self.assuranceDegressive = None
		self.taxeHabitationNulle = None

		FileUtilities.openFileAndApply("config.txt", lambda file : self.fromJson(file.read()))

	def fromJson(self, content) :
		payload = json.loads(content)

		def setValueFromJson(attrName, jsonKey, cast) :
			if jsonKey in payload :
				setattr(self, attrName, cast(payload[jsonKey]))			

		setValueFromJson("codePostal", "Code postal", int)
		setValueFromJson("apport", "Apport (euro)", float)
		setValueFromJson("prixDuBien", "Prix du bien (euro)", float)
		setValueFromJson("nbAnnees", "Nombre d'annees du pret", int)
		setValueFromJson("mensualiteMax", "Mensualité maximale (euro)", float)
		setValueFromJson("fraisNotaire", "Frais de notaire (pourcent)", float)
		setValueFromJson("tauxGarantie", "Taux de garantie (pourcent)", float)
		setValueFromJson("redevanceTele", "Redevance tele annuelle (euro)", float)
		setValueFromJson("nbMensualitesParAn", "Nombre de mensualites par an", int)
		setValueFromJson("tauxAnnuelPret", "Taux annuel du pret (pourcent)", float)
		setValueFromJson("fraisGestion", "Frais de gestion bancaire (euro)", float)
		setValueFromJson("prixLocatifMensuel", "Prix locatif mensuel (euro)", float)
		setValueFromJson("salaire", "Salaire mensuel net avant impot (euro)", float)
		setValueFromJson("chargesCopro", "Charges annuelles de copropriete (euro)", float)
		setValueFromJson("tauxEndettement", "Taux d'endettement maximal (pourcent)", float)
		setValueFromJson("taxeHabitationNulle", "Taxe d'habitation nulle (true/false)", bool)
		setValueFromJson("tauxAnnuelAssurance", "Taux annuel assurance emprunteur (pourcent)", float)
		setValueFromJson("assuranceDegressive", "Assurance emprunteur degressive (true/false)", bool)

