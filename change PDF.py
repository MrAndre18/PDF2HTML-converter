import PyPDF2
import re
from datetime import datetime
from langdetect import detect
from translate import Translator
import fitz

################################
# Редактирование инфо о законе #
################################

def translate_text(text):
  lang = detect(text)
  translator = Translator(from_lang=lang, to_lang='en')
  if lang != 'en':
    translation = translator.translate(text)
    return translation
  else:
    return text

def get_law_number(doc):
  law_number = [int(s) for s in str.split(doc[0]) if s.isdigit()]
  
  return law_number[0]

def get_law_create_date(doc):
  pattern = r'\d{2}/\d{1,}/\d{4}'  # Regular expression pattern for dd/dd/dddd format
  match = re.search(pattern, doc[1])
  
  if match:
    date_str = match.group()
    law_date = datetime.strptime(date_str, '%d/%m/%Y')
    return law_date
  else:
    return ''

def get_law_tipe(doc):
  doc_first_line = doc[0]
  
  # Удаляем цифры из строки
  law_tipe = re.sub("[0-9]", "", doc_first_line)
  
  # Удаляем заданные фразы из строки
  phrases = ["no", "№", "No."]
  for phrase in phrases:
    law_tipe = law_tipe.replace(phrase, '')
  
  return law_tipe.strip()

def get_law_name(doc):
  doc.pop(2)
  doc.pop(1)
  doc_first_line = translate_text(doc[0])
  doc.pop(0)
  
  # Подстановка знака № и очистка строки от ненужных символов
  phrases = ["no", "No", "No."]
  for phrase in phrases:
    doc_first_line = doc_first_line.replace(phrase, '№')
  phrases = [",", "."]
  for phrase in phrases:
    doc_first_line = doc_first_line.replace(phrase, '')
    
  law_number = [int(s) for s in str.split(doc_first_line) if s.isdigit()]
  
  # Убираем из строки номер закона и знак №, если этот знак после перевода не в конце
  doc_first_line = re.sub(str(law_number[0]), '', doc_first_line).strip()
  doc_first_line = re.sub('№', '', doc_first_line).strip()
  
  number = ''.join(['№', str(law_number[0])])
  
  law_name = ' '.join([doc_first_line, number, doc[0]])
  
  return law_name.strip()

def get_law_data(doc):
  text = translate_text('|'.join(doc))
  text = text.split('|')
  document_title = []
  
  for line in text:
    line = line.strip()  # Убираем лишние пробелы в начале и конце строки
    line = " ".join(line.split())  # Убираем лишние пробелы между словами
    document_title.append(line)
  
  law_number = get_law_number(document_title)
  law_date = get_law_create_date(document_title)
  law_tipe = get_law_tipe(document_title)
  law_name = get_law_name(document_title)
  
  #(!!!) РАССКОММЕНТИРОВАТЬ НА БИЛДЕ
  #processing_law_data(law_number, law_date, law_tipe, law_name)

def processing_law_data(law_number, law_date, law_tipe, law_name):
  # Обработчик информации о законе
  #(!!!) Тут будет запись в БД
  print('law_number:', law_number)
  print('law_date:', law_date)
  print('law_tipe:', law_tipe)
  print('law_name:', law_name)

########################
# Редактирование файла #
########################

def remove_empty_lines(lines):
  """Удаляет пустые строки из списка строк"""
  return list(filter(lambda x: x.strip(), lines))

def remove_first_last_lines(lines, phrase, pages_count):
  """Удаляет ненужные строки"""
  for index, line in enumerate(lines):
    if phrase in line: # Проверяем, содержит ли строка заданную фразу
      line = line.split()[1:]
      line = ' '.join(line)
      line = re.sub('/' + str(pages_count), '||', line).strip()
      line = line.split('||')[1:]
      line = ' '.join(line)
      lines[index] = line
      
    line = line.strip()  # Убираем лишние пробелы в начале и конце каждой строки
    lines[index] = line

  return lines[1:]

def join_page_text(page, lines):
  """Обновляет текст страницы"""
  page_content = ' \n'.join(lines)
  #page.merge_page(page_content)
  
  return page_content

def flags_decomposer(flags):
    """Make font flags human readable."""
    l = []
    if flags & 2 ** 4:
        l.append("bold")
    return ", ".join(l)

def extract_text_from_pdf(file_path):
  doc = fitz.open(file_path)
  result_doc = []
  
  for page in doc:
    doc_page = []
    blocks = page.get_text("dict", flags=11)["blocks"]
    
    for b in blocks:  # iterate through the text blocks
      paragraph = []
      
      for l in b["lines"]:  # iterate through the text lines
        for s in l["spans"]:  # iterate through the text spans
          if s["flags"] == 20:
            # Жирный шрифт оборачиваем в тег <b>
            paragraph.append('<b>'+ s["text"].strip() +'</b>')
          else:
            paragraph.append(s["text"].strip())
            
      paragraph = " ".join(paragraph)
      doc_page.append(paragraph)
      
    result_doc.append(doc_page)
    
  return result_doc

###################
# Главная функция #
###################

def process_pdf_file(input_file_path, output_file_path):
  """Обрабатывает файл PDF"""
  # Открываем файл для чтения и записи
  pdf_file = open(input_file_path, 'rb')
  pdf_reader = PyPDF2.PdfReader(pdf_file)
  
  doc = extract_text_from_pdf(input_file_path)
  
  # Обходим каждую страницу
  for page in doc:
    page = page[2:]
    print(page)
  
  # Обходим каждую страницу
  for page_num in range(len(pdf_reader.pages)):
    page = pdf_reader.pages[page_num]
    lines = page.extract_text().split('\n')
    
    non_empty_lines = remove_empty_lines(lines)
    cleared_page = remove_first_last_lines(non_empty_lines, 'https://', len(pdf_reader.pages))
    non_empty_lines = remove_empty_lines(cleared_page)
    
    if page_num == 0:
      document_title = non_empty_lines[:4]
      
      get_law_data(document_title)
    
    changed_page = join_page_text(page, non_empty_lines)
    
    
    
    # pdf_writer = PyPDF2.PdfWriter()
    # pdf_writer.add_page(changed_page)
    # output_file = open(output_file_path, 'wb')
    # pdf_writer.write(output_file)
    # output_file.close()
    
  pdf_file.close()

# Пути к файлам
input_pdf = "Abu Dhabi/Direction 1/Ministerial_Resolution_№_71_of_1989_Regarding_the_procedures_for.pdf"
output_pdf = 'Result PDF/Result.pdf'

# Используем функцию process_pdf_file для обработки файла PDF
process_pdf_file(input_pdf, output_pdf)