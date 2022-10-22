#-*- coding:utf-8 -*-


from calendar import month
import sys
import os
import shelve
import time
import threading
import organi.src.core as oc
import organi.src.interface as interface
from datetime import datetime

# Constantes para estilo no terminal
RED = "\033[1;31m"
WHITE = "\033[1;39m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
PURPLE = "\033[1;35m"
BLACK = "\033[1;40m"
END = "\033[0m"
MOVE_INIT = "\033[1G"
CLEAR_LINE = "\033[2K"
ABS_DIR_DB = ""
ABS_DIR_LOG = os.path.join(os.getcwd(), "log.txt")
SET_PRINT_INSTANCE = 0
SOFTWARE_STATE = True
MONTH = {
	1 : "Janeiro",
	2 : "Fevereiro",
	3 : "Março",
	4 : "Abril",
	5 : "Maio",
	6 : "Junho",
	7 : "Julho",
	8 : "Agosto",
	9 : "Setembro",
	10 : "Outubro",
	11 : "Novembro",
	12 : "Dezembro",
}
TK_INSTANCE = 0

def print_instance(text, files_to_format="" , exception="", cycle=False, **argvs):
	global SET_PRINT_INSTANCE, TK_INSTANCE
	if SET_PRINT_INSTANCE == 1:
		if exception != "":
			text = "Error Type: {}".format(exception)

		TK_INSTANCE.insert(END, text.strip("{}").strip("\n") + "\n")
		
		if cycle:
			last_column = int(TK_INSTANCE.index(END)[0]) - 2
			string_index_init = "{}.{}".format(last_column, 0)
			string_index_end = "{}.{}".format(last_column+1, 0)
			TK_INSTANCE.delete(string_index_init, string_index_end)
	else:
		print(text.format(*files_to_format), **argvs)


def log(error: str) -> tuple:
	"""
	Função que grava o log de erro para consulta
	"""
	try:
		with open(ABS_DIR_LOG, "a") as file_log:
			file_log.write(error)
	except Exception as exception:
		return (False, exception)
	
	return (True, "")

def help() -> bool:
	"""
	Help do software
	"""

	_help =  f"""
  {YELLOW}OrGaNi{END}
    Software voltado para organização de arquivos e backups.

  {YELLOW}Funcionamento{END}
    O software funciona da seguinte forma:

    {PURPLE}python3 -m organi PATH_FROM PATH_TO [--mode]{END}

    {PURPLE}path_from{END} : Diretório que será organizado, caso haja alguma pasta que possua permissão de root,""" \
	f""" use `sudo` antes do python3.\n	Obs.: Os arquivos nessa pasta serão movidos!.

    {PURPLE}path_to{END} : Diretório para onde os arquivos serão movidos.
	Obs.: Esse diretório não pode estar dentro do `path_from` e não recomenda-se que haja arquivos nele.
	E já não deve existir antes da execução do programa

    {PURPLE}mode{END} : Modos para organização, podem ser `--ext` ou `--common`.
	
    {YELLOW}Ext{END}
    {PURPLE}   
	path_to/
		|--- Png/
		|------ *.png
		|--- Mp3/
		|------ *.mp3
		|--- .../
    {END}
	{END}
    {YELLOW}Common{END}
    {PURPLE}	  
	path_to/
		|--- Images/
		|------ *.png, *.jpg
		|--- Sounds/
		|------ *.mp3, *.wav
		|--- .../
    {END}
  {YELLOW}Algumas outras funções!{END}
    {PURPLE}--update (-p){END}

	Atualiza o banco de dados da aplicação, é necessário para executa-lá.

    {PURPLE}--help (-h){END}

	Mostra o menu de ajuda, com todas as informações da aplicação.

    {PURPLE}--month (-m){END}

	Além da organização já definida pelo modo, também irá organizar de acordo com o mês de criação do arquivo
    
    {PURPLE}--gui (-g){END}

	Irá executar no modo interface gráfica, entretanto não está funcionando corretamente.

  {YELLOW}Exemplo{END}
  
    {PURPLE}python3 Organi_App.py --update{END}
    {PURPLE}python3 Organi_App.py /home/carlinhos /home/arquivos_organizados_carlinhos --ext{END}
  """
	print_instance(_help)
	return True

