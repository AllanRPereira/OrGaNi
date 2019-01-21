#-*- coding:utf-8 -*-


import sys
import os
import shelve
import time
import threading
import Organi_Core as oc
import subprocess

code_RED = "\033[1;31m"
code_WHITE = "\033[1;39m"
code_GREEN = "\033[1;32m"
code_YELLOW = "\033[1;33m"
code_PURPLE = "\033[1;35m"
code_BLACK = "\033[1;40m"
code_END = "\033[0m"
code_MOVE_INIT = "\033[1G"
code_CLEAR_LINE = "\033[2K"
abs_dir_db = ""
abs_dir_log = os.path.join(os.getcwd(), "log.txt")
progress_var = True
md5_list_file = tuple()

format_help = (code_YELLOW, code_END,
 	code_YELLOW, code_END,
  	code_PURPLE, code_END, 
  	code_PURPLE, code_END, 
  	code_PURPLE, code_END,
  	code_PURPLE, code_END, 
	code_YELLOW, code_END, 
	code_PURPLE, code_END, 
	code_YELLOW, code_END, 
	code_PURPLE, code_END,
	code_YELLOW, code_END,
	code_PURPLE, code_END,
	code_PURPLE, code_END,
	code_YELLOW, code_END,
	code_PURPLE, code_END,
	code_PURPLE, code_END)

def log(error):
	"""
	Função que gera arquivo, para eventuais erros em relação as extensões.
	"""

	log = open(abs_dir_log, "a")
	log.write(error)
	log.close()

def help():
	"""
	Help do software
	"""

	_help =  """
  {}OrGaNi{}
    Software voltado para organização de arquivos com base nas preferências do usuário. Esse software foi testado apenas no Deepin 15.
  {}Funcionamento{}
    O software funciona da seguinte forma:

    {}python3 Organi_App.py PATH_FROM PATH_TO [--mode]{}

    {}path_from{} : Diretório que será organizado, caso haja alguma pasta que possua permissão de root, use `sudo` antes do python3. Obs.: Os arquivos 
    nessa pasta serão movidos!.

    {}path_to{} : Diretório para onde os arquivos serão movidos. Obs.: Esse diretório não pode estar dentro do `path_from` e não recomenda-se que haja arquivos nele.

    {}mode{} : Modos para organização, podem ser `--ext` ou `--common`. Obs.: O modo common ainda não está 100%.

    {}Ext{}
    {}   path_to/
	        |--- Png/
		    |------ *.png
		    |--- Mp3/
		    |------ *.mp3
		    |--- .../
    {}

    {}Common{}
    {}	  path_to/
		    |--- Images/
		    |------ *.png, *jpg
		    |--- Sounds/
		    |------ *.mp3, *.wav
		    |--- .../
    {}
  {}Algumas outras funções!{}
    {}--update (-p){}

      Atualiza o banco de dados da aplicação, é necessário para executa-lá.

    {}--help (-h){}

	  Mostra o menu de ajuda, com todas as informações da aplicação.
  {}Exemplo{}
  
    {}python3 Organi_App.py --update{}
    {}python3 Organi_App.py /home/carlinhos /home/arquivos_organizados_carlinhos --ext{}
  """.format(*format_help)
	print(_help)
	return True

def check_db():
	"""
	Checka se o Db existe, e força o update caso não
	"""

	global abs_dir_db
	abs_dir_db = os.path.join(os.getcwd(), "extensions.db")
	return os.path.isfile("extensions.db")

def condition(*argv):
	"""
	Principais condições do software
	"""

	assert os.path.isdir(argv[1]), "{}Diretório de {}{}path_from{}{} inválido!{}".format(code_RED, code_END, code_BLACK, code_END, code_RED, code_END)
	assert os.path.isdir(argv[2]), "{}Diretório de {}{}path_to{}{} inválido!{}".format(code_RED, code_END, code_BLACK, code_END, code_RED, code_END)
	assert os.path.commonpath([argv[1], argv[2]]) != argv[1], "{}path_to{}{} não pode estar dentro de {}{}path_from{}".format(code_BLACK,code_END, code_RED, code_END, code_BLACK, code_END)
	assert check_db(), "{}Banco de Dados não existe! Dê uma olhada no --help ou use --update{}".format(code_RED, code_END)

