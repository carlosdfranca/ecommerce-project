from django.db.models import Min, Max


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

    return minimo,  maximo