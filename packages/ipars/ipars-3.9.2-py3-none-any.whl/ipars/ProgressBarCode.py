from progress.bar import Bar

class ProgressBarManager:
    '''Класс для создания прогресс-бара

    max: обязательный параметр, который указывает максимальное значение итераций в прогресс-баре
    message: сообщение перед прогресс-баром
    color: цвет прогресс-бара
    fill: заполнитель для сделанной части
    width: размер прогресс-бара в символах'''
    def __init__(self, max, message='Процесс работы', color='green', fill='#', width=32):
        self.bar = Bar(max=max, message=message, color=color, fill=fill, suffix='%(index)d/%(max)d (%(percent)d%%)', width=width)

    def next(self):
        '''Запускаем следущую итерацию прогресс-бара'''
        self.bar.next()

    def finish(self):
        '''Завершаем работу класса'''
        self.bar.finish()