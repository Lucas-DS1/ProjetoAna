import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt

TAXA_AMOSTRAGEM = 44100
DURACAO = 3

CALIBRACAO_DB = 94
LIMITE_ALERTA = 85

print("========================================")
print("       MEDIDOR DE POLUIÇÃO SONORA")
print("========================================")

input("\nPressione ENTER para iniciar...")

print("\nGravando por 3 segundos...")

audio = sd.rec(
    int(DURACAO * TAXA_AMOSTRAGEM),
    samplerate=TAXA_AMOSTRAGEM,
    channels=1,
    dtype="float32"
)

sd.wait()

audio = audio[:, 0]

TAMANHO_JANELA = int(0.1 * TAXA_AMOSTRAGEM)

niveis_db = []
tempos = []

for inicio in range(0, len(audio), TAMANHO_JANELA):
    trecho = audio[inicio:inicio + TAMANHO_JANELA]

    if len(trecho) == 0:
        continue

    rms = np.sqrt(np.mean(trecho ** 2))

    if rms < 0.000001:
        rms = 0.000001

    db = 20 * np.log10(rms) + CALIBRACAO_DB

    niveis_db.append(db)
    tempos.append(inicio / TAXA_AMOSTRAGEM)

nivel_medio = np.mean(niveis_db)

fft = np.fft.rfft(audio)

frequencias = np.fft.rfftfreq(
    len(audio),
    1 / TAXA_AMOSTRAGEM
)

intensidade = np.abs(fft)

intensidade[frequencias < 20] = 0

indice = np.argmax(intensidade)

frequencia_principal = frequencias[indice]

print("\n========================================")
print("              RESULTADO")
print("========================================")

print(f"Frequência predominante: {frequencia_principal:.1f} Hz")
print(f"Nível sonoro médio: {nivel_medio:.1f} dB")

plt.figure(figsize=(10, 5))

plt.plot(tempos, niveis_db, linewidth=2)

plt.axhline(
    LIMITE_ALERTA,
    linestyle="--",
    linewidth=2,
    label="Limite de alerta: 85 dB"
)

plt.xlabel("Tempo (segundos)")
plt.ylabel("Nível sonoro estimado (dB)")

plt.title(
    f"Medidor de Poluição Sonora | "
    f"Média: {nivel_medio:.1f} dB"
)

plt.grid()
plt.legend()

if nivel_medio >= LIMITE_ALERTA:
    plt.text(
        DURACAO / 2,
        LIMITE_ALERTA + 3,
        "⚠️ ALERTA!\nNível sonoro elevado",
        fontsize=14,
        ha="center"
    )
else:
    plt.text(
        DURACAO / 2,
        LIMITE_ALERTA + 3,
        "✓ Nível abaixo do limite de alerta",
        fontsize=14,
        ha="center"
    )

plt.tight_layout()
plt.show()