def progress():
	"""
	Thread que verifica o progresso do download, e o exibe. Sempre resetar ao fim do thread
	"""

	while oc._progress <= 100 and progress_var == True:
		n = int(oc._progress) if int(oc._progress + 0.5) >= oc._progress else int(oc._progress) + 1
		print("{}{}{}{}% dos arquivos baixados{}".format(code_CLEAR_LINE, code_MOVE_INIT, code_PURPLE, n, code_END), flush=True, end="")
		time.sleep(1)
	oc._progress = 0

def update():
	"""
	Atualiza ou Cria o Banco de Dados
	"""

	try:
		global progress_var		

		print("{}Iniciando update{}".format(code_YELLOW, code_END))
		print("{}Download página inicial!{}".format(code_GREEN, code_END))
		html = oc.get_main()
		
		print("{}Gerando mapa de links!{}".format(code_GREEN, code_END))
		links = oc.gen_links(html)

		print("{}Baixando cada link do mapa e Gerando tabelas!{}".format(code_GREEN, code_END))
		thread_progress = threading.Thread(target=progress).start()
		oc.down_links(links)
		progress_var = False
		print("\n{}Download Concluído!{}".format(code_GREEN, code_RED))		

		print("{}Salvando arquivos no banco de dados{}".format(code_GREEN, code_END))
		oc.gen_db_ext()

		print("{}Update finalizado{}".format(code_GREEN, code_END))
		os.chdir("..")

		time.sleep(2)
	except Exception as e:
		print("{}Error!! Type{}:{}{}{}".format(code_WHITE, code_END, code_RED, e, code_END))
		return False

	return True

def args_check(arg):
	"""
	Checagem de argumentos
	"""

	dict_of_args = {("--help", "-h"):"help", ("--update", "-p"):"update", ("--ext", "-e"):0, ("--common", "-c"):1}
	for key, value in dict_of_args.items():
		if arg in key:
			try:
				return globals()[value]()
			except:
				return value
	return False

def start_app(*argv):
	"""
	O coração do App
	"""

	if len(argv) <= 2:
		assert args_check(argv[len(argv) - 1]), "{}Argumentos inválidos! Olhe o --help{}".format(code_RED, code_END)
		return True

	try:
		os.mkdir(argv[2])
	except Exception as e:
		print("{}Error: {}{}".format(code_RED, e, code_END))


	condition(*argv)

	os.chdir(argv[2])	


	mode_function = args_check(argv[3])
	db = shelve.open(abs_dir_db, "c")
	if mode_function == False and mode_function != 0:
		print("{}Você não digitou nenhum comando! Por favor, consulte o --help{}")
	else:
		init_app(argv[1], argv[2], db, mode_function)

	return True

def init_app(path_from, path_to, db_object, mode):
	"""
	O Cerebro do App
	"""
	global md5_list_file
	n_files = 1

	for path, list_path, files in os.walk(path_from):
		for aqv in files:
			print("{}{}{}Processando arquivos:{}{}".format(code_CLEAR_LINE, code_MOVE_INIT, code_GREEN, n_files, code_END), end="", flush=True)
			n_files += 1
			name, ext = os.path.splitext(aqv)
			ext = ext.replace(".", "")
			ext = ext if ext != "" else "others"
			list_mode = [ext.capitalize()]
			file_info = subprocess.getoutput("ls -l \"{}/{}\"".format(path, aqv)).split(" ")
			file_date = file_info[5].capitalize()
			try:
				list_mode.append(db_object[ext][1]) 
			except:
				msg = "File: não foi encontrado no Db, será adicionado em uma pasta com sua extensão!"
				log(msg)
				list_mode.append(ext.capitalize())
			try:
				os.mkdir(list_mode[mode])
				os.chdir((list_mode[mode]))
			except:
				os.chdir(list_mode[mode])
			try:
				os.mkdir(file_date)
				os.chdir(file_date)
			except:
				os.chdir(file_date)
			try:
				files_local = os.path.join(path, aqv)
				md5_file = subprocess.run(["md5sum", "{}".format(files_local)], stdout=subprocess.PIPE)
				md5_file = md5_file.stdout.decode().split()[0]

				if md5_file in md5_list_file:
					pass
				else:
					os.replace(os.path.join(path, aqv), os.path.join(os.getcwd(), aqv))
					md5_list_file += (md5_file,)
			except Exception as e:
				print("{}Error: {}{}".format(code_RED, e, code_END))
			os.chdir("..")
			os.chdir("..")
	print("")
if __name__ == "__main__":
	print("{}Bem Vindo! {} {}".format(code_BLACK, os.uname()[1].capitalize(), code_END))
	app = start_app(*sys.argv)
	print("{}Processo finalizado!!{}".format(code_WHITE, code_END))
	sys.exit()
