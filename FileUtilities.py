def openFileAndApply(filename, funcToApply) :
	try :
		with open(filename) as f :
			return funcToApply(f)
	except :
		print("Le fichier {} est manquant ou mal formaté".format(filename))
		raise

