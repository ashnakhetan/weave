# This file contains classes to define the return type for GenAI requests.
from typing import Optional, List
from pydantic import BaseModel, Field

######## ------ PART 2: RELEVANT FIELD SELECTION ------- #########

class ColumnMapping(BaseModel):
    """Simple mapping from column name to question/survey field.
    Example of format:
    [
    "s01q01 – Combien de personnes vivent dans ce village/quartier?",
    "s01q02 – Quelle sont les deux principales langues parlées dans ce village/quartier?"
    ]
    """

    # ^ Doc-string for the entity ColumnMapping.
    # This doc-string is sent to the LLM as the description of the schema,
    # and it can help to improve extraction results.

    # Note that:
    # 1. Each field is an `optional` -- this allows the model to decline to extract it!
    # 2. Each field has a `description` -- this description is used by the LLM.
    # Having a good description can help improve extraction results.
    section_name: Optional[str] = Field(default=None, description="The name of the section")
    mappings: Optional[List[str]] = Field(
        default=None, description="A list of the mappings from column name to the question or survey field associated with it"
    )

#     section_name: SECTION 0: HOUSEHOLD IDENTIFICATION AND CONTROL INFORMATION
class ColumnSelectionReasoning(BaseModel):
    """Decide which columns are relevant to the task and provide reasoning for all columns.
    Example:
    section_name: GSEC1A
    column_code: s00q01
    column_question: What is the region?
    is_selected: True
    selection_reasoning: [FILL IN SOON]
    """
    section_name: Optional[str] = Field(default=None, description="The code of the section")
    column_code: Optional[str] = Field(default=None, description="The column code")
    column_question: Optional[str] = Field(default=None, description="The question/field of the column, from the mapping")
    is_selected: Optional[bool] = Field(default=None, description="Whether or not this column is selected")
    selection_reasoning: Optional[str] = Field(default=None, description="Reasoning for why the column was or wasn't selected")

class ColumnSelectionMapping(BaseModel):
    """List of ColumnSelectionReasonings for the whole datatable.
    ex:
    section_name: GSEC1A: HOUSEHOLD ROSTER
    column_selection_mapping: [ColumnSelectionReasoning(...), ....]
    """
    section_name: Optional[str] = Field(default=None, description="The name of the section")
    column_selection_mapping: Optional[List[ColumnSelectionReasoning]]



######## ------ PART 3: DATASET TRANSFORMATION (AGGREGATION) ------- #########

class FunctionalCode(BaseModel):
    """Provide executable code ready to run. Do not include backticks.
    Example:
    prefix: Description of the problem and approach
    imports: Code block import statements
    code: Code block not including import statements
    """
    prefix: Optional[str] = Field(default=None, description="Description of the problem and approach")
    imports: Optional[str] = Field(default=None, description="Code block import statements")
    code: Optional[str] = Field(default=None, description="Code block not including import statements")
