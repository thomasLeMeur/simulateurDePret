#!/usr/bin/python3

import math
import CsvUtilities
import FileUtilities
from ConfigLoader import *

class Simulator :
	def __init__(self, configs, nomsVariables, nomsParametres) :
		fail = False
		for index, nomVariable in enumerate(nomsVariables) :
			if getattr(configs, nomVariable) is None :
				print("Il manque {} dans le fichier de configuration".format(nomsParametres[index]))
				fail = True
		if fail :
			raise

		for nomVariable in nomsVariables :
			setattr(self, nomVariable, getattr(configs, nomVariable))

	def getTauxPeriodique(tauxAnnuel, nbPeriodesParAn) :
		return (tauxAnnuel / 100) / nbPeriodesParAn

	def getNombreMensualites(nbAnnees, nbPeriodesParAn) :
		return nbAnnees * nbPeriodesParAn

	def getMensualite(capitalEmprunte, tauxAnnuel, nbAnnees, nbPeriodesParAn) :
		tauxPeriodique = Simulator.getTauxPeriodique(tauxAnnuel, nbPeriodesParAn)
		nbMensualites = Simulator.getNombreMensualites(nbAnnees, nbPeriodesParAn)
		return (capitalEmprunte * tauxPeriodique) / (1 - ((1 + tauxPeriodique) ** -nbMensualites))

	def getTotalInterets(capitalEmprunte, nbAnnees, nbPeriodesParAn, mensualite) :
		return nbAnnees * nbPeriodesParAn * mensualite - capitalEmprunte

	def getInteretRembourse(capitalRestantARembourse, tauxAnnuel, nbPeriodesParAn) :
		tauxPeriodique = Simulator.getTauxPeriodique(tauxAnnuel, nbPeriodesParAn)
		return capitalRestantARembourse * tauxPeriodique

class MaxCapacitySimulator(Simulator) :
	def __init__(self, configs) :
		parametres = 												\
		["apport", "l'apport"], 									\
		["salaire", "le salaire"],									\
		["nbAnnees", "le nombre d'années"],							\
		["nbMensualitesParAn", "le nombre de mensualités par an"]

		super().__init__(configs, [elem[0] for elem in parametres], [elem[1] for elem in parametres])

	def compute(self) :
		self.mensualiteMax = self.salaire / 3.
		self.capaciteRemboursement = self.mensualiteMax * self.nbMensualitesParAn * self.nbAnnees + self.apport

	def __repr__(self) :
		msgs = []
		msgs.append("Emprunt sur {} ans".format(self.nbAnnees))
		msgs.append("Salaire mensuel net avant impôts : {}€ sur {} mois".format(self.salaire, self.nbMensualitesParAn))
		msgs.append("  Soit une mensualité maximale de {}€ (pour un endettement de 33%)".format(self.mensualiteMax))
		msgs.append("Apport : {}€".format(self.apport))
		msgs.append("Capacité de remboursement maximal : {}€".format(self.capaciteRemboursement))
		return "\n".join(msgs)

