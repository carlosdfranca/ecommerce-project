# Ecommerce Django com MercadoPago API

Este é um projeto de Ecommerce desenvolvido utilizando Django Framework como base e integrando a API do MercadoPago para processamento de pagamentos. Este projeto foi inspirado no site da Reserva e visa fornecer uma plataforma simples e eficiente para venda de produtos online.

## Funcionalidades Principais

- Cadastro de usuários
- Autenticação de usuários
- Adição de produtos ao carrinho de compras
- Visualização e edição do carrinho de compras
- Processamento de pagamentos via API do MercadoPago
- Confirmação de pedidos e envio de e-mails de confirmação

## Pré-requisitos

- Python 3.11.5
- Django Framework
- Conta no MercadoPago para integração da API
- Conexão com a internet para processamento de pagamentos

## Instalação

1. Clone o repositório para sua máquina local:
```bash
git clone https://github.com/carlosdfranca/ecommerce-project.git
```

2. Acesse o diretório do projeto:
```bash
cd seu-projeto
```

3. Instale as dependências do projeto:
```bash
pip install -r requirements.txt
```

4. Execute as migrações do banco de dados:

```bash
python manage.py makemigrations
python manage.py migrate
```

5. Configure as variáveis de ambiente para a integração com o MercadoPago. Você precisará definir `MERCADOPAGO_ACCESS_TOKEN` com seu token de acesso do MercadoPago.

6. Inicie o servidor:
```bash
- python manage.py runserver
```

7. Acesse o projeto em seu navegador:
http://localhost:8000


## Configuração da API do MercadoPago

Para configurar a integração com a API do MercadoPago, é necessário seguir os seguintes passos:

1. Crie uma conta no MercadoPago, se ainda não tiver uma.
2. Acesse o painel de desenvolvedor do MercadoPago e crie uma aplicação para obter suas credenciais de integração.
3. Obtenha seu token de acesso (access token) no painel de controle do MercadoPago.
4. Configure a variável de ambiente `MERCADOPAGO_ACCESS_TOKEN` com seu token de acesso.

## Contribuindo

Contribuições são bem-vindas! Se você encontrar bugs ou tiver sugestões para melhorias, sinta-se à vontade para abrir uma issue ou enviar um pull request.

## Licença

Este projeto está licenciado sob a [Licença MIT](https://opensource.org/licenses/MIT).
