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
  """Преобразует двухмерный массив в одномерный"""
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

def check_article(text, is_title):
  """Проверяет, является ли параграф заголовком раздела"""
  if is_title:
    text = remove_html_tags(text)
    text = " ".join(text)
    text = '<h3 class="law-title center">' + text + '</h3>'
  else:
    text = " ".join(text)
    text = '<p class="law-text">' + text + '</p>'
  
  return text

def set_left_side_paragraph(paragraph):
  """Задаёт классы параграфа, расположенного слева относительно страницы"""
  class_str = re.findall(r'class=\"(.*)\"', paragraph)
  classes = class_str[0].split()
  if 'law-title' in classes:
    classes[classes.index('law-title')] = 'law-text'
    classes.append('bold')
  if 'center' in classes:
    classes.remove('center')
  classes.append('left')
  
  pattern = r'class="(.+?)"'
  paragraph = re.sub(pattern, r'class="{}"'.format(' '.join(classes)), paragraph)
  paragraph = re.sub('h3', 'p', paragraph)
  
  return paragraph

def wrap_doc_title(doc):
  """Редактирует заголовок документа и оборачивает в нужный тег"""
  law_title_number = 0
  title_end_index = 0
  paragraph_number = 0
  law_title = []
  
  for paragraph in doc:
    if 'h3' in paragraph:
      law_title_number += 1
    
    if law_title_number == 2:
      title_end_index = paragraph_number
      break
    
    paragraph_number += 1
  
  law_title = doc[:(title_end_index + 1)] # получаем из документа заголовок
  doc = doc[(title_end_index + 1):] # убираем из документа заголовок
  
  for i, item in enumerate(law_title):
    law_title[i] = re.sub('<br>', ';', item)
  
  for i, item in enumerate(law_title):
    if 'h3' in item:
      item = remove_html_tags([item])
      item = '<span class="bold">'+ item[0] +'</span>'
      law_title[i] = item
    else:
      item = remove_html_tags([item])
      law_title[i] = item[0]
  
  for i, item in enumerate(law_title):
    law_title[i] = re.sub(';', '<br>', item)
  
  law_title = '<h2 class="law-title center main">' + '<br>'.join(law_title) + '</h2'
  
  return [law_title] + doc

def join_articles(doc):
  """Объединяет попарно идущие заголовки разделов"""
  first_article_index = 0
  last_article_index = 0
  is_multiple_article = False
  
  tag_to_find = 'h3'
  
  for index, item in enumerate(doc):
    if tag_to_find in item and tag_to_find not in doc[index - 1]:
      first_article_index = index
    
    if tag_to_find in item and tag_to_find in doc[index - 1]:
      last_article_index = index
      is_multiple_article = True
    
    if tag_to_find not in item and tag_to_find in doc[index - 1] and is_multiple_article:
      item = doc[first_article_index:(last_article_index + 1)]
      for aricle_part in item:
        doc.remove(aricle_part)
      item = remove_html_tags(item)
      item = '<h3 class="law-title center">' + '<br>'.join(item) + '</h3'
      doc.insert(first_article_index, item)
      
      is_multiple_article = False
  
  return doc

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
      x1 = b['bbox'][2] # Позиция правого края параграфа
      is_title = True
      
      for l in b["lines"]:  # iterate through the text lines
        for s in l["spans"]:  # iterate through the text spans
          if s["flags"] == 20:
            # Жирный шрифт оборачиваем в тег <span>
            paragraph.append('<span class="bold">'+ s["text"].strip() +'</span>')
          else:
            paragraph.append(s["text"].strip())
            is_title = False
        paragraph.append('<br>')
      
      # Удаляем последний <br>
      paragraph.pop()
      
      # Проверка, является ли параграф заголовком раздела
      paragraph = check_article(paragraph, is_title)
      
      # Проверка, расположен ли параграф слева
      if x1 < page_width / 2:
        paragraph = set_left_side_paragraph(paragraph)
      
      doc_page.append(paragraph)
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
  
  # Преобразование двухмерного списка в одномерный
  doc = flatten_list(doc)
  
  # Редактирование заголовка документа
  doc = wrap_doc_title(doc)
  
  # Объединение заголовков разделов, идущих друг за другом
  doc = join_articles(doc)
  
  print(doc)
  
  # Запись в новый HTML
  #
  #
  #
  ######
  
  # Извлечение данных о законе
  get_law_data(input_file_path)
  

# Пути к файлам
input_pdf = "Abu Dhabi/Direction 1/Ministerial_Resolution_№_71_of_1989_Regarding_the_procedures_for.pdf"
output_pdf = 'Result PDF/Result.pdf'

# Ministerial_Resolution_№_71_of_1989_Regarding_the_procedures_for
# Federal_Law_№_47_of_2022_in_the_matter_of_corporate_and_business

# Используем функцию process_pdf_file для обработки файла PDF
process_pdf_file(input_pdf, output_pdf)