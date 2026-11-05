```python
# Bibliotecas utilizadas:
# NumPy      -> cálculos matemáticos e processamento do áudio
# SoundDevice -> gravação através do microfone
# Matplotlib -> criação do gráfico
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt


# ==========================================================
# CONFIGURAÇÕES
# ==========================================================

# Quantidade de amostras capturadas por segundo.
# 44.100 Hz é uma taxa comum para áudio.
TAXA_AMOSTRAGEM = 44100

# Duração da gravação em segundos.
DURACAO = 3

# Valor utilizado como referência para converter
# a intensidade do sinal em uma estimativa de decibéis.
#
# IMPORTANTE:
# Este projeto NÃO substitui um decibelímetro profissional.
# O valor em dB é uma estimativa e depende do microfone
# e da calibração utilizada.
CALIBRACAO_DB = 94

# Nível sonoro utilizado para gerar o alerta.
LIMITE_ALERTA = 85


# ==========================================================
# INÍCIO DO PROGRAMA
# ==========================================================

print("========================================")
print("       MEDIDOR DE POLUIÇÃO SONORA")
print("========================================")

# Aguarda o usuário pressionar ENTER antes de iniciar
# a gravação.
input("\nPressione ENTER para iniciar...")

print("\nGravando por 3 segundos...")


# ==========================================================
# GRAVAÇÃO DO ÁUDIO
# ==========================================================

# Calcula a quantidade total de amostras:
#
# duração × quantidade de amostras por segundo
#
# Neste caso:
# 3 × 44.100 = 132.300 amostras
#
# channels=1 indica que estamos utilizando apenas
# um canal de áudio (mono).
audio = sd.rec(
    int(DURACAO * TAXA_AMOSTRAGEM),
    samplerate=TAXA_AMOSTRAGEM,
    channels=1,
    dtype="float32"
)

# Aguarda a gravação terminar.
sd.wait()


# O SoundDevice retorna o áudio como uma matriz.
# Como estamos utilizando apenas um canal, cada amostra
# fica armazenada dentro de uma pequena lista.
#
# Exemplo:
#
# [[0.012],
#  [0.018],
#  [0.025]]
#
# O [:, 0] significa:
#   : -> todas as amostras
#   0 -> primeiro canal
#
# O resultado passa a ser uma sequência simples:
#
# [0.012, 0.018, 0.025]
audio = audio[:, 0]


# ==========================================================
# ANÁLISE DO NÍVEL SONORO
# ==========================================================

# Define o tamanho de cada janela de análise.
#
# 0.1 segundo × 44.100 amostras/segundo
# = 4.410 amostras por janela.
#
# Isso permite analisar como o nível sonoro varia
# durante a gravação.
TAMANHO_JANELA = int(0.1 * TAXA_AMOSTRAGEM)

# Listas que armazenarão:
# - nível sonoro de cada janela
# - instante correspondente no áudio
niveis_db = []
tempos = []


# Percorre o áudio de janela em janela.
for inicio in range(0, len(audio), TAMANHO_JANELA):

    # Extrai uma pequena parte do áudio.
    trecho = audio[inicio:inicio + TAMANHO_JANELA]

    # Verifica se existe algum dado nesse trecho.
    if len(trecho) == 0:
        continue

    # Calcula o RMS (Root Mean Square).
    #
    # O RMS representa a intensidade média do sinal
    # de áudio naquele intervalo.
    rms = np.sqrt(np.mean(trecho ** 2))

    # Evita problemas matemáticos ao calcular log10(0).
    #
    # Como log10(0) não existe, utilizamos um valor
    # mínimo para representar sinais muito baixos.
    if rms < 0.000001:
        rms = 0.000001

    # Converte a intensidade do sinal para uma escala
    # aproximada de decibéis.
    #
    # O logaritmo é utilizado porque o decibel é uma
    # escala logarítmica.
    db = 20 * np.log10(rms) + CALIBRACAO_DB

    # Guarda o nível calculado.
    niveis_db.append(db)

    # Calcula o tempo correspondente ao início da janela.
    tempos.append(inicio / TAXA_AMOSTRAGEM)


# Calcula a média de todos os níveis registrados.
nivel_medio = np.mean(niveis_db)


# ==========================================================
# ANÁLISE DE FREQUÊNCIA
# ==========================================================

# Aplica a Transformada Rápida de Fourier (FFT).
#
# A FFT transforma o sinal do domínio do tempo
# para o domínio das frequências.
#
# Isso permite descobrir quais frequências estão
# presentes no áudio.
fft = np.fft.rfft(audio)


# Cria o eixo de frequências correspondente
# aos resultados da FFT.
frequencias = np.fft.rfftfreq(
    len(audio),
    1 / TAXA_AMOSTRAGEM
)


# Calcula a intensidade de cada frequência.
intensidade = np.abs(fft)


# Ignora frequências abaixo de 20 Hz.
#
# 20 Hz é aproximadamente o limite inferior
# da faixa de audição humana.
intensidade[frequencias < 20] = 0


# Procura a posição da frequência que possui
# a maior intensidade.
indice = np.argmax(intensidade)


# Utiliza o índice encontrado para descobrir
# qual é a frequência predominante.
frequencia_principal = frequencias[indice]


# ==========================================================
# EXIBIÇÃO DOS RESULTADOS
# ==========================================================

print("\n========================================")
print("              RESULTADO")
print("========================================")

# Mostra a frequência mais intensa encontrada.
print(f"Frequência predominante: {frequencia_principal:.1f} Hz")

# Mostra o nível sonoro médio estimado.
print(f"Nível sonoro médio: {nivel_medio:.1f} dB")


# ==========================================================
# CRIAÇÃO DO GRÁFICO
# ==========================================================

# Cria uma janela de gráfico com 10 × 5 polegadas.
plt.figure(figsize=(10, 5))


# Desenha a variação do nível sonoro ao longo do tempo.
#
# Eixo X -> tempo
# Eixo Y -> nível sonoro
plt.plot(tempos, niveis_db, linewidth=2)


# Cria uma linha horizontal indicando
# o limite de alerta configurado.
plt.axhline(
    LIMITE_ALERTA,
    linestyle="--",
    linewidth=2,
    label="Limite de alerta: 85 dB"
)


# Nomeia os eixos.
plt.xlabel("Tempo (segundos)")
plt.ylabel("Nível sonoro estimado (dB)")


# Define o título do gráfico.
# Também mostra o nível médio calculado.
plt.title(
    f"Medidor de Poluição Sonora | "
    f"Média: {nivel_medio:.1f} dB"
)


# Adiciona uma grade para facilitar
# a leitura dos valores.
plt.grid()

# Exibe a legenda do limite de alerta.
plt.legend()


# ==========================================================
# ALERTA
# ==========================================================

# Verifica se o nível médio atingiu ou ultrapassou
# o limite configurado.
if nivel_medio >= LIMITE_ALERTA:

    # Exibe uma mensagem de alerta no gráfico.
    plt.text(
        DURACAO / 2,
        LIMITE_ALERTA + 3,
        "⚠️ ALERTA!\nNível sonoro elevado",
        fontsize=14,
        ha="center"
    )

else:

    # Caso o nível médio esteja abaixo do limite,
    # informa que não houve alerta.
    plt.text(
        DURACAO / 2,
        LIMITE_ALERTA + 3,
        "✓ Nível abaixo do limite de alerta",
        fontsize=14,
        ha="center"
    )


# Ajusta automaticamente o espaçamento
# dos elementos do gráfico.
plt.tight_layout()


# Exibe o gráfico na tela.
plt.show()
```
