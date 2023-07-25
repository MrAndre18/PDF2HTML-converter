import PyPDF2
import re
from datetime import datetime

def get_law_number(doc):
  law_number = [int(s) for s in str.split(doc[0]) if s.isdigit()]
  print('Номер закона:', law_number[0])

def get_law_create_date(doc):
  pattern = r'\d{2}/\d{1,}/\d{4}'  # Regular expression pattern for dd/dd/dddd format
  match = re.search(pattern, doc[1])
  
  if match:
    date_str = match.group()
    law_date = datetime.strptime(date_str, '%d/%m/%Y')
    print('Дата принятия закона:', law_date)
  else:
    print('Дата не найдена')

def get_law_tipe(doc):
  doc_first_line = doc[0]
  law_tipe = re.sub("[0-9]", "", doc_first_line)
  print('Вид НПА:', law_tipe)

def get_law_name(doc):
  doc.pop(2)
  law_name = ' '.join(doc)
  
  print('Название закона:', law_name)

def remove_empty_lines(lines):
    """Удаляет пустые строки из списка строк"""
    return list(filter(lambda x: x.strip(), lines))

def remove_first_last_lines(lines):
    """Удаляет первую и последнюю строку из списка строк"""
    return lines[2:]

def join_page_text(page, lines):
    """Обновляет текст страницы"""
    page_content = ' \n'.join(lines)
    #page.merge_page(page_content)
    
    return page_content

def process_pdf_file(input_file_path, output_file_path):
  """Обрабатывает файл PDF"""
  # Открываем файл для чтения и записи
  pdf_file = open(input_file_path, 'rb')
  pdf_reader = PyPDF2.PdfReader(pdf_file)
  
  # Обходим каждую страницу
  for page_num in range(len(pdf_reader.pages)):
    page = pdf_reader.pages[page_num]
    lines = page.extract_text().split('\n')
    
    non_empty_lines = remove_empty_lines(lines)
    cleared_page = remove_first_last_lines(non_empty_lines)
    # changed_page = join_page_text(page, non_empty_lines)
    
    if page_num == 0:
      document_title = cleared_page[:4]
      print(document_title)
      
      get_law_number(document_title)
      get_law_create_date(document_title)
      get_law_tipe(document_title)
      get_law_name(document_title)
    
    # print(cleared_page)
    # print('\n#############################################')
    # print('#############################################')
    # print('#############################################\n')
    
    # pdf_writer = PyPDF2.PdfWriter()
    # pdf_writer.add_page(changed_page)
    # output_file = open(output_file_path, 'wb')
    # pdf_writer.write(output_file)
    # output_file.close()

# Пути к файлам
input_pdf = "Abu Dhabi/Direction 1/Federal_Decree_Law_№_32_of_2021_regarding_trading_companies.pdf"
output_pdf = 'Result PDF/Result.pdf'

# Используем функцию process_pdf_file для обработки файла PDF
process_pdf_file(input_pdf, output_pdf)