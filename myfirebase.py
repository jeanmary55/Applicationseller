import requests
from kivy.app import App
class Myfirebase():
    API_KEY = "AIzaSyALyIGpZdNdCwxzcyXDzWfNfVygClR4s4w"
    
    def criaconta(self, email, senha):
        link = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.API_KEY}"
        dados = {"email": email, "password": senha, "returnSecureToken": True}
        requisicao = requests.post(link, data=dados)
        requisicao_dic = requisicao.json() 
        
  
        if requisicao.ok:
            # print("Parabens você cadastrou no sistema")
            # requisicao_dic['kind']
            id_token = requisicao_dic['idToken'] # Authentifica
            # requisicao_dic['email']
            refresh_token = requisicao_dic['refreshToken'] # diz se vai permanecer 
            local_id = requisicao_dic['localId'] # Id do usuasrio

            meu_applicativo = App.get_running_app()
            meu_applicativo.local_id = local_id
            meu_applicativo.id_token = id_token
            
            with open("refreshtoken.txt", "w") as arquivo:
                arquivo.write(refresh_token)
            
            requisicao_id = requests.get(f'https://bancodoapp-c0574-default-rtdb.firebaseio.com/proximo_id_vendedor.json?auth={id_token}')
            id_vendedor = requisicao_id.json()
            print(id_vendedor)
            
            link = f'https://bancodoapp-c0574-default-rtdb.firebaseio.com/{local_id}.json?auth={id_token}'
            dados = f'{{"avatar": "foto1.png", "equipe": "", "total_vendas": "0", "vendas": "", "id_vendedor" : "{id_vendedor}"}}'
            requisicao = requests.patch(link, data= dados)
            meu_applicativo.carregar_info_usuario()
            meu_applicativo.mudar_pagina("homepage")

            proximo_id_vendedor = int(id_vendedor) + 1
            dados = f'{{"proximo_id_vendedor" : {proximo_id_vendedor}}}'

            requests.patch(f"https://bancodoapp-c0574-default-rtdb.firebaseio.com/.json?auth={id_token}", data= dados)
        else:
            mensagem_erro = requisicao_dic["error"]["message"]
            meu_applicativo = App.get_running_app()
            pagina_login = meu_applicativo.root.ids['paginalogin']
            pagina_login.ids['erro_label'].text = mensagem_erro
            pagina_login.ids['erro_label'].color = (1,0, 0, 1)
   
    def fazerlogin(self, email, senha):
        link = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.API_KEY}"
        dados = {"email": email, "password": senha, "returnSecureToken": True}
        requisicao = requests.post(link, data=dados)
        requisicao_dic = requisicao.json() 
        
  
        if requisicao.ok:
            # print("Parabens você cadastrou no sistema")
            # requisicao_dic['kind']
            id_token = requisicao_dic['idToken'] # Authentifica
            # requisicao_dic['email']
            refresh_token = requisicao_dic['refreshToken'] # diz se vai permanecer 
            local_id = requisicao_dic['localId'] # Id do usuasrio

            meu_applicativo = App.get_running_app()
            meu_applicativo.local_id = local_id
            meu_applicativo.id_token = id_token
            
            with open("refreshtoken.txt", "w") as arquivo:
                arquivo.write(refresh_token)
            
  
            meu_applicativo.carregar_info_usuario()
            meu_applicativo.mudar_pagina("homepage")
        else:
            mensagem_erro = requisicao_dic["error"]["message"]
            meu_applicativo = App.get_running_app()
            pagina_login = meu_applicativo.root.ids['paginalogin']
            pagina_login.ids['erro_label'].text = mensagem_erro
            pagina_login.ids['erro_label'].color = (1,0, 0, 1)
        
    def trocartoken(self, refresh_token):
        link = f'https://securetoken.googleapis.com/v1/token?key={self.API_KEY}'
        dados = {"grant_type" : "refresh_token", "refresh_token": refresh_token}
        requisicao = requests.post(link, data=dados)
        requisicao_dict = requisicao.json()

        local_id = requisicao_dict['user_id']
        id_token = requisicao_dict['id_token']
        return local_id, id_token

