import tkinter as tk
from tkinter import simpledialog, messagebox
from math import sqrt
import sys
import time
import math
from math import sin, radians, cos, tan
from pydub import AudioSegment
from pydub.playback import play
import io
import traceback

try:
    import winsound
except Exception:
    winsound = None

# try pygame for direct MP3 playback (preferred)
try:
    import pygame
    pygame_available = True
    try:
        pygame.mixer.init()
    except Exception:
        # initialization may fail in some headless contexts; still keep pygame_available
        pass
except Exception:
    pygame = None
    pygame_available = False


def play_error_sound():
    """Play the loaded Error1.mp3 using pygame if possible; otherwise fall back to pydub/winsound."""
    try:
        # Prefer pygame (direct MP3 playback)
        if 'loaded_sound_path' in globals() and pygame_available and loaded_sound_path:
            try:
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                # stop any currently playing music and play the error sound
                try:
                    pygame.mixer.music.stop()
                except Exception:
                    pass
                pygame.mixer.music.load(loaded_sound_path)
                pygame.mixer.music.play()
                return
            except Exception:
                print("pygame playback failed:")
                traceback.print_exc()

        # If we have an AudioSegment, use winsound SND_MEMORY or pydub
        if musik is not None:
            try:
                buf = io.BytesIO()
                musik.export(buf, format="wav")
                data = buf.getvalue()
                if winsound:
                    winsound.PlaySound(data, winsound.SND_MEMORY | winsound.SND_ASYNC)
                    return
            except Exception:
                print("Playback via winsound SND_MEMORY failed:")
                traceback.print_exc()
            try:
                play(musik)
                return
            except Exception:
                print("pydub.play fallback failed:")
                traceback.print_exc()

        # Last resort: system sound
        if winsound:
            winsound.PlaySound("SystemHand", winsound.SND_ALIAS)
    except Exception:
        traceback.print_exc()


def _play_segment_with_winsound(segment):
    """Play a pydub.AudioSegment using winsound via in-memory WAV (SND_MEMORY).
    Falls back to pydub.play if winsound/SND_MEMORY fails.
    """
    if segment is None:
        return
    # Try winsound SND_MEMORY first (no temp files)
    if winsound:
        try:
            buf = io.BytesIO()
            segment.export(buf, format="wav")
            data = buf.getvalue()
            # Play asynchronously so UI isn't blocked
            winsound.PlaySound(data, winsound.SND_MEMORY | winsound.SND_ASYNC)
            return
        except Exception:
            print("Fehler beim Abspielen mit winsound (SND_MEMORY):")
            traceback.print_exc()
    # Fallback: use pydub.play (may require simpleaudio/pyaudio/ffplay)
    try:
        play(segment)
    except Exception:
        print("Fehler beim Abspielen mit pydub.play:")
        traceback.print_exc()

titel = "Rechner 2 (V.1.2) von ScarZomb"

# try to load custom error sound from multiple possible locations
import os

# Get all possible paths where the sound file might be
possible_paths = [
    "Error1.mp3",  # Current working directory
    os.path.join(os.getcwd(), "Error1.mp3"),  # Absolute path to current working directory
    os.path.abspath("Error1.mp3")  # Another way to get absolute path
]

# If running as script, add script directory
if '__file__' in globals():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    possible_paths.append(os.path.join(script_dir, "Error1.mp3"))

print("\nSuche Error1.mp3 in:")
for path in possible_paths:
    print(f"- {path} ({'gefunden' if os.path.exists(path) else 'nicht gefunden'})")

musik = None
for error_sound_path in possible_paths:
    if os.path.exists(error_sound_path):
        try:
            musik = AudioSegment.from_mp3(error_sound_path)
            loaded_sound_path = error_sound_path
            print(f"\nError-Sound erfolgreich geladen von: {error_sound_path}")
            break
        except Exception as e:
            print(f"Konnte {error_sound_path} nicht laden: {str(e)}")

if musik is None:
    print("\nKonnte Error1.mp3 nicht finden oder laden. Verwende Windows-Sound.")

root = tk.Tk()
root.withdraw()

