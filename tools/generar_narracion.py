"""Genera la narración de la animación con voz neuronal (Kokoro) y la
transforma en voz infantil.

Salida:
  audio/<id>.mp3   un clip por frase
  narracion.js     los mismos clips en base64 y su duración, para index.html

Requisitos (en un entorno virtual):
  pip install kokoro-onnx soundfile pyworld numpy "setuptools<81"
  y los modelos kokoro-v1.0.onnx y voices-v1.0.bin de
  https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0

Uso:
  python tools/generar_narracion.py RUTA_A_LOS_MODELOS
"""
import base64
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import pyworld as pw
import soundfile as sf
from kokoro_onnx import Kokoro

ROOT = Path(__file__).resolve().parent.parent
LANG = "es-419"  # español latinoamericano: seseo, acento neutro

# id, texto tal como se pronuncia, voz
LINES = [
    ("titulo", "El Principito. Capítulo uno.", "nino"),
    ("libro", "Cuando tenía seis años, vi una vez una imagen magnífica en un libro sobre la Selva Virgen, que se llamaba: Historias vividas.", "nino"),
    ("boa", "Mostraba una serpiente boa que se tragaba a una fiera. Esta es la copia del dibujo.", "nino"),
    ("cita1", "En el libro se decía: Las serpientes boas tragan a su presa entera, sin masticarla.", "nino"),
    ("cita2", "Después ya no pueden moverse, y duermen durante los seis meses que dura su digestión.", "nino"),
    ("reflexion", "Entonces reflexioné mucho sobre las aventuras de la jungla y, a mi vez, conseguí trazar con un lápiz de color mi primer dibujo.", "nino"),
    ("dibujo1", "Mi dibujo número uno. Era así.", "nino"),
    ("mostre", "Mostré mi obra maestra a las personas mayores, y les pregunté si mi dibujo les daba miedo.", "nino"),
    ("respondieron", "Me respondieron:", "nino"),
    ("sombrero", "¿Por qué habría de dar miedo un sombrero?", "adulto"),
    ("noera", "Mi dibujo no representaba un sombrero. Representaba una serpiente boa que digería un elefante.", "nino"),
    ("interior", "Entonces dibujé el interior de la serpiente boa, para que las personas mayores pudieran entender.", "nino"),
    ("siempre", "Siempre necesitan explicaciones.", "nino"),
    ("fin", "Fin de la primera página.", "nino"),
]

VOICES = {
    # voz base, velocidad
    "nino": ("ef_dora", 1.0),
    "adulto": ("em_alex", 0.92),
}

# Transformación a voz infantil: tono más alto y más expresivo, y
# formantes desplazados hacia arriba (un tracto vocal más corto).
CHILD_F0 = 1.6        # factor de tono (de ~165 Hz a ~265 Hz de mediana)
CHILD_SWING = 1.15    # amplía la entonación alrededor de la media
CHILD_FORMANT = 1.18  # factor de formantes


def warp_frequency(env, alpha):
    """Estira la envolvente espectral en frecuencia: env'(f) = env(f / alpha)."""
    bins = env.shape[1]
    src = np.arange(bins) / alpha
    out = np.empty_like(env)
    for i in range(env.shape[0]):
        out[i] = np.interp(src, np.arange(bins), env[i])
    return out


def to_child(x, sr):
    x = x.astype(np.float64)
    f0, t = pw.harvest(x, sr, f0_floor=80, f0_ceil=600, frame_period=5.0)
    sp = pw.cheaptrick(x, f0, t, sr)
    ap = pw.d4c(x, f0, t, sr)
    voiced = f0 > 0
    if voiced.any():
        logf = np.log(f0[voiced])
        mean = logf.mean()
        f0[voiced] = np.exp(mean + (logf - mean) * CHILD_SWING) * CHILD_F0
    sp = warp_frequency(sp, CHILD_FORMANT)
    ap = warp_frequency(ap, CHILD_FORMANT)
    return pw.synthesize(f0, sp, ap, sr, frame_period=5.0).astype(np.float32)


def trim(x, sr, thresh=0.01, pad=0.08):
    idx = np.where(np.abs(x) > thresh)[0]
    if not len(idx):
        return x
    a = max(0, idx[0] - int(pad * sr))
    b = min(len(x), idx[-1] + int(pad * sr))
    return x[a:b]


def normalize(x, target_rms=0.085, peak=0.93):
    rms = np.sqrt(np.mean(x ** 2)) or 1
    x = x * (target_rms / rms)
    m = np.max(np.abs(x))
    if m > peak:
        x = x * (peak / m)
    return x


def main(models):
    models = Path(models)
    kokoro = Kokoro(str(models / "kokoro-v1.0.onnx"), str(models / "voices-v1.0.bin"))
    out_dir = ROOT / "audio"
    out_dir.mkdir(exist_ok=True)
    clips = []
    for cid, text, role in LINES:
        voice, speed = VOICES[role]
        x, sr = kokoro.create(text, voice=voice, speed=speed, lang=LANG)
        if role == "nino":
            x = to_child(x, sr)
        x = normalize(trim(x, sr))
        mp3 = out_dir / f"{cid}.mp3"
        with tempfile.NamedTemporaryFile(suffix=".wav") as wav:
            sf.write(wav.name, x, sr)
            subprocess.run(
                ["ffmpeg", "-y", "-loglevel", "error", "-i", wav.name,
                 "-ac", "1", "-codec:a", "libmp3lame", "-b:a", "64k", str(mp3)],
                check=True,
            )
        dur = round(len(x) / sr, 3)
        clips.append({"id": cid, "dur": dur, "src": "data:audio/mpeg;base64," + base64.b64encode(mp3.read_bytes()).decode()})
        print(f"{cid:13s} {dur:5.2f}s  {text}")
    js = "/* Generado por tools/generar_narracion.py: narración en voz infantil (Kokoro, es-419) */\n"
    js += "window.NARRACION = " + json.dumps({c["id"]: {"dur": c["dur"], "src": c["src"]} for c in clips}) + ";\n"
    (ROOT / "narracion.js").write_text(js)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "models")
