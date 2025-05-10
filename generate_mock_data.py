import pandas as pd
import numpy as np
import os
from fpdf import FPDF

# Set up output directory
base_dir = "data/game_data_upload"
os.makedirs(base_dir, exist_ok=True)

# --------- Helper to create PDFs ---------
def create_pdf(path, text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    for line in text.split('\n'):
        pdf.multi_cell(0, 10, line)
    pdf.output(path)

# --------- Task Description ---------
task_description_text = (
    "TASK: Analyze cross-source game analytics data to understand user engagement drivers.\n"
    "We want to:\n"
    "- Identify behaviors that correlate with increased playtime.\n"
    "- Understand player sentiment impact on churn.\n"
    "- Correlate forum activity with in-game performance.\n"
    "- Link market forecasts with gameplay patterns.\n"
)
create_pdf(os.path.join(base_dir, "task_description.pdf"), task_description_text)

# --------- Data Documentation ---------
documentation_text = (
    "DATA DOCUMENTATION\n"
    "==================\n\n"
    "1. player_stats.csv\n"
    "- player_id: Unique user identifier\n"
    "- session_length: Time in minutes\n"
    "- level: Current game level\n"
    "- region: Region code\n\n"
    "2. game_interactions.csv\n"
    "- user_id: User identifier (note different name)\n"
    "- num_clicks: Count of user interactions\n"
    "- items_collected: Number of in-game items\n"
    "- time_spent: Time spent in seconds\n\n"
    "3. forum_discussions.csv\n"
    "- uid: Unique user handle\n"
    "- post_count: Number of forum posts\n"
    "- avg_sentiment: Scaled -1 to 1\n\n"
    "4. market_forecasts.csv\n"
    "- region_code: Game region\n"
    "- forecast_score: Marketing engagement forecast\n\n"
    "5. sentiment_analysis.csv\n"
    "- player_handle: User name\n"
    "- mood_score: Aggregated mood score from forums and reviews\n"
    "- anger_index: Relative anger (0-100)\n"
)
create_pdf(os.path.join(base_dir, "data_documentation.pdf"), documentation_text)

# --------- Section-specific metadata ---------
section_metadata = {
    "player_stats": "player_id (int), session_length (minutes), level (int), region (string)",
    "game_interactions": "user_id (string), num_clicks (int), items_collected (int), time_spent (seconds)",
    "forum_discussions": "uid (string), post_count (int), avg_sentiment (-1 to 1 float)",
    "market_forecasts": "region_code (string), forecast_score (float 0-1)",
    "sentiment_analysis": "player_handle (string), mood_score (float), anger_index (0-100 int)"
}

for section, text in section_metadata.items():
    folder = os.path.join(base_dir, section)
    os.makedirs(folder, exist_ok=True)
    create_pdf(os.path.join(folder, f"{section}_metadata.pdf"), f"METADATA FOR {section.upper()}\n\n{text}")

# --------- Generate CSV data tables ---------
n = 10
regions = ['NA', 'EU', 'AS', 'SA']

# player_stats.csv
player_stats = pd.DataFrame({
    "player_id": [f"user_{i}" for i in range(n)],
    "session_length": np.random.randint(5, 180, n),
    "level": np.random.randint(1, 50, n),
    "region": np.random.choice(regions, n)
})
player_stats.to_csv(os.path.join(base_dir, "player_stats", "player_stats_0.csv"), index=False)

# game_interactions.csv
game_interactions = pd.DataFrame({
    "user_id": [f"user_{i}" for i in range(n)],
    "num_clicks": np.random.randint(10, 500, n),
    "items_collected": np.random.randint(0, 100, n),
    "time_spent": np.random.randint(100, 10000, n)
})
game_interactions.to_csv(os.path.join(base_dir, "game_interactions", "game_interactions_0.csv"), index=False)

# forum_discussions.csv
forum_discussions = pd.DataFrame({
    "uid": [f"user_{i}" for i in range(n)],
    "post_count": np.random.randint(0, 50, n),
    "avg_sentiment": np.round(np.random.uniform(-1, 1, n), 2)
})
forum_discussions.to_csv(os.path.join(base_dir, "forum_discussions", "forum_discussions_0.csv"), index=False)

# market_forecasts.csv
market_forecasts = pd.DataFrame({
    "region_code": regions,
    "forecast_score": np.round(np.random.uniform(0, 1, len(regions)), 2)
})
market_forecasts.to_csv(os.path.join(base_dir, "market_forecasts", "market_forecasts_0.csv"), index=False)

# sentiment_analysis.csv
sentiment_analysis = pd.DataFrame({
    "player_handle": [f"user_{i}" for i in range(n)],
    "mood_score": np.round(np.random.uniform(-1, 1, n), 2),
    "anger_index": np.random.randint(0, 100, n)
})
sentiment_analysis.to_csv(os.path.join(base_dir, "sentiment_analysis", "sentiment_analysis_0.csv"), index=False)

# import pandas as pd
# import numpy as np
# import os
# import json

# # Set up directory structure
# base_dir = "data/test_uploads"
# os.makedirs(base_dir, exist_ok=True)

# # Create sample task description
# with open(os.path.join(base_dir, "task_description.txt"), "w") as f:
#     f.write("Merge and unify household and community-level data to prepare for a poverty analysis task.")

# # Create sample data documentation
# with open(os.path.join(base_dir, "data_documentation.txt"), "w") as f:
#     f.write("This dataset includes household and community information from a survey in Region X.\n"
#             "Each section includes metadata and data files. Column names follow the sXXqYY format.\n"
#             "You should use metadata files to match column codes with question text.")

# # Generate metadata and data for two sections: household and community
# sections = {
#     "GSEC1": {
#         "metadata": {
#             "s01q01": "How many people live in the household?",
#             "s01q02": "What is the household's main source of income?",
#             "s01q03": "Is the household head employed?"
#         },
#         "data": pd.DataFrame({
#             "s01q01": np.random.randint(1, 10, 5),
#             "s01q02": np.random.choice(["farming", "business", "employment"], 5),
#             "s01q03": np.random.choice([True, False], 5)
#         })
#     },
#     "GSEC2": {
#         "metadata": {
#             "s02q01": "What is the primary language spoken in the village?",
#             "s02q02": "Is there a health clinic in the village?",
#             "s02q03": "What type of roads connect the village?"
#         },
#         "data": pd.DataFrame({
#             "s02q01": np.random.choice(["Luganda", "Swahili", "English"], 5),
#             "s02q02": np.random.choice([True, False], 5),
#             "s02q03": np.random.choice(["paved", "dirt", "gravel"], 5)
#         })
#     }
# }

# # Save metadata and data
# for section, content in sections.items():
#     folder = os.path.join(base_dir, section)
#     os.makedirs(folder, exist_ok=True)

#     # Metadata
#     with open(os.path.join(folder, f"{section}_metadata.json"), "w") as f:
#         json.dump(content["metadata"], f, indent=2)

#     # Data
#     for i in range(2):  # Save two copies of each dataset
#         content["data"].to_csv(os.path.join(folder, f"{section}_data_{i}.csv"), index=False)