class PretSimulator(Simulator) :
	def __init__(self, configs, avecDepensesAdditionnelles, avecNombreDAnnees) :
		parametres = 																\
		["apport", "l'apport"], 													\
		["salaire", "le salaire"],													\
		["prixDuBien", "le prix du bien"],											\
		["tauxGarantie", "le taux de grantie"],										\
		["fraisGestion", "les frais de gestion"],									\
		["fraisNotaire", "les frais de notaire"],									\
		["tauxAnnuelPret", "le taux annuel du prêt"],								\
		["tauxAnnuelAssurance", "le taux annuel de l'assurance"],					\
		["nbMensualitesParAn", "le nombre  de mensualités par an"],					\
		["assuranceDegressive", "le fait que l'assurance soit dégressive ou non"]

		if avecNombreDAnnees :
			parametres += ["nbAnnees", "le nombre d'années"],

		if avecDepensesAdditionnelles :
			parametres += 															\
			["codePostal", "le code postal"],										\
			["redevanceTele", "la redevance télé"],									\
			["mensualiteMax", "la mensualité maximale"],							\
			["chargesCopro", "les charges de copropriété"],							\
			["prixLocatifMensuel", "le prix locatif mensuel estimé"]

		super().__init__(configs, [elem[0] for elem in parametres], [elem[1] for elem in parametres])
		self.avecDepenses = avecDepensesAdditionnelles
		self.avecAnnees = avecNombreDAnnees

	#Les villes avec arrondissements ont un code INSEE différent dans les fichiers de données
	def checkVilleAvecCodePostalParticulier(nomVille) :
		if "PARIS" in nomVille :
			return CsvUtilities.getInfosTaxes("75", 56)
		elif "MARSEILLE" in nomVille :
			return CsvUtilities.getInfosTaxes("13", 55)
		else :
			return None, None, None, None

	def compute(self) :
		if self.avecDepenses :
			self.nomVille, dpt, code = CsvUtilities.getInfosDeLaPoste(self.codePostal)
			if self.nomVille == None or dpt == None or code == None :
				print("Le code postal {} ne fait pas partie des données La Poste".format(self.codePostal))
				return False
			self.TFC, self.TFD, self.TEOM, self.TH = CsvUtilities.getInfosTaxes(dpt, code)
			if self.TFC == None or self.TFD == None or self.TEOM == None or self.TH == None : 
				self.TFC, self.TFD, self.TEOM, self.TH = PretSimulator.checkVilleAvecCodePostalParticulier(self.nomVille)
			if self.TFC == None or self.TFD == None or self.TEOM == None or self.TH == None : 
				print("Le code postal {} ne correspond à aucune donnée fournie par l'État".format(self.codePostal))
				return False
			self.THAnnuelle = self.prixLocatifMensuel / 2. / 1. * 12. * self.TH / 100.
			self.TFCAnnuelle = self.prixLocatifMensuel / 2. / 2. * 12. * self.TFC / 100.
			self.TFDAnnuelle = self.prixLocatifMensuel / 2. / 2. * 12. * self.TFD / 100.
			self.TEOMAnnuelle = self.prixLocatifMensuel / 2. / 2. * 12. * self.TEOM / 100.
			self.depensesAdditionnellesAnnuelles = self.THAnnuelle + self.TFCAnnuelle + self.TFDAnnuelle + self.TEOMAnnuelle + self.chargesCopro + self.redevanceTele
			self.depensesAdditionnellesMensuelles = self.depensesAdditionnellesAnnuelles / 12.
			self.depensesLocataireAnnuelles = self.THAnnuelle + self.redevanceTele + self.prixLocatifMensuel * 12
			self.depensesLocataireMensuelles = self.depensesLocataireAnnuelles / 12.
			self.enomomiesAnnuellesPropriete = self.depensesLocataireAnnuelles - self.depensesAdditionnellesAnnuelles
			self.enomomiesMensuellesPropriete = self.enomomiesAnnuellesPropriete / 12.

		self.coutNotaire = self.prixDuBien * self.fraisNotaire / 100.
		self.coutGarantie = self.prixDuBien * self.tauxGarantie / 100.
		self.mensualiteMaximale = (self.salaire * self.nbMensualitesParAn) / 12. / 3.
		self.capitalEmprunte = (self.prixDuBien + self.coutGarantie + self.fraisGestion + self.coutNotaire) - self.apport

		nbAnnees = 0
		mensualite = self.mensualiteMaximale + 1
		while mensualite > self.mensualiteMaximale or (self.avecDepenses and mensualite > self.mensualiteMax - self.depensesAdditionnellesMensuelles) : #Seulement avec add
			nbAnnees += 1
			coutTotalAssurance = 0
			nbMensualites = nbAnnees * 12
			capitalRestant = self.capitalEmprunte
			mensualiteHorsAssurance = Simulator.getMensualite(self.capitalEmprunte, self.tauxAnnuelPret, nbAnnees, 12)
			while capitalRestant > 0 :
				coutTotalAssurance += Simulator.getInteretRembourse(capitalRestant if self.assuranceDegressive else self.capitalEmprunte, self.tauxAnnuelAssurance, 12)
				interetsCourants = Simulator.getInteretRembourse(capitalRestant, self.tauxAnnuelPret, 12)
				capitalRembourse = mensualiteHorsAssurance - interetsCourants
				capitalRestant -= capitalRembourse
			mensualiteAssuranceLissee = coutTotalAssurance / nbMensualites
			mensualite = mensualiteHorsAssurance + mensualiteAssuranceLissee

		if self.avecAnnees and nbAnnees < self.nbAnnees :
			nbAnnees = self.nbAnnees
		elif not self.avecAnnees :
			self.nbAnnees = nbAnnees

		self.detailMensualites = []
		self.coutTotalAssurance = 0
		self.nbAnneesNecessaires = nbAnnees
		self.nbMensualites = Simulator.getNombreMensualites(self.nbAnnees, 12)
		self.mensualiteHorsAssurance = Simulator.getMensualite(self.capitalEmprunte, self.tauxAnnuelPret, self.nbAnnees, 12)

		idMensualite = 0
		capitalRestant = self.capitalEmprunte
		while capitalRestant > 0 :
			self.coutTotalAssurance += Simulator.getInteretRembourse(capitalRestant if self.assuranceDegressive else self.capitalEmprunte, self.tauxAnnuelAssurance, 12)
			interetsCourants = Simulator.getInteretRembourse(capitalRestant, self.tauxAnnuelPret, 12)
			capitalRembourse = self.mensualiteHorsAssurance - interetsCourants
			capitalRestant -= capitalRembourse
			idMensualite += 1

			self.detailMensualites.append((idMensualite, interetsCourants, capitalRembourse, capitalRestant))

		self.mensualiteAssuranceLissee = self.coutTotalAssurance / self.nbMensualites
		self.mensualite = self.mensualiteHorsAssurance + self.mensualiteAssuranceLissee
		self.totalInterets = Simulator.getTotalInterets(self.capitalEmprunte, self.nbAnnees, 12, self.mensualiteHorsAssurance)
		self.prixTotal = self.mensualite * self.nbMensualites

		if self.avecDepenses :
			self.nbAnneesPourRemboursementPret = int(math.ceil(self.prixTotal / self.enomomiesAnnuellesPropriete))

		return True

	def __repr__(self) :
		msgs = []
		msgs.append("Prix du bien : {:.2f}€".format(self.prixDuBien))
		msgs.append("Frais de gestion : {:.2f}€".format(self.fraisGestion))
		msgs.append("Coût de la garantie : {:.2f}€ ({:.2f}%), avec un remboursement à échéance possible de {:.2f}€".format(self.coutGarantie, self.tauxGarantie, self.coutGarantie * 75. / 100.))
		msgs.append("Frais de notaire : {:.2f}€ ({:.2f}%)".format(self.coutNotaire, self.fraisNotaire))
		msgs.append("Apport : {:.2f}€".format(self.apport))
		msgs.append("Capital emprunté : {:.2f}€".format(self.capitalEmprunte))
		msgs.append("Salaire mensuel net avant impôts : {:.2f}€ sur {} mois".format(self.salaire, self.nbMensualitesParAn))
		msgs.append("  Soit une mensualité maximale de {:.2f}€ (pour un endettement de 33%){}".format(self.mensualiteMaximale, "" if not self.avecDepenses else " face à un désir de {:.2f}€".format(self.mensualiteMax)))
		msgs.append("Taux annuel du prêt : {:.2f}%".format(self.tauxAnnuelPret))
		msgs.append("Taux annuel de l'assurance{}dégressive: {:.2f}%".format(" " if self.assuranceDegressive else " non ", self.tauxAnnuelAssurance))
		
		if self.avecDepenses :
			msgs.append("Le bien, d'une valeur locative mensuelle estimée à {:.2f}€, se situe à {} ({})".format(self.prixLocatifMensuel, self.nomVille, self.codePostal))
			msgs.append("  Redevance télé annuelle : {:.2f}€".format(self.redevanceTele))
			msgs.append("  Charges annuelles de copropriété : {:.2f}€".format(self.chargesCopro))
			msgs.append("  Montant annuel de la taxe d'habitation : {:.2f}€ ({:.2f}%)".format(self.THAnnuelle, self.TH))
			msgs.append("  Montant annuel des taxes foncières : {:.2f}€ (TFC:{:.2f}% + TFD:{:.2f}% + TEOM:{:.2f}%)".format(self.TFCAnnuelle + self.TFDAnnuelle + self.TEOMAnnuelle, self.TFC, self.TFD, self.TEOM))
			msgs.append("  Montant annuel cumulé des dépenses additionnelles de propriété : {:.2f}€, soit {:.2f}€ par mois".format(self.depensesAdditionnellesAnnuelles, self.depensesAdditionnellesAnnuelles / 12.))		
			msgs.append("  Montant annuel cumulé des dépenses additionnelles de location : {:.2f}€, soit {:.2f}€ par mois".format(self.depensesLocataireAnnuelles, self.depensesLocataireAnnuelles / 12.))		
		
		if self.avecAnnees and self.nbAnneesNecessaires != self.nbAnnees :
			salaireSuffisant = self.salaire >= self.mensualite * 3.
			msgs.append("Pour un tel prêt, la mensualité nécessaire est de {:.2f}€{}".format(self.mensualite + (0 if not self.avecAnnees else self.depensesAdditionnellesMensuelles), "" if salaireSuffisant else ", soit un salaire minimum de {:.2f}€".format(self.mensualite * 3.)))
			msgs.append("Avec {}, il faudrait {} ans pour remboursé ce prêt".format("la mensualité maximale actuelle" if salaireSuffisant else "le salaire actuel", self.nbAnneesNecessaires))
		else :
			preMsgs = []
			preMsgs.append("Détails des {} mensualités :".format(self.nbMensualites))
			for idMensualite, interetsCourants, capitalRembourse, capitalRestant in self.detailMensualites :
				preMsgs.append("Mensualité {: >3} : part des intérêts {: >7.2f}€, part du capital {: >7.2f}€, part de l'assurance {: >7.2f}€, capital restant {: >10.2f}€"
					.format(idMensualite, interetsCourants, capitalRembourse, self.mensualiteAssuranceLissee, capitalRestant))
			preMsgs.append("")
			msgs = preMsgs + msgs

			if self.avecDepenses and self.mensualiteMax <= self.depensesAdditionnellesMensuelles :
				msgs.append("La mensualité maximale désirée ne peut donc pas couvrir les dépenses additionnelles et le remboursement du prêt")
			else :
				if not self.avecAnnees :
					msgs.append("Avec une mensualité de {:.2f}€, le prêt sera remboursé en {} ans, soit {} mensualités".format(self.mensualite + (0 if not self.avecDepenses else self.depensesAdditionnellesMensuelles), self.nbAnnees, self.nbMensualites))
				else :
					msgs.append("Nombre d'années du prêt : {} ans, soit {} mensualités".format(self.nbAnnees, self.nbMensualites))
					msgs.append("Mensualité nécessaire : {:.2f}€".format(self.mensualite + (0 if not self.avecDepenses else self.depensesAdditionnellesMensuelles)))
				msgs.append("Avec une mensualité hors assurance{} de {:.2f}€, le total des intérêts s'élève à {:.2f}€".format("" if not self.avecDepenses else " et dépenses additionnelles", self.mensualiteHorsAssurance, self.totalInterets))
				msgs.append("Avec une assurance mensuelle lissée de {:.2f}€, le coût total de l'assurance s'élève à {:.2f}€".format(self.mensualiteAssuranceLissee, self.coutTotalAssurance))
				msgs.append("Avec un coût du prêt de {:.2f}€, on a un donc un remboursement de {:.2f}€".format(self.totalInterets + self.coutTotalAssurance, self.prixTotal))
				msgs.append("Il faut donc attendre la mensualité {} avant de ne pas revendre le bien à perte".format(math.ceil((self.totalInterets + self.coutTotalAssurance) / self.mensualite)))
			
				if self.avecDepenses and self.enomomiesAnnuellesPropriete < 0 :
					msgs.append("Les charges annuelles de propriété sont plus importantes que les charges de location ({:.2f}€ contre {:.2f}€)".format(self.depensesAdditionnellesAnnuelles, self.depensesLocataireAnnuelles))
					msgs.append("Ce bien coûtera donc {:.2f}€ de plus par mois si l'achat est réalisé".format(-self.enomomiesMensuellesPropriete))
				elif self.avecDepenses and self.enomomiesAnnuellesPropriete > 0 :
					msgs.append("Les charges annuelles de propriété sont moins importantes que les charges de location ({:.2f}€ contre {:.2f}€)".format(self.depensesAdditionnellesAnnuelles, self.depensesLocataireAnnuelles))
					msgs.append("Ce bien fera donc 'économiser' {:.2f}€ par mois si l'achat est réalisé".format(self.enomomiesMensuellesPropriete))
					msgs.append("En cumulant ces économies, on peut considérer que le prêt sera amorti au bout de {} ans après la signature".format(self.nbAnneesPourRemboursementPret))
		
		return "\n".join(msgs)

