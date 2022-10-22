#-*- coding:utf-8 -*-

import urllib.request
import shelve
import os
import subprocess
import concurrent.futures
"""
OrGaNi_Core, parte responsável pelo update do banco de dados!
"""
_progress = 0
_father_group = []
_all_html_code = []


def get_main() -> str:
	"""
	Obtém o html principal da página File-Extensions e o retorna.
	"""

	html = urllib.request.urlopen("https://www.file-extensions.org")
	aqv_read = html.read()
	html.close()
	return str(aqv_read)

def gen_links(html:str) -> list:
	"""
	A partir do HTML principal, ele captura o menu principal e retorna uma lista com as urls desse menu.
	"""

	prefix = "https://www.file-extensions.org"

	s = html.find("<ul class=\"submenu01\">")
	f = html.find("</ul>", s)
	menu = html[s:f] + "<ul>"
	list_of_links= []

	while menu.find("href=") != -1:
		s = len("href=") + menu.find("href=") + 1
		f = menu.find("\"", s)
		list_of_links.append(prefix + menu[s:f])
		menu = menu[f:]

	del list_of_links[0] # Extensões comuns

	return list_of_links

def instance_download(link:str, time_max:int) -> bool:
	global _progress
	global _all_html_code

	_HTMLCode = urllib.request.urlopen(link, timeout=time_max)
	_HTMLCodeData = _HTMLCode.read()
	_HTMLCodeStr = _HTMLCodeData.decode()
	_progress += 100/93
	_all_html_code.append((link, _HTMLCodeStr))

	#list_extra_links_names = gen_page_links(_HTMLCodeStr, link)

	return True

def thread_downloads(list_links:list) -> bool:

	with concurrent.futures.ThreadPoolExecutor(max_workers=len(list_links)) as thread_html:
		dict_threads = {thread_html.submit(instance_download, link, 20): link for link in list_links}
		for thread_unit in concurrent.futures.as_completed(dict_threads):    
			link = dict_threads[thread_unit]
			try:
				status_thread = thread_unit.result()
				if not status_thread:
					raise Exception("")
			except Exception as exc:
				print(f'{link} não pode ser baixado: Erro {exc}')
				
	return True

def down_links(list_of_links:list) -> bool:
	"""
	Recebe uma lista de links e faz o download destes e caso haja um sublink específico no no código HTML
	faz o download deste também!
	"""
	global _father_group
	global _all_html_code
	global _progress
	identificador = 0

	try:
		os.mkdir("Files")
	except Exception as err:
		print(f"Error: {err}")
	finally:
		os.chdir("Files")

	thread_downloads(list_of_links)
	list_of_secondary_links = []
	for link, _HTMLCode in _all_html_code:
		list_of_secondary_links.extend(gen_page_links(_HTMLCode, link))
	thread_downloads(list_of_secondary_links)

	for link, _HTMLCode in _all_html_code:
		start = link.find("name/") + len("name/")
		end = len(link) if link.find("/", start) == -1 else link.find("/", start) 
		src_file = link[start:end] + "_{}.html".format(identificador)
		identificador += 1
		gen_table_ext(_HTMLCode, src_file) #Gera tabela para esse HTML
		_father_group.append(src_file)

	return True

def gen_page_links(_HTMLCodeSecund:str, prefix_link:str) -> list:
	"""
	A partir da HTML da página, obtém as outras páginas secundárias!
	"""
	list_of_secondary_page_links = []
	start_paragraf = _HTMLCodeSecund.find("<p class=\"pagenumber\"")
	end_paragraf = _HTMLCodeSecund.find("</p>", start_paragraf)
	paragraf = _HTMLCodeSecund[start_paragraf:end_paragraf]

	start_a = paragraf[::-1].find("a<")
	end_a = paragraf[::-1].find(">a/<")
	paragraf = paragraf[::-1][end_a:start_a][::-1]

	start_link = paragraf.find("\"") + 1
	end_link = paragraf.find("\"", start_link)
	last_link = paragraf[start_link:end_link]

	_pre = last_link[::-1].find("/")
	try:
		_range = int(last_link[::-1][:_pre][::-1]) + 1
	except:
		_range = 2

	for i in range(2, _range):
		list_of_secondary_page_links.append("{}/sortBy/extension/order/asc/page/{}".format(prefix_link, i, i))

	return list_of_secondary_page_links

def gen_table_ext(HTMLCode:str, src:str) -> bool:
	"""
	Obtém tabela com base no código HTML enviado.
	"""

	with open(src, "w") as file:
		init_table = HTMLCode.find("<table")
		end_table = HTMLCode.find("</table>") + len("</table>")
		file.write(HTMLCode[init_table:end_table])

	return True

def gen_db_ext() -> bool:
	"""
	Obtém as extensões e descrições com base na tabela obtida. 
	"""

	global _father_group

	list_of_extensions = []
	list_of_description_wfather = []
	for file_dir in _father_group:
		table = open(file_dir, "r").read()
		menu = table[:]
		while menu.find("<strong class=\"color3\">") != -1:
			s = menu.find("<strong class=\"color3\">")
			f = menu.find("</strong>")
			extension = menu[s + len("<strong class=\"color3\">"):f]
			list_of_extensions.append(extension)
			menu = menu[f+len("</strong>"):]

		man_description = table[:]
		while man_description.find("<td") != -1:
			s = man_description.find("<td")
			m = man_description.find(">", s)
			f = man_description.find("</td>", m)
			description = man_description[m + 1:f]

			if description.find("<span") == -1 and description.find("<a") == -1:
				resolution = file_dir.replace("-", " ")[:file_dir.index("_")]
				list_of_description_wfather.append((description, "".join(resolution).capitalize()))

			man_description = man_description[f+len("</td>"):]

	os.chdir("..")
	db = shelve.open("extensions.db", "c")
	for index in range(len(list_of_extensions)):
		db[list_of_extensions[index]] = list_of_description_wfather[index]

	db.close()
	
	subprocess.run(("rm", "-r", "Files"))
	
	return True

