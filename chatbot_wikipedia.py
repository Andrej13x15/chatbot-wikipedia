import wikipedia
import json
import os
import random
import difflib

wikipedia.set_lang("pl")

DATA_FILE = "data.json"
CONTEXT_FILE = "context.json"

# Wczytanie bazy wiedzy
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        knowledge = json.load(f)
else:
    knowledge = {}

# Wczytanie kontekstu
if os.path.exists(CONTEXT_FILE):
    with open(CONTEXT_FILE, "r", encoding="utf-8") as f:
        context = json.load(f)
else:
    context = {"ostatni_temat": None, "ostatnie_zrodlo": None}

ostatni_temat = context.get("ostatni_temat")
ostatnie_zrodlo = context.get("ostatnie_zrodlo")

def zapisz_kontekst():
    with open(CONTEXT_FILE, "w", encoding="utf-8") as f:
        json.dump({"ostatni_temat": ostatni_temat, "ostatnie_zrodlo": ostatnie_zrodlo}, f, ensure_ascii=False, indent=2)

def znajdz_podobne_pytanie(pytanie, baza, prog=0.7):
    for klucz in baza:
        podobienstwo = difflib.SequenceMatcher(None, pytanie.lower(), klucz.lower()).ratio()
        if podobienstwo >= prog:
            return klucz
    return None

def ludzkie_odpowiedzi(wiadomosc):
    wiadomosc = wiadomosc.lower()

    przywitania = ["cześć", "hej", "witaj", "siema"]
    pytania_o_samopoczucie = ["jak się masz", "co u ciebie", "jak leci"]
    pozegnania = ["pa", "do zobaczenia", "na razie", "żegnaj"]
    pytania_o_bota = ["kim jesteś", "co potrafisz", "czym się zajmujesz"]
    wiecej_info = ["powiedz coś więcej", "rozwiń", "co możesz jeszcze dodać"]

    if any(s in wiadomosc for s in przywitania):
        return random.choice([
            "Hejka! Jak się masz? 😄",
            "Cześć! Co słychać?",
            "Witaj! O czym dziś pogadamy?"
        ])

    if any(s in wiadomosc for s in pytania_o_samopoczucie):
        return random.choice([
            "Świetnie, dziękuję! A Ty? 😊",
            "Wszystko OK, gotowy do rozmowy!",
            "Czuję się znakomicie, a Ty?"
        ])

    if any(s in wiadomosc for s in pozegnania):
        return random.choice([
            "Do zobaczenia! 👋",
            "Na razie! Trzymaj się!",
            "Miłego dnia! 😊"
        ])

    if any(s in wiadomosc for s in pytania_o_bota):
        return random.choice([
            "Jestem twoim wirtualnym pomocnikiem z dostępem do Wikipedii i pamięcią rozmów.",
            "Potrafię szukać informacji w Wikipedii, uczyć się od Ciebie i prowadzić rozmowę.",
            "Jestem botem, który chce się rozwijać dzięki Tobie! 😄"
        ])

    if any(s in wiadomosc for s in wiecej_info):
        return "KONTYNUUJ"

    return None

print("🤖 Hej! Jestem botem Wikipedyjno-rozmownym z pamięcią długoterminową.")
if ostatni_temat:
    print(f"(📌 Pamiętam, że ostatnio rozmawialiśmy o: {ostatni_temat})")
print("Wpisz 'koniec', żeby zakończyć, lub 'popraw' aby zmienić zapamiętaną odpowiedź.\n")

while True:
    pytanie = input("Ty: ").strip()
    if pytanie.lower() == "koniec":
        zapisz_kontekst()
        print("Bot: Trzymaj się! 😊")
        break

    if pytanie.lower() == "popraw":
        temat = input("Podaj temat, którego odpowiedź chcesz zmienić: ")
        podobne = znajdz_podobne_pytanie(temat, knowledge)
        if podobne:
            print(f"Bot: Aktualna odpowiedź to: {knowledge[podobne]}")
            nowa = input("Podaj nową odpowiedź: ")
            knowledge[podobne] = nowa
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(knowledge, f, ensure_ascii=False, indent=2)
            print("Bot: Zmienione! 👍")
        else:
            print("Bot: Nie mam jeszcze takiego tematu w pamięci.")
        continue

    odp = ludzkie_odpowiedzi(pytanie)
    if odp == "KONTYNUUJ":
        if ostatni_temat and ostatnie_zrodlo == "wiki":
            try:
                streszczenie = wikipedia.summary(ostatni_temat, sentences=5)
                print(f"Bot: Jasne! Oto więcej informacji o {ostatni_temat}: {streszczenie}")
            except:
                print("Bot: Nie mogę znaleźć więcej informacji w tej chwili.")
        elif ostatni_temat and ostatnie_zrodlo == "user":
            print(f"Bot: To wszystko, co mi powiedziałeś o {ostatni_temat}: {knowledge[ostatni_temat]}")
        else:
            print("Bot: Nie pamiętam, o czym rozmawialiśmy. 😅")
        continue
    elif odp:
        print(f"Bot: {odp}")
        continue

    podobne = znajdz_podobne_pytanie(pytanie, knowledge)
    if podobne:
        print(f"Bot (z pamięci): {knowledge[podobne]}")
        ostatni_temat = podobne
        ostatnie_zrodlo = "user"
        zapisz_kontekst()
        continue

    try:
        wyniki = wikipedia.search(pytanie)
        if not wyniki:
            print("Bot: Hmm… nie znalazłem tego w Wikipedii.")
            odpowiedz = input("Możesz mi powiedzieć coś na ten temat? Chętnie się nauczę:\nTy: ")
            knowledge[pytanie] = odpowiedz
            ostatni_temat = pytanie
            ostatnie_zrodlo = "user"
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(knowledge, f, ensure_ascii=False, indent=2)
            zapisz_kontekst()
            print("Bot: Dzięki! Zapamiętałem to. 😊")
            continue

        streszczenie = wikipedia.summary(wyniki[0], sentences=3)
        print(f"Bot: {random.choice(['Świetne pytanie!', 'Hmm… ciekawe!', 'Postaram się wyjaśnić!'])} {streszczenie}")
        ostatni_temat = wyniki[0]
        ostatnie_zrodlo = "wiki"
        zapisz_kontekst()

    except wikipedia.exceptions.DisambiguationError as e:
        print(f"Bot: To pytanie jest trochę niejednoznaczne. Może chodziło Ci o coś z tych: {e.options[:5]}")
    except Exception as ex:
        print(f"Bot: Ups, coś poszło nie tak: {ex}")

