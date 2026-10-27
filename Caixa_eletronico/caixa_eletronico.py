import tkinter as tk
from tkinter import messagebox
import os
import json
import hashlib
import hmac
import secrets


# O arquivo fica na mesma pasta do código, mesmo abrindo por outro lugar
arquivo_saldos = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saldos.txt")
conta_atual = ""
saldo = 1000
COR_BEGE = "#101B2D"
COR_CARTAO = "#192840"
COR_TEXTO = "#EAF0F8"
COR_DESTAQUE = "#34D399"
arquivo_senhas = os.path.join(os.path.dirname(os.path.abspath(__file__)), "senhas.json")


def validar_senha(conta, senha, confirmacao):
    try:
        with open(arquivo_senhas, "r", encoding="utf-8") as f:
            senhas = json.load(f)
    except FileNotFoundError:
        senhas = {}

    if conta in senhas:
        registro = senhas[conta]
        resumo = hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"),
                                      bytes.fromhex(registro["sal"]), 600000).hex()
        if not hmac.compare_digest(resumo, registro["hash"]):
            messagebox.showerror("Acesso negado", "Senha incorreta para esta conta.")
            return False
    else:
        if senha != confirmacao:
            messagebox.showerror("Senhas diferentes", "Digite a mesma senha nos dois campos para cadastrar a conta.")
            return False
        sal = secrets.token_bytes(16)
        senhas[conta] = {
            "sal": sal.hex(),
            "hash": hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), sal, 600000).hex()
        }
        temporario = arquivo_senhas + ".tmp"
        with open(temporario, "w", encoding="utf-8") as f:
            json.dump(senhas, f, indent=2)
        os.replace(temporario, arquivo_senhas)
    return True


# LEITURA E ESCRITA DO ARQUIVO

def carregar_saldos():
    saldos = {}

    try:
        with open(arquivo_saldos, "r", encoding="utf-8") as f:
            for linha in f:
                # Cada linha guarda conta;saldo. O rsplit separa pelo último ;
                conta, valor = linha.strip().rsplit(";", 1)
                saldos[conta] = int(valor)
                if saldos[conta] < 0:
                    raise ValueError
    except FileNotFoundError:
        # Na primeira utilização ainda não existe arquivo
        pass

    return saldos


def salvar_saldo():
    saldos = carregar_saldos()
    saldos[conta_atual] = saldo

    with open(arquivo_saldos, "w", encoding="utf-8") as f:
        # Grava todas as contas para não apagar o saldo dos outros usuários
        for conta, valor in saldos.items():
            f.write(f"{conta};{valor}\n")


# FUNÇÕES DO CAIXA

def entrar():
    global conta_atual, saldo

    conta = entry_conta.get().strip()
    senha = entry_senha.get()

    if not conta or not senha:
        messagebox.showerror("Erro", "Preencha a conta e a senha.")
        return

    try:
        saldos = carregar_saldos()
    except (OSError, ValueError, UnicodeError):
        messagebox.showerror("Erro", "Não foi possível ler os saldos. Verifique o arquivo saldos.txt.")
        return

    # A senha só é pedida para iniciar, como foi solicitado na atividade
    conta_atual = conta
    if conta in saldos:
        saldo = saldos[conta]
    else:
        saldo = 1000

    entry_senha.delete(0, tk.END)
    frame_login.pack_forget()
    frame_menu.pack(pady=15)
    label_conta.config(text=f"Conta: {conta_atual}")
    label_resultado.config(text="Escolha uma operação no menu.")


def ler_valor():
    texto = entry_valor.get().strip()

    try:
        valor = int(texto)
    except ValueError:
        if "." in texto or "," in texto:
            messagebox.showerror("Erro", "Valores fracionários não são aceitos. Digite um valor inteiro.")
        else:
            messagebox.showerror("Erro", "Digite um valor numérico inteiro.")
        return None

    if valor <= 0:
        messagebox.showerror("Erro", "O valor precisa ser maior que zero.")
        return None

    return valor


def consultar_saldo():
    label_resultado.config(text=f"Seu saldo atual é: R$ {saldo},00")


