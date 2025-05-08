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
            "Please convert the given mapping from French (or the provided language) to English. "
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

aggregation_code_gen_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert data merging code generation algorithm. "
            "You are given context on what aggregated columns a final dataset should/might have. "
            "You are also given a list of attributes that we DO HAVE about a given household. Some information is per-person, not per-household. "
            "Our goal is to keep every attribute to be per-household. You need to decide what aggregations to perform to achieve this. "
            "You will write code specific to the GIVEN attributes to do this. ONLY use this information, as we do not have access to other info. "
            "If you do not know how to aggregate something, "
            "leave it and put a note about it in the prefix.",
        ),
        ("human", "{text}"),
    ]
)