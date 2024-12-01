# «Причёсыватель адресов»

Парсер адресов (address_parser.py) выделит из географического адреса страну, почтовый индекс, название субъекта федерации и тип этого субъекта (область, республика, город федерального значения и др.), район, название населённого пункта и его тип (город, посёлок городского типа, деревня, село, аул и др.), название улицы и её тип (улица, проспект, бульвар, шоссе и др.) и номер дома, даже если в адресе отсутствует буква «д» и указан только его номер.

![image](https://github.com/user-attachments/assets/b29c7b13-c140-4352-a8f3-7620dbc53719)

Парсер обрабатывает только адреса Российской Федерации, написанные на русском языке. Все части будут помещены в словарь и выведены на экран в формате «ключ — значение» (ключи — на русском).

Чтобы использовать парсер, запустите address_parser.py и введите географический адрес в консоль. Работа скрипта на примерах демонстрируется в папке "check".

## match_supervisor.py
This script works with two files.
The first one is a main file. It's an *.xlsx with agents. Each agent has: 1) the address of their work; 2) an ID of a workplace.
The second file is a reference. Its structure is: 1) subject of the Russian Federation; 2) directorate of the bank which manages this subject; 3) manager that works in this directorate; 4) manager's ID; 5) a settlement which is curated by this manager.

The goal is to define the directorate and the manager for each agent in the first (main) file.

The difficulty is, all addresses are written a bit differently which makes the formalization a harsh task. For example, the address can start from the sity straightaway, omitting the subject.
My solution is to search for keywords (to be more precise, letters) in the address which indicate that this part of an address contains the name of the city or the region.

## Материалы по теме

- https://qna.habr.com/q/725517
- https://habr.com/ru/articles/192518/
- https://habr.com/ru/articles/573018/
- https://www.planetaexcel.ru/forum/?PAGE_NAME=read&FID=1&TID=118994&TITLE_SEO=118994-makros-dlya-parsinga-geograficheskikh-adresov
- https://github.com/nboravlev/Data_parsing
