#-*- coding:utf-8 -*-

import urllib.request
import shelve
import os

"""
OrGaNi_Core, parte responsável pelo update do banco de dados!
"""
_progress = 0
_father_group = []


def get_main():
	"""
	Obtém o html principal da página File-Extensions e o retorna.
	"""

	html = urllib.request.urlopen("https://www.file-extensions.org")
	aqv_read = html.read()
	html.close()
	return str(aqv_read)

def gen_links(html):
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

def down_links(list_of_links):
	"""
	Recebe uma lista de links e faz o download destes e caso haja um sublink específico no no código HTML
	faz o download deste também!
	"""
	global _progress
	global _father_group 

	try:
		os.mkdir("Files")
	except:
		pass
	finally:
		os.chdir("Files")

	for link in list_of_links:
		_HTMLCode = urllib.request.urlopen(link).read().decode()
		_progress += 100/91
		list_extra_links_names = gen_page_links(_HTMLCode, link)
		list_of_links.extend(list_extra_links_names)
		start = link.find("name/") + len("name/")
		end = link.find("/", start)
		src_file = link[start:end] + ".html"
		gen_table_ext(_HTMLCode, src_file) #Gera tabela para esse HTML
		_father_group.append(src_file)

	return True

def gen_page_links(_HTMLCodeSecund, prefix_link):
	"""
	A partir da HTML da página, obtém as outras páginas secundárias!
	"""
	list_of_page_links = []
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
	_range = int(last_link[::-1][:_pre][::-1]) + 1 if last_link != "" else 2

	for i in range(2, _range):
		list_of_page_links.append("{}/sortBy/extension/order/asc/page/{}".format(prefix_link, i))

	return list_of_page_links
def gen_table_ext(HTMLCode, src):
	"""
	Obtém tabela com base no código HTML enviado.
	"""

	write = False

	with open(src, "w") as file:
		for line in HTMLCode:
			index_of_table = line.find("<table")
			if index_of_table != -1:
				write = True
				index_of_table_end = line.find("</table>")
				if index_of_table != -1:
					file.write(line[index_of_table:index_of_table_end + len("</table>")])
					break
			elif write == True:
				if line.find("</table>") != -1:
					index_of_table_end = str(line).find("</table>")
					file.write(line[:index_of_table + len("</table>")])
					break

			else:
				pass

	return True

def gen_db_ext():
	"""
	Obtém as extensões e descrições com base na tabela obtida. 
	"""

	global _father_group

	list_of_extensions = []
	list_of_description_wfather = []
	for file_dir in _father_group:
		table = open(file_dir, "rb").read()
		menu = str(table[:])
		while menu.find("<strong class=\"color3\">") != -1:
			s = menu.find("<strong class=\"color3\">")
			f = menu.find("</strong>")
			extension = menu[s + len("<strong class=\"color3\">"):f]
			list_of_extensions.append(extension)
			menu = menu[f+len("</strong>"):]

		man_description = str(table[:])
		while man_description.find("<td") != -1:
			s = man_description.find("<td")
			m = man_description.find(">", s)
			f = man_description.find("</td>", m)
			description = man_description[m + 1:f]

			if description.find("<span") == -1 and description.find("<a") == -1:
				list_of_description_wfather.append((description, file_dir.replace("-", " ").capitalize()))

			man_description = man_description[f+len("</td>"):]


	db = shelve.open("extensions", "c")
	for index in range(len(list_of_extensions)):
		db[list_of_extensions[index]] = list_of_description_wfather[index]

	db.close()

	return True
