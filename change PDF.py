import PyPDF2
import re
from datetime import datetime
from langdetect import detect
from translate import Translator
import fitz


################################
# Редактирование инфо о законе #
################################

def remove_html_tags(lst):
  cleaned_list = []
  for string in lst:
    cleaned_string = re.sub('<.*?>', '', string)
    cleaned_list.append(cleaned_string)
  return cleaned_list

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

def remove_empty_lines(lines):
  """Удаляет пустые строки из списка строк"""
  return list(filter(lambda x: x.strip(), lines))

def get_doc_title(path):
  # Открываем файл для чтения
  pdf_file = open(path, 'rb')
  pdf_reader = PyPDF2.PdfReader(pdf_file)
  
  doc_title = []
  
  # Обходим первую страницу и достаёт заголовок
  page = pdf_reader.pages[0]
  lines = page.extract_text().split('\n')
  
  cleared_page = remove_first_last_lines(lines, 'https://', len(pdf_reader.pages))
  
  if len(pdf_reader.pages) == 1:
    doc_title = cleared_page[5:9]
  else:
    doc_title = cleared_page[:5]
  
  pdf_file.close()
  return doc_title

def translate_text(text):
  lang = detect(text)
  translator = Translator(from_lang=lang, to_lang='en')

  if lang != 'en':
    translation = translator.translate(text)
    return translation
  else:
    return None

def get_law_number(doc):
  law_number = [int(s) for s in str.split(doc[0]) if s.isdigit()]
  
  if law_number[0]:
    return law_number[0]
  else:
    return None

def get_law_create_date(doc):
  pattern = r'\d{1,}/\d{1,}/\d{4}'  # Регулярное выражение для даты dd/dd/dddd
  match = re.search(pattern, doc[1])
  
  if match:
    date_str = match.group()
    law_date = datetime.strptime(date_str, '%d/%m/%Y').date()
    return law_date
  else:
    return None

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
  doc_first_line = doc[0]
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

def get_law_data(path):
  doc_title_arr = get_doc_title(path)
  doc_title_arr = remove_empty_lines(doc_title_arr)
  
  # Переводим заголовок на английский
  text = translate_text('|'.join(doc_title_arr))
  if text == None:
    print('Ошибка перевода')
    return

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

def flatten_list(lst):
  flattened_list = []
  for sublist in lst:
    for item in sublist:
      flattened_list.append(item)
  return flattened_list

def remove_matching_strings(doc, phrases):
  result_doc = []
  
  for string_list in doc:
    list = [string for string in string_list if not any(phrase in string for phrase in phrases)]
    result_doc.append(list)

  return result_doc

def join_page_text(page, lines):
  """Обновляет текст страницы"""
  page_content = ' \n'.join(lines)
  #page.merge_page(page_content)
  
  return page_content

def extract_text_from_pdf(file_path):
  # Открываем файл для чтения
  doc = fitz.open(file_path)
  result_doc = []
  
  for page in doc:
    doc_page = []
    blocks = page.get_text("dict", flags=11, sort=True)
    page_width = blocks['width']

    for b in blocks["blocks"]:  # iterate through the text blocks
      paragraph = []
      x0 = b['bbox'][0]
      x1 = b['bbox'][2]
      is_title = True
      
      for l in b["lines"]:  # iterate through the text lines
        #print(l)
        
        for s in l["spans"]:  # iterate through the text spans
          if s["flags"] == 20:
            # Жирный шрифт оборачиваем в тег <span>
            paragraph.append('<span class="bold">'+ s["text"].strip() +'</span>')
          else:
            paragraph.append(s["text"].strip())
            is_title = False
      
      if is_title:
        paragraph = remove_html_tags(paragraph)
        paragraph = " ".join(paragraph)
        paragraph = '<h4 class="law-title center">' + paragraph + '</h4>'
      else:
        paragraph = " ".join(paragraph)
        paragraph = '<p class="law-text">' + paragraph + '</p>'
      
      if x1 < page_width / 2:
        class_str = re.findall(r'class=\"(.*)\"', paragraph)
        classes = class_str[0].split()
        if 'law-title' in classes:
          classes[classes.index('law-title')] = 'law-text'
          classes.append('bold')
        if 'center' in classes:
          classes.remove('center')
        classes.append('left')
        
        ######
        # (!!!) Доделать изменение в paragraph
        ######
        print(classes)
      
      doc_page.append(paragraph)
      
      if x1 < page_width / 2:
        print('x0:', x0, '---', 'x1:', x1)
        print(paragraph, '\n\n')
    
    result_doc.append(doc_page)
  
  doc.close()
  return result_doc


#################
# Создание HTML #
#################




###################
# Главная функция #
###################

def process_pdf_file(input_file_path, output_pdf_path):
  """Обрабатывает файл PDF"""
  doc = extract_text_from_pdf(input_file_path)
  
  # Обходим каждую страницу и удаляем первую и последнюю строки
  for i in range(len(doc)):
    doc[i].pop(0)
    doc[i].pop()
  doc[-1].pop()
  
  # Удаление слов-заглушек
  phrases_to_remove = {"Image", "Table"}
  doc = remove_matching_strings(doc, phrases_to_remove)
  
  #print(doc)
  
  # Преобразование двухмерного списка в одномерный
  doc = flatten_list(doc)
  
  #print(doc)
  
  # Запись в новый HTML
  
  # Извлечение данных о законе
  get_law_data(input_file_path)
  

# Пути к файлам
input_pdf = "Abu Dhabi/Direction 1/Ministerial_Resolution_№_71_of_1989_Regarding_the_procedures_for.pdf"
output_pdf = 'Result PDF/Result.pdf'

# Ministerial_Resolution_№_71_of_1989_Regarding_the_procedures_for
# Federal_Law_№_47_of_2022_in_the_matter_of_corporate_and_business

# Используем функцию process_pdf_file для обработки файла PDF
process_pdf_file(input_pdf, output_pdf)