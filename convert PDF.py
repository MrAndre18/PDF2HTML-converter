import PyPDF2

def extract_text_from_pdf(file_path):
  # Открываем файл для чтения
  pdf_file = open(file_path, 'rb')
  pdf_reader = PyPDF2.PdfReader(pdf_file)
  
  result_doc = []
  
  # Обходим первую страницу и достаёт заголовок
  page = pdf_reader.pages[0]
  lines = page.extract_text().split('\n')
  
  print(lines)

def process_pdf_file(input_file_path, output_html_directory):
  """Обрабатывает файл PDF"""
  doc = extract_text_from_pdf(input_file_path)

# Пути к файлам
input_pdf = "Abu Dhabi/Direction 1/Ministerial_Resolution_№_71_of_1989_Regarding_the_procedures_for.pdf"
output_html_directory = 'Result HTML/'

# Ministerial_Resolution_№_71_of_1989_Regarding_the_procedures_for
# Federal_Law_№_47_of_2022_in_the_matter_of_corporate_and_business

# Используем функцию process_pdf_file для обработки файла PDF
process_pdf_file(input_pdf, output_html_directory)