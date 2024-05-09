# Desafio Técnico - LuizaLabs/Magalu

Olá! Eu sou a Débora, e esta é a minha API para o desafio técnico da Magalu.

### Instruções para iniciar os testas

Utilizei Python no desenvolvimento e MySQL para o banco de dados.

`Python 3.8.8`

Para começar, instale as dependências necessárias de acordo com o arquivo requirements.txt rodando o código no terminal:

```
pip install -r requirements.txt
```

Você pode se conectar a um servidor MySQL setando as variáveis de ambiente no arquivo `config.py`, como eu fiz, usando o arquivo que deixei na pasta `database` para criar as tabelas clients e wishlist rodando o código com seu `username` e `database_name`:

```
mysql -u username -p database_name create_tables.sql
```

Para fazer as requisições, é necessário antes rodar o arquivo `main.py` no terminal:

```
python main.py
```

Pronto! A API está pronta para ser testada :)

## Endpoints da API

Todos os endpoints precisam de autenticação com token para as requisições, então primeiramente você precisa de um token:

`/token` -> `GET` -> Pegar um token com validade de 30 minutos.

`/clients/<clientId>` -> `GET` -> Ver os dados do cliente `clientId`.

`/clients/<clientId>` -> `PUT` -> Atualizar os dados do cliente `clientId`.

`/clients/<clientId>` -> `POST` -> Criar um cliente com ID `clientId`.

`/clients/<clientId>` -> `DELETE` -> Deletar os dados do cliente `clientId`.

`/clients/<clientId>/wishlist` -> `GET` -> Listar os produtos na lista de favoritos do cliente `clientId`.

`/clients/<clientId>/wishlist/<productId>` -> `POST` -> Adicionar um produto na lista de favoritos do cliente `clientId`.

`/clients/<clientId>/wishlist/<productId>` -> `DELETE` -> Deletar um produto da lista de favoritos do cliente `clientId`.