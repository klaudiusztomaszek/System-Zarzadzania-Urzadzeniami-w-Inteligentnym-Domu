from abc import ABC, abstractmethod

class IPrzelaczalne(ABC):
    def wlacz(self):
        self.status = "ON"

    def wylacz(self):
        self.status = "OFF"

class IRegulowalne(ABC):
    @abstractmethod
    def ustawPoziom(self, poziom):
        pass

class Urzadzenie(ABC):
    aktualneID = 1

    def __init__(self, nazwaPrzyjazna, lokalizacja, status="OFF"):
        self._idUrzadzenia = Urzadzenie.aktualneID
        Urzadzenie.aktualneID += 1
        self._nazwaPrzyjazna = nazwaPrzyjazna
        self._lokalizacja = lokalizacja
        self._status = status

    @property
    def idUrzadzenia(self):
        return self._idUrzadzenia

    @property
    def nazwaPrzyjazna(self):
        return self._nazwaPrzyjazna

    @nazwaPrzyjazna.setter
    def nazwaPrzyjazna(self, nowa_nazwa):
        self._nazwaPrzyjazna = nowa_nazwa

    @property
    def lokalizacja(self):
        return self._lokalizacja

    @lokalizacja.setter
    def lokalizacja(self, nowa_lokalizacja):
        self._lokalizacja = nowa_lokalizacja

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, nowy_status):
        if nowy_status not in ("ON", "OFF"):
            raise ValueError("Niepoprawny status")
        self._status = nowy_status

    def pobierzStatus(self):
        return self._status

    @abstractmethod
    def pobierzSzczegolowyOpis(self):
        pass

class Pralka(Urzadzenie, IPrzelaczalne):
    def __init__(self, nazwaPrzyjazna, lokalizacja, status="OFF", program="Standard"):
        super().__init__(nazwaPrzyjazna, lokalizacja, status)
        self._program = program

    @property
    def program(self):
        return self._program

    @program.setter
    def program(self, nowy_program):
        self._program = nowy_program

    def pobierzSzczegolowyOpis(self):
        return f"Obiekt o id {self.idUrzadzenia} - Pralka {self.nazwaPrzyjazna} w lokalizacji {self.lokalizacja} jest aktualnie {self.status} i używa programu {self.program}"
    
class Lodowka(Urzadzenie, IPrzelaczalne, IRegulowalne):
    def __init__(self, nazwaPrzyjazna, lokalizacja, status="OFF", temperatura=4.0):
        super().__init__(nazwaPrzyjazna, lokalizacja, status)
        self._temperatura = temperatura

    @property
    def temperatura(self):
        return self._temperatura

    @temperatura.setter
    def temperatura(self, nowa_temperatura):
        if not 1.0 <= nowa_temperatura <= 10.0:
            raise ValueError("Temperatura lodówki musi być w zakresie 1-10°C")
        self._temperatura = nowa_temperatura

    def ustawPoziom(self, poziom):
        self.temperatura = poziom

    def pobierzSzczegolowyOpis(self):
        return f"Obiekt o id {self.idUrzadzenia} - Lodowka {self.nazwaPrzyjazna} w lokalizacji {self.lokalizacja} jest aktualnie {self.status} i utrzymuje temperaturę {self.temperatura}°C"


class InteligentnyDom:
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
    
    def wyswietlStatusWszystkichUrzadzen(self):
        for urzadzenie in self._listaUrzadzen:
            print(urzadzenie.pobierzSzczegolowyOpis())

    def zarzadzajUrzadzeniem(self, idUrzadzenia, nowy_status):
        urzadzenie = self.znajdzUrzadzenie(idUrzadzenia)
        if urzadzenie:
            urzadzenie.status = nowy_status
        else:
            print("Nie znaleziono urządzenia o podanym ID")

def main():
    print("Witaj w systemie inteligentnego domu!")

    # Stwórz obiekt InteligentnyDom.
    Dom1 = InteligentnyDom("Domek")

    # Stwórz kilka różnych obiektów urządzeń z różnymi ID, nazwami i lokalizacjami.
    Pralka1 = Pralka("Pralka1", "Łazienka")
    Pralka2 = Pralka("Pralka2", "Piwnica")
    Lodowka1 = Lodowka("Lodówka1", "Kuchnia")

    # Dodaj je do domu
    Dom1.dodajUrzadzenie(Pralka1)
    Dom1.dodajUrzadzenie(Pralka2)
    Dom1.dodajUrzadzenie(Lodowka1)

    # Wyświetl status wszystkich urządzeń.
    print("\nStatus wszystkich urządzeń po dodaniu:")
    Dom1.wyswietlStatusWszystkichUrzadzen()

    # Spróbuj włączyć i wyłączyć niektóre urządzenia korzystając z metody zarządzającej w InteligentnyDom, która użyje interfejsu IPrzelaczalne
    print("\nZarządzanie urządzeniami:")
    Dom1.zarzadzajUrzadzeniem(Pralka1.idUrzadzenia, "ON")
    Dom1.zarzadzajUrzadzeniem(Lodowka1.idUrzadzenia, "ON")
    Dom1.wyswietlStatusWszystkichUrzadzen()
    Dom1.zarzadzajUrzadzeniem(Pralka1.idUrzadzenia, "OFF")
    Dom1.wyswietlStatusWszystkichUrzadzen()

    # Spróbuj dostosować poziom/wartość dla urządzeń implementujących IRegulowalne
    print("\nDostosowywanie poziomu temperatury lodówki:")
    Dom1.zarzadzajUrzadzeniem(Lodowka1.idUrzadzenia, "ON")
    Lodowka1.temperatura = 3.0

    # Wyświetl status ponownie, aby zobaczyć zmiany
    Dom1.wyswietlStatusWszystkichUrzadzen()

    #Wywołaj metody demonstrujące polimorfizm przez interfejsy
    print("\nDemonstracja polimorfizmu:")
    for urzadzenie in Dom1._listaUrzadzen:
        print(urzadzenie.pobierzSzczegolowyOpis())

if __name__ == "__main__":
    main()