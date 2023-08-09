import fitz
from bs4 import BeautifulSoup

# Функция для загрузки HTML-файла


def load_html_from_file(html_path, encoding='utf-16'):
    with open(html_path, 'r', encoding=encoding) as f:
        html = f.read()
    return html

# Функция для конвертации HTML в PDF


def convert_html_to_pdf(html_path, pdf_path):
    html = load_html_from_file(html_path)

    soup = BeautifulSoup(html, 'html.parser')
    style_tags = soup.find_all('style')
    styles = ''
    for tag in style_tags:
        styles += str(tag)

    with fitz.open() as doc:
        pdf_bytes = doc.convert_to_pdf(html)

        tmp_pdf_path = pdf_path + '.pdf'
        with open(tmp_pdf_path, 'wb') as f:
            f.write(pdf_bytes)

        pdf_doc = fitz.open(tmp_pdf_path)
        for page in pdf_doc:
            page.insert_textbox(
                (0, 0, page.rect.width, page.rect.height), styles, fontsize=10, align=0)

        pdf_doc.save(pdf_path)
        pdf_doc.close()

    return pdf_path


# Пример использования
html_path = 'Result HTML/Ministerial_Resolution_№_71_of_1989_Regarding_the_procedures_for.html'
pdf_path = 'output.pdf'
convert_html_to_pdf(html_path, pdf_path)
