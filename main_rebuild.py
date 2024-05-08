from bs4 import BeautifulSoup
import requests
import json
import os
import re

HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "User_Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0"
}

URL = "https://dota2protracker.com/"
req = requests.get(URL, headers=HEADERS)
src = req.text

CONVERT_HERO_POS = {
    0:  "1",
    2: "2",
    4: "3",
    6: "4",
    8: "5"

}
POS_HERO = {
    1: 0,
    2: 2,
    3: 4,
    4: 6,
    5: 8
}
heroes_name_list = []
with open("heroes_name.txt", "r", encoding="utf-8") as file:
   for line in file:
       heroes_name_list.append(line.strip())

def hero_request():
    copy_list = []
    hero_info = input()
    words = re.findall(r'\w+', hero_info)

    for i in range(0, len(words)):
        if words[i].isalpha():
            copy_list.append(words[i])
    hero_name = " ".join(copy_list)
    if hero_name == "Nature s Prophet":
        hero_name = "Nature's Prophet"

    if not hero_name in heroes_name_list:
        print("Ошибка в записи")
        return hero_request()

    last_word = words[-1]
    if not last_word.isdigit() or int(last_word) not in range(1, 6):
        print("Ошибка в записи")
        return hero_request()

    return hero_name, last_word

def create_against_hero(*args): #hero_name, pos_value
    full_matchup_against_info_heroes = {}
    pos_value = int(args[1])
    local_name = args[0]

    if os.path.isdir(f"HeroWinRate/pos{pos_value}/{local_name}"):
        if os.path.exists(f"HeroWinRate/pos{pos_value}/{local_name}/full_matchup_against_info_heroes_{local_name}.json"):
            return

    req = requests.get(f"https://dota2protracker.com/hero/{local_name}/new", headers=HEADERS)
    src = req.text

    soup = BeautifulSoup(src, 'lxml')

    hero_against = soup.find_all('div', class_="flex flex-col mt-2 lg:w-1/2 matchup-table")
    if pos_value < len(hero_against):
        hero_info = hero_against[POS_HERO[pos_value]].find_all("div", attrs={"data-hero": True, "data-wr": True,
                                                                   "data-pos": True, "data-matches": True})
    else:
        print("Некорректное значение pos_value")
        return

    for item in hero_info:
        hero_data = [float(item['data-wr'][0:4]), item['data-matches']]
        if item['data-pos'][0:5] == "pos 1":
            if "pos1" not in full_matchup_against_info_heroes:
                full_matchup_against_info_heroes["pos1"] = {}
            full_matchup_against_info_heroes["pos1"].setdefault(item['data-hero'], []).extend(hero_data)
        elif item['data-pos'][0:5] == "pos 2":
            if "pos2" not in full_matchup_against_info_heroes:
                full_matchup_against_info_heroes["pos2"] = {}
            full_matchup_against_info_heroes["pos2"].setdefault(item['data-hero'], []).extend(hero_data)
        elif item['data-pos'][0:5] == "pos 3":
            if "pos3" not in full_matchup_against_info_heroes:
                full_matchup_against_info_heroes["pos3"] = {}
            full_matchup_against_info_heroes["pos3"].setdefault(item['data-hero'], []).extend(hero_data)
        elif item['data-pos'][0:5] == "pos 4":
            if "pos4" not in full_matchup_against_info_heroes:
                full_matchup_against_info_heroes["pos4"] = {}
            full_matchup_against_info_heroes["pos4"].setdefault(item['data-hero'], []).extend(hero_data)
        else:
            if "pos5" not in full_matchup_against_info_heroes:
                full_matchup_against_info_heroes["pos5"] = {}
            full_matchup_against_info_heroes["pos5"].setdefault(item['data-hero'], []).extend(hero_data)

    if not os.path.isdir(f"HeroWinRate/pos{pos_value}/{local_name}"):
        print("Создание директории")
        os.mkdir(f"HeroWinRate/pos{pos_value}/{local_name}", mode=0o777, dir_fd=None)

    if not os.path.exists(f"data/HeroWinRate/pos{pos_value}/{local_name}/full_matchup_against_info_heroes_{local_name}.json"):
        with open(f"HeroWinRate/pos{pos_value}/{local_name}/full_matchup_against_info_heroes_{local_name}.json",
                  'w', encoding="utf-8") as file:
            print("Создание json файла для against")
            json.dump(full_matchup_against_info_heroes, file, indent=4, ensure_ascii=False)

    full_matchup_against_info_heroes.clear()
