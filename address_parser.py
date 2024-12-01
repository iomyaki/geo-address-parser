from string import digits

cyrillic = {
    "а", "б", "в", "г", "д", "е", "ж", "з", "и", "к", "л", "м", "н", "о", "п", "р", "с", "т", "у", "ф", "х", "ц", "ч",
    "ш", "щ", "э", "ю", "я"
}


def get_postcode(s: str, data: dict) -> None:
    for i in range(len(s) - 5):
        if s[i:i + 6].isdigit():
            data["индекс"] = s[i:i + 6]
            return


def get_country(s: str, data: dict) -> None:
    if "Россия" in s:
        data["страна"] = "Россия"
        return


def get_subject(s: str, data: dict) -> None:
    for city in ("москва", "петербург", "севастополь"):
        if city in s.lower():
            if city == "москва":
                data["субъект"] = "Москва"
                data["населённый пункт"] = "Москва"
            elif city == "петербург":
                data["субъект"] = "Санкт-Петербург"
                data["населённый пункт"] = "Санкт-Петербург"
            elif city == "севастополь":
                data["субъект"] = "Севастополь"
                data["населённый пункт"] = "Севастополь"
            data["тип субъекта"] = "город федерального значения"
            data["тип населённого пункта"] = "город"
            return

    for abbr in ("обл ", "обл.", " обл"):
        if abbr in s:
            temp = s.replace(abbr, "")
            temp = temp.split()
            for part in temp:
                if not part.isdigit():
                    data["субъект"] = part
                    data["тип субъекта"] = "область"
                    return

    for abbr in (" край", "край "):
        if abbr in s.lower():
            temp = s.replace(abbr, "")
            temp = temp.split()
            for part in temp:
                if not part.isdigit():
                    data["субъект"] = part
                    data["тип субъекта"] = "край"
                    return

    for abbr in (" Респ", "Респ.", "Респ ", " респ", "респ.", "респ "):
        if abbr in s:
            temp = s.replace(abbr, "")
            temp = temp.split()
            for part in temp:
                if not part.isdigit():
                    data["субъект"] = part
                    data["тип субъекта"] = "республика"
                    return


def get_settlement(s: str, data: dict) -> None:
    for abbr in ("г ", "г.", " г"):  # "г." is required because it can be merged with city name (w/o space)
        if abbr in s:
            temp = s.replace(abbr, "")
            temp = temp.split()
            data["населённый пункт"] = " ".join([part for part in temp if not part.isdigit()])
            data["тип населённого пункта"] = "город"
            return

    for abbr in ("пгт ", "пгт.", " пгт"):
        if abbr in s:
            data["населённый пункт"] = s.replace(abbr, "").strip()
            data["тип населённого пункта"] = "посёлок городского типа"
            return

    for abbr in ("рп ", " рп", "р. п.", "р.п.", "р. п", "р п.", "р.п", "рп.", "р п"):  # must be checked before "п."
        if abbr in s:
            data["населённый пункт"] = s.replace(abbr, "").strip()
            data["тип населённого пункта"] = "рабочий посёлок"
            return

    for abbr in ("п ", "п.", " п", "поселок", "посёлок"):
        if abbr in s and "респ" not in s.lower():
            data["населённый пункт"] = s.replace(abbr, "").strip()
            data["тип населённого пункта"] = "посёлок"
            return

    for abbr in ("д ", "д.", " д", "деревня"):
        if abbr in s:
            data["населённый пункт"] = s.replace(abbr, "").strip()
            data["тип населённого пункта"] = "деревня"
            return

    for abbr in ("аул ", " аул"):
        if abbr in s:
            data["населённый пункт"] = s.replace(abbr, "").strip()
            data["тип населённого пункта"] = "аул"
            return

    for abbr in ("с ", "с.", " с", "село"):  # handle also: "сельсовет"
        if abbr in s:
            data["населённый пункт"] = s.replace(abbr, "").strip()
            data["тип населённого пункта"] = "село"
            return

    for abbr in ("х ", "х.", " х", "хутор"):
        if abbr in s:
            data["населённый пункт"] = s.replace(abbr, "").strip()
            data["тип населённого пункта"] = "хутор"
            return

    for abbr in ("ст-ца", "ст-ца.", " ст", "станица"):
        if abbr in s:
            data["населённый пункт"] = s.replace(abbr, "").strip()
            data["тип населённого пункта"] = "станица"
            return

    if "сельсовет" in s:
        data["населённый пункт"] = s.replace("сельсовет", "").strip()
        data["тип населённого пункта"] = "сельсовет"
        return

    if "ж/д_ст" in s:
        data["населённый пункт"] = s.replace("ж/д_ст", "").strip()
        data["тип населённого пункта"] = "железнодорожная станция"
        return


