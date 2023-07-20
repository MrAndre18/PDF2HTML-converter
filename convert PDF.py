import PyPDF2
from bs4 import BeautifulSoup

def convert_pdf_to_html(pdf_path, output_html):
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        num_pages = len(pdf_reader.pages)

        # Создать HTML-структуру с сохранением исходного форматирования текста
        html_content = "<html><body>"
        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            page_content = page.extract_text()
            soup = BeautifulSoup(page_content, 'html.parser')
            
            # Оборачиваем каждый абзац в тег <p>
            paragraphs = soup.find_all('p')
            for paragraph in paragraphs:
                paragraph.wrap(soup.new_tag('p'))
            
            page_content = str(soup)
            html_content += f"<div class='page' id='page-{page_num + 1}'>{page_content}</div>"
        html_content += "</body></html>"

        # Сохранить HTML-контент в файл
        with open(output_html, 'w', encoding='utf-8') as output_file:
            output_file.write(html_content)

    print("Конвертация PDF в HTML завершена.")

pdf_path = "Abu Dhabi/Direction 1/Ministerial_Resolution_№_71_of_1989_Regarding_the_procedures_for.pdf"
result_path = 'Result HTML/Result.html'

convert_pdf_to_html(pdf_path, result_path)