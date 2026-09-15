import tkinter as tk
from tkinter import messagebox
from tkinter import ttk


# CORES E VALORES DAS FAIXAS

cores_digitos = {
    "Preto": 0,
    "Marrom": 1,
    "Vermelho": 2,
    "Laranja": 3,
    "Amarelo": 4,
    "Verde": 5,
    "Azul": 6,
    "Violeta": 7,
    "Cinza": 8,
    "Branco": 9
}

multiplicadores = {
    "Prateado": 0.01,
    "Dourado": 0.1,
    "Preto": 1,
    "Marrom": 10,
    "Vermelho": 100,
    "Laranja": 1000,
    "Amarelo": 10000,
    "Verde": 100000,
    "Azul": 1000000,
    "Violeta": 10000000,
    "Cinza": 100000000,
    "Branco": 1000000000
}

tolerancias = {
    "Cinza": 0.05,
    "Violeta": 0.1,
    "Azul": 0.25,
    "Verde": 0.5,
    "Marrom": 1,
    "Vermelho": 2,
    "Dourado": 5,
    "Prateado": 10
}

# Cores usadas para pintar o resistor no Canvas
cores_tela = {
    "Preto": "#171717",
    "Marrom": "#7A3E20",
    "Vermelho": "#D52B2B",
    "Laranja": "#F47C20",
    "Amarelo": "#F2CF35",
    "Verde": "#218C5B",
    "Azul": "#246BCE",
    "Violeta": "#7E3FA0",
    "Cinza": "#7F8C8D",
    "Branco": "#F4F6F7",
    "Dourado": "#C99A22",
    "Prateado": "#B8BEC5"
}


# JANELA PRINCIPAL

root = tk.Tk()
root.title("SENAI - Calculadora de Resistores")
root.geometry("820x650+50+50")
root.resizable(False, False)
root.configure(bg="#EAF1F5")

modo_escolhido = tk.StringVar(value="cores")

# Guarda as quatro cores que aparecem no desenho
cores_do_resistor = ["Vermelho", "Vermelho", "Laranja", "Dourado"]


# FUNÇÕES DE CÁLCULO

def formatar_resistencia(valor):
    """Mostra o valor em Ω, kΩ, MΩ ou GΩ."""

    if valor >= 1000000000:
        return f"{valor / 1000000000:g} GΩ"
    elif valor >= 1000000:
        return f"{valor / 1000000:g} MΩ"
    elif valor >= 1000:
        return f"{valor / 1000:g} kΩ"
    else:
        return f"{valor:g} Ω"


def ler_valor_digitado():
    """Transforma entradas como 3300, 3,3k ou 2M em ohms."""

    texto = entry_valor.get().strip().replace(" ", "")
    texto = texto.replace(",", ".")
    texto = texto.upper()
    texto = texto.replace("OHMS", "").replace("OHM", "").replace("Ω", "")

    fator = 1

    if texto.endswith("K"):
        fator = 1000
        texto = texto[:-1]
    elif texto.endswith("M"):
        fator = 1000000
        texto = texto[:-1]
    elif texto.endswith("G"):
        fator = 1000000000
        texto = texto[:-1]

    valor = float(texto) * fator

    if valor <= 0:
        raise ValueError

    return valor


def descobrir_cores(valor):
    """Procura as três faixas que mais se aproximam do valor digitado."""

    if valor < 0.1 or valor > 99000000000:
        raise ValueError

    melhor_diferenca = None
    melhor_numero = None
    melhor_multiplicador = None
    melhor_valor = None

    # Um resistor de 4 faixas possui dois algarismos significativos.
    for nome_multiplicador, multiplicador in multiplicadores.items():
        for numero in range(10, 100):
            valor_testado = numero * multiplicador
            diferenca = abs(valor_testado - valor)

            if melhor_diferenca is None or diferenca < melhor_diferenca:
                melhor_diferenca = diferenca
                melhor_numero = numero
                melhor_multiplicador = nome_multiplicador
                melhor_valor = valor_testado

    numero_para_cor = {}

    for nome_cor, numero_cor in cores_digitos.items():
        numero_para_cor[numero_cor] = nome_cor

    primeiro_numero = melhor_numero // 10
    segundo_numero = melhor_numero % 10

    primeira_cor = numero_para_cor[primeiro_numero]
    segunda_cor = numero_para_cor[segundo_numero]

    return primeira_cor, segunda_cor, melhor_multiplicador, melhor_valor