def get_district(s: str, data: dict) -> None:
    if "р-н" in s:
        data["район"] = s.replace("р-н", "").strip()
        return


def get_street(s: str, data: dict) -> None:
    for abbr in ("ул ", "ул.", " ул"):
        if abbr in s:
            data["улица"] = s.replace(abbr, "").strip()
            data["тип улицы"] = "улица"
            return

    for abbr in ("пр-кт", "проспект"):
        if abbr in s:
            data["улица"] = s.replace(abbr, "").strip()
            data["тип улицы"] = "проспект"
            return

    for abbr in ("ш ", " ш", "ш.", "шоссе"):
        if abbr in s:
            data["улица"] = s.replace(abbr, "").strip()
            data["тип улицы"] = "шоссе"
            return

    for abbr in ("пл ", " пл", "пл.", "площадь"):
        if abbr in s:
            data["улица"] = s.replace(abbr, "").strip()
            data["тип улицы"] = "площадь"
            return

    for abbr in ("б-р", "бульвар"):
        if abbr in s:
            data["улица"] = s.replace(abbr, "").strip()
            data["тип улицы"] = "бульвар"
            return

    for abbr in ("наб ", "наб.", " наб"):
        if abbr in s:
            data["улица"] = s.replace(abbr, "").strip()
            data["тип улицы"] = "набережная"
            return


def get_house(s: str, data: dict) -> None:
    for abbr in ("зд ", "зд.", " зд", "здание"):  # must be checked before "д."
        if abbr in s:
            data["дом"] = s.replace(abbr, "").strip().upper()
            data["тип дома"] = "здание"
            return

    for abbr in ("д ", "д.", " д", "дом"):
        if abbr in s:
            data["дом"] = s.replace(abbr, "").strip().upper()
            data["тип дома"] = "дом"
            return

    if len(s) < 6 and all(c in {*cyrillic, *digits, "/"} for c in s.lower()):
        data["дом"] = s.upper()
        data["тип дома"] = "дом"
        return


def parse_address(address: str, data: dict) -> None:
    address_parts = address.split(",")
    mask = 0
    for part in address_parts:
        part = part.strip()

        if mask & (1 << 0) == 0:
            get_country(part, data)
            if data["страна"] is not None:
                mask ^= (1 << 0)

        if mask & (1 << 1) == 0:
            get_postcode(part, data)
            if data["индекс"] is not None:
                mask ^= (1 << 1)

        if mask & (1 << 2) == 0:
            get_subject(part, data)
            if data["субъект"] is not None:
                mask ^= (1 << 2)

        if mask & (1 << 4) == 0:
            get_settlement(part, data)
            if data["населённый пункт"] is not None:
                mask ^= (1 << 4)

        if mask & (1 << 6) == 0:
            get_district(part, data)
            if data["район"] is not None:
                mask ^= (1 << 6)

        if mask & (1 << 7) == 0:
            get_street(part, data)
            if data["улица"] is not None:
                mask ^= (1 << 7)

        if mask & (1 << 9) == 0:
            get_house(part, data)
            if data["дом"] is not None:
                mask ^= (1 << 9)


def main() -> None:
    """
    Known issues:
    • разделять номер дома и литеру;
    • после номера дома следует что-то ещё, без запятой или с нею (e.g. корпус, помещение);
    • лишние авторские приписки к названиям (e.g. «площадь им. Карла Маркса»).
    """

    data = {
        "страна": None,  # 0
        "индекс": None,  # 1
        "субъект": None,  # 2
        "тип субъекта": None,  # 3
        "район": None,  # 6
        "населённый пункт": None,  # 4
        "тип населённого пункта": None,  # 5
        "улица": None,  # 7
        "тип улицы": None,  # 8
        "дом": None,  # 9
        "тип дома": None,  # 10
    }

    parse_address(input(), data)
    for key, value in data.items():
        print(f"{key.capitalize()}: {value}")


if __name__ == "__main__":
    main()