def check_db() -> bool:
	"""
	Confere se o Db existe e força o update caso não
	"""
	global ABS_DIR_DB
	ABS_DIR_DB = os.path.join(os.getcwd(), "extensions.db")
	return os.path.isfile("extensions.db")

def condition(*argv):
	"""
	Principais condições do software
	"""
	cond_one = os.path.isdir(argv[1])
	cond_two = os.path.isdir(argv[2])
	cond_three = os.path.commonpath([argv[1], argv[2]]) != argv[1]
	cond_four = check_db()

	if not cond_one:
		print_instance("{}Diretório de {}{}path_from{}{} inválido!{}", (RED, END, BLACK, END, RED, END))
	elif not cond_two:
		print_instance("{}Diretório de {}{}path_to{}{} inválido!{}", (RED, END, BLACK, END, RED, END))
	elif not cond_three:
		print_instance("{}path_to{}{} não pode estar dentro de {}{}path_from{}", (BLACK,END, RED, END, BLACK, END))
	elif not cond_four:
		print_instance("{}Banco de Dados não existe! Dê uma olhada no --help ou use --update{}", (YELLOW, END))
		return "BD"
	else:
		return True
	
	return False

def progress():
	"""
	Thread que verifica o progresso do download, e o exibe. Sempre reseta ao fim do thread
	"""
	global SET_PRINT_INSTANCE
	global SOFTWARE_STATE
	while oc._progress <= 100 and progress_var == True and SET_PRINT_INSTANCE != 1:
		if not SOFTWARE_STATE: return False
		n = int(oc._progress) if int(oc._progress + 0.5) >= oc._progress else int(oc._progress) + 1
		print_instance("{}{}{}{}% dos arquivos baixados{}", (CLEAR_LINE, MOVE_INIT, PURPLE, n, END), flush=True, end="")
		time.sleep(1)

	oc._progress = 101
	return True

def update():
	"""
	Atualiza ou Cria o Banco de Dados
	"""
	try:
		global progress_var		

		print_instance("{}Iniciando update{}", (YELLOW, END))
		print_instance("{}Download página inicial!{}", (GREEN, END))
		html = oc.get_main()
		
		print_instance("{}Gerando mapa de links!{}", (GREEN, END))
		links = oc.gen_links(html)

		print_instance("{}Baixando cada link do mapa e Gerando tabelas!{}", (GREEN, END))
		threading.Thread(target=progress).start()
		oc.down_links(links)
		time.sleep(1) # Sincronizar 100%
		progress_var = False

		print_instance("\n{}Download Concluído!{}", (GREEN, RED))

		print_instance("{}Salvando arquivos no banco de dados{}", (GREEN, END))
		oc.gen_db_ext()

		print_instance("{}Update finalizado{}", (GREEN, END))
		os.chdir("..")

		time.sleep(2)
	except Exception as e:
		global SOFTWARE_STATE
		SOFTWARE_STATE = False
		print_instance("{}Error!! Type {}:{}{}{}", (WHITE, END, RED, e, END), exception=e)
		return False

	return True

def graphics() -> bool:
	try:
		threading.Thread(target=interface.interface_creation).start()
	except Exception as e:
		print_instance("{}Error!! Type {}:{}{}{}", (WHITE, END, RED, e, END), exception=e)
		return False
	return True

def args_check(arg: list) -> bool:
	"""
	Checagem de argumentos
	"""

	avaliable_args = {
		("--help", "-h") : help, 
		("--update", "-p") : update,
		("--gui", "-g") : graphics,
		("--ext", "-e") : 0, 
		("--common", "-c") : 1
	}
	for key, value in avaliable_args.items():
		if arg in key:
			return (True, value)
	return (False, None)

