```python
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt


# ==========================================================
# CONFIGURAÇÕES
# ==========================================================

# Taxa de amostragem do áudio.
# 44.100 Hz significa que o áudio será medido 44.100 vezes por segundo.
TAXA_AMOSTRAGEM = 44100

# Tempo de gravação em segundos.
DURACAO = 3

# Valor de referência utilizado para estimar o nível em decibéis.
# IMPORTANTE: este valor não substitui a calibração de um decibelímetro
# profissional. O resultado deve ser considerado uma estimativa.
CALIBRACAO_DB = 94

# Nível utilizado como referência para gerar o alerta.
LIMITE_ALERTA = 85


# ==========================================================
# INÍCIO DO PROGRAMA
# ==========================================================

print("========================================")
print("       MEDIDOR DE POLUIÇÃO SONORA")
print("========================================")

input("\nPressione ENTER para iniciar...")

print("\nGravando por 3 segundos...")


# Grava o áudio utilizando o microfone padrão do computador.
#
# O número total de amostras é calculado multiplicando:
# duração × taxa de amostragem.
audio = sd.rec(
    int(DURACAO * TAXA_AMOSTRAGEM),
    samplerate=TAXA_AMOSTRAGEM,
    channels=1,
    dtype="float32"
)

# Aguarda a gravação terminar antes de continuar.
sd.wait()

# Remove a dimensão referente ao canal de áudio.
audio = audio[:, 0]


# ==========================================================
# ANÁLISE DO NÍVEL SONORO
# ==========================================================

# O áudio será analisado em pequenas janelas de 0,1 segundo.
TAMANHO_JANELA = int(0.1 * TAXA_AMOSTRAGEM)

niveis_db = []
tempos = []


# Percorre todo o áudio dividindo-o em janelas.
for inicio in range(0, len(audio), TAMANHO_JANELA):

    trecho = audio[inicio:inicio + TAMANHO_JANELA]

    if len(trecho) == 0:
        continue

    # Calcula o RMS (Root Mean Square) do trecho.
    # O RMS representa a intensidade média do sinal de áudio.
    rms = np.sqrt(np.mean(trecho ** 2))

    # Evita calcular logaritmo de zero ou de um valor muito próximo de zero.
    if rms < 0.000001:
        rms = 0.000001

    # Converte a intensidade do sinal para uma escala aproximada de decibéis.
    db = 20 * np.log10(rms) + CALIBRACAO_DB

    niveis_db.append(db)

    # Registra o instante correspondente ao trecho analisado.
    tempos.append(inicio / TAXA_AMOSTRAGEM)


# Calcula o nível sonoro médio durante toda a gravação.
nivel_medio = np.mean(niveis_db)


# ==========================================================
# ANÁLISE DA FREQUÊNCIA
# ==========================================================

# Aplica a Transformada Rápida de Fourier (FFT).
# Ela permite identificar quais frequências estão presentes no áudio.
fft = np.fft.rfft(audio)

# Cria o eixo de frequências correspondente aos resultados da FFT.
frequencias = np.fft.rfftfreq(
    len(audio),
    1 / TAXA_AMOSTRAGEM
)

# Calcula a intensidade de cada frequência.
intensidade = np.abs(fft)

# Ignora frequências abaixo de 20 Hz,
# que estão abaixo da faixa normalmente considerada audível.
intensidade[frequencias < 20] = 0

# Localiza a frequência com maior intensidade.
indice = np.argmax(intensidade)

# Obtém a frequência predominante encontrada na gravação.
frequencia_principal = frequencias[ind
