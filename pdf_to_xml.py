from PyPDF2.utils import bbox, PointObject
from PyPDF2 import PdfFileReader


def is_centered(text, page):
    width, height = page.mediaBox.upperRight
    text_box = page.search_for(text)
    if text_box:
        # Получаем координаты левого верхнего угла текста
        x0, y0 = text_box[0], text_box[1]
        # Получаем размеры текста
        text_width, text_height = (text_box[2] - text_box[0]), (text_box[3] - text_box[1])
        # Рассчитываем координаты центра текста
        center_x, center_y = x0 + text_width / 2, y0 + text_height / 2
        # Проверяем, находится ли центр текста в центре страницы
        if abs(center_x - width / 2) < text_width / 2 and abs(center_y - height / 2) < text_height / 2:
            return True
    return False


def process_pdf(pdf_file):
    with open(pdf_file, 'rb') as f:
        pdf = PdfFileReader(f)
        for page in pdf.pages:
            page_text = page.extract_text()
            for text in page_text.split('\n'):
                if is_centered(text, page):
                    print(f"Найден текст '{text.strip()}' на странице {pdf_file.name}")



pdf_file = 'Abu Dhabi/Direction 1/Ministerial_Resolution_№_71_of_1989_Regarding_the_procedures_for.pdf'
process_pdf(pdf_file)