import time

class TimerManager:
    '''Класс для отслеживания времени работы'''
    def __init__(self):
        '''Инициализация'''
        self.startTime = 0
        self.endTime = 0
        self.workTime = 0

    def start(self) -> None:
        '''Устанавливает начальное время'''
        self.startTime = time.time()

    def end(self) -> None:
        '''Устанавливает конечное время'''
        self.endTime = time.time()
        self.workTime = self.endTime - self.startTime

    def getWorkTime(self, format :str = 'seconds', ndigits :int = None) -> int:
        '''Возвращает время в нужном формате'''
        time_units = {
            'seconds': 1,
            'minutes': 60,
            'hours': 3600
        }

        # Обработка ошибок
        if self.startTime == 0:
            raise ValueError('Для замера времени обязательно надо использовать метод "start" ДО выполнения кода')

        if self.endTime == 0:
            raise ValueError('Для замера времени обязательно надо использовать метод "stop" ПОСЛЕ выполнения кода')

        if format not in time_units:
            raise ValueError(f"Неподдерживаемый формат '{format}'. Должен быть один из {list(time_units.keys())}")

        # Округление результата
        if ndigits is None:
            return self.workTime / time_units[format]
        else:
            return round(self.workTime / time_units[format], ndigits=ndigits)
