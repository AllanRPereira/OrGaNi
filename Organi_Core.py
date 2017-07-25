#-*- coding:utf-8 -*-

import urllib.request
import shelve
import os

def get_main():
	html = urllib.request.urlopen("https://www.file-extensions.org")
	aqv_read = html.read()
	html.close()
	return str(aqv_read)

def gen_links(html):
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


def gen_table_ext(list_of_links):
	father_group = []

	try:
		os.mkdir("Files")
	except:
		pass
	finally:
		os.chdir("Files")

	for link in list_of_links:
		_HTMLCode = urllib.request.urlopen(link)
		ind_name = link[::-1].find("/")
		src_file = link[::-1][:ind_name][::-1] + ".html"
		father_group.append(src_file)

		write = False

		with open(src_file, "w") as file:
			for line in _HTMLCode:
				line = str(line)
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

	return father_group

def gen_db_ext(father_group):
	list_of_extensions = []
	list_of_description_wfather = []
	for file_dir in father_group:
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