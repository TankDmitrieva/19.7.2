from app import PetFriends
from settings import valid_email, valid_password, invalid_email, invalid_password
import os
import pytest
pf = PetFriends()


class Testapipf:
    def test_auth_key_key_for_valid_user(self, email=valid_email, password=valid_password):
        """Проверяем что запрос api ключа возвращает статус 200 и в тезультате содержится слово key"""

        # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
        status, result = pf.get_api_key(email, password)

        # Сверяем полученные данные с нашими ожиданиями
        assert status == 200
        assert 'key' in result

    def test_get_all_pets_with_valid_key(self, filter=''):
        """Проверяем что запрос всех питомцев возвращает не пустой список и код ответа 200.
        Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее используя этого ключ
        запрашиваем список всех питомцев и проверяем что список не пустой.
        Доступное значение параметра filter - 'my_pets' либо ''"""

        _, auth_key = pf.get_api_key(valid_email, valid_password)
        status, result = pf.get_list_of_pets(auth_key, filter)

        assert status == 200
        assert len(result['pets']) > 0

    def test_add_new_pet_with_valid_data(self, name='Барбос', animal_type='двортерьер', age='4',
                                         pet_photo='pictures/pet1.jpg'):
        """Проверяем что можно добавить питомца с корректными данными"""

        # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
        pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

        # Запрашиваем ключ api и сохраняем в переменую auth_key
        _, auth_key = pf.get_api_key(valid_email, valid_password)

        # Добавляем питомца
        status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

        # Сверяем полученный ответ с ожидаемым результатом
        assert status == 200
        assert result['name'] == name

    def test_successful_delete_self_pet(self):
        """Проверяем возможность удаления питомца"""

        # Получаем ключ auth_key и запрашиваем список своих питомцев
        _, auth_key = pf.get_api_key(valid_email, valid_password)
        _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')

        # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
        if len(my_pets['pets']) == 0:
            pf.add_new_pet(auth_key, 'Суперкот', 'кот', '3', 'images/pet1.jpg')
            _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')

        # Берём id первого питомца из списка и отправляем запрос на удаление
        pet_id = my_pets['pets'][0]['id']
        status, _ = pf.delete_pets(auth_key, pet_id)

        # Ещё раз запрашиваем список своих питомцев
        _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')

        # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
        assert status == 200
        assert pet_id not in my_pets.values()

    def test_successful_update_self_pet_info(self, name='Мурзик', animal_type='Котэ', age='5'):
        """Проверяем возможность обновления информации о питомце"""

        # Получаем ключ auth_key и список своих питомцев
        _, auth_key = pf.get_api_key(valid_email, valid_password)
        _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')

        # Еслди список не пустой, то пробуем обновить его имя, тип и возраст
        if len(my_pets['pets']) > 0:
            status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

            # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
            assert status == 200
            assert result['name'] == name
        else:
            # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
            raise Exception("There is no my pets")

    # 1
    def test_add_pet_with_valid_data_without_photo(self, name='Kotbezphoto', animal_type='кот', age='6'):
        """Проверяем возможность добавления нового питомца без фото"""

        # Получаем ключ auth_key
        _, auth_key = pf.get_api_key(valid_email, valid_password)

        # Добавляем нового питомца без фото
        status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)

        # Сверяем полученный ответ с ожидаемым результатом
        assert status == 200
        assert result['name'] == name

    # 2
    def test_add_photo_at_pet(self, pet_photo='pictures/pet11.jpg'):
        """Проверяем возможность добавления новой фотографии существующего питомца"""
        # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
        pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

        # Получаем ключ auth_key и список своих питомцев
        _, auth_key = pf.get_api_key(valid_email, valid_password)
        _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')

        # Если есть питомцы, то берем первого и меняем ему фотографию
        if len(my_pets['pets']) > 0:
            status, result = pf.add_photo_of_pet(auth_key, my_pets['pets'][0]['id'], pet_photo)

            # Получаем снова список питомцев
            _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')

            # Проверяем что код ответа 200 и что фото у 1го питомца обновлено
            assert status == 200
            assert result['pet_photo'] == my_pets['pets'][0]['pet_photo']
        else:
            # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
            raise Exception("Питомцы отсутствуют")

    # 3
    def test_add_pet_with_photo_negative_age(self, name='Negativcat', animal_type='cat', age='-3',
                                             pet_photo='pictures/pet1.jpg'):
        """Проверка что нельзя добавить питомца с отрицательным возрастом. Тест не пройден если удалось добавить"""
        # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
        pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

        # Получаем ключ auth_key
        _, auth_key = pf.get_api_key(valid_email, valid_password)
        # Добавляем нового питомца с некорректным возрастом
        _, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
        # Проверяем что питомец успешно добавлен. В этом случае тест выдаст failed. По идее не должно быть возраста < 0
        # на будущее - нужно добавить проверку входных данных в методы класса.
        assert age not in result['age'], 'Питомец добавлен на сайт с отрицательным числом в поле возраст'

    # 4
    def test_add_pet_with_photo_with_big_age(self, name='Oldcat', animal_type='cat', age='134',
                                             pet_photo='pictures/pet1.jpg'):
        """Добавление питомца с числом более 100 в переменной age.
        Тест не будет пройден ели питомец будет добавлен на сайт с числом превышающим 100 в поле возраст."""
        # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
        pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

        # Получаем ключ auth_key
        _, auth_key = pf.get_api_key(valid_email, valid_password)

        # добавляем нового питомца
        _, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
        number = int(result['age'])
        # Проверяем что нельзя добавить питомца с нереалистичным возрастом
        assert number < 100, 'Питомец добавлен на сайт с числом превышающим 100 в поле возраст'

    # 5
    def test_add_pet_with_empty_name(self, name='', animal_type='cat', age='2', pet_photo='pictures/pet1.jpg'):
        """Проверяем возможность добавления питомца с пустым значением в переменной name
        Тест не будет пройден если питомец будет добавлен на сайт с пустым значением в поле "имя\""""
        # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
        pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

        # Получаем ключ auth_key
        _, auth_key = pf.get_api_key(valid_email, valid_password)

        # добавляем нового питомца
        status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

        # Проверяем результат запроса и какое значение было в поле name
        assert status == 200
        assert result['name'] != '', 'Питомец добавлен на сайт с пустым значением в имени'

    # 6
    def test_add_pet_with_illegal_characters_in_animal_type(self, name='Illegalcat', animal_type='Ca2t%@', age='3',
                                                            pet_photo='pictures/pet11.jpg'):
        """Добавление питомца с символами или числами вместо букв в переменной animal_type.
        Тест не будет пройден если питомец будет добавлен на сайт с спец.символами или числами вместо букв в поле
        animal_type.
        """
        # Создаем массив запретных символов
        symbols = '#$%^&*{}|?/><=+_~@1234567890'
        symbol = []

        # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
        pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

        # Получаем ключ auth_key
        _, auth_key = pf.get_api_key(valid_email, valid_password)

        # добавляем нового питомца
        status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

        # Проверяем код ответа. Из ответа выбираем поле animal_type и ищем в нем запретыные символы. если находим то
        # добавляем в массив symbol. Если по итогу массив не пустой то тест не пройден
        assert status == 200
        for i in symbols:
            if i in result['animal_type']:
                symbol.append(i)
        assert symbol[0] not in result['animal_type'], 'Питомец добавлен с недопустимыми символами в поле animal_type'

    # 7
    def test_add_pet_with_illegal_characters_in_name(self, name='Illegalcat2!', animal_type='Cat', age='3',
                                                     pet_photo='pictures/pet11.jpg'):
        """Добавление питомца с символами или числами вместо букв в имени.
        Тест не будет пройден если питомец будет добавлен на сайт с спец.символами или числами вместо букв в имени.
        """
        # Создаем массив запретных символов и массив в который будем складывать найденные запретные символы
        symbols = '#$%^&*{}|?/><=+_~@1234567890'
        symbol = []

        # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
        pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

        # Получаем ключ auth_key
        _, auth_key = pf.get_api_key(valid_email, valid_password)

        # добавляем нового питомца
        status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

        # Проверяем код ответа. Из ответа выбираем поле animal_type и ищем в нем запретыные символы. если находим то
        # добавляем в массив symbol. Если по итогу массив не пустой то тест не пройден
        assert status == 200
        for i in symbols:
            if i in result['name']:
                symbol.append(i)
        assert symbol[0] not in result['name'], 'Питомец добавлен с недопустимыми символами в поле name'

    # 8
    def test_get_auth_key_with_wrong_password_and_correct_mail(self, email=valid_email, password=invalid_password):
        """Проверяем запрос с невалидным паролем и с валидным емейлом.
        Проверяем нет ли ключа в ответе"""
        status, result = pf.get_api_key(email, password)
        assert status == 403
        assert 'key' not in result

    # 9
    def test_get_auth_key_with_wrong_email_and_correct_password(self, email=invalid_email, password=valid_password):
        """Проверяем запрос с невалидным паролем и с валидным емейлом.
        Проверяем нет ли ключа в ответе"""
        status, result = pf.get_api_key(email, password)
        assert status == 403
        assert 'key' not in result

    # 10
    def test_add_photo_to_illegal_pet(self, pet_photo='pictures/pet11.jpg'):
        """Проверяем возможность добавления новой фотографии несуществующего питомца"""
        # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
        pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

        # Получаем ключ auth_key, получаем список питомцев (чтобы убедиться что они вообще есть) и
        # создаем несуществующий pet_id
        _, auth_key = pf.get_api_key(valid_email, valid_password)
        _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')
        pet_id = 'sadf1532#$'

        # Если есть питомцы, то берем питомца с несуществующим pet_id и меняем ему фотографию
        if len(my_pets['pets']) > 0:
            status, result = pf.add_photo_of_pet(auth_key, pet_id, pet_photo)

            # Проверяем что код ответа 400 что говорит о некорректно введенных данных
            assert status == 400
        else:
            # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
            raise Exception("Питомцы отсутствуют")



