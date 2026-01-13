import os
import zipfile

class ZipManager:
    """        
    Параметр:
    - compression (str): 
        - 'none': Без сжатия
        - 'normal': Обычное сжатие
        - 'hard': Увеличенное сжатие
        - 'maximum': Максимальное сжатие
    """
    def __init__(self, compression :str = 'normal'):
        self.compression = self.setСompression(compression)

    def setСompression(self, compressionStr):
        if compressionStr == 'none':
            return zipfile.ZIP_STORED
        elif compressionStr == 'normal':
            return zipfile.ZIP_DEFLATED
        elif compressionStr == 'hard':
            return zipfile.ZIP_BZIP2
        elif compressionStr == 'maximum':
            return zipfile.ZIP_LZMA
        else:
            raise ValueError("Некорректное значение compression. Допустимы значения none, normal, hard, maximun")

    def zipFile(self, filePath:str, zipFilePath:str):
        """Архивируем один файл
        
        filePath (str): Путь к файлу, который нужно заархивировать
        zipFilePath (str): Путь к выходному ZIP-файлу
        """

        with zipfile.ZipFile(zipFilePath, 'w', compression=self.compression) as zipf:
            zipf.write(filePath, os.path.basename(filePath))

    def zipFolder(self, folderPath:str, zipFilePath:str):
        """Архивируем папку
        
        folderPath (str): Путь к папке, которую нужно заархивировать
        zipFilePath (str): Путь к выходному ZIP-файлу
        """

        with zipfile.ZipFile(zipFilePath, 'w', compression=self.compression) as zipf:
            baseName = os.path.basename(os.path.normpath(folderPath))
            for root, _, files in os.walk(folderPath):
                for file in files:
                    filePath = os.path.join(root, file)
                    arcname = os.path.join(baseName, os.path.relpath(filePath, folderPath))
                    zipf.write(filePath, arcname)
