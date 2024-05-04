def openFileAndApply(filename, funcToApply) :
	try :
		with open(filename, encoding="utf-8") as f :
			return funcToApply(f)
	except :
		print("Le fichier {} est manquant ou mal formaté".format(filename))
		raise

