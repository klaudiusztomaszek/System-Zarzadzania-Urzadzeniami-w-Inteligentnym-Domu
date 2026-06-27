"""Interfejs graficzny aplikacji inteligentnego domu."""

import PySimpleGUI as sg
from modele import InteligentnyDom, Pralka, Lodowka

PLIK_ZAPISU = "stan_domu.txt"
DOMYSLNY_PLIK_KONFIGURACJI = "konfiguracja.json"


def uruchom_gui():
    dom = InteligentnyDom("Inteligentny Dom Byka")

    komunikat_startowy = "Wczytano zapisany stan systemu z pliku tekstowego."
    try:
        dom.wczytaj_z_pliku(PLIK_ZAPISU)
    except FileNotFoundError as exc:
        komunikat_startowy = str(exc)
        dom.dodajUrzadzenie(Pralka("Pralka Główna", "Łazienka"))
        dom.dodajUrzadzenie(Lodowka("Lodówka Kuchenna", "Kuchnia", temperatura=4.0))
    except Exception as exc:
        komunikat_startowy = f"Błąd startu: {exc}"

    def odswiez_liste_gui():
        return [f"{urzadzenie.idUrzadzenia}: {urzadzenie.nazwaPrzyjazna} ({urzadzenie.lokalizacja})" for urzadzenie in dom._listaUrzadzen]

    def zresetuj_panel_urzadzenia():
        window["-INFO-URZADZENIE-"].update("Wybierz urządzenie z listy...")
        window["-BTN-ON-"].update(disabled=True)
        window["-BTN-OFF-"].update(disabled=True)
        window["-SUWAK-TEMP-"].update(disabled=True)

    sg.theme("DarkBlue3")

    kolumna_lewa = [
        [sg.Text("Urządzenia:", font=("Helvetica", 11, "bold"))],
        [sg.Listbox(values=odswiez_liste_gui(), size=(35, 8), key="-LISTA-", enable_events=True)],
        [sg.HorizontalSeparator()],
        [sg.Text("Dodaj nowe urządzenie:", font=("Helvetica", 10, "bold"))],
        [sg.Text("Nazwa:"), sg.Input(size=(20, 1), key="-NOWA-NAZWA-")],
        [sg.Text("Pokój:"), sg.Input(size=(20, 1), key="-NOWA-LOK-")],
        [sg.Text("Typ:  "), sg.Combo(["Pralka", "Lodówka"], default_value="Pralka", key="-NOWY-TYP-", readonly=True)],
        [sg.Button("Dodaj", size=(10, 1)), sg.Button("Usuń wybrane", size=(12, 1))],
    ]

    kolumna_prawa = [
        [sg.Text("Panel kontrolny", font=("Helvetica", 11, "bold"))],
        [sg.Text("Wybierz urządzenie z listy...", key="-INFO-URZADZENIE-", size=(40, 2), text_color="yellow")],
        [sg.Frame("Zasilanie", [[sg.Button("WŁĄCZ (ON)", key="-BTN-ON-", disabled=True), sg.Button("WYŁĄCZ (OFF)", key="-BTN-OFF-", disabled=True)]])],
        [sg.Frame("Temperatura", [[sg.Slider(range=(1.0, 10.0), resolution=0.5, orientation="h", size=(20, 15), key="-SUWAK-TEMP-", enable_events=True, disabled=True)], [sg.Text("Zakres: 1.0 - 10.0 °C")]])],
        [sg.Text("", size=(1, 1))],
        [sg.Button("Eksportuj konfigurację", size=(18, 1)), sg.Button("Importuj konfigurację", size=(18, 1))],
        [sg.Button("ZAPISZ STAN", button_color=("white", "green"), size=(14, 1)), sg.Button("Wyjście", size=(10, 1))],
    ]

    layout = [
        [sg.Text(dom._nazwaDomu, font=("Helvetica", 16, "bold"))],
        [sg.HorizontalSeparator()],
        [sg.Column(kolumna_lewa), sg.VerticalSeparator(), sg.Column(kolumna_prawa)],
        [sg.HorizontalSeparator()],
        [sg.Text("Status operacji / logi:")],
        [sg.Multiline(default_text=komunikat_startowy + "\n", size=(80, 4), key="-LOGI-", disabled=True, text_color="lightgreen")],
    ]

    window = sg.Window("Smart Home System v2.0", layout, finalize=True)
    wybrane_urzadzenie = None

    def loguj(tekst, blad=False):
        kolor = "red" if blad else "lightgreen"
        window["-LOGI-"].update(tekst + "\n", append=True, text_color_for_value=kolor)

    def generuj_podglad_polimorficzny():
        opis = "=== AKTUALNY STAN URZĄDZEŃ ===\n"
        for urzadzenie in dom._listaUrzadzen:
            opis += urzadzenie.pobierzSzczegolowyOpis() + "\n"
        loguj(opis)

    generuj_podglad_polimorficzny()

    while True:
        event, values = window.read()

        if event in (sg.WINDOW_CLOSED, "Wyjście"):
            break

        if event == "-LISTA-" and values["-LISTA-"]:
            try:
                wybrany_tekst = values["-LISTA-"][0]
                id_urzadzenia = int(wybrany_tekst.split(":")[0])
                wybrane_urzadzenie = dom.znajdzUrzadzenie(id_urzadzenia)

                if wybrane_urzadzenie:
                    window["-INFO-URZADZENIE-"].update(wybrane_urzadzenie.pobierzSzczegolowyOpis())
                    window["-BTN-ON-"].update(disabled=False)
                    window["-BTN-OFF-"].update(disabled=False)

                    if isinstance(wybrane_urzadzenie, Lodowka):
                        window["-SUWAK-TEMP-"].update(disabled=False, value=wybrane_urzadzenie.temperatura)
                    else:
                        window["-SUWAK-TEMP-"].update(disabled=True)
            except Exception as exc:
                loguj(f"Błąd wyboru: {exc}", blad=True)

        if event in ("-BTN-ON-", "-BTN-OFF-") and wybrane_urzadzenie:
            nowy_status = "ON" if event == "-BTN-ON-" else "OFF"
            try:
                dom.zarzadzajUrzadzeniem(wybrane_urzadzenie.idUrzadzenia, nowy_status)
                window["-INFO-URZADZENIE-"].update(wybrane_urzadzenie.pobierzSzczegolowyOpis())
                generuj_podglad_polimorficzny()
            except ValueError as exc:
                loguj(f"Błąd zmiany statusu: {exc}", blad=True)

        if event == "-SUWAK-TEMP-" and isinstance(wybrane_urzadzenie, Lodowka):
            try:
                wybrane_urzadzenie.ustawPoziom(values["-SUWAK-TEMP-"])
                window["-INFO-URZADZENIE-"].update(wybrane_urzadzenie.pobierzSzczegolowyOpis())
            except ValueError as exc:
                loguj(f"Błąd regulacji: {exc}", blad=True)

        if event == "Dodaj":
            nazwa = values["-NOWA-NAZWA-"].strip()
            lokalizacja = values["-NOWA-LOK-"].strip()
            typ = values["-NOWY-TYP-"]

            try:
                nowe = Pralka(nazwa, lokalizacja) if typ == "Pralka" else Lodowka(nazwa, lokalizacja)

                dom.dodajUrzadzenie(nowe)
                window["-LISTA-"].update(values=odswiez_liste_gui())
                loguj(f"Pomyślnie dodano urządzenie: {nazwa}")
                generuj_podglad_polimorficzny()

                window["-NOWA-NAZWA-"].update("")
                window["-NOWA-LOK-"].update("")
            except ValueError as exc:
                loguj(f"Nie udało się dodać urządzenia: {exc}", blad=True)
                sg.popup_error(f"Nie można dodać urządzenia!\nPowód: {exc}", title="Błąd danych")

        if event == "Usuń wybrane" and wybrane_urzadzenie:
            try:
                dom.usunUrzadzenie(wybrane_urzadzenie)
                wybrane_urzadzenie = None
                window["-LISTA-"].update(values=odswiez_liste_gui())
                zresetuj_panel_urzadzenia()
                loguj("Usunięto wybrane urządzenie z systemu.")
                generuj_podglad_polimorficzny()
            except Exception as exc:
                loguj(f"Błąd podczas usuwania: {exc}", blad=True)

        if event == "Eksportuj konfigurację":
            try:
                sciezka = sg.popup_get_file(
                    "Zapisz konfigurację",
                    save_as=True,
                    default_path=DOMYSLNY_PLIK_KONFIGURACJI,
                    file_types=(("Pliki JSON", "*.json"),),
                )
                if sciezka:
                    dom.eksportuj_konfiguracje(sciezka)
                    loguj(f"Konfiguracja została wyeksportowana do: {sciezka}")
                    sg.popup("Gotowe", "Konfiguracja została zapisana w formacie JSON.", button_color="green")
            except Exception as exc:
                loguj(f"Błąd eksportu: {exc}", blad=True)
                sg.popup_error(f"Nie udało się wyeksportować konfiguracji!\n{exc}")

        if event == "Importuj konfigurację":
            try:
                sciezka = sg.popup_get_file(
                    "Wybierz plik konfiguracji",
                    default_path=DOMYSLNY_PLIK_KONFIGURACJI,
                    file_types=(("Pliki JSON", "*.json"),),
                )
                if sciezka:
                    dom.importuj_konfiguracje(sciezka)
                    wybrane_urzadzenie = None
                    window["-LISTA-"].update(values=odswiez_liste_gui())
                    zresetuj_panel_urzadzenia()
                    loguj(f"Konfiguracja została zaimportowana z: {sciezka}")
                    generuj_podglad_polimorficzny()
                    sg.popup("Gotowe", "Konfiguracja została zaimportowana z pliku JSON.", button_color="green")
            except Exception as exc:
                loguj(f"Błąd importu: {exc}", blad=True)
                sg.popup_error(f"Nie udało się zaimportować konfiguracji!\n{exc}")

        if event == "ZAPISZ STAN":
            try:
                dom.zapisz_do_pliku(PLIK_ZAPISU)
                loguj("Stan systemu został zapisany do pliku tekstowego.")
                sg.popup("Zapisano", "Stan urządzeń został zapisany w pliku tekstowym.", button_color="green")
            except IOError as exc:
                loguj(str(exc), blad=True)
                sg.popup_error(f"Nie udało się zapisać danych!\n{exc}")

    window.close()