def calcular_pelas_cores(evento=None):
    """Calcula a resistência usando as cores selecionadas."""

    primeira_cor = combo_faixa1.get()
    segunda_cor = combo_faixa2.get()
    cor_multiplicador = combo_multiplicador.get()
    cor_tolerancia = combo_tolerancia_cores.get()

    primeiro_numero = cores_digitos[primeira_cor]
    segundo_numero = cores_digitos[segunda_cor]
    multiplicador = multiplicadores[cor_multiplicador]
    tolerancia = tolerancias[cor_tolerancia]

    numero_formado = (primeiro_numero * 10) + segundo_numero
    resistencia = numero_formado * multiplicador

    label_resultado.config(
        text=f"Resistência: {formatar_resistencia(resistencia)} ±{tolerancia:g}%"
    )

    label_detalhes.config(
        text=(
            f"Faixas: {primeira_cor} • {segunda_cor} • "
            f"{cor_multiplicador} • {cor_tolerancia}"
        )
    )

    cores_do_resistor[0] = primeira_cor
    cores_do_resistor[1] = segunda_cor
    cores_do_resistor[2] = cor_multiplicador
    cores_do_resistor[3] = cor_tolerancia

    desenhar_resistor()


def calcular_pelo_valor(evento=None):
    """Descobre as cores usando o valor informado pelo usuário."""

    try:
        valor = ler_valor_digitado()

        primeira_cor, segunda_cor, cor_multiplicador, valor_encontrado = descobrir_cores(valor)
        cor_tolerancia = combo_tolerancia_valor.get()
        tolerancia = tolerancias[cor_tolerancia]

        cores_do_resistor[0] = primeira_cor
        cores_do_resistor[1] = segunda_cor
        cores_do_resistor[2] = cor_multiplicador
        cores_do_resistor[3] = cor_tolerancia

        label_resultado.config(
            text=(
                f"Cores: {primeira_cor}, {segunda_cor}, "
                f"{cor_multiplicador} e {cor_tolerancia}"
            )
        )

        if abs(valor_encontrado - valor) < 0.000001:
            label_detalhes.config(
                text=f"{formatar_resistencia(valor_encontrado)} ±{tolerancia:g}%"
            )
        else:
            label_detalhes.config(
                text=(
                    "Valor de 4 faixas mais próximo: "
                    f"{formatar_resistencia(valor_encontrado)} ±{tolerancia:g}%"
                )
            )

        desenhar_resistor()

    except ValueError:
        messagebox.showerror(
            "Valor inválido",
            "Digite uma resistência válida entre 0,1 Ω e 99 GΩ.\n"
            "Exemplos: 3300, 3,3k ou 2M."
        )


# TROCA ENTRE OS DOIS MODOS

def trocar_modo():
    """Exibe apenas os campos do modo escolhido."""

    if modo_escolhido.get() == "cores":
        frame_valor.grid_remove()
        frame_cores.grid()
        calcular_pelas_cores()
    else:
        frame_cores.grid_remove()
        frame_valor.grid()
        label_resultado.config(text="Digite o valor da resistência")
        label_detalhes.config(text="Depois, clique em Calcular cores")


# DESENHO DO RESISTOR

