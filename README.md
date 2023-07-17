# Бот напоминаниий (python-telegram-bot)

## Настройка перед работой
* Создать файл gs_creds.json с данными для доступа к GoogleSheets (см. gs_creds.example.json)
* Создать файл token.txt с токеном бота (см. token.example.txt)
* Создать файл manager_id.txt (см. manager_id.example.txt)
* В любом месте в документе GS в одну строку прописать заголовки столбцов(скопировать):
    - <code>tel_id
    - Текст
    - Дата(yyyy-mm-dd)
    - Время(hh:mm)
    - Ожидание(сек)
    - Ответ</code>
    
Бот самостоятельно найдёт эти заголовки и будет идти построчно вниз для отправки уведомлений.

## Взаимодействие с ботом
<code>/send</code> - для запуска отправки уведомлений

В документе необходимо указать нужные данные во всех столбцах, кроме столбца "Ответ". В "Ответ" будет дублироваться ответ на уведомление.

Пользователю tel_id прийдёт уведомление с кнопками "Выполнено" и "Не сделано". Ответ (или его остутствие) на полученное уведомление отправляется менеджеру, прописанному в manager_id.txt.

## Что я не успел сделать за отведённое под это задание время
* Ограничение для использования команды /send. В данной версии кода, запуск уведомлений может производить любой пользователь, а не только менеджер.
* Ограничить возможность ответа после истечения времени ожидания. В данной версии кода, пользователь может нажать кнопку с ответом даже после того, как уведомление было отмечено проигнорированным.
В таблице ответ поменяется, менеджер получит оба уведомления.