def main_menu():
    resultminus_box("ACHTUNG: Manche Fenster wie dieses hier schließen sich irgendwann von selbst!", "", "1300x75")
    message_box("Willkommen zum Rechner 2 V.1.2! (Erstellt von ScarZomb)")
    message_box("Dieses Programm ist nicht fehlerfrei.")
    message_box("Wenn Sie einen Fehler finden, melden Sie es bitte dem Entwickler.")

    while True:
        start = inputInt("Welche Art von Berechnungen möchten Sie tun? (1 = Standard) (2 = Pythagoras) (3 = Formen) (4 = Binomische Formeln) (5 = Seite 2) (0 = Beenden)")

        if start == 1:
            standard_rechner()
        elif start == 2:
            pythagoras_rechner()
        elif start == 3:
            formen_rechner()
        elif start == 4:
            binomische_formeln_rechner()
        elif start == 5:
            main_menu_seite2()
        elif start == 0:
            message_box("Programm beendet. Auf Wiedersehen!")
            sys.exit(0)
        else:
            message_box("❗❗❗ERROR! Ungültige Eingabe❗❗❗")

def main_menu_seite2():
    start = inputInt("Was möchtest du berechnen? (6 = Trigonometrie) (7 = Brüche/Dezimalzahlen umrechnen) (0 = Zurück zum Hauptmenü)")

    if start == 0:
        return

    if start < 0 or start > 7:
        message_box("❗❗❗ERROR! Ungültige Eingabe❗❗❗", is_error=True)
        return

    if start == 6:
        trigonometrie_rechner()

    if start == 7:
        bruch_dezimal_rechner()

def inputInt(prompt):
    while True:
        res = simpledialog.askstring(title=titel, prompt=prompt, parent=root)
        if res is None:
            message_box("Programm beendet. Auf Wiedersehen!")
            sys.exit(0)
        try:
            res = res.replace(',', '.')
            return float(res)
        except ValueError:
            # play error sound (prefer MP3 if available, else winsound)
            try:
                play_error_sound()
            except Exception:
                traceback.print_exc()
            messagebox.showerror("Fehler", "Bitte eine gültige Zahl eingeben.", parent=root)

def message_box(text, is_error: bool = False):
    win = tk.Toplevel(root)
    win.title(titel)
    win.geometry("1000x75")
    # win.transient(root)  # transient kann Probleme machen wenn root withdrawn ist
    win.attributes("-topmost", True)
    text_label = tk.Label(win, text=text, fg="black", font=("Arial", 22))
    text_label.pack(pady=20)
    try:
        win.update_idletasks()
        win.lift()
        win.wait_visibility()
        win.update()
    except tk.TclError:
        pass
    # Only check for error if not explicitly set
    should_play_sound = is_error
    if not should_play_sound:
        # Striktere Fehlererkennung: Nur bei eindeutigen Fehlermeldungen
        if "❗❗❗" in text:  # Nutze das dreifache Ausrufezeichen als eindeutigen Marker
            should_play_sound = True
        # Oder bei spezifischen Fehlermeldungen
        elif text.startswith("❗"):  # Einzelnes Ausrufezeichen am Anfang
            should_play_sound = True
        else:
            lowered = text.lower()
            # Spezifische Fehlermeldungen
            error_phrases = [
                "division durch null nicht möglich",
                "ungültige auswahl",
                "ungültige eingabe",
                "rechnung nicht möglich",
                "ungültiger radius",
                "ungültige seitenlänge",
                "ungültige maße",
                "ungültiger winkel"
            ]
            should_play_sound = any(phrase in lowered for phrase in error_phrases)
    
    if should_play_sound:
        try:
            play_error_sound()
        except Exception:
            traceback.print_exc()
    end = time.time() + 2.0
    while time.time() < end:
        try:
            root.update()
        except tk.TclError:
            break
        time.sleep(0.02)
    try:
        win.destroy()
    except tk.TclError:
        pass

def resultplus_box(text, number, größe):
    win = tk.Toplevel(root)
    win.title(titel)
    win.geometry(größe)
    # win.transient(root)
    win.attributes("-topmost", True)
    text_label = tk.Label(win, text=f"{text}{number}", fg="green", font=("Arial", 22))
    text_label.pack(pady=20)
    try:
        win.update_idletasks()
        win.lift()
        win.wait_visibility()
        win.update()
    except tk.TclError:
        pass
    end = time.time() + 7.5
    while time.time() < end:
        try:
            root.update()
        except tk.TclError:
            break
        time.sleep(0.02)
    try:
        win.destroy()
    except tk.TclError:
        pass

