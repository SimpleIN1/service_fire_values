import math
import os

from fpdf import FPDF
from fpdf.fonts import FontFace

from fpdf.fpdf import check_page
from contextlib import contextmanager

from FireApp.models import FireValue, Subject
from FireApp.services.pdf.pdf_table import TableOverride
from FireApp.services.shapefile import Base


class PDF(Base, FPDF):

    @check_page
    @contextmanager
    def table(self, *args, **kwargs):
        table = TableOverride(self, *args, **kwargs)
        yield table
        table.render()

    path = 'FireApp/services/out_files/pdf'
    path_static = 'FireApp/services/pdf'
    TEXT_HEADER = { # текст для заголовка
        'organization_name': u'Сибирский центр ФГБУ «Научно-исследовательский центр '
                             u'космической гидрометеорологии «Планета»',
        'title': 'Космический мониторинг лесных пожаров',
        'domain': 'www.rcpod.ru',
    }
    TEXT_CONTACT_FOOTER = { # контактные данные футере(снизу)
        'contact_addr_phone': '630099, г.Новосибирск ул.Советская, 30, оф. 127, тел./факс (383) 363-46-05',
        'contact_email': 'kav@rcpod.siberia.net'
    }
    AUTHOR = 'СЦ ФГБУ «НИЦ «Планета», 630099, г. Новосибирск, ул. Советская, 30, оф. 127, ' \
             'тел./факс (383) 334-45-42, 334-41-11, avn@rcpod.ru'
    CREATOR = 'СЦ ФГБУ «НИЦ «Планета»'
    SUBJECT = 'Оперативная отчетность о точках вероятного возгорания (ТВВ)'

    def __init__(
            self,
            date_time, # дата и время отчетности о твв
            cloud_shielding: int, # экранирование облачностью
            operator_fio: str, # фио оператора
            subject_tag: str = '', # Субъект
            queryset=None,  # данные твв
    ):

        FPDF.__init__(
            self,# настройки страницы
            orientation='landscape',
            unit='mm',
            format='A4'
        )
        Base.__init__(
            self,
            subject_tag,
            date_time,
        )
        self.table_data = None
        self.satellites = ''
        self.read_fire_point(queryset)

        self.HEADER_FIRST = f'Оперативная отчетность'
        self.HEADER_SECOND = f'о точках вероятного возгорания (ТВВ) за ' \
                             f'{self.get_date()} на {self.get_time(only_minutes_and_hours=True)} ВСВ'
        self.cloud_shielding = cloud_shielding
        self.operator_fio = operator_fio

        self.dir_name = self.make_file_name(is_dir=True)
        self.filename = self.make_file_name() #FireApp/services/
        self.path_to_file = f'{self.path}/{self.dir_name}/{self.filename}.pdf'

    def get_path_to_file(self):
        # print(self.filename)
        return self.path_to_file

    def get_region_name(self):
        item = Subject.objects.get(tag=self.subject_tag)
        return item.name

    def build_file(self): # сборка файла

        self.make_dir(f'{self.path}/{self.dir_name}')
        if not self.is_exist_file(self.path_to_file):
            # self.read_fire_point(queryset)
            self.add_font('TimesNewRoman', fname=f'{self.path_static}/ttf/times_new_roman.ttf')

            # self.alias_nb_pages()
            self.make_margin()
            self.add_page()

            self.make_meta()
            self.make_content()
            self.write_to_file(self.path_to_file)

        return self.path_to_file

    def make_margin(self): # добавление отступов
        t, l, r = self.t_margin, self.l_margin, self.r_margin
        self.set_margin(35)
        self.set_margins(l, t, r)

    def make_meta(self): # добавление мета тегов
        self.set_title(self.TEXT_HEADER['title'])
        self.set_author(self.AUTHOR)
        self.set_creator(self.CREATOR)
        self.set_subject(self.SUBJECT)

    def header(self): # добавление заголовка для страницы
        self.set_font('TimesNewRoman', size=12)
        self.set_text_color(60, 60, 60)
        self.set_draw_color(60, 60, 60)

        self.image(f'{self.path_static}/img/logoPlaneta.png', x=20, y=7, w=20, h=20)

        self.cell(w=0, h=7, txt=self.TEXT_HEADER['organization_name'], align='C')
        self.ln(4)
        self.cell(w=0, h=7, txt=self.TEXT_HEADER['title'], align='C')
        self.ln(4)
        self.cell(w=0, h=7, txt=self.TEXT_HEADER['domain'], align='C')
        self.ln(4)

        self.set_line_width(.3)
        self.cell(w=0, h=7, border='B', align='C')

        self.ln(12)

    def footer(self): # добаваление нижнего контитула документа
        self.set_font('TimesNewRoman', size=12)
        self.set_text_color(60, 60, 60)
        self.set_draw_color(60, 60, 60)
        self.set_y(-35)
        self.set_text_color(60, 60, 60)
        self.set_draw_color(60, 60, 60)

        self.set_line_width(.3)
        self.cell(w=0, h=7, border='B', align='C')

        self.ln(10)
        self.cell(w=0, h=7, txt=self.TEXT_CONTACT_FOOTER['contact_addr_phone'], align='C')
        self.ln(4)
        self.cell(w=0, h=7, txt=self.TEXT_CONTACT_FOOTER['contact_email'], align='C')
        self.ln(4)
        self.image(f'{self.path_static}/img/logoPlaneta1.png', x=257, y=self.y-9, w=20, h=20)

    @classmethod
    def get_fractional_part(cls, value):
        return value % 1 * 60

    @classmethod
    def to_geo_coordinates(cls, value):
        degree = math.floor(value)
        t = cls.get_fractional_part(value)
        minutes = math.floor(t)
        seconds = round(cls.get_fractional_part(t))
        return f'{degree}° {minutes}\' {seconds}\"'

    def read_fire_point(self, queryset):
        # queryset = self.get_fire_values()

        self.table_data = [  # данные для таблицы
            [self.get_region_name(), ],
            ["№", "Широта ТВВ", "Долгота ТВВ",
             "Район обнаружения ТВВ",
             "\nБлижайший населенный пункт к ТВВ",
             "Направление на ТВВ от населенного пункта",
             "Расстояние до ТВВ от населенного пункта, КМ",
             "Лесхоз", "Лесничество", "Квартал"],
        ]

        for index, item in enumerate(queryset):
            self.table_data.append([
                str(index+1),
                self.to_geo_coordinates(item.latitude),
                self.to_geo_coordinates(item.longitude),
                str(item.district.name),
                str(item.settlement.name),
                FireValue.Directly(item.directly_from_stlm).label,
                str(item.distance_to_stln), "", "", ""
            ])

            if item.satellite.tag not in self.satellites:
                self.satellites += '_'+item.satellite.tag

    def make_content(self): # основное содержимое страницы
        self.set_font('TimesNewRoman', size=15)
        self.set_text_color(0, 0, 0)
        self.set_draw_color(0, 0, 0)
        self.set_line_width(0.2)
        self.cell(w=0, h=7, txt=self.HEADER_FIRST, align='C')
        self.ln(5)
        self.cell(w=0, h=7, txt=self.HEADER_SECOND, align='C')
        self.ln(12)

        self.set_font('TimesNewRoman', size=9)
        headings_style = FontFace(fill_color=(179, 225, 255))

        with self.table(
            text_align="CENTER",
            headings_style=headings_style,
            col_widths=(10, 25, 25, 40, 40, 30, 30, 30, 30, 30)
        ) as tb:
            for i, data_row in enumerate(self.table_data):
                row = tb.row()

                for datum in data_row:
                    row.cell(datum)

        self.set_font('TimesNewRoman', size=15)
        self.ln(6)
        self.cell(w=0, h=7, txt=f'Экранирование облачностью {self.cloud_shielding}%', align='C')
        self.ln(10)
        self.cell(w=0, h=7, txt=f'Оператор: {self.operator_fio}')

    def write_to_file(self, filename): # запись в файл
        self.output(
            name=filename
        )

