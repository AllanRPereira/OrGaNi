import sys
import os
import shelve
import time
import Organi_Core as oc

code_RED = "\033[1;31m"
code_WHITE = "\033[1;39m"
code_GREEN = "\033[1;32m"
code_YELLOW = "\033[1;33m"
code_END = "\033[0m"

def core():
	if "Files" not in os.listdir():
		try:
			print("%sIniciando configurações%s" % (code_YELLOW, code_END))
			print("%sDownload página inicial!%s" % (code_GREEN, code_END))
			html = oc.get_main()
			print("%sGerando mapa de links!%s" % (code_GREEN, code_END))
			links = oc.gen_links(html)
			print("%sBaixando cada link do mapa!%s" % (code_GREEN, code_END))
			father_group = oc.gen_table_ext(links)
			print("%sSalvando arquivos no banco de dados%s" % (code_GREEN, code_END))
			oc.gen_db_ext(father_group)
			print("%sProcesso finalizado!%s" % (code_GREEN, code_END))
			os.chdir("..")
			time.sleep(3)
		except Exception as e:
			print("%sError!! Type%s:%s%s%s" % (code_WHITE, code_END, code_RED, e, code_END))
			return False
	return True

def start_app(*argv):
	if len(argv) < 3:
		print("%sVocê não inseriu as opções\nDê uma olhada no -help%s" % (code_RED, code_END))
		return False

	if core() == False:
		print("%sHouve um erro no Core!%s" % (code_RED, code_END))
		return False

	try:
		os.mkdir("Organized_Files")
		os.chdir("Organized_Files")
	except:
		os.chdir("Organized_Files")

	if argv[2] == "ext":
		db = shelve.open("../Files/extensions", "r")
		start_core(argv[1], db, 0)
		db.close()
	elif argv[2] == "common":
		db = shelve.open("Files/extensions", "r")
		start_core(argv[1], db, 1)
		db.close()
	else:
		return False
	return True

def start_core(path, db_object, mode):
	for path, list_path, files in os.walk(path):
		for file in files:
			name, ext = os.path.splitext(file)
			ext = ext.replace(".", "")
			list_mode = [ext.capitalize()]
			try:
				list_mode.append(db_object[ext][1])
			except:
				mode = 0
			try:
				os.mkdir(list_mode[mode])
				os.chdir(list_mode[mode])
			except:
				os.chdir(list_mode[mode])
			finally:
				os.replace(os.path.join(path, file), os.path.join(os.getcwd(), file))
				os.chdir("..")


if __name__ == "__main__":
	app = start_app(*sys.argv)
	print("%sProcesso finalizado!!%s" % (code_WHITE, code_END))
	sys.exit()