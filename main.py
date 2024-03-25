from kivy.app import App
from kivy.lang import Builder
from telas import *
from botoes import *
import requests
from bannervenda import BannerVenda
import os
import certifi
from functools import partial
from myfirebase import Myfirebase
from bannervendedor import BannerVendedor
from datetime import date


os.environ["SSL_CERT_FILE"] = certifi.where()
GUI = Builder.load_file('main.kv')
class MainApp(App) :
    
    unidade = None
    cliente = None
    produto = None

    id_usuario = 1
    def build(self):
        self.myfirebase = Myfirebase()
        return GUI
    
    def mudar_pagina(self, id_page) :
        gerenciador_tela = self.root.ids['screen-manager']
        gerenciador_tela.current = id_page

    def on_start(self):
        arquivos = os.listdir("icones/fotos_perfil")
        mudar_perfilpage = self.root.ids['mudarperfilpage']
        lista_fotos_perfil = mudar_perfilpage.ids['lista_foto_perfil']

        for foto in arquivos :
            imagem = ImageButton(source = f'icones/fotos_perfil/{foto}', on_release = partial(self.mudar_foto_perfil, foto))
            lista_fotos_perfil.add_widget(imagem)


        arquivo_cliente = os.listdir("icones/fotos_clientes")
        pagina_adicionnar_vend = self.root.ids['adicionarvendapage']
        lista_cliente = pagina_adicionnar_vend.ids['lista_cliente']

        for foto_cl in arquivo_cliente:
            imagem_cl = ImageButton(source = f"icones/fotos_clientes/{foto_cl}", on_release = partial(self.mudar_estado_cliente,foto_cl))
            label_cl = LabelButton(text = foto_cl.replace(".png", "").capitalize())

            lista_cliente.add_widget(imagem_cl)
            lista_cliente.add_widget(label_cl)

        arquivo_produto = os.listdir("icones/fotos_produtos")
        pagina_adicionnar_vend = self.root.ids['adicionarvendapage']
        lista_produto = pagina_adicionnar_vend.ids['lista_produto']

        for foto_pd in arquivo_produto:
            imagem_pd = ImageButton(source = f"icones/fotos_produtos/{foto_pd}", on_release = partial(self.mudar_estado_produto,foto_pd))
            label_pd = LabelButton(text = foto_pd.replace(".png", "").capitalize())

            lista_produto.add_widget(imagem_pd)
            lista_produto.add_widget(label_pd)

        pagina_adicionnar_vend = self.root.ids['adicionarvendapage']
        pagina_adicionnar_vend.ids['data_venda'].text = f"Data: {date.today().strftime('%d/%m/%Y')}"






        self.carregar_info_usuario()
        

    def carregar_info_usuario(self):    
        try:
            with open('refreshtoken.txt', "r") as arquivo:
              refresh_token = arquivo.read()
            
            local_id, id_token = self.myfirebase.trocartoken(refresh_token)
            self.local_id = local_id
            self.id_token = id_token

            requisicao = requests.get(f'https://bancodoapp-c0574-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}')
            requisicao_dic = requisicao.json()
            avatar = requisicao_dic['avatar']
            
            self.avatar = avatar
            foto_perfil = self.root.ids['foto_perfil']
            foto_perfil.source = f"icones/fotos_perfil/{avatar}"

            try:
                vendas = requisicao_dic['vendas']
                pagina_homepage = self.root.ids['homepage']
                lista_vendas = pagina_homepage.ids['lista_vendas']
                for id_venda in vendas:
                    venda = vendas[id_venda]
                    banner = BannerVenda(cliente= venda['cliente'],data = venda['data'],
                                        foto_cliente = venda['foto_cliente'],foto_produto = venda['foto_produto'],
                                            preco = venda['preco'], produto = venda['produto'],
                                            quantidade = venda['quantidade'], unidade = venda['unidade'])
                    
                    
                    lista_vendas.add_widget(banner) 
                    
                    #   print(venda)
                # Ajuste o ID unico
                id_vendedor = requisicao_dic['id_vendedor']
                
                self.id_vendedor = id_vendedor

                pagina_ajuste = self.root.ids['ajustepage']
                pagina_ajuste.ids['id_vendedor'].text = f'Seu ID Único é: {id_vendedor}'

                        
            except Exception as erro:
                print(erro)

            #Ajustar total de venda
            total_vendas = requisicao_dic["total_vendas"]
                
            self.total_vendas = total_vendas

            pagina_home = self.root.ids['homepage']
               
               
            pagina_home.ids["id_vendas"].text = f'Total de vendas: R${total_vendas}'

            equipe = requisicao_dic['equipe']

            self.equipe = equipe
            lista_equipe = equipe.split(",")
            pagina_vendedores = self.root.ids["verlistavendedorespage"]
            lista_vendedores = pagina_vendedores.ids['lista_vendedores']

            for id_vend_equipe in lista_equipe :
                if id_vend_equipe != "" :
                    banner_vendedor = BannerVendedor(id_vendedor = id_vend_equipe)
                    lista_vendedores.add_widget(banner_vendedor)
                    print('oi jean toudufuh')
            
            self.mudar_pagina("homepage")      
        except:
            pass       

    def mudar_foto_perfil(self,foto, *args) :
        foto_perfil = self.root.ids['foto_perfil']
        foto_perfil.source = f"icones/fotos_perfil/{foto}"
        self.mudar_pagina('ajustepage')
            
        dados = f'{{"avatar": "{foto}"}}'
        requisicao = requests.patch(f'https://bancodoapp-c0574-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}', data=dados)
        print(requisicao.json())

    def adicionar_vendedor(self, id_vendedor_adicionado):
        link = f'https://bancodoapp-c0574-default-rtdb.firebaseio.com/.json?orderBy="id_vendedor"&equalTo="{id_vendedor_adicionado}"'

        requisicao = requests.get(link)
        requisicao_dic = requisicao.json()
        print(requisicao_dic)
        

        pagina_acompanha = self.root.ids["acompanharvendedorpage"]
        mensagem_outro_vendedor = pagina_acompanha.ids["mensagem_outro_vendedor"]

        if requisicao_dic == {} :
            mensagem_outro_vendedor.text = "Vendedor não encontrado"
        
        else :
            equipe = self.equipe.split(',')

            if id_vendedor_adicionado in equipe :
                mensagem_outro_vendedor.text = "Vendedor Já faz parte da equipe"
            else:
                self.equipe = self.equipe + f',{id_vendedor_adicionado}'
                dados = f'{{"equipe": "{self.equipe}"}}'
                requisicao = requests.patch(f'https://bancodoapp-c0574-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}', data=dados)
                mensagem_outro_vendedor.text = "Vendedor adicionado com sucesso"
                
                pagina_vendedores = self.root.ids["verlistavendedorespage"]
                lista_vendedores = pagina_vendedores.ids['lista_vendedores']
                
                banner_vendedor = BannerVendedor(id_vendedor = id_vendedor_adicionado)
                lista_vendedores.add_widget(banner_vendedor)

    
    
    def mudar_estado_cliente(self, foto_cl, *args) :
        self.cliente = foto_cl.replace(".png", "")
        pagina_adicionnar_vend = self.root.ids['adicionarvendapage']
        lista_cliente = pagina_adicionnar_vend.ids['lista_cliente']

        for item in list(lista_cliente.children) :
            item.color = (1,1,1,1)

            try:
                texto = item.text
                texto = texto.lower()
                texto = texto + ".png"
                if foto_cl == texto :
                    item.color = (0,207/255, 219/255,1)
            except:
                pass


    def mudar_estado_produto(self, foto_pd, *args) :
        self.produto = foto_pd.replace(".png", "")
        pagina_adicionnar_vend = self.root.ids['adicionarvendapage']
        lista_produto = pagina_adicionnar_vend.ids['lista_produto']

        for item in list(lista_produto.children) :
            item.color = (1,1,1,1)

            try:
                texto = item.text
                texto = texto.lower()
                texto = texto + ".png"
                if foto_pd == texto :
                    item.color = (0,207/255, 219/255,1)
            except:
                pass
    
    def selecionar_unidade(self, id_selecionado, *args):
        self.unidade = id_selecionado
        pagina_adicionnar_vend = self.root.ids['adicionarvendapage']
        pagina_adicionnar_vend.ids['unidades_kg'].color = (1, 1, 1,1)
        pagina_adicionnar_vend.ids['unidades_unidades'].color = (1, 1, 1,1)
        pagina_adicionnar_vend.ids['unidades_litros'].color = (1, 1, 1,1)
        

        pagina_adicionnar_vend.ids[id_selecionado].color = (0,207/255, 219/255,1)
    

    def adicionar_venda(self):
        unidade = self.unidade
        unidade = str(unidade)
        unidade = unidade.replace('unidades_', "")
        cliente = self.cliente
        produto = self.produto
        pagina_vendedores = self.root.ids["adicionarvendapage"]
        data =pagina_vendedores.ids['data_venda'].text.replace("Data: ", "")
        preco = pagina_vendedores.ids['preco'].text
        quantidade = pagina_vendedores.ids['quantidade'].text
        if not cliente:
            pagina_vendedores.ids["selecionar_venda"].color = (1,0,0,1)
        if not produto:
            pagina_vendedores.ids['selecionar_produto'].color = (1,0,0,1)
        if not unidade :
            pagina_vendedores.ids['unidades_kg'].color = (1,0,0,1)
            pagina_vendedores.ids['unidades_unidades'].color = (1,0,0,1)
            pagina_vendedores.ids['unidades_litros'].color = (1,0,0,1)
        if not preco:
            pagina_vendedores.ids['label_preco'].color = (1,0,0,1)
        else:
            try:
                preco = float(preco)
             
            except:
                pagina_vendedores.ids['label_preco'].color = (1,0,0,1)

        if not quantidade :
            pagina_vendedores.ids['label_qantidade'].color = (1,0,0,1)
        
        else :
            try:
                quantidade = float(quantidade)
            except :
                pagina_vendedores.ids['label_qantidade'].color = (1,0,0,1)
        
        if cliente and produto and unidade and preco and quantidade and (type(preco) == float) and (type(quantidade)== float):
            foto_cliente = self.cliente + ".png"
            foto_produto = self.produto + ".png"
            
            dados = f'{{"cliente": "{cliente}", "produto": "{produto}", "foto_cliente": "{foto_cliente}", "foto_produto": "{foto_produto}", "data": "{data}", "unidade": "{unidade}", "preco": "{preco}", "quantidade": "{quantidade}"}}'
            link = f'https://bancodoapp-c0574-default-rtdb.firebaseio.com/{self.local_id}/vendas.json?auth={self.id_token}'
            requests.post(link, data= dados)

            banner = BannerVenda(cliente= cliente, data = data ,foto_cliente =foto_cliente ,foto_produto = foto_produto,preco = preco, produto = produto ,quantidade = quantidade, unidade = unidade)
            
            pagina_homepage = self.root.ids['homepage']
            lista_vendas = pagina_homepage.ids['lista_vendas']
            
            lista_vendas.add_widget(banner)
            
            link2 = f'https://bancodoapp-c0574-default-rtdb.firebaseio.com/{self.local_id}/total_vendas.json?auth={self.id_token}'
            requisicao = requests.get(link2)
            total_vendas = float(requisicao.json())
            total_vendas += preco
            
            dados_2 = f'{{"total_vendas": "{total_vendas}"}}'
            requests.patch(f'https://bancodoapp-c0574-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}', data=dados_2)
            
            pagina_homepage.ids["id_vendas"].text = f'Total de Vendas {total_vendas}'

            self.mudar_pagina("homepage")


        unidade = None
        cliente = None
        produto = None


    def carregar_todas_vendas(self):
        requisicao = requests.get(f'https://bancodoapp-c0574-default-rtdb.firebaseio.com/.json?orderBy="id_vendedor"')
        requisicao_dic = requisicao.json()
        
        pagina_vertodasvendas = self.root.ids['vertodasvendaspage']
        lista_vendas = pagina_vertodasvendas.ids['lista_vendas']
        
        for item in list(lista_vendas.children) :
            lista_vendas.remove_widget(item)
        
       
        foto_perfil = self.root.ids['foto_perfil']
        foto_perfil.source = f"icones/fotos_perfil/hash2.png"
        
        total_vendas = 0
        for id_cada_vendedor in requisicao_dic :
            try: 
               vendas = requisicao_dic[id_cada_vendedor]['vendas']
               for id_venda in vendas :
                  venda = vendas[id_venda]

                  total_vendas += float(venda['preco'])
                  banner = BannerVenda(cliente= venda['cliente'],data = venda['data'],
                                        foto_cliente = venda['foto_cliente'],foto_produto = venda['foto_produto'],
                                            preco = venda['preco'], produto = venda['produto'],
                                            quantidade = venda['quantidade'], unidade = venda['unidade'])
                  lista_vendas.add_widget(banner)
        
        
            except:
                pass

        pagina_vertodasvendas.ids['label_total_venda'].text = f'Total Vendas da empresa:{total_vendas}'

        

        self.mudar_pagina('vertodasvendaspage')
    
    def sair_paginatodasvendas(self, id_tela) :
        foto_perfil = self.root.ids['foto_perfil']
        foto_perfil.source = f"icones/fotos_perfil/{self.avatar}"
        
        self.mudar_pagina(id_tela)


    
    def carregar_vendas_vendedor(self, dicionario_vendas, *args):
        pagina_outrovendedor = self.root.ids['outrovendedorpage']
        lista_vendas = pagina_outrovendedor.ids['lista_vendas']
        
        for item in list(lista_vendas.children) :
           lista_vendas.remove_widget(item)   
        try:  
            vendas = dicionario_vendas['vendas']
            for id_venda in vendas :
                venda = vendas[id_venda]
                banner = BannerVenda(cliente= venda['cliente'],data = venda['data'],
                                        foto_cliente = venda['foto_cliente'],foto_produto = venda['foto_produto'],
                                            preco = venda['preco'], produto = venda['produto'],
                                            quantidade = venda['quantidade'], unidade = venda['unidade'])
                lista_vendas.add_widget(banner)      
        except:
            pass

        avatar = dicionario_vendas['avatar']   
        foto_perfil = self.root.ids['foto_perfil']
        foto_perfil.source = f"icones/fotos_perfil/{avatar}"

        total_vendas = dicionario_vendas['total_vendas'] 
        pagina_outrovendedor.ids['label_total_venda'].text = f'Total Vendas {total_vendas}'
        self.mudar_pagina('outrovendedorpage')
        
MainApp().run()