def create_synergies_hero(*args): #hero_name, pos_value
    full_matchup_synergy_info_heroes = {}
    pos_value = int(args[1])
    local_name = args[0]

    if os.path.isdir(f"HeroWinRate/pos{pos_value}/{local_name}"):
        if os.path.exists(f"HeroWinRate/pos{pos_value}/{local_name}/full_matchup_synergy_info_heroes_{local_name}.json"):
            return

    req = requests.get(f"https://dota2protracker.com/hero/{local_name}/new", headers=HEADERS)
    src = req.text

    soup = BeautifulSoup(src, 'lxml')

    hero_synergy = soup.find_all('div', class_="flex flex-col mt-2 lg:w-1/2 matchup-table")
    if pos_value < len(hero_synergy):
        hero_info = hero_synergy[POS_HERO[pos_value] + 1].find_all("div", attrs={"data-hero": True, "data-wr": True,
                                                                   "data-pos": True, "data-matches": True})
    else:
        print("Некорректное значение pos_value")
        return

    for item in hero_info:
        hero_data = [float(item['data-wr'][0:4]), item['data-matches']]
        if item['data-pos'][0:5] == "pos 1":
            if "pos1" not in full_matchup_synergy_info_heroes:
                full_matchup_synergy_info_heroes["pos1"] = {}
            full_matchup_synergy_info_heroes["pos1"].setdefault(item['data-hero'], []).extend(hero_data)
        elif item['data-pos'][0:5] == "pos 2":
            if "pos2" not in full_matchup_synergy_info_heroes:
                full_matchup_synergy_info_heroes["pos2"] = {}
            full_matchup_synergy_info_heroes["pos2"].setdefault(item['data-hero'], []).extend(hero_data)
        elif item['data-pos'][0:5] == "pos 3":
            if "pos3" not in full_matchup_synergy_info_heroes:
                full_matchup_synergy_info_heroes["pos3"] = {}
            full_matchup_synergy_info_heroes["pos3"].setdefault(item['data-hero'], []).extend(hero_data)
        elif item['data-pos'][0:5] == "pos 4":
            if "pos4" not in full_matchup_synergy_info_heroes:
                full_matchup_synergy_info_heroes["pos4"] = {}
            full_matchup_synergy_info_heroes["pos4"].setdefault(item['data-hero'], []).extend(hero_data)
        else:
            if "pos5" not in full_matchup_synergy_info_heroes:
                full_matchup_synergy_info_heroes["pos5"] = {}
            full_matchup_synergy_info_heroes["pos5"].setdefault(item['data-hero'], []).extend(hero_data)

    if not os.path.isdir(f"HeroWinRate/pos{pos_value}/{local_name}"):
        print("Создание директории")
        os.mkdir(f"HeroWinRate/pos{pos_value}/{local_name}", mode=0o777, dir_fd=None)
    if not os.path.exists(f"HeroWinRate/pos{pos_value}/{local_name}/full_matchup_synergy_info_heroes_{local_name}.json"):
        with open(f"HeroWinRate/pos{pos_value}/{local_name}/full_matchup_synergy_info_heroes_{local_name}.json",
                  'w', encoding="utf-8") as file:
            print("Создание json файла для synergy")
            json.dump(full_matchup_synergy_info_heroes, file, indent=4, ensure_ascii=False)

    full_matchup_synergy_info_heroes.clear()

def count_average_values(*args): #hero_name, hero_pos, position
    hero_name = args[0]
    hero_pos = args[1]
    position = args[2]
    final_dict_synergy = {}
    with open(f"HeroWinRate/pos{hero_pos}/{hero_name}/full_matchup_synergy_info_heroes_{hero_name}.json", "r", encoding="utf-8") as file:
        dict_heroes_name = json.load(file)

    count_percent = 0
    count_matches = 0
    i = 1

    for item in heroes_name_list:
        try:
            count_percent += dict_heroes_name[f"pos{position}"][item][0]
            count_matches += int(dict_heroes_name[f"pos{position}"][item][1])
            i += 1
        except KeyError:
            pass

    for item in heroes_name_list:
        try:
            if (dict_heroes_name[f"pos{position}"][item][0] > count_percent / i)\
                    and (int(dict_heroes_name[f"pos{position}"][item][1]) > count_matches / i):
                final_dict_synergy[item] = [dict_heroes_name[f"pos{position}"][item][0],
                                            dict_heroes_name[f"pos{position}"][item][1]]

        except KeyError:
            pass
    return final_dict_synergy