def calcular_cedulas(valor):
    cedulas = [100, 50, 20, 10, 5, 2]
    quantidades = [0, 0, 0, 0, 0, 0]
    restante = valor

    # Se for ímpar, separa uma nota de 5 antes de calcular as notas pares.
    # Isso evita sobrar R$ 1 em valores como 7 (5 + 2) e 101.
    if restante % 2 != 0:
        if restante < 5:
            return None
        quantidades[4] = 1
        restante -= 5

    i = 0
    while i < len(cedulas):
        if cedulas[i] != 5:
            # // conta as notas inteiras e % guarda o que ainda falta entregar
            quantidades[i] = restante // cedulas[i]
            restante = restante % cedulas[i]
        i += 1

    return quantidades


def sacar():
    global saldo

    valor = ler_valor()
    if valor is None:
        return

    if valor > saldo:
        messagebox.showerror("Erro", "Saldo insuficiente para realizar o saque.")
        return

    # O enunciado pede que R$ 11 seja recusado, mesmo sendo possível com 5 + 2 + 2 + 2
    if valor == 11:
        messagebox.showerror("Erro", "O caixa não trabalha com saque de R$ 11,00, conforme a atividade.")
        return

    quantidades = calcular_cedulas(valor)
    if quantidades is None:
        messagebox.showerror("Erro", "Não é possível formar esse valor com notas de 100, 50, 20, 10, 5 e 2.")
        return

    saldo -= valor
    cedulas = [100, 50, 20, 10, 5, 2]
    resultado = "Saque realizado com sucesso!\nEntregar:\n"

    i = 0
    while i < len(cedulas):
        if quantidades[i] > 0:
            resultado += f"{quantidades[i]} cédula(s) de R$ {cedulas[i]},00\n"
        i += 1

    resultado += f"\nSaldo atual: R$ {saldo},00"
    label_resultado.config(text=resultado)
    entry_valor.delete(0, tk.END)


def depositar():
    global saldo

    valor = ler_valor()
    if valor is None:
        return

    saldo += valor
    label_resultado.config(text=f"Depósito realizado com sucesso!\nSaldo atual: R$ {saldo},00")
    entry_valor.delete(0, tk.END)


def sair():
    global conta_atual

    try:
        salvar_saldo()
    except (OSError, ValueError, UnicodeError):
        messagebox.showerror("Erro", "Não foi possível salvar o saldo. Tente sair novamente.")
        return

    messagebox.showinfo("Encerramento", "Saldo salvo. Obrigado por usar nosso sistema!")
    conta_atual = ""
    frame_menu.pack_forget()
    frame_login.pack(pady=25)
    entry_conta.delete(0, tk.END)
    entry_senha.delete(0, tk.END)
    entry_valor.delete(0, tk.END)
    entry_opcao.delete(0, tk.END)
    entry_confirmacao.delete(0, tk.END)
    entry_conta.focus_set()


def executar_opcao():
    opcao = entry_opcao.get().strip()

    if opcao == "1":
        consultar_saldo()
    elif opcao == "2":
        sacar()
    elif opcao == "3":
        depositar()
    elif opcao == "4":
        sair()
    else:
        messagebox.showerror("Erro", "Opção inválida! Escolha uma opção de 1 a 4.")


def fechar_janela():
    # Fechar pelo X também salva o saldo da conta que estiver aberta
    if conta_atual:
        sair()
        if conta_atual:
            return
    root.destroy()


# JANELA PRINCIPAL

root = tk.Tk()
root.title("Simulador de Caixa Eletrônico")
root.geometry("580x800")
root.resizable(False, False)
root.config(bg=COR_BEGE)
root.protocol("WM_DELETE_WINDOW", fechar_janela)

label_titulo = tk.Label(root, text="Caixa Eletrônico", font=("Arial", 22, "bold"), bg=COR_BEGE)
label_titulo.pack(pady=20)


# TELA DE CONTA E SENHA

frame_login = tk.Frame(root, bg=COR_BEGE)
frame_login.pack(pady=25)

label_boas_vindas = tk.Label(frame_login, text="Bem-vindo ao seu caixa digital", bg=COR_BEGE)
label_boas_vindas.pack(pady=10)

label_conta_login = tk.Label(frame_login, text="Conta:", bg=COR_BEGE)
label_conta_login.pack(pady=5)
entry_conta = tk.Entry(frame_login, width=28)
entry_conta.pack(pady=5)

