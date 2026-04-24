# R4Bot-Module-Logger

Внешний модуль логирования для [R4Bot](https://github.com/Rarmash/R4Bot).

## Что делает
- логирует удалённые сообщения
- логирует отредактированные сообщения
- учитывает banned channels/users/categories из модульного конфига
- использует сервисы, полученные из `bot.r4_services`

## Конфиг
Базовый `accent_color` берётся из `servers.json`.

Специфичные поля logger хранятся в `config/modules/logger.json`.

Пример структуры:

```json
{
    "646322883555098644": {
        "log_channel": 952519133117960192,
        "bannedChannels": [647756597904408617],
        "bannedUsers": [184405311681986560],
        "bannedCategories": [938665995940274247, 1006910617833177118]
    }
}
```

## Требования
- R4Bot `>= 2.0`
- runtime context с `bot.r4_services`
- сервисы `config`, `firebase`, `module_config`

## Структура
- `module.json` — метаданные модуля
- `cog.py` — Discord cog
- `logger.example.json` — пример модульного конфига

## Установка в R4Bot
```powershell
python manage_modules.py install github:Rarmash/R4Bot-Module-Logger@master --enable
```
## Разработка
Для нормальной подсветки импортов в IDE и локальной проверки модуля рекомендуется установить зависимости:

```powershell
python -m pip install -r requirements.txt
```
