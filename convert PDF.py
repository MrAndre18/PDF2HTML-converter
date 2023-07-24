import PyPDF2
from bs4 import BeautifulSoup

def pdf_to_html(pdf_path, html_path):
    # Открыть PDF-файл
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        # Получить количество страниц в файле
        num_pages = len(pdf_reader.pages)
        
        # Перебрать все страницы и извлечь текст
        pdf_text = ''
        for page_num in range(num_pages):
            pdf_page = pdf_reader.pages[page_num]
            pdf_text += pdf_page.extract_text()

        # Преобразовать текст в HTML
        soup = BeautifulSoup('<html><head></head><body></body></html>', 'html.parser')
        body = soup.find('body')
        for line in pdf_text.split('\n'):
            paragraph = soup.new_tag('p')
            paragraph.string = line
            body.append(paragraph)
        
        # Сохранить результат в HTML-файл
        with open(html_path, mode='w', encoding='utf-8') as file:
            file.write(str(soup))
    
    print(f'Файл "{pdf_path}" успешно преобразован в "{html_path}"')

pdf_path = "Abu Dhabi/Direction 1/Ministerial_Resolution_№_71_of_1989_Regarding_the_procedures_for.pdf"
result_path = 'Result HTML/Result.html'

pdf_to_html(pdf_path, result_path)