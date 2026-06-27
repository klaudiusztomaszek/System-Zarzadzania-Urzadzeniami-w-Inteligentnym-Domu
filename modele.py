"""Modele aplikacji inteligentnego domu."""

from abc import ABC, abstractmethod
import json
import os


class IPrzelaczalne(ABC):
    """Interfejs dla urządzeń, które można włączać i wyłączać."""

    def wlacz(self):
        self.status = "ON"

    def wylacz(self):
        self.status = "OFF"


class IRegulowalne(ABC):
    """Interfejs dla urządzeń z regulowanym parametrem."""

    @abstractmethod
    def ustawPoziom(self, poziom):
        pass


class Urzadzenie(ABC):
    """Bazowa klasa dla wszystkich urządzeń w inteligentnym domu."""

    aktualneID = 1

    def __init__(self, nazwaPrzyjazna, lokalizacja, status="OFF"):
        if not nazwaPrzyjazna or not lokalizacja:
            raise ValueError("Nazwa i lokalizacja nie mogą być puste!")

        self._idUrzadzenia = Urzadzenie.aktualneID
        Urzadzenie.aktualneID += 1
        self._nazwaPrzyjazna = nazwaPrzyjazna
        self._lokalizacja = lokalizacja

        if status not in ("ON", "OFF"):
            raise ValueError("Niepoprawny status początkowy!")
        self._status = status

    @property
    def idUrzadzenia(self):
        return self._idUrzadzenia

    @property
    def nazwaPrzyjazna(self):
        return self._nazwaPrzyjazna

    @nazwaPrzyjazna.setter
    def nazwaPrzyjazna(self, nowa_nazwa):
        if not nowa_nazwa:
            raise ValueError("Nazwa nie może być pusta!")
        self._nazwaPrzyjazna = nowa_nazwa

    @property
    def lokalizacja(self):
        return self._lokalizacja

    @lokalizacja.setter
    def lokalizacja(self, nowa_lokalizacja):
        if not nowa_lokalizacja:
            raise ValueError("Lokalizacja nie może być pusta!")
        self._lokalizacja = nowa_lokalizacja

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, nowy_status):
        if nowy_status not in ("ON", "OFF"):
            raise ValueError("Niepoprawny status. Dozwolone: ON lub OFF")
        self._status = nowy_status

    def pobierzStatus(self):
        return self._status

    @abstractmethod
    def pobierzSzczegolowyOpis(self):
        pass


class Pralka(Urzadzenie, IPrzelaczalne):
    """Reprezentuje pralke sterowaną z poziomu aplikacji."""

    def __init__(self, nazwaPrzyjazna, lokalizacja, status="OFF", program="Standard"):
        super().__init__(nazwaPrzyjazna, lokalizacja, status)
        self._program = program

    @property
    def program(self):
        return self._program

    @program.setter
    def program(self, nowy_program):
        if not nowy_program:
            raise ValueError("Program nie może być pusty!")
        self._program = nowy_program

    def pobierzSzczegolowyOpis(self):
        return f"ID {self.idUrzadzenia} - Pralka '{self.nazwaPrzyjazna}' [{self.lokalizacja}] -> Status: {self.status}, Program: {self.program}"


class Lodowka(Urzadzenie, IPrzelaczalne, IRegulowalne):
    """Reprezentuje lodówkę z regulacją temperatury."""

    def __init__(self, nazwaPrzyjazna, lokalizacja, status="OFF", temperatura=4.0):
        super().__init__(nazwaPrzyjazna, lokalizacja, status)
        self.temperatura = temperatura

    @property
    def temperatura(self):
        return self._temperatura

    @temperatura.setter
    def temperatura(self, nowa_temperatura):
        try:
            temp_float = float(nowa_temperatura)
        except (ValueError, TypeError):
            raise ValueError("Temperatura musi być liczbą!")

        if not 1.0 <= temp_float <= 10.0:
            raise ValueError("Temperatura lodówki musi być w zakresie 1-10°C")
        self._temperatura = temp_float

    def ustawPoziom(self, poziom):
        self.temperatura = poziom

    def pobierzSzczegolowyOpis(self):
        return f"ID {self.idUrzadzenia} - Lodówka '{self.nazwaPrzyjazna}' [{self.lokalizacja}] -> Status: {self.status}, Temp: {self.temperatura}°C"


