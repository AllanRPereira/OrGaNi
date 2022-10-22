# Organi

Software voltado para organização de arquivos com base nas preferências do usuário. Esse software funciona apenas em sistemas Linux.
   

## Funcionamento
	
O software funciona de duas formas 

### Pelo Terminal

`python3 -m organi [path_from] [path_to] [--mode]`

`path_from` : Diretório que será organizado, caso haja alguma pasta que possua permissão de root, use `sudo` antes do 
python3. Obs.: Os arquivos nessa pasta serão movidos!

`path_to` : Diretório para onde os arquivos serão movidos. Obs.: Esse diretório não pode estar dentro do `path_from` e
não recomenda-se que haja arquivos nele

`mode` : Modos para organização, podem ser `ext` ou `common`.

### Pela Interfáce Gráfica 

`python3 -m organi --gui`: Com esse código toda interfáce gŕáfica do software irá iniciar e eles funcionará adequadamente

### Formas de Organização

#### Ext

```
path_to/
|--- Png/
|------Jan/
|--------- *.png
|--- Mp3/
|------Jan/
|--------- *.mp3organi
|------Jan/
|--------- *.png, *jpg
|--- Sounds/
|------Jan/
|--------- *.mp3, *.wav
|--- .../
```

## Algumas outras funções!

`--update (-p)`: Atualiza o banco de dados da aplicação, é necessário para executa-lá.

`--help (-h)`: Mostra o menu, com todas as informações da aplicação.

`--month (-m)`: Além da organização definida, organiza também pelo mês de modificação de cada arquivo.

## Testes

`python3 -m unittest -v`: Executa as unidades de teste para verificar a integridade do software.

## Exemplo

```
python3 -m organi --update
python3 -m organi /home/carlinhos /home/arquivos_organizados_carlinhos --ext
```


## Requerimentos

Os requerimentos para executar esse software são:

* python3
* conexão com a internet

Nada mais é necessário para executá-lo

![Release](https://img.shields.io/badge/Release-2.0-lightgrey.svg)
![Build](https://img.shields.io/badge/Build-Passive-brightgreen.svg)
