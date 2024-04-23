from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from .models import *
from .utils import *

import uuid
from datetime import datetime
from .api_mercadopago import criar_pagamento

# Create your views here.
def homepage(request):
    banners = Banner.objects.filter(ativo=True)
    context = {"banners": banners}
    return render(request, 'homepage.html', context)



def loja(request, filtro=None):
    # Pegando os produtos, juntamente com o Filtro (caso tenha)
    produtos = Produto.objects.all()
    produtos = filtrar_produtos(produtos, filtro)


    # Pegando as categorias existentes para colocar no filtro da barra lateral
    id_categorias = list(produtos.values_list("categoria", flat=True).distinct())
    categorias = Categoria.objects.filter(id__in=id_categorias)

    # Lógica para o filtro da barra lateral
    if request.method == "POST":
        dados = request.POST.dict()
        print(dados)
        produtos = produtos.filter(preco__gte=dados.get("preco_minimo"), preco__lte=dados.get("preco_maximo"))
        if "tamanho" in dados:
            itens = ItemEstoque.objects.filter(produto__in=produtos, tamanho=dados.get("tamanho"))
            ids_produtos = itens.values_list("produto").distinct()
            produtos = produtos.filter(id__in=ids_produtos)
        if "tipo" in dados:
            produtos = produtos.filter(tipo__slug=dados.get("tipo"))
        if "categoria" in dados:
            produtos = produtos.filter(categoria__slug=dados.get("categoria"))
    
    # Ordenando os produtos de acordo com o filtro passado na página
    ordem = request.GET.get("ordem", "")
    produtos = ordenar_por_ordem(produtos, ordem)


    # Pegando os tamanhos e ordenando-os de forma correta para o filtro da barra lateral.
    itens = ItemEstoque.objects.filter(produto__in=produtos)
    tamanhos = list(itens.values_list("tamanho", flat=True).distinct())
    tamanhos = ordrnar_tamanhos(tamanhos)

    context = {
        "produtos": produtos,
        "tamanhos": tamanhos,
        "categorias": categorias,
    }
    return render(request, 'loja.html', context)



def produto(request, id_produto, id_cor=None):
    produto = Produto.objects.get(id=id_produto)
    itens_estoque = ItemEstoque.objects.filter(produto=produto, quantidade__gt=0)

    tem_estoque = False
    cores = {}
    tamanhos = {}
    cor_selecionada = None

    if len(itens_estoque)>0:
        tem_estoque = True
        cores = {item.cor for item in itens_estoque}
        if id_cor:
            itens_estoque = ItemEstoque.objects.filter(produto=produto, quantidade__gt=0, cor__id=id_cor)
            tamanhos = {item.tamanho for item in itens_estoque}
            cor_selecionada = Cor.objects.get(id=id_cor)
    
    context = {
        "produto": produto, 
        "itens_estoque": itens_estoque, 
        "tem_estoque": tem_estoque,
        "cores": cores,
        "tamanhos": tamanhos, 
        "cor_selecionada": cor_selecionada
    }
    
    return render(request, 'produto.html', context)



def adicionar_carrinho(request, produto_id):
    if request.method == "POST" and produto_id:
        dados = request.POST.dict()
        tamanho = dados.get("tamanho")
        cor_id = dados.get("cor")
        if not tamanho and not cor_id:
            return redirect('loja')
        
        # Peagr o cliente
        resposta = redirect('carrinho')
        if request.user.is_authenticated:
            cliente = request.user.cliente
        else:
            if request.COOKIES.get("id_sessao"):
                id_sessao = request.COOKIES.get("id_sessao")
            else:
                id_sessao = str(uuid.uuid4())
                resposta.set_cookie(key="id_sessao", value=id_sessao, max_age=60*60*24*30)
            
            cliente, criado = Cliente.objects.get_or_create(id_sessao=id_sessao)
        
        # Criar o pedido , ou pegar o que está em aberto
        pedido, criado = Pedido.objects.get_or_create(cliente=cliente, finalizado=False)
        item_estoque = ItemEstoque.objects.get(produto__id=produto_id, tamanho=tamanho, cor__id=cor_id)
        item_pedido, criado = ItensPedido.objects.get_or_create(itens_estoque=item_estoque, pedido=pedido)

        # Adicionando quantidade no carrinho
        item_pedido.quantidade += 1
        item_pedido.save()

        return resposta
    else:
        return redirect('loja')
    