def desenhar_resistor():
    canvas.delete("all")

    # Fios metálicos
    canvas.create_line(25, 105, 165, 105, fill="#70777D", width=5)
    canvas.create_line(555, 105, 695, 105, fill="#70777D", width=5)

    # Corpo do resistor
    canvas.create_oval(
        140, 70, 220, 140,
        fill="#E7D4A1",
        outline="#6E5A32",
        width=2
    )

    canvas.create_oval(
        500, 70, 580, 140,
        fill="#E7D4A1",
        outline="#6E5A32",
        width=2
    )

    canvas.create_rectangle(
        180, 65, 540, 145,
        fill="#F0DFA8",
        outline="#6E5A32",
        width=2
    )

    # Brilho na parte superior
    canvas.create_line(190, 75, 530, 75, fill="#FFF2C8", width=3)

    # As quatro faixas coloridas
    posicoes = [235, 310, 395, 490]

    for posicao, nome_cor in zip(posicoes, cores_do_resistor):
        canvas.create_rectangle(
            posicao - 13, 67,
            posicao + 13, 143,
            fill=cores_tela[nome_cor],
            outline="#4C4434"
        )

    canvas.create_text(
        360, 25,
        text="Resistor de 4 faixas",
        fill="#173247",
        font=("Arial", 13, "bold")
    )

    nomes = "   •   ".join(cores_do_resistor)

    canvas.create_text(
        360, 180,
        text=nomes,
        fill="#53697A",
        font=("Arial", 10)
    )


# TÍTULO

label_titulo = tk.Label(
    root,
    text="Calculadora de Resistores",
    bg="#EAF1F5",
    fg="#173247",
    font=("Arial", 22, "bold")
)
label_titulo.pack(pady=(18, 2))

label_subtitulo = tk.Label(
    root,
    text="Calcule o valor ou descubra as cores de um resistor de quatro faixas.",
    bg="#EAF1F5",
    fg="#53697A",
    font=("Arial", 10)
)
label_subtitulo.pack(pady=(0, 14))


# ESCOLHA DO MODO

frame_principal = tk.Frame(root, bg="#FFFFFF", padx=20, pady=15)
frame_principal.pack(padx=25, fill="x")

label_modo = tk.Label(
    frame_principal,
    text="Como deseja informar o resistor?",
    bg="#FFFFFF",
    fg="#173247",
    font=("Arial", 11, "bold")
)
label_modo.grid(row=0, column=0, columnspan=4, sticky="w")

radio_cores = tk.Radiobutton(
    frame_principal,
    text="Pelas cores",
    variable=modo_escolhido,
    value="cores",
    command=trocar_modo,
    bg="#FFFFFF",
    activebackground="#FFFFFF"
)
radio_cores.grid(row=1, column=0, sticky="w", pady=(7, 10))

radio_valor = tk.Radiobutton(
    frame_principal,
    text="Pelo valor da resistência",
    variable=modo_escolhido,
    value="valor",
    command=trocar_modo,
    bg="#FFFFFF",
    activebackground="#FFFFFF"
)
radio_valor.grid(row=1, column=1, columnspan=2, sticky="w", pady=(7, 10))


# MODO 1: ENTRADA PELAS CORES

frame_cores = tk.Frame(frame_principal, bg="#FFFFFF")
frame_cores.grid(row=2, column=0, columnspan=4, sticky="w")

lista_digitos = list(cores_digitos.keys())
lista_multiplicadores = list(multiplicadores.keys())
lista_tolerancias = list(tolerancias.keys())

tk.Label(frame_cores, text="Faixa 1:", bg="#FFFFFF").grid(
    row=0, column=0, padx=(0, 10), sticky="w"
)

tk.Label(frame_cores, text="Faixa 2:", bg="#FFFFFF").grid(
    row=0, column=1, padx=10, sticky="w"
)

tk.Label(frame_cores, text="Multiplicador:", bg="#FFFFFF").grid(
    row=0, column=2, padx=10, sticky="w"
)

tk.Label(frame_cores, text="Tolerância:", bg="#FFFFFF").grid(
    row=0, column=3, padx=10, sticky="w"
)

combo_faixa1 = ttk.Combobox(frame_cores, values=lista_digitos, state="readonly", width=16)
combo_faixa1.set("Vermelho")
combo_faixa1.grid(row=1, column=0, padx=(0, 10), pady=5)

combo_faixa2 = ttk.Combobox(frame_cores, values=lista_digitos, state="readonly", width=16)
combo_faixa2.set("Vermelho")
combo_faixa2.grid(row=1, column=1, padx=10, pady=5)

