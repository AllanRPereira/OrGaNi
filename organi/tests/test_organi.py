import unittest
import os
import shutil
from hashlib import blake2b
from random import random
import organi.src.main as org_app

class TestOrgani(unittest.TestCase):

    def setUp(self) -> None:
        workflow_dir = os.getcwd()
        try:
            path = os.path.split(__file__)[0]
            with open(os.path.join(path, "extensions.txt"), "r") as file:
                list_common_extensions = file.read().split("\n")
            self.path_organizer = os.path.join(path, "files_to_organize")
            os.mkdir(self.path_organizer)
            os.chdir(self.path_organizer)
            for extension in list_common_extensions:
                for i in range(2):
                    name = blake2b(bytes(f"{random()}", "utf-8"), digest_size=5).hexdigest() + f"{extension}"
                    with open(f"{name}", "w") as aqv:
                        aqv.write("Arquivo criado para testes")
            os.chdir("..")
            self.path_organized = os.path.join(path, "organized_files")

            files_dictionary = {}
            for file in os.listdir(self.path_organizer):
                extension = os.path.splitext(file)[1]
                if extension in files_dictionary:
                    files_dictionary[extension].append(file)
                else:
                    files_dictionary[extension] = [file,]
            self.files_dictionary = files_dictionary

            os.chdir(workflow_dir)
        except Exception as e:
            raise Exception(f"Erro durante a criação do ambiente de teste! {e}")

    def tearDown(self) -> None:
        try:
            pass
            shutil.rmtree(self.path_organizer)
            shutil.rmtree(self.path_organized)
        except Exception as e:
            raise Exception(f"Erro durante a criação do ambiente de teste! {e}")        
            
    def test_organi_ext_mode(self):

        cond_program_return = org_app.start_app(*["Organi", self.path_organizer, self.path_organized, "--ext"])
        assert cond_program_return, "Programa não funcionou corretamente!"

        list_dirs = [f".{path.lower()}" for path in os.listdir()]
        io = list_dirs.index(".others")
        list_dirs[io] = ""
        equal_dirs = [False for path in list_dirs if path not in self.files_dictionary.keys()]
        assert equal_dirs == [], "Pastas não coincidem"

        cond_same_files = True
        for path, list_path, files_path in os.walk(self.path_organized):
            if list_path == []:
                extension = f".{os.path.split(path)[1].lower()}"
                if extension == ".others": extension = ""
                for file in self.files_dictionary[extension]:
                    if file not in files_path:
                        cond_same_files = False
                        break
        
        assert cond_same_files, "Arquivos não foram organizados corretamente"        
        return True

if __name__ == "__main__":
    unittest.main()