import pandas as pd

from address_parser import parse_address


def main() -> None:
    df = pd.read_excel("List of agents_copy.xlsx")["Адрес"]
    for line in df:
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

        parse_address(line, data)
        for key, value in data.items():
            print(f"{key.capitalize()}: {value}")
        print()


if __name__ == "__main__":
    main()
