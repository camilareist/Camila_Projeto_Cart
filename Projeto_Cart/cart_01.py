from fastapi import FastAPI
from typing import List
from pydantic import BaseModel

app = FastAPI()

OK = "OK"
FALHA = "FALHA"

# Classe representando os dados do endereço do cliente
class Endereco(BaseModel):
    rua: str
    cep: str
    cidade: str
    estado: str

# Classe representando os dados do cliente
class Usuario(BaseModel):
    id: int
    nome: str
    email: str
    senha: str

# Classe representando a lista de endereços de um cliente
class ListaDeEnderecosDoUsuario(BaseModel):
    usuario: Usuario
    enderecos: List[Endereco] = []

# Classe representando os dados do produto
class Produto(BaseModel):
    id: int
    nome: str
    descricao: str
    preco: float

# Classe representando o carrinho de compras de um cliente com uma lista de produtos
class CarrinhoDeCompras(BaseModel):
    id_usuario: int
    id_produtos: List[Produto] = []
    preco_total: float
    quantidade_de_produtos: int

db_usuarios = []
db_produtos = []
db_end = []
db_carrinhos = []
          
# Criar um usuário,
# se tiver outro usuário com o mesmo ID retornar falha, 
# se o email não tiver o @ retornar falha, 
# senha tem que ser maior ou igual a 3 caracteres, 
# senão retornar OK
@app.post("/usuario/")
async def criar_usuário(user: Usuario):
    new_user = True
    valida_email = '@' in user.email
    valida_senha = len(user.senha) >= 3

    for usuario in db_usuarios:
        if user.id == usuario.id:
            new_user = False
            break

    if valida_senha and valida_email and new_user:
        db_usuarios.append(user)
        return OK

    return FALHA
  
# Se o id do usuário existir, retornar os dados do usuário
# senão retornar falha
@app.get("/usuario/")
async def retornar_usuario(id: int):
    for user in db_usuarios:
        if user.id == id:
            return user
    return FALHA

# Se existir um usuário com exatamente o mesmo nome, retornar os dados do usuário
# senão retornar falha
@app.get("/usuario/nome")
async def retornar_usuario_com_nome(nome: str):
    for user in db_usuarios:
        if user.nome == nome:
            return user
    return FALHA

# Se o id do usuário existir, deletar o usuário e retornar OK
# senão retornar falha
# ao deletar o usuário, deletar também endereços e carrinhos vinculados a ele
@app.delete("/usuario/")
async def deletar_usuario(id: int):
    for user in db_usuarios:
        if user.id == id:
            db_usuarios.remove(user)
        for endereco in db_end:
            if endereco.usuario == id:
                db_end.remove(endereco)
        return OK
    return FALHA            

# Se não existir usuário com o id_usuario retornar falha, 
# senão retornar uma lista de todos os endereços vinculados ao usuário
# caso o usuário não possua nenhum endereço vinculado a ele, retornar 
# uma lista vazia
### Estudar sobre Path Params (https://fastapi.tiangolo.com/tutorial/path-params/)
@app.get("/usuario/{id_usuario}/enderecos/")
async def retornar_enderecos_do_usuario(id_usuario: int):
    for user in db_usuarios:
        if user.id == id_usuario:
            for endereco in db_end:
                if endereco.user.id == id_usuario:
                    return endereco.enderecos
                else:
                    return "[]"
    return FALHA
           
# Retornar todos os emails que possuem o mesmo domínio
# (domínio do email é tudo que vêm depois do @)
# senão retornar falha
emails = []   
@app.get("/usuarios/emails/")
async def retornar_emails(dominio: str):
    for user in db_usuarios:
        if user.email.split("@")[1] == dominio:
            emails.append(user.email)
            if not emails:
                return FALHA
    return emails

# Se não existir usuário com o id_usuario retornar falha, 
# senão cria um endereço, vincula ao usuário e retornar OK
@app.post("/endereco/{id_usuario}/")
async def criar_endereco(endereco: Endereco, id_usuario: int):
    for user in db_usuarios:
        if user.id == id_usuario:
            lista_enderecos = ListaDeEnderecosDoUsuario(
                usuario=user, enderecos=[endereco])
            db_end.append(lista_enderecos)
            return OK
    return FALHA

