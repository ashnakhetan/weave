import pandas as pd
import numpy as np
import os
import json

# Set up directory structure
base_dir = "data/test_uploads"
os.makedirs(base_dir, exist_ok=True)

# Create sample task description
with open(os.path.join(base_dir, "task_description.txt"), "w") as f:
    f.write("Merge and unify household and community-level data to prepare for a poverty analysis task.")

# Create sample data documentation
with open(os.path.join(base_dir, "data_documentation.txt"), "w") as f:
    f.write("This dataset includes household and community information from a survey in Region X.\n"
            "Each section includes metadata and data files. Column names follow the sXXqYY format.\n"
            "You should use metadata files to match column codes with question text.")

# Generate metadata and data for two sections: household and community
sections = {
    "GSEC1": {
        "metadata": {
            "s01q01": "How many people live in the household?",
            "s01q02": "What is the household's main source of income?",
            "s01q03": "Is the household head employed?"
        },
        "data": pd.DataFrame({
            "s01q01": np.random.randint(1, 10, 5),
            "s01q02": np.random.choice(["farming", "business", "employment"], 5),
            "s01q03": np.random.choice([True, False], 5)
        })
    },
    "GSEC2": {
        "metadata": {
            "s02q01": "What is the primary language spoken in the village?",
            "s02q02": "Is there a health clinic in the village?",
            "s02q03": "What type of roads connect the village?"
        },
        "data": pd.DataFrame({
            "s02q01": np.random.choice(["Luganda", "Swahili", "English"], 5),
            "s02q02": np.random.choice([True, False], 5),
            "s02q03": np.random.choice(["paved", "dirt", "gravel"], 5)
        })
    }
}

# Save metadata and data
for section, content in sections.items():
    folder = os.path.join(base_dir, section)
    os.makedirs(folder, exist_ok=True)

    # Metadata
    with open(os.path.join(folder, f"{section}_metadata.json"), "w") as f:
        json.dump(content["metadata"], f, indent=2)

    # Data
    for i in range(2):  # Save two copies of each dataset
        content["data"].to_csv(os.path.join(folder, f"{section}_data_{i}.csv"), index=False)