def remover_carrinho(request, produto_id):
    if request.method == "POST" and produto_id:
        dados = request.POST.dict()
        tamanho = dados.get("tamanho")
        cor_id = dados.get("cor")
        if not tamanho and not cor_id:
            return redirect('loja')
        
        # Pegar o cliente
        if request.user.is_authenticated:
            cliente = request.user.cliente
        else:
            if request.COOKIES.get("id_sessao"):
                id_sessao = request.COOKIES.get("id_sessao")
                cliente, criado = Cliente.objects.get_or_create(id_sessao = id_sessao)
            else: 
                return redirect('loja')
        
        # Criar o pedido , ou pegar o que está em aberto
        pedido, criado = Pedido.objects.get_or_create(cliente=cliente, finalizado=False)
        item_estoque = ItemEstoque.objects.get(produto__id=produto_id, tamanho=tamanho, cor__id=cor_id)
        item_pedido, criado = ItensPedido.objects.get_or_create(itens_estoque=item_estoque, pedido=pedido)

        # Removendo uma unidade do carrinho
        item_pedido.quantidade -= 1
        item_pedido.save()
        if item_pedido.quantidade <= 0:
            item_pedido.delete()
        return redirect('carrinho') 
    else:
        return redirect('loja')



def carrinho(request):

    if request.user.is_authenticated:
        cliente = request.user.cliente
    else:
        if request.COOKIES.get("id_sessao"):
            id_sessao = request.COOKIES.get("id_sessao")
            cliente, criado = Cliente.objects.get_or_create(id_sessao = id_sessao)
        else: 
            context = {"itens_pedido": None, "pedido": None, "cliente_existente": False}
            return render(request, 'carrinho.html', context)

    pedido, criado = Pedido.objects.get_or_create(cliente=cliente, finalizado=False)

    itens_pedido = ItensPedido.objects.filter(pedido=pedido)    

    context = {"itens_pedido": itens_pedido, "pedido": pedido, "cliente_existente": True}

    return render(request, 'carrinho.html', context)



def checkout(request):
    if request.user.is_authenticated:
        cliente = request.user.cliente
    else:
        if request.COOKIES.get("id_sessao"):
            id_sessao = request.COOKIES.get("id_sessao")
            cliente, criado = Cliente.objects.get_or_create(id_sessao = id_sessao)
        else: 
            
            return redirect('loja')

    pedido, criado = Pedido.objects.get_or_create(cliente=cliente, finalizado=False)

    enderecos = Endereco.objects.filter(cliente=cliente)

    context = {"pedido": pedido, "enderecos": enderecos, "erro":None}

    return render(request, 'checkout.html', context)



def finalizar_pedido(request, pedido_id):
    if request.method == "POST":
        erro = None
        dados = request.POST.dict()
        total = float(dados.get("total").replace(",", "."))
        email = dados.get("email")
        pedido = Pedido.objects.get(id=pedido_id)
        endereco_id = dados.get("endereco")


        # Vendo se o usuário tentou mudar o preço total no HTML
        if total != float(pedido.preco_total_itens):
            erro = 'preco'
        else:
            # Verificando se o usuário Preencheu o espaço de e-mail ou possui ou está cadastrado para pegarmos o e-mail dele
            if not request.user.is_authenticated and email == "":
                erro = "email_inexistente"
                if not erro:
                    clientes = Cliente.objects.filter(email=email)
                    if clientes:
                        pedido.cliente = clientes[0]
                    else:
                        pedido.cliente.email = email
                        pedido.cliente.save()

            
            # Verificando enrdereços
            if not "endereco" in dados:
                erro = "endereco"
                print(erro)
            else: 
                endereco = Endereco.objects.get(id=endereco_id)
                pedido.endereco = endereco

        # criando código de tranzação e data de finalização
        codigo_transacao = f"{pedido.id}-{datetime.now().timestamp()}"
        pedido.codigo_transacao = codigo_transacao

        pedido.save()
        
        context = {"erro": erro}

        if erro:
            enderecos = Endereco.objects.filter(cliente=pedido.cliente)

            context = {
                "erro": erro,
                "pedido": pedido,
                "enderecos": enderecos
            }
            return render(request, "checkout.html", context)
        else:
            link = request.build_absolute_uri(reverse("finalizar_pagamento"))
            link_pagamento, id_pagamento = criar_pagamento(ItensPedido.objects.filter(pedido=pedido), link, email, endereco)

            pagamento = Pagamento.objects.create(id_pagamento=id_pagamento)
            pagamento.pedido = pedido
            pagamento.save()

            return redirect(link_pagamento)
    else:
        return redirect("loja")



