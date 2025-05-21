# This file contains prompt templates to use Langchain for GenAI generations.

from models.return_models import ColumnMapping, ColumnSelectionMapping, ColumnSelectionReasoning
from langchain_core.prompts import ChatPromptTemplate

######## ------ PART 2: RELEVANT FIELD SELECTION ------- #########

# INFO EXTRACTION
# 1) You can add examples into the prompt template to improve extraction quality
# 2) Introduce additional parameters to take context into account (e.g., include metadata
#    about the document from which the text was extracted.)
info_extraction_prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert extraction algorithm. "
            "Only extract relevant information from the text. "
            "If you do not know the value of an attribute asked to extract, "
            "return null for the attribute's value.",
        ),
        # Please see the how-to about improving performance with
        # reference examples.
        # MessagesPlaceholder('examples'),
        ("human", "{text}"),
    ]
)

# TRANSLATE
translation_prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert translation algorithm. "
            "IF THE DATA IS GIVEN IN A LANGUAGE OTHER THAN ENGLISH, "
            "Please convert the given mapping from that language (likely French) to English. "
            "If you do not know the translation of an attribute asked to translate, "
            "return null for the attribute's value.",
        ),
        ("human", "{text}"),
    ]
)


# SELECTION
field_selection_prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert field selection algorithm. "
            "Given your instructions, please indicate whether or not you would include each field and WHY. "
            "Be lenient and accept more than you would want to. "
            "If you do not know if a field is useful, "
            "do not select it, but explain your confusion. "
            "Output your answer as JSON that  "
            "matches the given schema: \`\`\`json\n{model_json_schema}\n\`\`\`. "
            "Make sure to wrap the answer in \`\`\`json and \`\`\` tags",
        ),
        ("human", "{text}"),
    ]
).partial(model_json_schema=ColumnSelectionMapping.model_json_schema())


######## ------ PART 3: DATASET TRANSFORMATION (AGGREGATION) ------- #########

# aggregation_code_gen_template = ChatPromptTemplate.from_messages(
#     [
#         (
#             "system",
#             "You are an expert data merging code generation algorithm. "
#             "You are given context on what aggregated columns a final dataset should have. "
#             "You are also given a list of attributes that we DO HAVE about a given household. Some information is per-person, not per-household. "
#             "Our goal is to keep every attribute to be per-household. You need to decide what aggregations to perform to achieve this. "
#             "You will write code specific to the GIVEN attributes to do this. ONLY use this information, as we do not have access to other info. "
#             "If you do not know how to aggregate something, "
#             "leave it and put a note about it in the prefix.",
#         ),
#         ("human", "{text}"),
#     ]
# )


# aggregation_code_gen_template = ChatPromptTemplate.from_messages(
#     [
#         (
#             "system",
#             "You are an expert data merging code generation algorithm. "
#             "You are given context on what aggregated columns a final dataset should have. "
#             "You are also given a list of attributes that we DO HAVE about a given entity. Some information is per-person, not per-household. "
#             "Our goal is to keep every attribute to be per-household. You need to decide what aggregations to perform to achieve this. "
#             "You will write code specific to the GIVEN attributes to do this. ONLY use this information, as we do not have access to other info. "
#             "If you do not know how to aggregate something, "
#             "leave it and put a note about it in the prefix.",
#         ),
#         ("human", "{text}"),
#     ]
# )
aggregation_code_gen_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert data transformation and aggregation algorithm. "
            "Your task is to generate Python code (using pandas) to convert a dataset into a per-entity format, such as per-household or per-player. "
            "You are given a list of column names we already have. Some columns may be per-individual or row-wise and need to be aggregated. "
            "You will write code that intelligently aggregates these columns to produce one row per entity (e.g., per player or household). "
            "IN THE CODE, PLEASE PLACE PERIODIC PRINT STATEMENTS TO HELP DEBUGGING. "
            "You must define a variable named `agg_df` as the final result. Do not print it, just have it."
            "Only use the columns that are provided. If a column cannot be aggregated, leave a note in the code comments but do not guess."

            "\n\nExample:\n"
            "If we have a table with columns [player_id, asset_type, quantity], where each row shows how many of each asset a player owns, "
            "then we should convert this into one row per player with a separate column for each asset:\n"
            "- 'num_sword', 'num_shield', 'num_potion', etc.\n"
            "- The code to do this would involve pivoting on asset_type and summing quantity."

            "\n\nWhen in doubt, favor:\n"
            "- `.groupby(...).sum()` or `.mean()` for numeric fields\n"
            "- `.pivot_table()` for row-wise entity-type tables\n"
            "- `.drop_duplicates()` if the rows are redundant"

            "\n\nOutput only Python code, no extra text.",
        ),
        ("human", "{text}"),
    ]
)


column_rename_mapping_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a schema-matching assistant that identifies semantically equivalent column names across datasets. "
            "You are given two lists of column names: one from a source dataset and one from a target dataset. "
            "Your job is to determine if any column in the source set refers to the same concept as a column in the target set, even if the names are different. "

            "You must return a Python dictionary that maps source column names to the corresponding target column names. "
            "Only include mappings if the source and target columns clearly represent the same concept. "
            "Do not guess. If no match exists for a source column, do not include it in the mapping."

            "\n\nExample:\n"
            "Given:\n"
            "source_columns = ['clicks_total', 'session_time', 'user_id']\n"
            "target_columns = ['num_clicks', 'time_spent', 'player_id']\n"
            "Return:\n"
            "{\n"
            "  'clicks_total': 'num_clicks',\n"
            "  'session_time': 'time_spent'\n"
            "}"

            "\n\nReturn only the Python dictionary. No explanations or extra text.",
        ),
        ("human", "{text}"),
    ]
)