label_senha = tk.Label(frame_login, text="Senha:", bg=COR_BEGE)
label_senha.pack(pady=5)
entry_senha = tk.Entry(frame_login, show="*", width=28)
entry_senha.pack(pady=5)

tk.Label(frame_login, text="Confirme a senha (somente no primeiro acesso):", bg=COR_BEGE).pack(pady=(15, 5))
entry_confirmacao = tk.Entry(frame_login, show="*", width=28)
entry_confirmacao.pack(pady=5)
tk.Label(frame_login, text="Conta nova? Escolha uma senha e repita acima.\nConta existente? Use a senha cadastrada.", bg=COR_BEGE).pack(pady=12)

botao_entrar = tk.Button(frame_login, text="Entrar", width=15, command=entrar)
botao_entrar.pack(pady=20)


# MENU (continua na tela até clicar em Sair)

frame_menu = tk.Frame(root, bg=COR_BEGE)

label_conta = tk.Label(frame_menu, text="", font=("Arial", 12, "bold"), bg=COR_BEGE)
label_conta.pack(pady=5)

label_valor = tk.Label(frame_menu, text="Valor inteiro para saque ou depósito (R$):", bg=COR_BEGE)
label_valor.pack(pady=5)
entry_valor = tk.Entry(frame_menu, width=25)
entry_valor.pack(pady=5)

frame_botoes = tk.Frame(frame_menu, bg=COR_BEGE)
frame_botoes.pack(pady=10)

botao_saldo = tk.Button(frame_botoes, text="1 - Consultar saldo", width=18, command=consultar_saldo)
botao_saldo.grid(row=0, column=0, padx=5, pady=5)
botao_sacar = tk.Button(frame_botoes, text="2 - Sacar", width=18, command=sacar)
botao_sacar.grid(row=0, column=1, padx=5, pady=5)
botao_depositar = tk.Button(frame_botoes, text="3 - Depositar", width=18, command=depositar)
botao_depositar.grid(row=1, column=0, padx=5, pady=5)
botao_sair = tk.Button(frame_botoes, text="4 - Sair", width=18, command=sair)
botao_sair.grid(row=1, column=1, padx=5, pady=5)

label_opcao = tk.Label(frame_menu, text="Ou digite uma opção de 1 a 4:", bg=COR_BEGE)
label_opcao.pack(pady=5)
entry_opcao = tk.Entry(frame_menu, width=8)
entry_opcao.pack(pady=5)
botao_executar = tk.Button(frame_menu, text="Executar opção", command=executar_opcao)
botao_executar.pack(pady=5)

label_resultado = tk.Label(frame_menu, text="", bg=COR_BEGE, font=("Arial", 11), justify="left", wraplength=460)
label_resultado.pack(pady=15)

def aplicar_estilo(widget):
    for filho in widget.winfo_children():
        if isinstance(filho, tk.Label):
            filho.configure(fg=COR_TEXTO, font=("Segoe UI", 11))
        elif isinstance(filho, tk.Entry):
            filho.configure(bg=COR_CARTAO, fg=COR_TEXTO, insertbackground=COR_DESTAQUE,
                            relief="flat", font=("Segoe UI", 13),
                            highlightthickness=1, highlightbackground="#34465F",
                            highlightcolor=COR_DESTAQUE)
        elif isinstance(filho, tk.Button):
            filho.configure(bg=COR_DESTAQUE, fg="#102A24", activebackground="#6EE7B7",
                            activeforeground="#102A24", relief="flat", bd=0,
                            font=("Segoe UI", 11, "bold"), padx=12, pady=10,
                            cursor="hand2")
        aplicar_estilo(filho)


aplicar_estilo(root)
label_titulo.configure(fg=COR_DESTAQUE, font=("Segoe UI", 24, "bold"))
label_resultado.configure(bg=COR_CARTAO, padx=18, pady=16, width=48)
entry_senha.bind("<Return>", lambda event: entrar())
entry_confirmacao.bind("<Return>", lambda event: entrar())
entry_opcao.bind("<Return>", lambda event: executar_opcao())
entry_conta.focus_set()
root.mainloop()