def finalizar_pagamento(request):
    dados = request.GET.dict()
    status = dados.get("status")
    id_pagamento = dados.get("preference_id")

    if status == "approved":
        # Aprovando o pagamento
        pagamento = Pagamento.objects.get(id_pagamento=id_pagamento)
        pagamento.aprovado=True
        pedido = pagamento.pedido
        pedido.finalizado = True
        pedido.data_finalizacao = datetime.now()
        pagamento.save()
        pedido.save()
        enviar_email_compra(pedido)
        if request.user.is_authenticated:
            return redirect("meus_pedidos")
        else:
            return redirect("pedido_aprovado", pedido.id)
    else:
        return redirect("checkout")
    


def pedido_aprovado(request, pedido_id):
    pedido = Pedido.objects.get(id=pedido_id)
    context = {
        "pedido": pedido
    }
    return render(request, "pedido_aprovado.html", context)



def adicionar_endereco(request):
    if request.method == "POST":
        # Pegando o cliente
        if request.user.is_authenticated:
            cliente = request.user.cliente
        else:
            if request.COOKIES.get("id_sessao"):
                id_sessao = request.COOKIES.get("id_sessao")
                cliente, criado = Cliente.objects.get_or_create(id_sessao=id_sessao)
            else:
                return redirect('loja')

        # Pegando dados do formulário enviado
        dados = request.POST.dict()    
    
        cidade = dados.get("cidade")
        estado = dados.get("estado")
        rua = dados.get("rua")
        numero = dados.get("numero")
        complemento = dados.get("complemento")
        cep = dados.get("cep")

        # Criando o endereço no banco
        endereco = Endereco.objects.create(
            cliente=cliente,
            cidade=cidade,
            estado=estado,
            rua=rua,
            numero=int(numero),
            complemento=complemento,
            cep=cep
        )
        endereco.save()

        # Redirecionando para a página de Checkout
        return redirect("checkout")
    else:
        context = {}
        return render(request, 'adicionar_endereco.html', context)



# páginas dos usuários
@login_required
def minha_conta(request):
    erro = None
    alterado = False
    if request.method == "POST":
        dados = request.POST.dict()
        if "senha_atual" in dados:
            # Alterar a minha senha
            senha_atual = dados.get("senha_atual")
            nova_senha = dados.get("nova_senha")
            confirma_senha = dados.get("confirma_senha")


            if nova_senha == confirma_senha:
                usuario = authenticate(request, username=request.user.email, password=senha_atual)
                if usuario:
                    # Altera a Senha
                    usuario.set_password(nova_senha)
                    usuario.save()
                    alterado = True
                else:
                    erro = "senha_atual_incorreta"
            else: 
                erro = "senhas_diferentes"
            

        elif "email" in dados:
            # Alterar dados pessoais do usuário
            nome = dados.get("nome")
            email = dados.get("email")
            telefone = dados.get("telefone")

            if email != request.user.email:
                usuarios = User.objects.filter(email=email)
                if len(usuarios) > 0:
                    erro = "usuario_existente"
                else:
                    cliente = request.user.cliente
                    cliente.email = email
                    request.user.email = email
                    request.user.username = email
                    cliente.nome = nome
                    cliente.telefone = telefone
                    cliente.save()
                    request.user.save()
                    alterado = True
        else:
            erro = "formulário_invalido"

    context = {
        "erro": erro,
        "alterado": alterado
    }

    return render(request, 'usuarios/minha_conta.html', context)