def resultminus_box(text, number, größe):
    win = tk.Toplevel(root)
    win.title(titel)
    win.geometry(größe)
    # win.transient(root)
    win.attributes("-topmost", True)
    text_label = tk.Label(win, text=f"{text}{number}", fg="red", font=("Arial", 22))
    text_label.pack(pady=20)
    try:
        win.update_idletasks()
        win.lift()
        win.wait_visibility()
        win.update()
    except tk.TclError:
        pass
    end = time.time() + 7.5
    while time.time() < end:
        try:
            root.update()
        except tk.TclError:
            break
        time.sleep(0.02)
    try:
        win.destroy()
    except tk.TclError:
        pass

def pythagoras_rechner():
    startn = inputInt("Was möchten Sie berechnen? (2 = Hypothenuse) (3 = Kathete) (4 = Winkel) (0 = Zurück zum Hauptmenü)")

    if startn == 2:
        x = inputInt("↓↓↓ Länge der ersten Kathete ↓↓↓")
        y = inputInt("↓↓↓ Länge der zweiten Kathete ↓↓↓")
        if x < 0 or y < 0:
            message_box("❗❗❗ERROR! Rechnung nicht möglich❗❗❗")
        else:
            z = round(sqrt(x * x + y * y), 2)
            resultplus_box("Die Länge der Hypothenuse lautet: ", z, "700x75")

    elif startn == 3:
        x = inputInt("↓↓↓ Länge der Kathete ↓↓↓")
        y = inputInt("↓↓↓ Länge der Hypothenuse ↓↓↓")
        if x < 0 or y < 0 or y < x:
            message_box("❗❗❗ERROR! Rechnung nicht möglich❗❗❗")
        else:
            a = round(sqrt(y * y - x * x), 2)
            resultplus_box("Die Länge der Kathete lautet: ", a, "700x75")

    elif startn == 4:
        x = inputInt("↓↓↓ Erster Winkel ↓↓↓")
        y = inputInt("↓↓↓ Zweiter Winkel ↓↓↓")
        if x + y >= 180:
            message_box("❗❗❗ERROR! Rechnung nicht möglich❗❗❗")
        else:
            b = 180 - (x + y)
            resultplus_box("Der dritte Winkel lautet: ", b, "700x75")

    elif startn == 0:
        return

    else:
        message_box("❗❗❗ERROR! Ungültige Auswahl❗❗❗")

def standard_rechner():
    startm = inputInt("Was möchten Sie berechnen? (2 = Addieren) (3 = Subtrahieren) (4 = Multiplizieren) (5 = Division) (0 = Zurück zum Hauptmenü)")

    if startm == 2:
        x = inputInt("↓↓↓ Erster Summand ↓↓↓")
        y = inputInt("↓↓↓ Zweiter Summand ↓↓↓")
        xy = x + y

    elif startm == 3:
        x = inputInt("↓↓↓ Minuend ↓↓↓")
        y = inputInt("↓↓↓ Subtrahend ↓↓↓")
        xy = x - y

    elif startm == 4:
        x = inputInt("↓↓↓ Erster Faktor ↓↓↓")
        y = inputInt("↓↓↓ Zweiter Faktor ↓↓↓")
        xy = x * y

    elif startm == 5:
        x = inputInt("↓↓↓ Dividend ↓↓↓")
        y = inputInt("↓↓↓ Divisor ↓↓↓")
        if y == 0:
            message_box("❗❗❗Division durch Null nicht möglich❗❗❗")
            return
        xy = x / y
    
    elif startm == 0:
        return
    
    else:
        message_box("❗❗❗Ungültige Auswahl❗❗❗")
        return

    if xy >= 0:
        resultplus_box("Das Ergebnis lautet: ", xy, "700x75")
    else:
        resultminus_box("Das Ergebnis lautet: ", xy, "700x75")