def count_average_values_reverse(*args): #hero_name, hero_pos, position
    hero_name = args[0]
    hero_pos = args[1]
    position = args[2]

    final_dict_synergy = {}
    with open(f"HeroWinRate/pos{hero_pos}/{hero_name}/full_matchup_against_info_heroes_{hero_name}.json", "r", encoding="utf-8") as file:
        dict_heroes_name = json.load(file)

    count_percent = 0
    count_matches = 0
    i = 1
    for item in heroes_name_list:
        try:
            count_percent += dict_heroes_name[f"pos{position}"][item][0]
            count_matches += int(dict_heroes_name[f"pos{position}"][item][1])
            i += 1
        except KeyError:
            count_percent += 0
            count_matches += 0

    for item in heroes_name_list:
        try:
            if (dict_heroes_name[f"pos{position}"][item][0] < count_percent / i)\
                    and (int(dict_heroes_name[f"pos{position}"][item][1]) > count_matches / i):
                final_dict_synergy[item] = [dict_heroes_name[f"pos{position}"][item][0],
                                            dict_heroes_name[f"pos{position}"][item][1]]

        except KeyError:
            pass
    return final_dict_synergy

def compare_dict_for_heroes(**kwargs):
    first_dict = kwargs.get('first_dict', {})
    second_dict = kwargs.get('second_dict', {})

    if first_dict == {}:
        return second_dict
    if second_dict == {}:
        return first_dict

    first_list_keys = [key for key in first_dict if key in second_dict]
    second_list_keys = [key for key in second_dict if key in first_dict]

    result_list = [key for key in first_list_keys if key in second_list_keys]
    print(result_list)
    return result_list