@login_required
def meus_pedidos(request):
    cliente = request.user.cliente
    pedidos = Pedido.objects.filter(cliente=cliente, finalizado=True).order_by("-data_finalizacao")

    context = {
        "pedidos": pedidos
    }
    return render(request, 'usuarios/meus_pedidos.html', context)



def fazer_login(request):
    erro = False
    if request.user.is_authenticated:
        return redirect("loja")
    if request.method == "POST":
        dados = request.POST.dict()
        if "email" in dados and "senha" in dados:
            email = dados.get("email")
            senha = dados.get("senha")
            usuario = authenticate(request, username=email, password=senha)
            if usuario:
                login(request, usuario)
                return redirect("loja")
            else:
                erro = True
        else:
            erro = True
    
    context = {
        "erro": erro
    }

    return render(request, 'usuarios/login.html', context)



def criar_conta(request):
    erro = None
    if request.user.is_authenticated:
        return redirect("loja")
    if request.method == "POST":
        dados = request.POST.dict()
        for chave, valor in dados.items():
            if valor == "":
                erro = "preenchimento"
        if not erro:
            # Verificando se todos os campos do formulário foram preenchidos
            if "email" in dados and "senha" in dados and "confirmacao_senha" in dados:
                email = dados.get("email")
                senha = dados.get("senha")
                senha2 = dados.get("confirmacao_senha")

                # Verificando se o campo email, é realmente um email válido
                try:
                    validate_email(email)
                except ValidationError:
                    erro = "email_invalido"

                # Verificando se a senha e a confirmação de senha são compatíveis
                if senha == senha2:
                    # Vendo se o e-mail ja existe ou criando o usuário
                    usuario, criado = User.objects.get_or_create(username=email, email=email)
                    if not criado:
                        erro = "usuario_existente"
                    else:
                        # Colocando a senha para o usuário
                        usuario.set_password(senha)
                        usuario.save()

                        #Fazendo o Login
                        usuario = authenticate(request, username=email, password=senha)
                        login(request, usuario)

                        # Criando o cliente
                        # Verificar se existe o id_sessao nos cookies
                        if request.COOKIES.get("id_sessao"):
                            id_sessao = request.COOKIES.get("id_sessao")
                            cliente, criado = Cliente.objects.get_or_create(id_sessao=id_sessao)
                        else:
                            cliente, criado = Cliente.objects.get_or_create(email=email)
                        
                        cliente.usuario = usuario
                        cliente.email = email
                        cliente.save()
                        return redirect("loja")
                else:
                    erro = "senhas_diferentes"
            else:
                erro = "preenchimento"



    context = {
        "erro": erro
    }
    return render(request, 'usuarios/criar_conta.html', context)


@login_required
def fazer_logout(request):
    logout(request)
    return redirect('fazer_login')


@login_required
def gerenciar_loja(request):
    if request.user.groups.filter(name="equipe").exists():
        pedidos_finalizados = Pedido.objects.filter(finalizado=True)
        quantidade_pedidos = len(pedidos_finalizados)   
        faturamento = sum([pedido.preco_total_itens for pedido in pedidos_finalizados])
        quantidade_produtos = sum([pedido.quantidade_itens for pedido in pedidos_finalizados])
        context = {
            "quantidade_pedidos": quantidade_pedidos,
            "faturamento": faturamento,
            "quantidade_produtos": quantidade_produtos,
        }
        return render(request, 'interno/gerenciar_loja.html', context)
    else:
        return redirect('loja')
    

def exportar_relatorio(request, relatorio):
    if request.user.groups.filter(name="equipe").exists():
        if relatorio == 'pedidos':
            informacoes = Pedido.objects.filter(finalizado=True)
        elif relatorio == 'clientes':
            informacoes = Cliente.objects.all()
        elif relatorio == 'enderecos':
            informacoes = Endereco.objects.all()
        return exportar_csv(informacoes)
    else:
        return redirect('gerenciar_loja')