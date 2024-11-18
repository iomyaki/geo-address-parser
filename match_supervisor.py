import re
import sys

import pandas as pd
from tqdm import tqdm
import xlwings as xw

'''
Step 0: Warning the user
'''

if input('The extension of the file is *.xlsx? (Enter/n) ').lower() == 'n' \
or input('Are ";" replaced with "," in the file? (Enter/n) ').lower() == 'n' \
or input('Is the column with addresses called "Адрес" in the file? (Enter/n) ').lower() == 'n' \
or input('Is the column with point IDs called "ID ТТ" in the file? (Enter/n) ').lower() == 'n':
    sys.exit('Careful next time!')  

'''
Step 1: Initialization
'''

# paths
file = ''
while len(file) == 0:
    file = input('Enter the name of the file (without ".xlsx"): ')

folder = 'C:\\Users\\myakinkovio\\Documents\\Рабочие файлы\\Finbox id168059697 id170096231\\'
reference = 'Справочник.xlsx'

# read files as dataframes
df = pd.read_excel(folder + file + '.xlsx')
ref = pd.read_excel(folder + reference)

# defining the first empty cell to write the data into
numOfCol = df.shape[1]
firstEmptyCell = ''

if numOfCol // 26 != 0:
    firstEmptyCell = chr(numOfCol // 26 + ord('A') - 1) + chr(numOfCol % 26 + ord('A')) + '1'
else:
    firstEmptyCell = chr(numOfCol % 26 + ord('A')) + '1'

# creating columns to fill
df['SETTLEMENT_INTRMDT'] = df['SETTLEMENT'] = df['SUBJECT'] = df['DIRECTORATE'] = df['MANAGER'] = df['MANAGER_ID'] = ''

# description for the progress bar
if 'агент' in file:
    entity = 'agent'
elif 'точ' in file:
    entity = 'store'
else:
    entity = 'row of the file'

'''
Step 2: Comparing the address with the reference file
'''

# defining the function that searches for the directorate and the manager in the reference
def searchdirecmanag(rowCount, entity):
    for ent in ref['SUBJECT' if entity == 'subject' else 'CITY']:
        if df.iloc[rowCount, df.columns.get_loc('SUBJECT' if entity == 'subject' else 'SETTLEMENT')] == ent:
        
            df.iloc[rowCount, df.columns.get_loc('DIRECTORATE')] = ref.iloc[ref.loc[ref['SUBJECT' if entity == 'subject' else 'CITY'] == ent].index[0], 1]
            if ref.iloc[ref.loc[ref['SUBJECT' if entity == 'subject' else 'CITY'] == ent].index[0], 2] != 'ВАКАНСИЯ':
                df.iloc[rowCount, df.columns.get_loc('MANAGER')] = ref.iloc[ref.loc[ref['SUBJECT' if entity == 'subject' else 'CITY'] == ent].index[0], 2]
            else:
                df.iloc[rowCount, df.columns.get_loc('MANAGER')] = ref.iloc[ref.loc[ref['SUBJECT' if entity == 'subject' else 'CITY'] == ent].index[0], 3]
            df.iloc[rowCount, df.columns.get_loc('MANAGER_ID')] = ref.iloc[ref.loc[ref['SUBJECT' if entity == 'subject' else 'CITY'] == ent].index[0], 3]
            
            if df.iloc[rowCount, df.columns.get_loc('SUBJECT')]:
                df.iloc[rowCount, df.columns.get_loc('SUBJECT')] = ''
            break

# main part: parsing through the every entity
counter = 0
for address in tqdm(df['Адрес'], desc=f'Parsing through the every {entity}'):
    splittedAddress = str(address).split(',')
    
    refCityUsed = False
    
    # >> the beginning of the address parsing
    # extracting a pair "settlement" + "subject" (needed bc one settlement's name can exist in two subjects)
    for elem in splittedAddress:
        # if the settlement's name has already been found, there's no need to flip through the address further
        if df.iloc[counter, df.columns.get_loc('SETTLEMENT_INTRMDT')] or df.iloc[counter, df.columns.get_loc('SETTLEMENT')]:
            break
        
        # extracting the settlement's name & searching for the settlement's name if needed
        if (' г'    in elem or 'г '      in elem or 'г.'      in elem
            or ' пгт'   in elem or 'пгт.'    in elem
            or ' п'     in elem or 'поселок' in elem or 'посёлок' in elem
            or ' р. п.' in elem or ' р.п.'   in elem or ' р. п'   in elem or ' р.п'      in elem or ' р п.' in elem or ' рп.' in elem or ' р п' in elem or ' рп' in elem
            or ' д'     in elem or 'деревня' in elem
            or 'аул'    in elem
            or ' с'     in elem or 'с.'      in elem or 'село'    in elem or 'сельсовет' in elem
            or ' х'     in elem or 'х.'      in elem or 'хутор'   in elem
            or ' ст-ца' in elem or 'ст-ца.'  in elem or ' ст'     in elem or 'станица'   in elem
            or 'ж/д_ст' in elem) \
        and not ' пр'  in elem and not ' пл'  in elem \
        and not ' кор' in elem and not ' р-н' in elem \
        and not ' пом' in elem and not ' пер' in elem \
        and not ' ул'  in elem and not ' б-р' in elem \
        and not ' обл' in elem and not 'Ханты-Мансийский' in elem:
            df.iloc[counter, df.columns.get_loc('SETTLEMENT_INTRMDT')] = elem
            break
        else:
            for city in ref['CITY']:
                if (re.search(city + '$', elem) or re.search(city + '\s', elem)) \
                and (' г'   in elem or 'г '      in elem or 'г.'      in elem or 'город'     in elem
                     or ' пгт'   in elem or 'пгт.'    in elem
                     or ' п'     in elem or 'п.'      in elem or 'поселок' in elem or 'посёлок' in elem
                     or ' р. п.' in elem or ' р.п.'   in elem or ' р. п'   in elem or ' р.п'      in elem or ' р п.' in elem or ' рп.' in elem or ' р п' in elem or ' рп' in elem
                     or ' д'     in elem or 'д.'      in elem or 'деревня' in elem
                     or 'аул'    in elem
                     or ' с'     in elem or 'с.'      in elem or 'село'    in elem or 'сельсовет' in elem
                     or ' х'     in elem or 'х.'      in elem or 'хутор'   in elem
                     or ' ст-ца' in elem or 'ст-ца.'  in elem or ' ст'     in elem or 'станица'   in elem
                     or 'ж/д_ст' in elem) \
                and not ' пр'  in elem and not ' пл'  in elem \
                and not ' кор' in elem and not ' р-н' in elem \
                and not ' пом' in elem and not ' пер' in elem \
                and not ' ул'  in elem and not ' б-р' in elem \
                and not ' обл' in elem and not 'Ханты-Мансийский' in elem:
                    refCityUsed = True
                    df.iloc[counter, df.columns.get_loc('SETTLEMENT')] = city
                    break # this is the break of the reference parsing, not of the address parsing
        
        # if the subject's name has already been found, there's no need to search for it in this part of an address
        if df.iloc[counter, df.columns.get_loc('SUBJECT')]:
            continue
        
        # searching for the subject's name
        for subj in ref['SUBJECT']:
            if (re.search(subj + '$', elem) or re.search(subj + '\s', elem)) \
            and not ' г'     in elem and not 'г.'      in elem \
            and not ' пгт'   in elem and not 'пгт.'    in elem \
            and not ' п'     in elem and not 'поселок' in elem and not 'посёлок'   in elem \
            and not ' р. п.' in elem and not ' р.п.'   in elem and not ' р. п'   in elem and not ' р.п'      in elem and not ' р п.' in elem and not ' рп.' in elem and not ' р п' in elem and not ' рп' in elem \
            and not ' д'     in elem and not 'д.'      in elem and not 'деревня' in elem \
            and not 'аул'    in elem \
            and not ' с'     in elem and not 'с.'      in elem and not 'село'    in elem and not 'сельсовет' in elem \
            and not ' х'     in elem and not 'х.'      in elem and not 'хутор'   in elem \
            and not ' ст-ца' in elem and not 'ст-ца.'  in elem and not ' ст'     in elem and not 'станица'   in elem \
            and not 'ж/д_ст' in elem \
            and not ' пр'  in elem and not ' пл'  in elem \
            and not ' кор' in elem and not ' р-н' in elem \
            and not ' пом' in elem and not ' пер' in elem \
            and not ' ул'  in elem and not ' б-р' in elem: # case: "Волгоградская ул."
                df.iloc[counter, df.columns.get_loc('SUBJECT')] = subj
                break # this is the break of the reference parsing, not of the address parsing
    # >> the end of the address parsing
                
    # clearing the settlement's name
    if not refCityUsed:
        finalNameList = []
        splittedSettl = df.iloc[counter, df.columns.get_loc('SETTLEMENT_INTRMDT')].split(' ')
        df.iloc[counter, df.columns.get_loc('SETTLEMENT_INTRMDT')] = '' # no longer needed
        for elem in splittedSettl:
            if len(elem) != 0 and not elem[0].islower() and not elem.isdigit():
                finalNameList.append(elem)
        df.iloc[counter, df.columns.get_loc('SETTLEMENT')] = ' '.join(finalNameList)
                   
    # looking for a matching pair "settlement" + "subject"
    if df.iloc[counter, df.columns.get_loc('SUBJECT')] and df.iloc[counter, df.columns.get_loc('SETTLEMENT')]: # if both fields are filled, otherwise no point
        refCounter = 0
        for subject in ref['SUBJECT']:
            if df.iloc[counter, df.columns.get_loc('SUBJECT')] == subject \
            and df.iloc[counter, df.columns.get_loc('SETTLEMENT')] == ref.iloc[refCounter, 4]:
                
                df.iloc[counter, df.columns.get_loc('DIRECTORATE')] = ref.iloc[refCounter, 1]
                if ref.iloc[refCounter, 2] != 'ВАКАНСИЯ':
                    df.iloc[counter, df.columns.get_loc('MANAGER')] = ref.iloc[refCounter, 2]
                else:
                    df.iloc[counter, df.columns.get_loc('MANAGER')] = ref.iloc[refCounter, 3]
                df.iloc[counter, df.columns.get_loc('MANAGER_ID')] = ref.iloc[refCounter, 3]
                
                df.iloc[counter, df.columns.get_loc('SUBJECT')] = ''
                break
                
            refCounter += 1
            
    # if the pair does not exist, only the subject will be searched
    # this is the case when the settlement is not in the reference, but the subject is
    # reference to be updated by new "settlement" + "subject" pairs when managers report mismatches
    # first manager found will be picked
    if (not df.iloc[counter, df.columns.get_loc('DIRECTORATE')] or not df.iloc[counter, df.columns.get_loc('MANAGER')]) and df.iloc[counter, df.columns.get_loc('SUBJECT')]:
        searchdirecmanag(counter, 'subject')
                        
    # if information still not found, only the settlement will be searched
    # this is the case when the settlement is in the reference, but there is no subject in the address
    # the one can also fix that by creating "settlement" + "%no subject%" pairs in the reference but it seems to be bulky
    # must go in this order bc one settlement's name can exist in two subjects
    if (not df.iloc[counter, df.columns.get_loc('DIRECTORATE')] or not df.iloc[counter, df.columns.get_loc('MANAGER')]) and df.iloc[counter, df.columns.get_loc('SETTLEMENT')]:
        searchdirecmanag(counter, 'settlement')
                    
    # the fourth case is when no subject nor settlement is in the address/found in the reference

    # finally, dealing with multiplicity — when there are more than one manager in a settlement
    
    storeID = df.iloc[counter, df.columns.get_loc('ID ТТ')]
    
    if storeID in {10000021774, 10000028437, 10000029669, 10000011408, 10000011958, 10000009879, 10000004310,
                   10000029679, 10000029682, 10000025855, 10000015039, 10000010794, 108753119, 22227729,
                   28076009, 28076007, 111765820, 116030488, 10000028714, 88326931, 10000011002,
                   10000010782, 10000011144, 10000003039, 67347564, 30398413, 94199335, 70256995,
                   118349070, 70256996, 119999454, 10000026742, 10000025366, 6675016, 115766402,
                   118918667, 115766438, 115766418, 108428133, 87976381, 118918657, 118918663,
                   118918666, 118918665, 107525651, 16213182, 40086092, 16212183, 70330235,
                   33646648, 91914576, 89349690, 10000016612, 98784674, 10000012797, 10000011426,
                   10000010050, 10000006295, 10000012798, 10000011427, 10000007084, 10000022343, 10000021380,
                   10000004876, 10000005827, 10000027128, 10000006049, 10000012226, 10000022632, 116030477,
                   10000017875, 10000008284, 10000054656, 10000021378, 10000004863, 10000004865, 10000025152,
                   10000004871, 10000004872, 10000004870, 10000004867, 10000025153, 10000056632, 10000056634,
                   10000005826, 10000027846, 10000027845}:
        
        # managers with more stores should be manually placed closer to the beginning —
        # as the probability is higher they gonna be the first and the script will work faster, presumably
        
        if storeID in {10000016612, 98784674, 10000012797, 10000011426, 10000010050, 10000006295, 10000012798,
                       10000011427, 10000007084, 10000022343, 10000021380, 10000004876, 10000005827, 10000027128,
                       10000006049, 10000012226, 10000022632, 116030477, 10000017875, 10000008284, 10000054656,
                       10000021378, 10000004863, 10000004865, 10000025152, 10000004871, 10000004872, 10000004870,
                       10000004867, 10000025153, 10000056632, 10000056634, 10000005826, 10000027846, 10000027845}:
            df.iloc[counter, df.columns.get_loc('MANAGER')] = 'Щенева Наталья Александровна'
            df.iloc[counter, df.columns.get_loc('MANAGER_ID')] = '004003'
            
        elif storeID in {67347564, 30398413, 94199335, 70256995, 118349070, 70256996, 119999454,
                         10000026742, 10000025366, 6675016, 115766402, 118918667, 115766438, 115766418,
                         108428133, 87976381, 118918657, 118918663, 118918666, 118918665, 107525651,
                         16213182, 40086092, 16212183, 70330235, 33646648, 91914576, 89349690}:
            df.iloc[counter, df.columns.get_loc('MANAGER')] = 'Ромашкина Дарья Александровна'
            df.iloc[counter, df.columns.get_loc('MANAGER_ID')] = '004002'
            
        elif storeID in {10000028714, 88326931, 10000011002, 10000010782, 10000011144, 10000003039}:
            df.iloc[counter, df.columns.get_loc('MANAGER')] = 'Кочанов-Сорокин Николай Артемович'
            df.iloc[counter, df.columns.get_loc('MANAGER_ID')] = '007007'
            
        elif storeID in {108753119, 22227729, 28076009, 28076007, 111765820, 116030488}:
            df.iloc[counter, df.columns.get_loc('MANAGER')] = 'Асеева Екатерина Сергеевна'
            df.iloc[counter, df.columns.get_loc('MANAGER_ID')] = '009008'
            
        elif storeID in {10000011408, 10000011958, 10000009879}:
            df.iloc[counter, df.columns.get_loc('MANAGER')] = 'Запрягаев Денис Сергеевич'
            df.iloc[counter, df.columns.get_loc('MANAGER_ID')] = '007004'
    
        elif storeID in {10000004310, 10000029679, 10000029682}:
            df.iloc[counter, df.columns.get_loc('MANAGER')] = 'Бучацких Евгений Александрович'
            df.iloc[counter, df.columns.get_loc('MANAGER_ID')] = '010001'
    
        elif storeID in {10000025855, 10000015039, 10000010794}:
            df.iloc[counter, df.columns.get_loc('MANAGER')] = 'Мочалова Людмила Викторовна'
            df.iloc[counter, df.columns.get_loc('MANAGER_ID')] = '011004'

        elif storeID == 10000021774:
            df.iloc[counter, df.columns.get_loc('MANAGER')] = 'Марьин Артем Викторович'
            df.iloc[counter, df.columns.get_loc('MANAGER_ID')] = '007008'
        
        elif storeID == 10000028437:
            df.iloc[counter, df.columns.get_loc('MANAGER')] = 'Матвеев Дмитрий Юрьевич'
            df.iloc[counter, df.columns.get_loc('MANAGER_ID')] = '003006'
        
        else: # if storeID == 10000029669:
            df.iloc[counter, df.columns.get_loc('MANAGER')] = 'Кутин Евгений Михайлович'
            df.iloc[counter, df.columns.get_loc('MANAGER_ID')] = '002015'

    counter += 1

'''
Step 3: Saving the result into the new *.csv file
'''

# load workbook
app = xw.App(visible=False)
wb = xw.Book(folder + file + '.xlsx')
ws = wb.sheets['Лист1']

# update workbook at specified range
ws.range(firstEmptyCell).options(index=False).value = df[['SETTLEMENT', 'DIRECTORATE', 'MANAGER', 'MANAGER_ID']]

# close workbook
wb.save()
wb.close()
app.quit()
