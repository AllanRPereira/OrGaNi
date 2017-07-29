# OrGaNi

Software voltado para organização de arquivos com base nas preferências do usuário. Esse software foi testado apenas no Deepin 15
   

## Funcionamento
	
O software funciona da seguinte forma:

`python3 Organi_App.py [path_from] [path_to] [--mode]`

`path_from` : Diretório que será organizado, caso haja alguma pasta que possua permissão de root, use `sudo` antes do 
python3. Obs.: Os arquivos nessa pasta serão movidos!

`path_to` : Diretório para onde os arquivos serão movidos. Obs.: Esse diretório não pode estar dentro do `path_from` e
não recomenda-se que haja arquivos nele

`mode` : Modos para organização, podem ser `ext` ou `common`.

#### Ext

```
path_to/
|--- Png/
|------ *.png
|--- Mp3/
|------ *.mp3
|--- .../
```

#### Common

```
path_to/
|--- Images/
|------ *.png, *jpg
|--- Sounds/
|------ *.mp3, *.wav
|--- .../
```

## Algumas outras funções!

`--update (-p)`: Atualiza o banco de dados da aplicação, é necessário para executa-lá

`--help (-h)`: Mostra o menu, com todas as informações da aplicação

## Exemplo

```
python3 Organi_App.py --update
python Organi_App.py /home/carlinhos /home/arquivos_organizados_carlinhos --ext
```


## Requerimentos

Os requerimentos para executar esse software são:

* python3
* conexão internet

Nada mais é necessário para executá-lo

![Release](https://img.shields.io/badge/Relase-0.4-lightgrey.svg)
![Build](https://img.shields.io/badge/Build-Passive-brightgreen.svg)