def main() :
	configs = ConfigLoader()

	ret = None
	while ret not in [1, 2, 3, 4, 5] :
		msgs = []
		msgs.append("Quelle type de simulation voulez-vous lancer ? :")
		msgs.append("1- Capacité maximale de remboursement")
		msgs.append("2- Nombre d'années nécessaire suivant un salaire")
		msgs.append("3- Mensualité nécessaire suivant un nombre d'années et un salaire")
		msgs.append("4- Nombre d'années nécessaire suivant un salaire et des dépenses additionnelles")
		msgs.append("5- Mensualité nécessaire suivant un nombre d'années, un salaire et des dépenses additionnelles")
		msgs.append("")

		ret = input("\n".join(msgs))
		try :
			ret = int(ret)
		except :
			ret = None

	try :
		if ret == 1 :
			simulation = MaxCapacitySimulator(configs)
		elif ret == 2 :
			simulation = PretSimulator(configs, False, False)
		elif ret == 3 :
			simulation = PretSimulator(configs, False, True)
		elif ret == 4 :
			simulation = PretSimulator(configs, True, False)
		elif ret == 5  :
			simulation = PretSimulator(configs, True, True)
	except :
		return

	if simulation.compute() :
		print(simulation)
	
if __name__ == "__main__" :
	main()
	input()
