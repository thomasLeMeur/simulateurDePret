import csv
import FileUtilities

#On renvoie (le nom de la ville (str), le numéro INSEE du département (str car on peut avoir 2A par exmeple), le numéro de commune INSEE (int))
def getInfosDeLaPoste(codePostal) :
	def func(file) :
		reader = csv.reader(file)
		reader.__next__() #On passe la ligne des headers
		line = next(((codeINSEE, nom) for codeINSEE, nom, code in reader if int(code) == codePostal), None)
		if line != None :
			return line[1], line[0][:2], int(line[0][2:])
		else :
			return None, None, None

	return FileUtilities.openFileAndApply("datas/laposte_hexasmal_simplified.csv", func)

#On renvoie les taux de (TFC, TFD, TEOM, TH)
def getInfosTaxes(departement, codeCommune) :
	def func(file) :
		reader = csv.reader(file)
		reader.__next__() #On passe la ligne des headers
		line = next(((t1, t2, t3, t4) for dpt, index, _, t1, t2, t3, t4 in reader if dpt == departement and int(index) == codeCommune), None)
		if line != None :
			return float(line[0]), float(line[1]), float(line[2]), float(line[3])
		else :
			return None, None, None, None

	return FileUtilities.openFileAndApply("datas/REI_2018_simplified.csv", func)

