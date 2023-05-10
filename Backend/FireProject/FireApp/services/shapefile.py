
''' Номер ТВВ, географические координаты,  и температура в K. наверное это будем минимум из достаточного '''
import datetime
import os
import pathlib
import fiona
import shapely.wkt
from shapely.geometry import mapping

from FireApp.services.archive import Archiving


class Base:
    def __init__(self, subject_tag, date_time, operator_fio=None, cloud_shielding=None):
        self.subject_tag = subject_tag.upper()
        self.date_time = datetime.datetime.strptime(date_time, '%Y-%m-%dT%H:%M:%S')
        self.cloud_shielding = cloud_shielding
        self.operator_fio = operator_fio

    def make_file_name(self, is_dir=False, is_shp=False):
        if is_dir:
            if self.operator_fio and self.cloud_shielding and not is_shp:
                return f'{self.subject_tag}_{self.get_date("")}_{self.get_time("_")}{self.satellites}_{self.cloud_shielding}_{self.operator_fio.replace(" ", "_")}'
            else:
                return f'{self.subject_tag}_{self.get_date("")}_{self.get_time("_")}{self.satellites}'
        else:
            return f'{self.subject_tag}_{self.get_date("")}{self.satellites}_{self.get_time(delimiter="_", only_minutes_and_hours=True)}'

    def get_time(self, delimiter=':', only_minutes_and_hours=False, only_hour=False):
        if only_minutes_and_hours:
            return self.date_time.strftime(f"%H{delimiter}%M")
        elif only_hour:
            return self.date_time.strftime(f'%H')
        else:
            return self.date_time.strftime(f"%H{delimiter}%M{delimiter}%S")

    def get_date(self, delimiter='-'):
        return self.date_time.strftime(f"%Y{delimiter}%m{delimiter}%d")

    def make_dir(self, dir):
        pathlib.Path(dir).mkdir(parents=True, exist_ok=True)

    def is_exist_file(self, path):
        if not os.path.exists(path):
            return False
        return True

    def get_path_to_file(self):
        return self.path_to_file


class ShpFile(Base):

    schema = {
        'geometry': 'Point',
        'properties': [('id', 'int'), ('temperature', 'float')]
    }

    def get_satellite(self):
        satellite = ''
        for item in self.queryset:
            if item.satellite not in satellite:
                satellite += '_'+item.satellite
        return satellite

    def __init__(self, subject_tag, date_time, queryset):
        super().__init__(subject_tag, date_time)

        self.queryset = queryset
        self.satellites = self.get_satellite()
        self.filename = self.make_file_name(is_dir=False)
        self.dir_name = self.make_file_name(is_dir=True, is_shp=True)
        self.path = f'FireApp/services/out_files/shp/{self.dir_name}'
        self.path_to_file = f'{self.path}/{self.filename}.zip'

    def write_shp(self, path, filename):
        with fiona.open(f'{path}/{filename}.shp', mode='w', driver='ESRI Shapefile',
                        schema=self.schema, crs="EPSG:4326") as shp:

            for index, item in enumerate(self.queryset):
                shapelyObject = shapely.wkt.loads(f'POINT ({item.longitude} {item.latitude})')
                shape = {
                    'geometry': mapping(shapelyObject),
                    'properties': {'id': index+1, 'temperature': float(item.temperature)}
                }
                shp.write(shape)

    def make_archive(self):

        self.make_dir(self.path)
        if not os.path.exists(self.path_to_file):

            self.write_shp(self.path, self.filename)

            arch = Archiving(self.filename, self.path, 'zip')
            arch.make_archive()

        return self.get_path_to_file()


