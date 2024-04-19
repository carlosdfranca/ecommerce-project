import mercadopago
# from .models import ItensPedido

public_key = "TEST-d6fb579e-7f69-42b0-a7ac-51babd0b9320"
token = "TEST-6118982101085081-041910-19a622d3aebc9881aba5d4b1819698f9-200364962"

sdk = mercadopago.SDK(token)


# Cria um dicionário com cada um do Itenspedido

preference_data = {
    "items": [
        {
            "title": "My Item",
            "quantity": 1,
            "unit_price": 75.76
        }
    ],
    "back_urls": {
        "success": "https://www.success.com",
        "failure": "http://www.failure.com",
        "pending": "http://www.pending.com"
    },
}

preference_response = sdk.preference().create(preference_data)
preference = preference_response["response"]
link = preference['init_point']
id_pagamento = preference["id"]
