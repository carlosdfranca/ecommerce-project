import mercadopago
# from .models import ItensPedido

public_key = "TEST-d6fb579e-7f69-42b0-a7ac-51babd0b9320"
token = "TEST-6118982101085081-041910-19a622d3aebc9881aba5d4b1819698f9-200364962"

sdk = mercadopago.SDK(token)


# Cria um dicionário com cada um do Itenspedido

def criar_pagamento(itens_pedido, link):

    itens = []
    for item in itens_pedido:
        title = item.itens_estoque.produto.nome
        quantity = int(item.quantidade)
        unit_price = float(item.itens_estoque.produto.preco)
        itens.append({
            "title": title,
            "quantity": quantity,
            "unit_price": unit_price
        })

    preference_data = {
        "items": itens,
        "back_urls": {
            "success": link,
            "failure": link,
            "pending": link
        },
    }

    preference_response = sdk.preference().create(preference_data)
    preference = preference_response["response"]
    link_pagamento = preference['init_point']
    id_pagamento = preference["id"]
    return link_pagamento, id_pagamento