from math import prod
from datetime import datetime as Datetime
from fastapi import FastAPI, Response, status
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class Cliente(BaseModel):
    Id: Optional[int] = 0
    nome: str
    dataChegada: Datetime
    prioritario: str
    posicaoFila: int
    atendido: Optional[bool] = False

db_clientes = [
    Cliente(Id=1, nome="Cliente1", dataChegada = Datetime.now(), prioritario = 'N', posicaoFila = 1, atendido = False),
    Cliente(Id=2, nome="Cliente2", dataChegada = Datetime.now(), prioritario = 'N', posicaoFila = 2, atendido = False),
    Cliente(Id=3, nome="Cliente3", dataChegada = Datetime.now(), prioritario = 'N', posicaoFila = 3, atendido = True),
]


@app.get("/")
def root():
    return {"message":"API de fila"}


@app.get("/fila", status_code=200)
def MostrarFila():
    clientesAguardando = [cliente for cliente in db_clientes if cliente.atendido == False]
    if len(clientesAguardando) == 0:
        return {"clientes-aguardando" : ""}

    return {"clientes-aguardando" : clientesAguardando}


@app.get("/fila/{id}", status_code=200)
def ExibirCliente(id: int, response: Response):
    
    cliente = [cliente for cliente in db_clientes if cliente.Id == id]

    if len(cliente) != 0:
        return {"cliente" : cliente}
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"cliente" : "Não foi encontrado cliente com esse id"}


@app.post("/fila")
def NovoCliente(cliente: Cliente, response: Response):

    if len(cliente.nome) > 20 or len(cliente.nome) == 0:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"O nome é obrigatório e no máximo 20 caracteres"}

    if ((cliente.prioritario == "N" or cliente.prioritario == 'P') and len(cliente.prioritario) == 1) == False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"O atendimento é somente normal (N) ou prioritário (P)"}

    ultimaPosicao = ClienteUltimaPosicao()

    cliente.Id = db_clientes[-1].Id + 1
    cliente.posicaoFila = ultimaPosicao + 1 if ultimaPosicao != None else 1
    cliente.dataChegada = Datetime.now()
    
    db_clientes.append(cliente)

    return {"mensagem":"Cliente adicionado"}


def ClienteUltimaPosicao():
    
    clienteRetorno = None

    for c in db_clientes:

        if c.atendido == False:
            clienteRetorno = c
    
    return clienteRetorno.posicaoFila


@app.patch("/fila")
def AlterarFila():
    
    for c in db_clientes:
        if c.posicaoFila == 1:
            c.posicaoFila = 0
            c.atendido = True
        else:
            c.posicaoFila = c.posicaoFila - 1

    return {"Fila alterada"}


@app.delete("/fila/{id}")
def RemoverCliente(id: int, response: Response):
    
    cliente = [cliente for cliente in db_clientes if cliente.Id == id]

    if (len(cliente) == 0):
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"Cliente não encontrado"}
    
    db_clientes.remove(cliente[0])
    
    contadorFila = 1

    for c in db_clientes:

        if c.atendido == False:
            
            c.posicaoFila = contadorFila
            contadorFila = contadorFila + 1

    return {"Cliente removido e fila atualizada"}

