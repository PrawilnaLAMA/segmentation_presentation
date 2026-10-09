"""One-window launcher for the live segmentation demos."""
import shutil
import subprocess
import sys
import tkinter as tk
import tkinter.font as tkfont
from pathlib import Path

SCRIPT = Path(__file__).parent / "segment.py"
INK, PANEL, TEXT, MUTED = "#14161B", "#1B1E24", "#F2EFE9", "#A7AEB5"
DEMOS = [
    ("1  Klasyczna", "Próg koloru skóry + GrabCut. Bez sieci neuronowej.", "classical", "#8B939C"),
    ("2  Sieć wieloklasowa", "Całe ciało: tło, włosy, skóra, ubranie — osobne kolory.", "deep", "#D9A066"),
    ("3  Face parsing — 19 klas", "Brwi, oczy, usta, włosy i okulary — wykrywane, nie dorysowywane.", "face", "#2BB8C4"),
    ("4  Porównanie", "Wszystkie trzy metody obok siebie, ta sama klatka.", "compare", "#D9481F"),
]

proc = None


def launch(mode):
    global proc
    if proc and proc.poll() is None:
        proc.terminate()  # only one process can hold the camera
        proc.wait()
    # Run via uv so the demo gets the project's .venv even if this launcher was started with another python.
    python = ["uv", "run", "--project", str(SCRIPT.parent.parent), "python"] if shutil.which("uv") else [sys.executable]
    proc = subprocess.Popen([*python, str(SCRIPT), mode, "--camera", camera.get()])
    status.config(text=f"Uruchomiono: {mode}  ·  q w oknie demo = zamknij")


def on_close():
    if proc and proc.poll() is None:
        proc.terminate()
    root.destroy()


root = tk.Tk()
FONT = next((f for f in ("DejaVu Sans", "Noto Sans", "Liberation Sans", "Arial") if f in tkfont.families()), "TkDefaultFont")
root.title("Segmentacja obrazów — demo")
root.configure(bg=INK, padx=32, pady=28)
root.protocol("WM_DELETE_WINDOW", on_close)

tk.Label(root, text="SEGMENTACJA NA ŻYWO", bg=INK, fg="#D9481F", font=(FONT, 11, "bold")).pack(anchor="w")
tk.Label(root, text="Gdzie kończy się twarz?", bg=INK, fg=TEXT, font=(FONT, 22, "bold")).pack(anchor="w", pady=(2, 18))

for title, desc, mode, accent in DEMOS:
    card = tk.Frame(root, bg=PANEL, highlightbackground=accent, highlightthickness=2)
    card.pack(fill="x", pady=6)
    tk.Button(card, text=title, command=lambda m=mode: launch(m), bg=PANEL, fg=TEXT, activebackground=accent,
              activeforeground=INK, relief="flat", anchor="w", font=(FONT, 15, "bold"), cursor="hand2",
              padx=16, pady=8).pack(fill="x")
    tk.Label(card, text=desc, bg=PANEL, fg=MUTED, anchor="w", font=(FONT, 11), padx=18).pack(fill="x", pady=(0, 10))

row = tk.Frame(root, bg=INK)
row.pack(fill="x", pady=(16, 0))
tk.Label(row, text="Kamera:", bg=INK, fg=MUTED, font=(FONT, 11)).pack(side="left")
camera = tk.Spinbox(row, from_=0, to=9, width=3, font=(FONT, 11))
camera.pack(side="left", padx=8)
status = tk.Label(row, text="Wybierz tryb", bg=INK, fg=MUTED, font=(FONT, 11))
status.pack(side="left", padx=12)

for i, (_, _, mode, _) in enumerate(DEMOS, start=1):
    root.bind(str(i), lambda _e, m=mode: launch(m))

root.mainloop()