combo_multiplicador = ttk.Combobox(
    frame_cores,
    values=lista_multiplicadores,
    state="readonly",
    width=16
)
combo_multiplicador.set("Laranja")
combo_multiplicador.grid(row=1, column=2, padx=10, pady=5)

combo_tolerancia_cores = ttk.Combobox(
    frame_cores,
    values=lista_tolerancias,
    state="readonly",
    width=16
)
combo_tolerancia_cores.set("Dourado")
combo_tolerancia_cores.grid(row=1, column=3, padx=10, pady=5)

# Atualiza o resistor assim que uma cor for alterada
combo_faixa1.bind("<<ComboboxSelected>>", calcular_pelas_cores)
combo_faixa2.bind("<<ComboboxSelected>>", calcular_pelas_cores)
combo_multiplicador.bind("<<ComboboxSelected>>", calcular_pelas_cores)
combo_tolerancia_cores.bind("<<ComboboxSelected>>", calcular_pelas_cores)

botao_calcular_cores = tk.Button(
    frame_cores,
    text="Calcular resistência",
    command=calcular_pelas_cores,
    bg="#00858D",
    fg="#FFFFFF",
    activebackground="#006A70",
    activeforeground="#FFFFFF",
    font=("Arial", 10, "bold"),
    relief="flat",
    padx=15,
    pady=7,
    cursor="hand2"
)
botao_calcular_cores.grid(row=2, column=0, columnspan=4, sticky="w", pady=(8, 0))


# MODO 2: ENTRADA PELO VALOR

frame_valor = tk.Frame(frame_principal, bg="#FFFFFF")
frame_valor.grid(row=2, column=0, columnspan=4, sticky="w")

tk.Label(frame_valor, text="Valor da resistência:", bg="#FFFFFF").grid(
    row=0, column=0, padx=(0, 15), sticky="w"
)

tk.Label(frame_valor, text="Tolerância:", bg="#FFFFFF").grid(
    row=0, column=1, padx=(0, 15), sticky="w"
)

entry_valor = ttk.Entry(frame_valor, width=28)
entry_valor.insert(0, "3300")
entry_valor.grid(row=1, column=0, padx=(0, 15), pady=5)
entry_valor.bind("<Return>", calcular_pelo_valor)

combo_tolerancia_valor = ttk.Combobox(
    frame_valor,
    values=lista_tolerancias,
    state="readonly",
    width=18
)
combo_tolerancia_valor.set("Dourado")
combo_tolerancia_valor.grid(row=1, column=1, padx=(0, 15), pady=5)

botao_calcular_valor = tk.Button(
    frame_valor,
    text="Calcular cores",
    command=calcular_pelo_valor,
    bg="#00858D",
    fg="#FFFFFF",
    activebackground="#006A70",
    activeforeground="#FFFFFF",
    font=("Arial", 10, "bold"),
    relief="flat",
    padx=15,
    pady=7,
    cursor="hand2"
)
botao_calcular_valor.grid(row=2, column=0, columnspan=2, sticky="w", pady=(8, 0))


# RESULTADO E IMAGEM DO RESISTOR

frame_resultado = tk.Frame(root, bg="#FFFFFF", padx=20, pady=14)
frame_resultado.pack(padx=25, pady=15, fill="both", expand=True)

tk.Label(
    frame_resultado,
    text="Resultado",
    bg="#FFFFFF",
    fg="#173247",
    font=("Arial", 11, "bold")
).pack(anchor="w")

label_resultado = tk.Label(
    frame_resultado,
    text="",
    bg="#FFFFFF",
    fg="#006A70",
    font=("Arial", 16, "bold")
)
label_resultado.pack(anchor="w", pady=(5, 0))

label_detalhes = tk.Label(
    frame_resultado,
    text="",
    bg="#FFFFFF",
    fg="#53697A",
    font=("Arial", 10)
)
label_detalhes.pack(anchor="w", pady=(2, 8))

canvas = tk.Canvas(
    frame_resultado,
    width=720,
    height=205,
    bg="#F8FAFC",
    highlightthickness=1,
    highlightbackground="#D2DEE6"
)
canvas.pack()



trocar_modo()
root.mainloop()