class InteligentnyDom:
    """Zarządza całością urządzeń i ich stanem."""

    def __init__(self, nazwaDomu):
        self._listaUrzadzen = []
        self._nazwaDomu = nazwaDomu

    def dodajUrzadzenie(self, urzadzenie):
        self._listaUrzadzen.append(urzadzenie)

    def usunUrzadzenie(self, urzadzenie):
        self._listaUrzadzen.remove(urzadzenie)

    def znajdzUrzadzenie(self, idUrzadzenia):
        for urzadzenie in self._listaUrzadzen:
            if urzadzenie.idUrzadzenia == idUrzadzenia:
                return urzadzenie
        return None

    def zarzadzajUrzadzeniem(self, idUrzadzenia, nowy_status):
        urzadzenie = self.znajdzUrzadzenie(idUrzadzenia)
        if urzadzenie:
            urzadzenie.status = nowy_status
        else:
            raise ValueError("Nie znaleziono urządzenia o podanym ID")

    def eksportuj_konfiguracje(self, nazwa_pliku="konfiguracja.json"):
        """Zapisuje aktualną konfigurację domu do pliku JSON."""
        dane = {
            "nazwaDomu": self._nazwaDomu,
            "aktualneID": Urzadzenie.aktualneID,
            "urzadzenia": [],
        }

        for urzadzenie in self._listaUrzadzen:
            if isinstance(urzadzenie, Pralka):
                dane["urzadzenia"].append({
                    "id": urzadzenie.idUrzadzenia,
                    "typ": "Pralka",
                    "nazwa": urzadzenie.nazwaPrzyjazna,
                    "lokalizacja": urzadzenie.lokalizacja,
                    "status": urzadzenie.status,
                    "program": urzadzenie.program,
                })
            elif isinstance(urzadzenie, Lodowka):
                dane["urzadzenia"].append({
                    "id": urzadzenie.idUrzadzenia,
                    "typ": "Lodowka",
                    "nazwa": urzadzenie.nazwaPrzyjazna,
                    "lokalizacja": urzadzenie.lokalizacja,
                    "status": urzadzenie.status,
                    "temperatura": urzadzenie.temperatura,
                })

        katalog = os.path.dirname(nazwa_pliku)
        if katalog:
            os.makedirs(katalog, exist_ok=True)

        with open(nazwa_pliku, "w", encoding="utf-8") as plik:
            json.dump(dane, plik, ensure_ascii=False, indent=2)

    def importuj_konfiguracje(self, nazwa_pliku="konfiguracja.json"):
        """Wczytuje konfigurację domu z pliku JSON."""
        if not os.path.exists(nazwa_pliku):
            raise FileNotFoundError("Brak pliku konfiguracyjnego.")

        try:
            with open(nazwa_pliku, "r", encoding="utf-8") as plik:
                dane = json.load(plik)
        except json.JSONDecodeError as exc:
            raise ValueError("Plik konfiguracji ma niepoprawny format JSON.") from exc

        self._listaUrzadzen.clear()
        self._nazwaDomu = dane.get("nazwaDomu", self._nazwaDomu)

        najwyzsze_id = int(dane.get("aktualneID", 1))
        Urzadzenie.aktualneID = najwyzsze_id

        for element in dane.get("urzadzenia", []):
            typ = element.get("typ")
            nazwa = element.get("nazwa", "")
            lokalizacja = element.get("lokalizacja", "")
            status = element.get("status", "OFF")

            if typ == "Pralka":
                urzadzenie = Pralka(nazwa, lokalizacja, status, element.get("program", "Standard"))
            elif typ == "Lodowka":
                urzadzenie = Lodowka(nazwa, lokalizacja, status, element.get("temperatura", 4.0))
            else:
                continue

            urzadzenie._idUrzadzenia = int(element.get("id", urzadzenie.idUrzadzenia))
            if urzadzenie.idUrzadzenia >= Urzadzenie.aktualneID:
                Urzadzenie.aktualneID = urzadzenie.idUrzadzenia + 1
            self.dodajUrzadzenie(urzadzenie)

    def zapisz_do_pliku(self, nazwa_pliku="stan_domu.txt"):
        """Zapisuje bieżący stan urządzeń do pliku tekstowego."""
        try:
            with open(nazwa_pliku, "w", encoding="utf-8") as plik:
                plik.write(f"ZMIENNA_ID;{Urzadzenie.aktualneID}\n")

                for urzadzenie in self._listaUrzadzen:
                    if isinstance(urzadzenie, Pralka):
                        plik.write(
                            f"Pralka;{urzadzenie.nazwaPrzyjazna};{urzadzenie.lokalizacja};{urzadzenie.status};{urzadzenie.program}\n"
                        )
                    elif isinstance(urzadzenie, Lodowka):
                        plik.write(
                            f"Lodowka;{urzadzenie.nazwaPrzyjazna};{urzadzenie.lokalizacja};{urzadzenie.status};{urzadzenie.temperatura}\n"
                        )
            return True
        except IOError as exc:
            raise IOError(f"Błąd zapisu pliku: {exc.strerror}") from exc

    def wczytaj_z_pliku(self, nazwa_pliku="stan_domu.txt"):
        """Odczytuje stan urządzeń z pliku tekstowego."""
        if not os.path.exists(nazwa_pliku):
            raise FileNotFoundError("Brak pliku tekstowego 'stan_domu.txt'. Załadowano czysty profil.")

        try:
            self._listaUrzadzen.clear()
            with open(nazwa_pliku, "r", encoding="utf-8") as plik:
                for linia in plik:
                    linia = linia.strip()
                    if not linia:
                        continue

                    dane = linia.split(";")

                    if dane[0] == "ZMIENNA_ID":
                        Urzadzenie.aktualneID = int(dane[1])
                        continue

                    typ = dane[0]
                    nazwa = dane[1]
                    lokalizacja = dane[2]
                    status = dane[3]

                    if typ == "Pralka":
                        program = dane[4]
                        nowa_pralka = Pralka(nazwa, lokalizacja, status, program)
                        self.dodajUrzadzenie(nowa_pralka)
                    elif typ == "Lodowka":
                        temp = float(dane[4])
                        nowa_lodowka = Lodowka(nazwa, lokalizacja, status, temp)
                        self.dodajUrzadzenie(nowa_lodowka)
            return True
        except (IOError, ValueError, IndexError) as exc:
            raise IOError("Plik tekstowy jest uszkodzony lub ma niepoprawny format danych.") from exc