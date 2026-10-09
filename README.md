# Gdzie kończy się twarz? — wykład o segmentacji obrazów

Wykład dla studiów magisterskich (blok 90 min) + aplikacja z żywym demo na kamerze.

**Slajdy:** otwórz [slajdy.html](slajdy.html) w przeglądarce (w VS Code: prawy klik → *Open with Live Server* / *Show Preview* albo po prostu dwuklik w menedżerze plików). 90 slajdów, mniej więcej jeden na minutę, każdy z rysunkiem tego, o czym akurat mowa.

| Klawisz | Działanie |
|---|---|
| → / spacja / klik | następny slajd |
| ← | poprzedni |
| `n` | notatki prelegenta: dokładny tekst do wygłoszenia dla tego slajdu |
| `f` | pełny ekran |
| Ctrl+P | zapis do PDF (90 stron) |

Slajdy generuje [slajdy.py](slajdy.py) (sam Python, bez zależności): `python3 slajdy.py` po każdej zmianie. Ten sam tekst, podzielony na 90 slajdów, jest w `tekst_wykladu.docx`.

## Plan wykładu

Zamiast schematu „wstęp → metody → zastosowania → pytania" wykład jest jedną pętlą: zaczyna się od pytania, na które nie da się odpowiedzieć bez definicji, a kończy powrotem do tego samego obrazu.

| Min | Slajdy | Co się dzieje | Interakcja |
|---|---|---|---|
| 0–5 | 1–8 | Mozaika pikseli zamiast tytułu, potem iluzja wazonu Rubina | Sala głosuje: twarze czy wazon? |
| 5–15 | 9–19 | Segmentacja jako funkcja f(x,y) → c; semantyczna / instancyjna / panoptyczna | — |
| 15–40 | 20–55 | Warstwy czasu: od progowania przez FCN, U-Net, DeepLab, Mask R-CNN po transformery i SAM | Pytanie: „co tu jest skip connection?" |
| 40–60 | 56–63 | **Demo na żywo** z ochotnikiem z sali, potem tabela: co każda metoda zrobiła dobrze i źle | Ochotnik w okularach przed kamerą |
| 60–75 | 64–76 | IoU vs Dice vs dokładność na tym samym przykładzie; niezbalansowane klasy; zbiory danych | Policzcie IoU zanim pokażę wynik |
| 75–85 | 77–86 | Otwarte problemy (w tym bias w zbiorach twarzy) i segmentacja w codziennych produktach | Ręce w górę: kto dziś użył trybu portretowego? |
| 85–90 | 87–90 | Powrót do wazonu, teraz rozstrzygniętego; pytanie na koniec zamiast „Dziękuję" | Dyskusja |

Spójny motyw: te same kolory klas (tło, skóra, włosy, ubranie, **cyjan = okulary**) pojawiają się na diagramach i potem na żywo w demo.

## Demo na żywo

Środowisko jest zarządzane przez [uv](https://docs.astral.sh/uv/) (`pyproject.toml`, Python 3.12):

```bash
uv run live_demo/segment.py --selftest   # tworzy .venv, pobiera modele (~115 MB), sprawdza wszystko bez kamery
uv run live_demo/gui_launcher.py
```

Launcher zawsze uruchamia demo przez `uv run`, więc zadziała nawet odpalony zwykłym `python` z condy.

**Selftest uruchom przed wykładem, z internetem** — modele zostaną w `live_demo/models/` i na sali sieć nie jest potrzebna.

| Klawisz | Tryb | Co pokazuje |
|---|---|---|
| 1 | Klasyczna | Próg koloru skóry (YCrCb) + GrabCut, bez sieci |
| 2 | Sieć wieloklasowa | MediaPipe multiclass: tło, włosy, skóra, ubranie, „inne" |
| 3 | Face parsing | BiSeNet (CelebAMask-HQ), 19 klas: brwi, oczy, usta, włosy, **okulary** obrysowane cyjanem + napis „OKULARY WYKRYTE" |
| 4 | Porównanie | Wszystkie trzy obok siebie |

`q` lub Esc zamyka okno demo. Pole „Kamera" w launcherze wybiera kamerę zewnętrzną.

Pomysł na pokaz: ochotnik zakłada i zdejmuje okulary. Tryb 1 ich nie widzi, tryb 2 nie ma dla nich klasy, tryb 3 wykrywa je i obrysowuje. To jest puenta slajdów 13 i 16: zbiór danych decyduje, co model w ogóle może zauważyć.

Jak działa tryb 3: MediaPipe znajduje twarz, kadr jest wycinany do kwadratu z włosami (jak w zbiorze treningowym), BiSeNet liczy maskę 512×512, maska wraca na swoje miejsce w kadrze. Bez wycinania model gubi okulary już przy twarzy ~200 px (zmierzone: 129 vs 2553 piksele okularów).

Wskazówki:
- Dobre, równe światło z przodu. Przy słabym świetle kamera zwalnia (testowo ~10 kl/s w nocy).
- Sieci liczą w tle (tryb 2: ~10 masek/s, tryb 3: ~6 masek/s na CPU), więc obraz z kamery jest płynny, a maska lekko się spóźnia przy szybkim ruchu.
- Twarz musi być bliżej niż ~2 m od kamery (wykrywacz MediaPipe jest dostrojony do bliskich twarzy).

Modele: MediaPipe (Apache 2.0); BiSeNet face parsing z [yakhyo/face-parsing](https://github.com/yakhyo/face-parsing) (MIT), wytrenowany na CelebAMask-HQ, którego licencja dopuszcza tylko użycie niekomercyjne, badawcze i edukacyjne.
