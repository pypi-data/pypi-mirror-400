## Библиотека для работы с файлами во время парсинга

Во время парсинга часто приходится скачивать html-страницы, работать с json- и csv-файлами. Эта библиотека призвана облегчить написание кода для такого рода задач, а так же предоставляет ряд дополнительных возможностей.

Более удобная версия документации на сайте ([ru](https://iliamiheev.github.io/ipars-doc/#/./home), [en](https://iliamiheev.github.io/ipars-doc/#/./pages/en/README_EN))

#### В библиотеке есть три класса для основных работ:

1. **Pars** для работы с запросами и bs4
2. **JsonManager** для работы с json
3. **CsvManager** для работы с csv

### Так же есть три вспомогательных класса

1. **ProgressBarManager** для создания прогресс-баров
2. **TimerManager** для засечения времени выполнения определённого кода
3. **ZipManager** для архивации файлов и папок

### Установить библиотеку:

```bash
pip install ipars
```

или

```bash
pip3 install ipars
```

## Навигация

- [Работа с Pars](#работа-с-pars)
  - [Коротко о методах](#коротко-о-методах-pars)
  - [Пример использования класса Pars](#пример-использования-класса-pars)
  - [Пример использования методов getAttributes и getTexts](#пример-использования-методов-getattributes-и-gettexts)
- [Работа с JsonManager](#работа-с-jsonmanager)
  - [Коротко о методах](#коротко-о-методах-jsonmanager)
  - [Пример использования](#пример-использования-jsonmanager)
- [Работа с CsvManager](#работа-с-csvmanager)
  - [Коротко о методах](#коротко-о-методах-csvmanager)
  - [Пример использования](#пример-использования-csvmanager)
- [Работа с ProgressBarManager](#работа-с-progressbarmanager)
  - [Коротко о методах](#коротко-о-методах-progressbarmanager)
  - [Пример использования](#пример-использования-progressbarmanager)
- [Работа с TimerManager](#работа-с-timermanager)
  - [Коротко о методах](#коротко-о-методах-timermanager)
  - [Пример использования](#пример-использования-timermanager)
- [Работа с ZipManager](#работа-с-zipmanager)
  - [Коротко о методах](#коротко-о-методах-zipmanager)
  - [Пример использования](#пример-использования-zipmanager)

### Работа с Pars

Данный класс предназначен для работы с запросами и полученной html-страницей.

Класс Pars не принимает никаких данных для конструкторов.

```python
from ipars import Pars

p = Pars()
```

### Коротко о методах Pars:

- Метод **getStaticPage** принимает url страницы, путь по которому сохранится страница, метод записи и заголовки запроса. Метод записи «wb» используется для сохранения картинок, по умолчанию writeMethod установлен как «w», что используется для html-страниц. Если заголовки запросов не указаны, то будут использоваться заголовки со случайным user-agent. Метод возвращает статус ответа сайта, его можно использовать для проверкок.

```python
for index, url in enumerate(urlList):
    if p.getStaticPage(url, f'./page{index}') == 404:
        print('Не удалось получить страницу: ', url)
```

- Метод **getDynamicPage** с помощью библиотеки Selenium получает динамически обновляемую страницу. Это помогает, когда контент на странице подгружается динамически. Принимает url страницы, путь сохранения, closeWindow и timeSleep. По умолчанию браузер Selenium открывается в фоновом режиме, и работу браузера не видно, но если closeWindow указать как False, то будет виден процесс выполнения кода. С помощью timeSleep можно увеличить время загрузки страницы если контент на ней долго подгружается

- Метод **gpsa** (get page semi-automatically) похож на метод getDynamicPage, но работает в полуавтоматическом режиме. Он открывает страницу сайта и ждёт пока не будет нажат Enter в терминале. В этот момент можно зарегистрироваться на сайте и/или перейти на нужную вкладку сайта, после чего нажать Enter и метод спарсит страницу. Подходит для лент соцсетей, где неавторизованным пользователям контент ограничен. Принисает такие же аргументы для таких же целей, что и getDynamicPage, за исключением closeWindow

- Метод **returnBs4Object** возвращает объект beautifulsoup4. Принимает путь до html-страницы, содержимое которой преобразует в объект beautifulsoup, кодировку открытия файла (по умолчанию UTF-8) и тип парсера (по умолчанию lxml).

- Метод **getAttributes** нужена чтобы получить список атрибутов из списка объектов bs4. Принимает список объектов bs4 и название атрибута который будет извлекаться из элементов списка

- Метод **getTexts** нужена чтобы получить список текста из списка объектов bs4. Принимает список объектов bs4 и параметр needFix. Если этот параметр установлен как True, то из текста будут удалены \n, \t и пробелы с концов

- Метод **pprint** используется для вывода значений переменных у которых большая вложеность. Например, если у Вас есть массив объектов, где в качестве значения ключа используется другой массив объектов

- Метод **mkdir** используется для создания папки с именем _nameDir_ если она ещё не существует

- Метод **listdir** используется для получения списка файлов и папок в указанной директории

- Метод **exists** используется для проверки наличия файла или папки

### Пример использования класса Pars:

```py
# О классе ProgressBarManager читай ниже
from ipars import Pars, ProgressBarManager
p = Pars()
nameFile = 'index.html'
nameFolder = 'img'

def main():
	# Получаем html страницу
	p.getDynamicPage(nameFile, 'https://duckduckgo.com/?q=теплица+социальных+технологий+youtube&iar=videos&atb=v454-1', closeWindow=False, timeSleep=5)

    # Получаем объект BautifullSoup
    soup = p.returnBs4Object(nameFile)

    # Находим все карточки ответов
    # Первые результаты выдачи те что хотелось получить, а остальные нет. Поэтому нам желательно получить первые 84 элемента
    locator = 'b_NgmZrVnRtV8MZMEjLs'
    allCards = soup.find_all(class_=locator)[:84]
    if len(allCards) == 0:
        print(f'''Something went wrong. Here is a list of possible causes:
        1) DuckDuckGo has changed the class for video cards. The code uses the locator "{locator}"
        2) The site did not load. Try increasing the timeSleep parameter or make a request later.''')
        return

    # Получаем все изображения
    allImg = [card.find('img') for card in allCards]

    # Получаем все ссылки
    allSrc = p.getAttributes(allImg, 'src')

    # Создаём папку img если её ещё нет
    p.mkdir(nameFolder)

    # Создаём объект ProgressBarManager
    bar = ProgressBarManager(len(allSrc))

    # Скачиваем картинки
    for index, url in enumerate(allSrc):
        url = 'https:' + url
        p.getStaticPage(f'./{nameFolder}/img{index}.png', url, writeMethod='wb')
        bar.next()
    bar.finish()

    # Смотрим что появилось в папке img
    p.pprint(p.listdir(nameFolder))

if __name__=='__main__':
    main()
```

### Пример использования методов _getAttributes_ и _getTexts_

```py
from ipars import Pars
p = Pars()
nameFile = 'index.html'

p.getStaticPage(nameFile, 'https://google.com')
soup = p.returnBs4Object(nameFile)

allTegA = soup.find_all('a')
a1 = p.getTexts(allTegA, needFix=1)
p.pprint(a1)

a2 = p.getAttributes(allTegA, 'href')
p.pprint(a2)
```

### Работа с JsonManager

Данный класс предназначен для записи и извлечения информации из json-файлов.

JsonManager принимает принимает только encoding — кодировку в которой будут читаться файлы (по умолчанию UTF-8)

```py
from ipars import JsonManager

j = JsonManager(encoding="UTF-8")
```

### Коротко о методах JsonManager

- Метод **load** используется для получения данных из json-файла по указанному пути

- Метод **dump** используется для записи данных в json-файл. Принимает путь до файла и данные для записи

- Метод **pprint** такой же как и у Pars

### Пример использования JsonManager

```py
from ipars import JsonManager
j = JsonManager()
nameFile = 'data.json'

# Записываем данные
j.dump(nameFile, [1, 2, 3, 4, 5, 6, 7])

# Получаем данные
data = j.load(nameFile)
j.pprint(data) # [1, 2, 3, 4, 5, 6, 7]
```

### Работа с CsvManager

Данный класс предназначен для записи и извлечения информации из csv-файлов.

Класс CsvManager принимает три аргумента:

- newline — символ переноса на новую строку (по умолчанию используется пустая строка)

- encoding — кодировка открываемых файлов (UTF-8)

- delimiter — разделитель который используется в csv файле (;)

```py
from ipars import CsvManager

c = CsvManager(newline="", encoding="UTF-8", delimiter=";")
```

### Коротко о методах CsvManager

- Метод **writerow** записывает строку с csv файл. Метод принимает путь до csv файла, метод записи и список данных которые будут записанн в строку файла

- Метод **writerows** принимает теже самые аргументы что и writerow, только row должен быть двойным списком с данными для записи. Разница между этими методами в том что writerow записывает одну строку, а writerows столько сколько есть в двойном списке

- Метод **getRows** используется для получения списка строк в csv файле. Метод принимает путь до файла откуда будут получены строки

- Метод **pprint** такой же как и у Pars

### Пример использования CsvManager

```py
from ipars import CsvManager
c = CsvManager()
nameFile = 'data.csv'

# записываем заголовки
c.writerow(nameFile, 'w', ['Количество', 'Цена', 'Итог'])

# записываем данные
c.writerows(nameFile, 'a', [
    ["5", "5", "25"],
    ["6", "6", "36"],
    ["7", "7", "49"],
])

# получаем строки из таблицы
rows = c.getRows(nameFile)

# выводим строки таблицы
c.pprint(rows)
```

### Работа с ProgressBarManager

Класс создаёт прогресс-бар для для отображения процесса выполнения кода. Принимает пять аргументов:

- **max**: обязательный параметр, который указывает максимальное значение итераций в прогресс-баре

- **message**: сообщение перед прогресс-баром

- **color**: цвет прогресс-бара

- **fill**: заполнитель для выполненой части

- **width**: размер прогресс-бара в символах

```py
from ipars import ProgressBarManager

bar = ProgressBarManager(100) # Здесь max установлен как 100
```

### Коротко о методах ProgressBarManager

- Метод **next** запускает следущую итерацию прогресс-бара

- Метод **finish** завершает работу прогресс-бара

### Пример использования ProgressBarManager

```py
# Импортируем библиотеки
from ipars import ProgressBarManager
from time import sleep

maxValue = 300
# Создаём прогресс-бар по умолчанию
bar = ProgressBarManager(maxValue)

# Имитируем работу
for _ in range(maxValue//2):
    sleep(0.1)
    bar.next()

# Выключаем прогресс-бар
bar.finish()



# Создаём более кастомизированный прогресс-бар
bar = ProgressBarManager(
    maxValue,
    message='Процесс скачивания',
    color='red',
    fill='*',
    width=50
)

# Имитируем работу
for _ in range(maxValue):
    sleep(0.1)
    bar.next()

# Выключаем прогресс-бар
bar.finish()
```

### Работа с TimerManager

Класс TimerManager предназначен для отслеживания времени выполнения кода. Он позволяет получить общее время работы в различных форматах.

```py
from ipars import TimerManager

t = TimerManager()
```

### Коротко о методах TimerManager

- Метод **start** — точка начала отсчёта времени

- Метод **end** — конечная точка отсчёта времени

- Метод **getWorkTime** возвращает общее время работы в указанном формате. Поддерживаемые форматы: _seconds_, _minutes_, _hours_. Параметр _ndigits_ указывает количество знаков после запятой для округления, по умолчанию число не округляется.

### Пример использования TimerManager

```py
from time import sleep
from ipars import TimerManager
t = TimerManager()

# Засекаем время
t.start()
sleep(2) # имитация двухсекундной работы
t.end()

# Выводим результат в разных форматах
print(f"Время работы в секундах: {t.getWorkTime()}")                           # 2.0008320808410645
print(f"Время работы в минутах: {t.getWorkTime(ndigits=2, format='minutes')}") # 0.03
print(f"Время работы в часах: {t.getWorkTime(ndigits=4, format='hours')}")     # 0.0006
```

### Работа с ZipManager

Класс ZipManager нужен для архивации папоки файлов. Он принимает принимает только один аргумент — один из возможных уровней сжатия:

- none — без сжатия

- normal — обычное сжатие

- hard — увеличенное сжатие

- maximum — максимальное сжатие

```py
from ipars import ZipManager

z = ZipManager()
```

### Коротко о методах ZipManager

- Метод **zip_file** используется для архивирования одного файла. Принимает путь до исходного файла и путь выходного файла

- Метод **zip_folder** используется для архивирования каталога. Принимает путь до исходного каталога и путь выходного файла

### Пример использования ZipManager

```py
from ipars import ZipManager
z = ZipManager(compression='maximum')

z.zip_file('./your_file.txt', 'file_archive_maximum.zip')
z.zip_folder('./your_folder/', 'folder_archive_maximum.zip')
```

Если ты дочитал(-а) документацию до конца, то получай пожизненный запас здоровья ❤. Помни, оно у тебя одно.

+999999 HP