def formen_rechner():
    startf = inputInt("Welche Form möchten Sie berechnen? (1 = Kreis) (2 = Quadrat) (3 = Rechteck) (4 = Dreieck) (5 = Trapez) (6 = Parallelogramm) (7 = Seite 2) (0 = Zurück zum Hauptmenü)")

    if startf == 1:
        r = inputInt("↓↓↓ Radius des Kreises ↓↓↓")
        if r < 0:
            message_box("❗❗❗ERROR! Ungültiger Radius❗❗❗")
        else:
            fläche = round(3.14159 * r * r, 2)
            umfang = round(2 * 3.14159 * r, 2)
            resultplus_box("Fläche des Kreises: ", fläche, "700x75")
            resultplus_box("Umfang des Kreises: ", umfang, "700x75")

    elif startf == 2:
        a = inputInt("↓↓↓ Seitenlänge des Quadrats ↓↓↓")
        if a < 0:
            message_box("❗❗❗ERROR! Ungültige Seitenlänge❗❗❗")
        else:
            fläche = round(a * a, 2)
            umfang = round(4 * a, 2)
            resultplus_box("Fläche des Quadrats: ", fläche, "700x75")
            resultplus_box("Umfang des Quadrats: ", umfang, "700x75")

    elif startf == 3:
        l = inputInt("↓↓↓ Länge des Rechtecks ↓↓↓")
        b = inputInt("↓↓↓ Breite des Rechtecks ↓↓↓")
        if l < 0 or b < 0:
            message_box("❗❗❗ERROR! Ungültige Maße❗❗❗")
        else:
            fläche = round(l * b, 2)
            umfang = round(2 * (l + b), 2)
            resultplus_box("Fläche des Rechtecks: ", fläche, "700x75")
            resultplus_box("Umfang des Rechtecks: ", umfang, "700x75")

    elif startf == 4:
        grundlinie = inputInt("↓↓↓ Grundlinie des Dreiecks ↓↓↓")
        höhe = inputInt("↓↓↓ Höhe des Dreiecks ↓↓↓")
        if grundlinie < 0 or höhe < 0:
            message_box("❗❗❗ERROR! Ungültige Maße❗❗❗")
        else:
            fläche = round(0.5 * grundlinie * höhe, 2)
            resultplus_box("Fläche des Dreiecks: ", fläche, "700x75")

    elif startf == 5:
        a = inputInt("↓↓↓ Länge der ersten parallelen Seite ↓↓↓")
        b = inputInt("↓↓↓ Länge der zweiten parallelen Seite ↓↓↓")
        h = inputInt("↓↓↓ Höhe des Trapezes ↓↓↓")
        if a < 0 or b < 0 or h < 0:
            message_box("❗❗❗ERROR! Ungültige Maße❗❗❗")
        else:
            fläche = round(0.5 * (a + b) * h, 2)
            resultplus_box("Fläche des Trapezes: ", fläche, "700x75")

    elif startf == 6:
        grundlinie = inputInt("↓↓↓ Grundlinie des Parallelogramms ↓↓↓")
        höhe = inputInt("↓↓↓ Höhe des Parallelogramms ↓↓↓")
        if grundlinie < 0 or höhe < 0:
            message_box("❗❗❗ERROR! Ungültige Maße❗❗❗")
        else:
            fläche = round(grundlinie * höhe, 2)
            resultplus_box("Fläche des Parallelogramms: ", fläche, "700x75")

    elif startf == 7:
        formen_rechner_seite2()

    elif startf == 0:
        return

    else:
        message_box("❗❗❗ERROR! Ungültige Auswahl❗❗❗")

def formen_rechner_seite2():
    starts = inputInt("Wleche Form möchten Sie berechnen? (1 = Drache) (2 = Raute) (0 = Zurück zum Hauptmenü)")

    if starts == 1:
        d1 = inputInt("↓↓↓ Länge der ersten Diagonale ↓↓↓")
        d2 = inputInt("↓↓↓ Länge der zweiten Diagonale ↓↓↓")
        if d1 < 0 or d2 < 0:
            message_box("❗❗❗ERROR! Ungültige Maße❗❗❗")
        else:
            fläche = round(0.5 * d1 * d2, 2)
            resultplus_box("Fläche des Drachen: ", fläche, "700x75")

    elif starts == 2:
        a = inputInt("↓↓↓ Länge der Seite der Raute ↓↓↓")
        h = inputInt("↓↓↓ Höhe der Raute ↓↓↓")
        if a < 0 or h < 0:
            message_box("❗❗❗ERROR! Ungültige Maße❗❗❗")
        else:
            fläche = round(a * h, 2)
            umfang = round(4 * a, 2)
            resultplus_box("Fläche der Raute: ", fläche, "700x75")
            resultplus_box("Umfang der Raute: ", umfang, "700x75")

    elif starts == 0:
        return
    
    else:
        message_box("❗❗❗ERROR! Ungültige Auswahl❗❗❗")

