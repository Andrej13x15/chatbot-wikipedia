# chatbot_wikipedia.py
import wikipedia

# Ustawienie języka (np. polski)
wikipedia.set_lang("pl")

print("🤖 Chatbot Wikipedia — wpisz 'koniec' aby zakończyć\n")

while True:
    pytanie = input("Ty: ")
    if pytanie.lower() == "koniec":
        print("Bot: Do zobaczenia!")
        break

    try:
        # Wyszukiwanie w Wikipedii
        wyniki = wikipedia.search(pytanie)
        if not wyniki:
            print("Bot: Nie znalazłem informacji w Wikipedii.")
            continue

        # Pobranie streszczenia pierwszego wyniku
        streszczenie = wikipedia.summary(wyniki[0], sentences=3)
        print(f"Bot: {streszczenie}")
    except wikipedia.exceptions.DisambiguationError as e:
        print(f"Bot: Twoje pytanie jest niejednoznaczne. Możesz sprecyzować? Oto przykłady: {e.options[:5]}")
    except Exception as ex:
        print(f"Bot: Wystąpił błąd: {ex}")
