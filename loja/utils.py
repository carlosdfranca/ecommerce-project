from django.db.models import Min, Max
from django.core.mail import send_mail


def filtrar_produtos(produtos, filtro):
    if filtro:
        if "-" in filtro:
            categoria, tipo = filtro.split("-")
            produtos = produtos.filter(categoria__slug=categoria, tipo__slug=tipo)
        else:
            produtos = produtos.filter(categoria__slug=filtro)
    
    return produtos


def preco_minimo_maximo(produtos):
    minimo = 0
    maximo = 0

    if len(produtos) > 0:
        minimo = list(produtos.aggregate(Min("preco")).values())[0]
        minimo = str(round(minimo, 2))
        maximo = list(produtos.aggregate(Max("preco")).values())[0]
        maximo = str(round(maximo, 2))

    return minimo, maximo


def ordrnar_tamanhos(lista):
    dict_ordem_tamanhos = {
        "PP": 1,
        "P": 2,
        "M": 3,
        "G": 4,
        "GG": 5
    }

    # Função de chave personalizada
    def ordenar_tamanho(item):
        if item.isdigit():  # Se for um número
            return int(item) # Ordena os números
        else:
            return dict_ordem_tamanhos.get(item, len(dict_ordem_tamanhos) + 1)  # Obtém o valor do tamanho no dicionário

    # Ordena a lista usando a função de chave personalizada
    lista = sorted(lista, key=ordenar_tamanho)

    return lista



def ordenar_por_ordem(produtos, ordem):
    if ordem == "menor-preco":
        produtos = produtos.order_by("preco")
    elif ordem == "maior-preco":
        produtos = produtos.order_by("-preco")
    elif ordem == "mais-vendidos":
        lista_produtos = []
        for produto in produtos:
            lista_produtos.append((produto.total_vendas(), produto))
        lista_produtos = sorted(lista_produtos, reverse=True, key=lambda x: x[0])
        produtos = [item[1] for item in lista_produtos]
    return produtos

def enviar_email_compra(pedido):
    email = pedido.cliente.email
    assunto = f"Pedido Aprovado: {pedido.id}"
    corpo = f"""Parabens!!! Seu pedido foi aprovado.
    ID do pedido: {pedido.id}
    Valor Total: {pedido.preco_total_itens}"""

    remetente = "carlosdudu369@gmail.com"
    send_mail(assunto, corpo, remetente, [email])