def binomische_formeln_rechner():
    startx = inputInt("Welche binomische Formel möchten Sie verwenden? (1 = (a + b)²) (2 = (a - b)²) (3 = (a-b)(a+b)) (0 = Zurück zum Hauptmenü)")

    if startx == 1:
        a = inputInt("↓↓↓ Wert für a ↓↓↓")
        b = inputInt("↓↓↓ Wert für b ↓↓↓")
        ergebnis = round((a + b) ** 2, 2)
        resultplus_box("Das Ergebnis von (a + b)² lautet: ", ergebnis, "700x75")
    
    elif startx == 2:
        a = inputInt("↓↓↓ Wert für a ↓↓↓")
        b = inputInt("↓↓↓ Wert für b ↓↓↓")
        ergebnis = round((a - b) ** 2, 2)
        resultplus_box("Das Ergebnis von (a - b)² lautet: ", ergebnis, "700x75")
    
    elif startx == 3:
        a = inputInt("↓↓↓ Wert für a ↓↓↓")
        b = inputInt("↓↓↓ Wert für b ↓↓↓")
        ergebnis = round(a ** 2 - b ** 2, 2)
        resultplus_box("Das Ergebnis von a² - b² lautet: ", ergebnis, "700x75")
    
    elif startx == 0:
        return
    
    else:
        message_box("❗❗❗ERROR! Ungültige Auswahl❗❗❗")

def trigonometrie_rechner():
    starty = inputInt("Was möchten Sie berechnen? (1 = Gegen-/Hypo-) (2 = An-/Hypo-) (3 = Gegen-/An-) (4 = Winkel) (5 = Hypotenuse) (0 = Zurück zum Hauptmenü)")

    if starty <= 0 or starty >= 6:
        message_box("❗❗❗ERROR! Ungültige Auswahl❗❗❗")
        return

    if starty == 1:
        gegen = inputInt("↓↓↓ Länge der Gegenkathete ↓↓↓")
        winkel = inputInt("↓↓↓ Winkel in Grad ↓↓↓")
        if winkel <= 0 or winkel >= 90:
            message_box("❗❗❗ERROR! Ungültiger Winkel❗❗❗")
        else:
            hypo = round(gegen / (sin(radians(winkel))), 2)
            resultplus_box("Die Länge der Hypotenuse lautet: ", hypo, "700x75")
    
    elif starty == 2:
        an = inputInt("↓↓↓ Länge der Ankathete ↓↓↓")
        winkel = inputInt("↓↓↓ Winkel in Grad ↓↓↓")
        if winkel <= 0 or winkel >= 90:
            message_box("❗❗❗ERROR! Ungültiger Winkel❗❗❗")
        else:
            hypo = round(an / (cos(radians(winkel))), 2)
            resultplus_box("Die Länge der Hypotenuse lautet: ", hypo, "700x75")
    
    elif starty == 3:
        gegen = inputInt("↓↓↓ Länge der Gegenkathete ↓↓↓")
        an = inputInt("↓↓↓ Winkel in Grad ↓↓↓")
        if an <= 0 or an >= 90:
            message_box("❗❗❗ERROR! Ungültiger Winkel❗❗❗")
        else:
            ankathete = round(gegen / (tan(radians(an))), 2)
            resultplus_box("Die Länge der Ankathete lautet: ", ankathete, "700x75")

    elif starty == 4:
        trigonometriewinkel_rechner()

    elif starty == 5:
        trigonometriehypo_rechner()

    elif starty == 0:
        return

    else:
        message_box("❗❗❗ERROR! Ungültige Auswahl❗❗❗")

