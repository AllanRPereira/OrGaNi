from tkinter import *
import Organi_App as org_app
from threading import Thread
import time
import os

class OrganiInf:
	def __init__(self, master):
		main = Frame(master, bg="white", pady=30, padx=30)
		main.pack()

		title = Label(main, text="OrGaNi", fg="#22a6b3", bg="white", font=("Roboto", 18), pady=10)
		title.pack(side=TOP)

		dir_1 = Frame(main, bg="white", pady=10, padx=10)
		dir_1.pack()

		self.diretorio_1 = Label(dir_1, bg="white", text="Diretório Original", fg="black", width=20)
		self.diretorio_1.pack(side=LEFT)
		self.input_dir_1 = Entry(dir_1, bg="white")
		self.input_dir_1.pack(side=LEFT)

		dir_2 = Frame(main, bg="white", pady=10, padx=10)
		dir_2.pack()

		self.diretorio_2 = Label(dir_2, bg="white", text="Diretório de Destino", fg="black", width=20)
		self.diretorio_2.pack(side=LEFT)
		self.input_dir_2 = Entry(dir_2, bg="white")
		self.input_dir_2.pack(side=LEFT)

		modes = Frame(main, bg="white", pady=10, padx=10)
		modes.pack()

		self.value_radio = StringVar()
		mode_one = Radiobutton(modes, bg="white", variable=self.value_radio, value="--common", text="Tipo de Arquivo", padx=15, highlightcolor="white", highlightbackground="white")
		mode_two = Radiobutton(modes, bg="white", variable=self.value_radio, value="--ext", text="Por Extensão", padx=15, highlightcolor="white", highlightbackground="white")
		mode_one.pack()
		mode_two.pack()

		actions = Frame(main, bg="white", pady=10, padx=10)
		actions.pack()

		self.btn_iniciar = Button(actions, bg="white", text="Organizar!", fg="black", width=15, padx=15, command=self.iniciar)
		self.btn_iniciar.pack(side=LEFT)
		self.btn_atualizar = Button(actions, bg="white", text="Atualizar!", fg="black", width=15, padx=15, command=self.atualizar)
		self.btn_atualizar.pack(side=LEFT)

		options_check = Frame(main, bg="white", pady=10, padx=10)
		options_check.pack()

		self.check_one = IntVar()
		self.check_two = IntVar()

		self.check_month = Checkbutton(options_check, bg="white", padx=10, pady=10, text="Ordernar por mês", variable=self.check_one)
		self.check_replace = Checkbutton(options_check, bg="white", padx=10, pady=10, text="Remover Arquivos duplicados", variable=self.check_two)
		self.check_month.pack(side=LEFT)
		self.check_replace.pack(side=LEFT)

		history = Frame(main, bg="white", pady=10, padx=10)
		history.pack()

		self.historico = Text(history, bg="white", width=40, height=12, padx=10, pady=10)
		self.historico.pack()

	def iniciar(self):
		self.historico.delete(1.0, END)
		argv = ["Graphics", self.input_dir_1.get(),  self.input_dir_2.get(), self.value_radio.get(), self.historico, (self.check_one.get(), self.check_two.get())]
		instance_of_organi = Thread(target=org_app.start_app, args=argv).start()
		return True

	def atualizar(self):
		self.historico.delete(1.0, END)
		argv = ["Graphics", "--update", self.historico]
		instance_of_organi = Thread(target=org_app.start_app, args=argv).start()
		return True

root = Tk()
root.title("OrGaNi - Organização")
root.resizable(0,0)
icon_photo = PhotoImage(file="folder.png")
root.iconphoto("vm", icon_photo)
app = OrganiInf(root)
root.mainloop()
root.destroy()