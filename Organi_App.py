#-*- coding:utf-8 -*-


import sys
import os
import shelve
import time
import threading
import Organi_Core as oc
import subprocess
from tkinter import *

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
tk_instance_string = 0
set_print_instance = 0

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

def print_instance(text, files_to_format="" , exception="", cycle=False, **argvs):
	global set_print_instance, tk_instance_string
	if set_print_instance == 1:
		if exception != "":
			text = "Error Type: {}".format(exception)

		tk_instance_string.insert(END, text.strip("{}").strip("\n") + "\n")
		
		if cycle:
			last_column = int(tk_instance_string.index(END)[0]) - 2
			string_index_init = "{}.{}".format(last_column, 0)
			string_index_end = "{}.{}".format(last_column+1, 0)
			tk_instance_string.delete(string_index_init, string_index_end)
	else:
		print(text.format(*files_to_format), *argvs)


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
  """
	print_instance(_help, format_help)
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
	cond_one = os.path.isdir(argv[1]),
	cond_two = os.path.isdir(argv[2])
	cond_three = os.path.commonpath([argv[1], argv[2]]) != argv[1]
	cond_four = check_db()

	if not cond_one:
		print_instance("{}Diretório de {}{}path_from{}{} inválido!{}", (code_RED, code_END, code_BLACK, code_END, code_RED, code_END))
	elif not cond_two:
		print_instance("{}Diretório de {}{}path_to{}{} inválido!{}", (code_RED, code_END, code_BLACK, code_END, code_RED, code_END))
	elif not cond_three:
		print_instance("{}path_to{}{} não pode estar dentro de {}{}path_from{}", (code_BLACK,code_END, code_RED, code_END, code_BLACK, code_END))
	elif not cond_four:
		print_instance("{}Banco de Dados não existe! Dê uma olhada no --help ou use --update{}", (code_RED, code_END))
	else:
		pass
	
	return True

def progress():
	"""
	Thread que verifica o progresso do download, e o exibe. Sempre reseta ao fim do thread
	"""
	global set_print_instance

	while oc._progress <= 100 and progress_var == True and set_print_instance != 1:
		n = int(oc._progress) if int(oc._progress + 0.5) >= oc._progress else int(oc._progress) + 1
		print_instance("{}{}{}{}% dos arquivos baixados{}", (code_CLEAR_LINE, code_MOVE_INIT, code_PURPLE, n, code_END), flush=True, end="")
		time.sleep(1)
	else:
		print_instance("Fazendo Download dos Arquivos...")
		while progress_var == True:
			print_instance("Fazendo Download dos Arquivos...", cycle=True)

	oc._progress = 0

def update():
	"""
	Atualiza ou Cria o Banco de Dados
	"""

	try:
		global progress_var		

		print_instance("{}Iniciando update{}", (code_YELLOW, code_END))
		print_instance("{}Download página inicial!{}", (code_GREEN, code_END))
		html = oc.get_main()
		
		print_instance("{}Gerando mapa de links!{}", (code_GREEN, code_END))
		links = oc.gen_links(html)

		print_instance("{}Baixando cada link do mapa e Gerando tabelas!{}", (code_GREEN, code_END))
		thread_progress = threading.Thread(target=progress).start()
		oc.down_links(links)
		progress_var = False
		print_instance("\n{}Download Concluído!{}", (code_GREEN, code_RED))		

		print_instance("{}Salvando arquivos no banco de dados{}", (code_GREEN, code_END))
		oc.gen_db_ext()

		print_instance("{}Update finalizado{}", (code_GREEN, code_END))
		os.chdir("..")

		time.sleep(2)
	except Exception as e:
		print_instance("{}Error!! Type {}:{}{}{}", (code_WHITE, code_END, code_RED, e, code_END), expection=e)
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
	global set_print_instance
	global tk_instance_string
	
	if argv[0] == "Graphics":
		set_print_instance = 1
		tk_instance_string = argv[len(argv) - 2]

	if len(argv) <= 2 or argv[0] == "Graphics":
		response = args_check(argv[::-1][2])
		if response == False and response not in (0,1):
			print_instance("{}Argumentos inválidos! Olhe o --help{}", (code_RED, code_END))
			return False

	try:
		os.mkdir(argv[2])
	except Exception as e:
		pass

	condition(*argv)
	os.chdir(argv[2])	

	mode_function = args_check(argv[3])
	db = shelve.open(abs_dir_db, "c")
	if mode_function == False and mode_function != 0:
		print_instance("{}Você não digitou nenhum comando! Por favor, consulte o --help{}")
	else:
		if argv[0] == "Graphics":
			init_app(argv[1], argv[2], db, mode_function, argv[::-1][0])
		else:
			init_app(argv[1], argv[2], db, mode_function)

	return True

def init_app(path_from, path_to, db_object, mode, month_replace=(1,1)):
	"""
	O Cerebro do App
	"""
	global set_print_instance
	global md5_list_file
	n_files = 1
	print_instance("{}{}{}Processando arquivos... {}{}", (code_CLEAR_LINE, code_MOVE_INIT, code_GREEN, n_files, code_END), end="", flush=True)
	for path, list_path, files in os.walk(path_from):
		for aqv in files:
			print_instance("{}{}{}Processando arquivos... {}{}", (code_CLEAR_LINE, code_MOVE_INIT, code_GREEN, n_files, code_END), end="", flush=True, cycle=True)
			n_files += 1
			name, ext = os.path.splitext(aqv)
			ext = ext.replace(".", "")
			ext = ext if ext != "" else "others"
			list_mode = [ext.capitalize()]
			file_info = subprocess.getoutput("ls -l \"{}/{}\"".format(path, aqv)).split(" ")
			file_date_month = file_info[5].capitalize()
			try:
				list_mode.append(db_object[ext][1]) 
			except:
				msg = "File {}: não foi encontrado no Db, será adicionado em uma pasta com sua extensão!\n".format(name)
				log(msg)
				list_mode.append(ext.capitalize())
			try:
				os.mkdir(list_mode[mode])
				os.chdir((list_mode[mode]))
			except:
				os.chdir(list_mode[mode])

			if month_replace != "" and month_replace[0] == 1:
				try:
					os.mkdir(file_date_month)
					os.chdir(file_date_month)
				except:
					os.chdir(file_date_month)
			try:
				files_local = os.path.join(path, aqv)
				md5_file = subprocess.run(["md5sum", "{}".format(files_local)], stdout=subprocess.PIPE)
				md5_file = md5_file.stdout.decode().split()[0]

				if md5_file in md5_list_file and month_replace[1] == 1:
					pass
				else:
					os.replace(os.path.join(path, aqv), os.path.join(os.getcwd(), aqv))
					md5_list_file += (md5_file,)
			except Exception as e:
				print_instance("{}Error: {}{}", (code_RED, e, code_END), exception=e)
			os.chdir("..")
			if month_replace[0] == 1:
				os.chdir("..")

	if set_print_instance == 1:
		print_instance("Arquivos Organizados!!")
if __name__ == "__main__":
	print_instance("{}Bem Vindo! {} {}",(code_BLACK, os.uname()[1].capitalize(), code_END))
	app = start_app(*sys.argv)
	print_instance("{}Processo finalizado!!{}",(code_WHITE, code_END))
	sys.exit()