def trigonometriewinkel_rechner():
    startz = inputInt("Wie möchten sie ihr Winkel berechnen? (1 = Gegen-/Hypo-) (2 = An-/Hypo-) (3 = Gegen-/An-)")

    if startz <= 0 or startz >= 4:
        message_box("❗❗❗ERROR! Ungültige Auswahl❗❗❗")
        return

    if startz == 1:
        gegen = inputInt("↓↓↓ Länge der Gegenkathete ↓↓↓")
        hypo = inputInt("↓↓↓ Länge der Hypotenuse ↓↓↓")
        if hypo == 0 or gegen < 0 or hypo < 0 or gegen > hypo:
            message_box("❗❗❗ERROR! Ungültige Maße❗❗❗")
        else:
            winkel = round(math.degrees(math.asin(gegen / hypo)), 2)
            resultplus_box("Der Winkel lautet: ", winkel, "700x75")

    elif startz == 2:
        an = inputInt("↓↓↓ Länge der Ankathete ↓↓↓")
        hypo = inputInt("↓↓↓ Länge der Hypotenuse ↓↓↓")
        if hypo == 0 or an < 0 or hypo < 0 or an > hypo:
            message_box("❗❗❗ERROR! Ungültige Maße❗❗❗")
        else:
            winkel = round(math.degrees(math.acos(an / hypo)), 2)
            resultplus_box("Der Winkel lautet: ", winkel, "700x75")

    elif startz == 3:
        gegen = inputInt("↓↓↓ Länge der Gegenkathete ↓↓↓")
        an = inputInt("↓↓↓ Länge der Ankathete ↓↓↓")
        if an == 0 or gegen < 0 or an < 0:
            message_box("❗❗❗ERROR! Ungültige Maße❗❗❗")
        else:
            winkel = round(math.degrees(math.atan(gegen / an)), 2)
            resultplus_box("Der Winkel lautet: ", winkel, "700x75")

def trigonometriehypo_rechner():
    startw = inputInt("Wie möchten sie ihre Hypotenuse berechnen? (1 = Gegen-/Winkel) (2 = An-/Winkel)")

    if startw <= 0 or startw >= 3:
        message_box("❗❗❗ERROR! Ungültige Auswahl❗❗❗")
        return

    if startw == 1:
        gegen = inputInt("↓↓↓ Länge der Gegenkathete ↓↓↓")
        winkel = inputInt("↓↓↓ Winkel in Grad ↓↓↓")
        if winkel <= 0 or winkel >= 90:
            message_box("❗❗❗ERROR! Ungültiger Winkel❗❗❗")
        else:
            hypo = round(gegen / (sin(radians(winkel))), 2)
            resultplus_box("Die Länge der Hypotenuse lautet: ", hypo, "700x75")

    elif startw == 2:
        an = inputInt("↓↓↓ Länge der Ankathete ↓↓↓")
        winkel = inputInt("↓↓↓ Winkel in Grad ↓↓↓")
        if winkel <= 0 or winkel >= 90:
            message_box("❗❗❗ERROR! Ungültiger Winkel❗❗❗")
        else:
            hypo = round(an / (cos(radians(winkel))), 2)
            resultplus_box("Die Länge der Hypotenuse lautet: ", hypo, "700x75")

def bruch_dezimal_rechner():
    startq = inputInt("Möchten Sie einen Bruch in eine Dezimalzahl umrechnen (1) oder eine Dezimalzahl in einen Bruch umrechnen (2)? (0 = Zurück zum Hauptmenü)")

    if startq == 1:
        zaehler = inputInt("↓↓↓ Zähler des Bruchs (?/a) ↓↓↓")
        nenner = inputInt("↓↓↓ Nenner des Bruchs (a/?) ↓↓↓")
        if nenner == 0:
            message_box("❗❗❗ERROR! Division durch Null nicht möglich❗❗❗")
        else:
            dezimal = round(zaehler / nenner, 5)
            resultplus_box("Die Dezimalzahl lautet: ", dezimal, "700x75")

    elif startq == 2:
        dezimal = inputInt("↓↓↓ Dezimalzahl ↓↓↓")
        nenner = 100000  # Umwandlung in Bruch mit 5 Nachkommastellen
        zaehler = round(dezimal * nenner)
        # Kürzen des Bruchs
        def ggt(a, b):
            while b:
                a, b = b, a % b
            return a
        teiler = ggt(zaehler, nenner)
        zaehler //= teiler
        nenner //= teiler
        resultplus_box("Der Bruch lautet: ", f"{zaehler}/{nenner}", "700x75")

    elif startq == 0:
        return

    else:
        message_box("❗❗❗ERROR! Ungültige Auswahl❗❗❗")

# Start des Programms
main_menu()