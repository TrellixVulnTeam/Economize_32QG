"""
This file is part of Economize!.

Economize! is free software: you can redistribute
it and/or modify it under the terms of the GNU General Public License 
as published by the Free Software Foundation, either version 3 of
the License, or any later version.

Economize! is distributed in the hope that 
it will be useful, but WITHOUT ANY WARRANTY; without even the 
implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Economize!.  If not, see <https://www.gnu.org/licenses/>.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.modalview import ModalView
from kivy.uix.button import Button
from functools import partial
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.properties import ObjectProperty
from kivy.metrics import dp
import telaPrincipal as tp

#Carrega a tela .kv correspondente
Builder.load_file("telas/alteraContas.kv")

#Importa o banco de dados
from model import db

#Importa as configurações gerais do sistema
from appConfig import AppConfig

#Classe para o label com background_color
#   NOME DA CONTA
class NomeC(Label):
        def on_size(self, *args):
            self.canvas.before.clear()
            self.height=dp(40)
            self.font_size="22sp"
            self.text_size=self.width-dp(50), dp(40)
            self.valign="center"
            self.size_hint_y= None
            with self.canvas.before:
                Color(.94, .94, .94, 1)
                RoundedRectangle(pos=self.pos, 
                                size=self.size, 
                                radius= [(20, 20), (20,20), (1,1), (1,1)]
                )

#Classe para os outros labels
#   SALDO e TIPO DA CONTA
class Info(Label):
        def on_size(self, *args):
            self.height=self.texture_size[1] + dp(10)
            self.text_size=self.width-dp(50), self.texture_size[1]
            self.size_hint_y= None

#Classe para os botões
#   TORNAR PADRÃO e EXCLUIR CONTA
class btnFunc(Button):
        def on_size(self, *args):
            self.size_hint_y=None
            self.size_hint_x=0.5
            # self.height=dp(40)
            self.halign="center"
            self.font_size="16sp"
            self.background_normal= "imgs/btnAzul02.png"
            self.background_down= "imgs/btnAzul02.png"
                        
#Classe para o label que se comportará como uma linha
#   LINHA
class Linha(Label):
        def on_size(self, *args):
            self.canvas.before.clear()
            self.height=dp(1)
            self.size_hint_y= None
            with self.canvas.before:
                Color(.41, .58, .79, 1)
                Rectangle(pos=self.pos, size=self.size)

class ModalLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.padding=Window.width/20
        self.canvas.clear()
        self.canvas.before.clear()

#CLASS KV
class AlteraContas(Screen):
    #Objetos da tela criados no .py
    raiz = None
    box = None
    modal=None

    #Método que torna a conta selecionada como a padrão, que será exibida na tela principal
    def tornaPadrao(self, *args):
        AppConfig.set_config("contaPadrao", args[0])
        AppConfig.set_config("idConta", args[1])
        self.manager.current="principal"
        self.manager.transition.direction = "right"
        self.manager.current_screen.criarMensagem('Conta padrão alterada com sucesso')
        self.manager.current_screen.atualizaSaldo()
        self.manager.current_screen.mostrarMovimentacoes()

    #Método que abre um modal
    def desejaExcluirConta(self, *args):
        #Pergunta
        layout = ModalLayout(
                    size_hint_y=None
                )
        layout.add_widget(Label(
                            text=f"Quer mesmo excluir a \nconta [i]{args[0]}[/i]?",
                            markup=True,
                            size_hint_y=None
                        )
        )

        #Botões
        layoutBtn = ModalLayout(
            orientation ="horizontal",
            size_hint_y=None,
            spacing=Window.width/20

        )

        #Excluir
        btnSIM = Button(
            text='Sim', 
            size_hint_y=None,
            background_normal="imgs/btnVerde.png",
            background_down="imgs/btnVerde02.png"
        )
        btnSIM.bind(on_press=partial(self.excluiConta, args[0]))
        
        #Não faz nada
        btnNAO = Button(
            text='Não', 
            size_hint_y=None,
            background_normal="imgs/bordaBotaoAtivoVermelho.png",
            background_down="imgs/btnVermelho.png",
            color=(0,0,0,1)
        )

        layoutBtn.add_widget(btnSIM)
        layoutBtn.add_widget(btnNAO)

        layout.add_widget(layoutBtn)

        #Modal
        view = ModalView(
                size_hint=(0.58, 0.2),
                height=40,
                background="imgs/modalView.png")
        view.add_widget(layout)
        view.open()
        self.modal = view

        #Os dois botões fecham o modal
        btnSIM.bind(on_press=self.modal.dismiss)
        btnNAO.bind(on_press=self.modal.dismiss)

    #Método que exclue a conta selecionada 
    def excluiConta(self, *args):
        padrao = AppConfig.get_config("contaPadrao")
        if args[0] == padrao:
            AppConfig.set_config("contaPadrao", "")
            AppConfig.set_config("idConta", "")
        #Parece que tá errado, mas não tá
        conta = db.retorna_conta_nome(args[0])
        db.remove_conta_nome(conta[0])
        self.exibirContas()

    #Método que monta e exibe as contas  cadastradas
    def exibirContas(self):

        #Para que a tela apareça de forma correta é necessário 
        # limpar a tela antes de carrega-la de novo
        try:
            #Limpa o ScrollView
            self.raiz.clear_widgets()
        except AttributeError:
            #Se não conseguir é porque 
            # é a primeira vez que a tela é aberta,
            # portanto não precisa de limpeza
            pass

        try:
            #limpa o BoxLayout
            self.box.clear_widgets()
        except AttributeError:
            #Se não conseguir é porque 
            # é a primeira vez que a tela é aberta,
            # portanto não precisa de limpeza
            pass

        #ScrollView
        rolagem = ScrollView(pos_hint={"top": 0.85}, size_hint_y=0.71)

        #BoxLayout
        #Ele é necessário por causa da mensagem final e 
        # da mensagem para nenhuma conta cadastrada
        layout = BoxLayout(size_hint_y=None, padding=(Window.width/20,0), spacing=20)
        
        #Busca as contas cadastradas no banco de dados
        contas = db.retorna_contas()
        #Lê quantas são
        quant = len(contas)

        #Recebe a lista de tipos que o aplicativo tem disponível
        listaTipos = AppConfig.tipos

        if quant == 0:
            layout.add_widget(tp.Final(text="Não há contas cadastradas ainda", size_hint_y=None))
        else:
            #Adiciona os widgets à tela
            for ind, conta in enumerate(contas):
                #Nome da conta
                nome = NomeC(text=conta[1])
                layout.add_widget(nome)

                #GridLayout
                Contas = GridLayout(cols=2, size_hint_y=None, spacing=10, padding=(0,20))
                
                #Saldo da conta
                Contas.add_widget(Info(text=f"R$ {conta[3]:.2f}"))

                #Botão para tornar essa conta a conta padrão
                btn = btnFunc(text='Tornar\npadrão', size_hint_y=None)
                #Ligação do botão com a função 'tornaPadrão()'
                btn.bind(on_press=partial(self.tornaPadrao, conta[1], conta[0]))
                Contas.add_widget(btn)

                #Tipo da conta
                TextoTipo = listaTipos[conta[2]-1]
                Contas.add_widget(Info(text=f"{TextoTipo}", color=(.4, .4, .4, 1)))
                
                #Botão para excluir essa conta. Não há confirmação
                btn2 = btnFunc(text='Excluir\nconta', size_hint_y=None)
                #Ligação do botão com a função 'desejaExcluirConta()'
                btn2.bind(on_press=partial(self.desejaExcluirConta, conta[1]))
                Contas.add_widget(btn2)

                #Adiciona o GridLayout que contem as contas
                layout.add_widget(Contas)   

                #Adiciona uma linha
                layout.add_widget(Linha(text=" "))       
            
            #Marca o fim da lista
            layout.add_widget(tp.Final(text="Fim"))

        #Salva o objeto Boxlayout
        self.box = layout
        rolagem.add_widget(layout)
        #Salva o objeto ScrollView
        self.raiz = rolagem
        self.add_widget(rolagem)

    #Esse trio de funções serve para a utilização correta
    # da tecla "esc" e do botão voltar do android
    def on_pre_enter(self, *args):
        Window.bind(on_keyboard=self.voltar)
        return super().on_pre_enter(*args)

    def voltar(self, window, key, *args):
        if key == 27:
            self.manager.current="principal"
            self.manager.transition.direction="right"
            return True

    def on_pre_leave(self, *args):
        Window.unbind(on_keyboard=self.voltar)
        return super().on_pre_leave(*args)