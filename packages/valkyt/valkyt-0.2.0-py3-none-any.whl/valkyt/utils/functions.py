import jmespath
import shutil

from .directory import Dir
class Funct:

    @staticmethod
    def copy(source: str, destination: str) -> str:
        Dir.create_dir('/'.join(destination.split('/')[:-1]))
        destination: str = shutil.copy2(source=source, dst=destination)

        return destination
        ...
        
    @staticmethod
    def find(datas: list, value: str, key: str, **kwargs) -> dict:
        if not value:
            return datas
        try:
            for item in datas:
                if int(value) == int(item.get(key)):
                    return item
        except:
            for item in datas:
                if value.lower() in item.get(key).lower():
                    return item