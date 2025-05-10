# This file contains all functions for PART 1: RELEVANT MODULE SELECTION
async def find_relevant_datasets(spec_file_path, dataset_details_path):
    """
    Function to identify relevant dataset files based on specifications using LLM parsing.
    Also summarizes the specifications.

    Args:
        spec_file_path (str): Path to the PDF containing specifications
        dataset_details_path (str): Path to the PDF containing dataset details

    Returns:
        tuple: (list of relevant dataset names, specification summary)
    """
    from langchain_community.document_loaders import PyPDFLoader, TextLoader
    from langchain_core.vectorstores import InMemoryVectorStore
    from langchain_openai import OpenAIEmbeddings, ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import CommaSeparatedListOutputParser
    import os

    specs = []
    base_file_path = os.path.splitext(spec_file_path)[0]
    
    # Load specification file
    if os.path.exists(base_file_path + ".pdf"):
        base_file_path += ".pdf"
        spec_loader = PyPDFLoader(spec_file_path)
        async for spec in spec_loader.alazy_load():
            specs.append(spec)

    elif os.path.exists(base_file_path + ".txt"):
        base_file_path += ".txt"
        spec_loader = TextLoader(spec_file_path)
        specs = [spec_loader.load()[0]]  # returns a list with one Document

    else:
        raise FileNotFoundError("No .pdf or .txt found for spec file.")

    # Extract specification text
    spec_text = " ".join([spec.page_content for spec in specs])

    # Load dataset details file
    dataset_loader = PyPDFLoader(dataset_details_path)
    dataset_pages = []
    async for page in dataset_loader.alazy_load():
        dataset_pages.append(page)

    llm = ChatOpenAI(model="gpt-4o")
    dataset_descriptions = ChatPromptTemplate.from_template(
        """Look through this dataset document for any section that talks about dataset
        files or data information. Make a dictionary with all the dataset names and then
        their official descriptions based on the information in this document.

        DOCUMENT:
        {datasets}

        The format of the return should be
        datasetname1: description1,
        datasetname2: description2

        Additionally, make sure to include the dataset containing consumption information (the word "consumption" might or might not appear in the module name;
        here is an example of such a module).
        Also make sure that document weights are included. They will be in the document somewhere.
        """
    )

    summary_chain = dataset_descriptions | llm
    all_datasets = await summary_chain.ainvoke({"datasets": dataset_pages})

    # Set up LLM to analyze the dataset descriptions
    output_parser = CommaSeparatedListOutputParser()

    # Create a prompt template for dataset identification
    dataset_prompt = ChatPromptTemplate.from_template(
        """You are a data scientist analyzing research datasets.

        I have specifications for data I need and descriptions of available datasets.

        SPECIFICATIONS:
        {specifications}

        DATASET DESCRIPTIONS:
        {dataset_descriptions}

        Read the specifications VERY carefully. Based on the specifications, identify the names of all
        relevant datasets or data files that would be useful. If you think some datasets are redundant,
        do not include them in the list. Make the datasets choices as close to the specifications as possible.
        Focus on extracting the exact names of the datasets as they appear
        in the descriptions, not file extensions or formats.

        Return your answer in the form of a table. The first column of the table file name of the
        dataset, then we want the descriptions of the dataset (directly quoted from the source)
        and the reason we think they would be useful (1-2 sentences MAX).
        If you cannot identify any relevant datasets, return "No relevant datasets found".
        """
    )

    # Create chain for dataset identification
    dataset_chain = dataset_prompt | llm | output_parser

    # Run chain to get relevant datasets
    relevant_datasets = await dataset_chain.ainvoke({
        "specifications": spec_text,
        "dataset_descriptions": all_datasets
    })

    # postprocess to remove backticks
    relevant_datasets = [line for line in relevant_datasets if not line.startswith("```")]

    # extract just the filenames
    dataset_names = extract_dataset_names_from_markdown(relevant_datasets)
    return relevant_datasets, all_datasets, dataset_names


# Clean and extract dataset names from markdown-formatted list of strings
def extract_dataset_names_from_markdown(lines):
    dataset_names = []
    for line in lines:
        if line.strip().startswith("|") and not line.strip().startswith("| File Name"):  # skip header
            parts = line.strip().split("|")
            if len(parts) > 1:
                name = parts[1].strip()
                if name and name != '----------------------':
                    dataset_names.append(name)
    return dataset_names


async def analyze_datasets(spec_file, dataset_file):
      relevant_files, all_datasets, dataset_names = await find_relevant_datasets(spec_file, dataset_file)

      print("\n=== RELEVANT DATASET FILES ===")
      for file in dataset_names:
          print(f"- {file}")

      return relevant_files, all_datasets, dataset_names