# Se não existir endereço com o id_endereco retornar falha, 
# senão deleta endereço correspondente ao id_endereco e retornar OK
# (lembrar de desvincular o endereço ao usuário)
@app.delete("/endereco/{id_endereco}/")
async def deletar_endereco(id_endereco: int):
    return OK

# Se tiver outro produto com o mesmo ID retornar falha, 
# senão cria um produto e retornar OK
@app.post("/produto/")
async def criar_produto(produto: Produto):
    
    new_product = True
    
    for prod in db_produtos:
        if produto.id == prod.id:
            new_product = False
            break
    
    if new_product:
        db_produtos.append(produto)
        return OK

    return FALHA


@app.get("/produto/")
def valida_produto(id:int):
    for prod in db_produtos:
        if prod.id == id:
            return prod
    return FALHA

# Se não existir produto com o id_produto retornar falha, 
# senão deleta produto correspondente ao id_produto e retornar OK
# (lembrar de desvincular o produto dos carrinhos do usuário)
@app.delete("/produto/{id_produto}/")
async def deletar_produto(id_produto: int):
    return OK



# Se não existir usuário com o id_usuario ou id_produto retornar falha, 
# se não existir um carrinho vinculado ao usuário, crie o carrinho
# e retornar OK
# senão adiciona produto ao carrinho e retornar OK
@app.post("/carrinho/{id_usuario}/{id_produto}/")
async def adicionar_carrinho(id_usuario: int, id_produto: int): 
    
    usuarioExiste = False
    produtoExiste = False
    carrinhoExiste = False
    
    for user in db_usuarios:
        if user.id == id_usuario:
            usuarioExiste = True
        
    if usuarioExiste == False:
        return FALHA

    for prod in db_produtos:
        if prod.id == id_produto:
            produtoExiste = True
        
    if produtoExiste == False:
        return FALHA
        
    for carrinho in db_carrinhos:
        if carrinho.id_usuario == id_usuario:
            carrinhoExiste = True
            
    if usuarioExiste and produtoExiste:
        if carrinhoExiste:
            carrinho.id_produtos.append(prod)
            carrinho.preco_total += prod.preco
            carrinho.quantidade_de_produtos = len(carrinho.id_produtos)
            return OK
        else:
            lista_prod = CarrinhoDeCompras(id_usuario=id_usuario, id_produtos=[prod], 
                                           preco_total=prod.preco, quantidade_de_produtos=1)
            db_carrinhos.append(lista_prod)
            return OK
    return FALHA
                 
# Se não existir carrinho com o id_usuario retornar falha, 
# senão retorna o carrinho de compras.
@app.get("/carrinho/{id_usuario}/")
async def retornar_carrinho(id_usuario: int):
    for carrinho in db_carrinhos:
        if carrinho.id == id_usuario:
            return CarrinhoDeCompras

## =============================================
## VALIDAR
## =============================================
# Se não existir carrinho com o id_usuario retornar falha, 
# senão retorna o o número de itens e o valor total do carrinho de compras.
@app.get("/carrinho/{id_usuario}/")
async def retornar_total_carrinho(id_usuario: int, quantidade_de_produtos: int, preco_total: float):
    numero_itens = 0
    valor_total = 0
    
    for user in db_carrinhos:
        if user.id == id_usuario:
            numero_itens += quantidade_de_produtos
            valor_total += preco_total
            return numero_itens, valor_total
        
    return FALHA

    # numero_itens, valor_total = 0
    # return numero_itens, valor_total

# Se não existir usuário com o id_usuario retornar falha, 
# senão deleta o carrinho correspondente ao id_usuario e retornar OK
@app.delete("/carrinho/{id_usuario}/")
async def deletar_carrinho(id_usuario: int):
    for user in db_carrinhos:
        if user.id == id_usuario:
            db_carrinhos.remove(user)
            return OK
        
    return FALHA

@app.get("/")
async def bem_vinda():
    site = "Seja bem vinda"
    return site.replace('\n', '')