def start_app(*argv:list) -> bool:
	"""
	O coração do App
	"""
	global SET_PRINT_INSTANCE
	global TK_INSTANCE
	response_check = False
	month_mode = False
	argv = list(argv)
	if "-m" in argv or "--month" in argv:
		month_mode = True
		if "-m" in argv: argv.remove("-m")
		if "--month" in argv: argv.remove("--month")
		

	if argv[0] == "Graphics":
		SET_PRINT_INSTANCE = 1
		TK_INSTANCE = argv[len(argv) - 2]
		response_check = args_check(argv[::-1][2])
	else:
		response_check = args_check(argv[::-1][0])

	if not response_check[0]:	
		print_instance("{}Argumentos inválidos! Olhe o --help{}", (RED, END))
		return False
	elif callable(response_check[1]):
		return response_check[1]()
	try:
		os.mkdir(argv[2])
	except Exception as e:
		print_instance("{}Error: {} {}", (RED,e,END))
		return False
	
	condition_return = condition(*argv)

	if condition_return == False:
		return False
	elif condition_return == "BD":
		if response_check[1] == 0:
			pass
		else:
			print_instance("{}Modo de agrupamento --common necessita do banco de dados!{}", (RED, END))
			return False

	mode_function = response_check[1]
	
	if mode_function != 0:
		db = shelve.open(ABS_DIR_DB, "c")
	else:
		db = None

	if argv[0] == "Graphics":
		init_app(argv[1], argv[2], db, mode_function, argv[::-1][0], month_mode=month_mode)
	else:
		init_app(argv[1], argv[2], db, mode_function, month_mode=month_mode)

	return True

def change_dir(path:str) -> bool:
	try:
		if not os.path.isdir(path):
			os.mkdir(path)
		os.chdir(path)
	except Exception as error:
		print_instance("{}Error: {}{}", (RED, error, END), exception=error)
		return False
	return True

def init_app(path_from, path_to, db_object, mode, month_mode=False):
	"""
	O Cerebro do App
	"""
	global SET_PRINT_INSTANCE, MONTH
	n_files = 1

	#Mudança de contexto
	os.chdir(path_to)

	print_instance("{}{}{}Processando arquivos... {}{}", (CLEAR_LINE, MOVE_INIT, GREEN, n_files, END), end="", flush=True)
	for path, list_path, files in os.walk(path_from):
		for aqv in files:
			print_instance("{}{}{}Processando arquivos... {}{}", (CLEAR_LINE, MOVE_INIT, GREEN, n_files, END), end="\t", flush=True, cycle=True)
			n_files += 1
			name, ext = os.path.splitext(aqv)
			ext = ext.replace(".", "")
			ext = ext if ext != "" else "others"
			list_mode = [ext.capitalize(),]

			file_date = os.path.getmtime(os.path.join(path, aqv))
			file_date_month = MONTH[datetime.fromtimestamp(file_date).month]
		
			if month_mode:
				path_month = os.path.join(os.getcwd(), file_date_month)
				if not change_dir(path_month):
					return False

			if db_object != None and mode == 1:
				try:
					if ext in db_object:
						category = db_object[ext][1]
					else:
						category = list_mode[0]
					path_category = os.path.join(os.getcwd(), category)	
					if not change_dir(path_category):
						return False
				except Exception as error:
					print_instance("{}Error: {}{}", (RED, error, END), exception=error)
			else:
				if not change_dir(list_mode[mode]):
					return False

			try:
				os.replace(os.path.join(path, aqv), os.path.join(os.getcwd(), aqv))
			except Exception as error:
				print_instance("{}Error: {}{}", (RED, error, END), exception=error)
			os.chdir(path_to)


	if SET_PRINT_INSTANCE == 1:
		print_instance("Arquivos Organizados!!")

def organiApp(*args:tuple) -> bool:
	print_instance("{}Bem Vindo! {} {}",(BLACK, os.uname()[1].capitalize(), END))
	start_app(*args)
	print_instance("\n{}Processo finalizado!!{}",(WHITE, END))
	return True

if __name__ == "__main__":
	organiApp(*sys.argv)