def main_function():
    print("Введите имя первого героя и его позицию")
    first_hero_name = hero_request()
    create_against_hero(*first_hero_name)
    create_synergies_hero(*first_hero_name)

    print("Введите имя второго героя и его позицию")
    second_hero_name = hero_request()
    create_against_hero(*second_hero_name)
    create_synergies_hero(*second_hero_name)

    print("Введите имя первого вражеского героя")
    first_enemy_hero_name = hero_request()
    create_against_hero(*first_enemy_hero_name)
    create_synergies_hero(*first_enemy_hero_name)

    print("Введите имя второго вражеского героя")
    second_enemy_hero_name = hero_request()
    create_against_hero(*second_enemy_hero_name)
    create_synergies_hero(*second_enemy_hero_name)

    print("Для каких позиций подобрать героев?")
    hero_position = input()
    hero_position = hero_position.replace(" ", "")

    # print()
    # print(f"Синергия героев {hero_position[0]} позиции с {first_hero_name[0]} и {second_hero_name[0]}")
    # pprint.pprint(count_average_values(*first_hero_name, hero_position[0]))
    # print()
    # print(f"Синергия героев {hero_position[1]} позиции с {first_hero_name[0]} и {second_hero_name[0]}")
    # pprint.pprint(count_average_values(*first_hero_name, hero_position[1]))
    # print()
    # pprint.pprint(count_average_values_reverse(*second_hero_name, hero_position[1]))
    # print()
    # pprint.pprint(count_average_values_reverse(*second_enemy_hero_name, hero_position[1]))

    print(
        f"Список героев {hero_position[0]} позиции синергирующих с героями первого пика:"
        f" {first_hero_name[0]} позиции {first_hero_name[1]} и {second_hero_name[0]} позиции {second_hero_name[1]}")
    compare_dict_for_heroes(first_dict=count_average_values(*first_hero_name, hero_position[0]),
                            second_dict=count_average_values(*second_hero_name, hero_position[0]))
    print()
    print(
        f"Список героев {hero_position[1]} позиции синергирующих с героями первого пика:"
        f" {first_hero_name[0]} позиции {first_hero_name[1]} и {second_hero_name[0]} позиции {second_hero_name[1]}")
    compare_dict_for_heroes(first_dict=count_average_values(*first_hero_name, hero_position[1]),
                            second_dict=count_average_values(*second_hero_name, hero_position[1]))
    print()
    print(
        f"Список героев {hero_position[0]} позиции эффективных против вражеских героев первого пика:"
        f" {first_enemy_hero_name[0]} позиции {first_enemy_hero_name[1]} и {second_enemy_hero_name[0]} позиции {second_enemy_hero_name[1]}")
    compare_dict_for_heroes(first_dict=count_average_values_reverse(*first_enemy_hero_name, hero_position[0]),
                            second_dict=count_average_values_reverse(*second_enemy_hero_name, hero_position[0]))
    print()
    print(
        f"Список героев {hero_position[1]} позиции эффективных против вражеских героев первого пика:"
        f" {first_enemy_hero_name[0]}, {second_enemy_hero_name[0]} и {second_enemy_hero_name[0]} позиции {second_enemy_hero_name[1]}")
    compare_dict_for_heroes(first_dict=count_average_values_reverse(*first_enemy_hero_name, hero_position[1]),
                            second_dict=count_average_values_reverse(*second_enemy_hero_name, hero_position[1]))
    print()
    print(f"Результат объединения героев {hero_position[0]} позиции")
    val1 = compare_dict_for_heroes(
        first_dict=compare_dict_for_heroes(first_dict=count_average_values(*first_hero_name, hero_position[0]),
                            second_dict=count_average_values(*second_hero_name, hero_position[0])),
        second_dict=compare_dict_for_heroes(first_dict=count_average_values_reverse(*first_enemy_hero_name, hero_position[0]),
                            second_dict=count_average_values_reverse(*second_enemy_hero_name, hero_position[0])))
    print()
    print(f"Результат объединения героев {hero_position[1]} позиции")
    val2 = compare_dict_for_heroes(
        first_dict=compare_dict_for_heroes(first_dict=count_average_values(*first_hero_name, hero_position[1]),
                            second_dict=count_average_values(*second_hero_name, hero_position[1])),
        second_dict=compare_dict_for_heroes(first_dict=count_average_values_reverse(*first_enemy_hero_name, hero_position[1]),
                            second_dict=count_average_values_reverse(*second_enemy_hero_name, hero_position[1])))

    list = [1, 2, 3, 4, 5]
    list_hero = [first_hero_name[1], second_hero_name[1], hero_position[0], hero_position[1]]

    for item in list:
        if str(item) not in list_hero:
            print("Герой последней позиции")
            print(item)
            last_hero_position = item

    print(f'Введите имя героя второго пика и его позицию')
    third_hero = hero_request()
    create_against_hero(*third_hero)
    create_synergies_hero(*third_hero)
    print(f'Введите имя второго героя второго пика и его позицию')
    fourth_hero = hero_request()
    create_against_hero(*fourth_hero)
    create_synergies_hero(*fourth_hero)

    create_against_hero(*third_hero)
    create_synergies_hero(*fourth_hero)

    print(f'Введите имя вражеского героя второго пика и его позицию')
    third_enemy_hero = hero_request()
    create_against_hero(*third_enemy_hero)
    create_synergies_hero(*third_enemy_hero)
    print(f'Введите имя второго вражеского героя второго пика и его позицию')
    fourth_enemy_hero = hero_request()
    create_against_hero(*fourth_enemy_hero)
    create_synergies_hero(*fourth_enemy_hero)

    print(f"Список героев {last_hero_position} позиции синергирующих с героями второго пика:"
          f" {third_hero[0]} позиции {third_hero[1]} и {fourth_hero[0]} позиции {fourth_hero[1]}")
    compare_dict_for_heroes(first_dict=count_average_values(*third_hero, last_hero_position),
                            second_dict=count_average_values(*fourth_hero, last_hero_position))
    print()
    print(f"Список героев {last_hero_position} позиции эффективных против вражеских героев второго пика:"
          f" {third_enemy_hero[0]} позиции {third_enemy_hero[1]} и { fourth_enemy_hero[0]} позиции {fourth_enemy_hero[1]}")
    compare_dict_for_heroes(first_dict=count_average_values_reverse(*third_enemy_hero, last_hero_position),
                            second_dict=count_average_values_reverse(*fourth_enemy_hero, last_hero_position))
    print()
    print(f"Результат объединения героев {last_hero_position} позиции")
    val1 = compare_dict_for_heroes(first_dict=count_average_values(*third_hero, last_hero_position),
                            second_dict=count_average_values(*fourth_hero, last_hero_position))
    val2 = compare_dict_for_heroes(first_dict=count_average_values_reverse(*third_enemy_hero, last_hero_position),
                            second_dict=count_average_values_reverse(*fourth_enemy_hero, last_hero_position))
    compare_dict_for_heroes(first_dict=val1, second_dict=val2)

if __name__ == "__main__":
   main_function()

