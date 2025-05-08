# AUXILIARY UTILS
from re import S
from openpyxl import *
import os
import xlrd
from langchain_community.document_loaders import PyPDFLoader
import io
import contextlib
import google.generativeai as genai
import pandas as pd

UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER') or 'uploads'

######## ------ GENERAL UTILS -------- #########
def parquet_viewer(filepath):
  df = pd.read_parquet(filepath)
  return df

# def construct_path_dict():
#   """Given a folder of files, construct a dict"""
#   path_dict = {}
#   for file in os.listdir(UPLOAD_FOLDER):
#     if not file.startswith("data_documentation") and not file.startswith("task_description"):
#         section_name = file.rsplit('_', 1)[0] if '_' in file else ""

######## ------ PART 2: RELEVANT FIELD SELECTION ------- #########

def load_pdf(file_name, page_indices=[0]):
  loader = PyPDFLoader(file_name)
  documents = loader.load()
  return [documents[i] for i in page_indices]

def extract_all_sections(category, prefix):
  all_files = os.listdir(category)
  # extract section number and sort alphabetically
  return sorted([file_name[len(prefix):].replace(".csv", "") for file_name in all_files])

def load_xls(file_name, sheet_name=None):
  output = ""
  workbook = xlrd.open_workbook(file_name)
  sheet = workbook.sheet_by_index(0)
  if sheet_name:
    sheet = workbook.sheet_by_name(sheet_name)
  for r in range(sheet.nrows):
    output += '\n'
    for c in range(sheet.ncols):
      output += str(sheet.cell_value(r, c))

  return output

def sheet_to_text(sheet):
  output = ""
  for r in range(sheet.nrows):
    output += '\n'
    for c in range(sheet.ncols):
      output += str(sheet.cell_value(r, c))

  return output

def map_section_to_page_number(file_path):
  """
  Takes a path to a PDF file and returns a map of section names to page numbers.
  
  The section names are the strings on the left side of the colon in the extract_instructions string.
  The page numbers are the numbers on the right side of the colon, comma-separated.
  
  The function uses the gemini-1.5-flash model to generate the map.
  
  Args:
    file_path (str): The path to the PDF file.
  
  Returns:
    dict: A dictionary of section names to page numbers.
  """
  genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
  model = genai.GenerativeModel('gemini-1.5-flash')
  sample_file = genai.upload_file(path=file_path, display_name="Agriculture Questionnaire")
  extract_instructions = """What page numbers of this pdf correspond with which sections? Generate a map. Please zero-index the pages. Do NOT include anything but this new-line separated map.
  Example:
  1: 0
  2a: 1, 2
  2b: 3
  """
  response = model.generate_content([sample_file, extract_instructions])
  map_sections = response.text.split('\n')
  map = {}
  for section in map_sections:
    if len(section.split(":")) == 2:
      section_name, page_numbers = section.split(":")
      page_numbers = [int(i.strip()) for i in page_numbers.replace('*', '').split(',')]
      map[section_name.replace('*', '')] = page_numbers
  return map



######## ------ PART 3: DATASET TRANSFORMATION (AGGREGATION) ------- #########

def run_code_and_capture_df(code_str, df_name="df"):
    local_vars = {}
    output_buffer = io.StringIO()

    try:
        with contextlib.redirect_stdout(output_buffer):
            exec(code_str, {}, local_vars)
        output = output_buffer.getvalue()
        df = local_vars.get(df_name, None)
        return {"output": output, "dataframe": df}
    except Exception as e:
        return {"error": str(e), "output": output_buffer.getvalue()}
