# This file contains all instructions (context needed to run a given task) to be provided to a GenAI model.
# The instructions are concatenated with the template and other needed data. 

######## ------ PART 2: RELEVANT FIELD SELECTION ------- #########

# MODULE TO CREATE COLUMN CODE-QUESTION MAPPING
# column_mapping_instructions = """Those two questionnaires gave, after survey implementation, a set of datasets. The names of those datasets have three main parts and help create the link between the questionnaire and the Stata databases. The first part of the data sets’ names refers to the number of sections in the questionnaire. For example, s00 relates to section 00 of the questionnaire. Then, the second part refers to the type of questionnaire that has generated the database. This second part is the same for all variables linked to a specific questionnaire. More specifically, a second part, “men,” refers to the household questionnaire, and a second part that is “co,” refers to the community questionnaire. Finally, the third part refers to the country of interest and the year of the survey. This last part is the same across variables and questionnaires for a specific country of the WAEMU’s roster."""
column_mapping_instructions = """The different data sources used by the gaming company—such as player stats, game interaction logs, forum discussions, and external market data—were collected through various internal tools and APIs. Each resulting dataset has column names that follow distinct naming conventions based on the source system.

Typically, column names reflect:
1. The source system or module (e.g., stats, interactions, forum, sentiment, forecast).
2. The entity being measured (e.g., user ID, session time, mood score).
3. The version or date of the logging schema (e.g., v1, 2023Q4).

Some inconsistencies are expected:
- Different datasets may refer to the same entity using different column names (e.g., player_id, user_id, uid, handle).
- Similar metrics may have different units (e.g., time in seconds vs. minutes).
- Columns may need transformation or aggregation before comparison.

The goal is to create a mapping from column codes (e.g., user_id, time_spent, mood_score) to human-readable descriptions of what each column represents, based on the metadata files and the data itself. These descriptions will later be used to align fields across data sources.

Please output your mapping as a list of strings. Each string should look like:
    column_code – description

Example:
    session_length – Total length of gameplay sessions, in minutes
    user_id – Unique player identifier
    avg_sentiment – Average sentiment score of forum posts (-1 to 1)

If column codes are unclear or ambiguous, infer meaning based on surrounding context in the metadata file.
"""

# MODULE TO SELECT THE RELEVANT FIELDS NOW THAT WE HAVE LIST
# field_selection_instructions = """
# Task: You will receieve a 'mapping' object with a list of fields/questions. Select survey fields for inclusion as predictors in learning transfer policies.

# Goal: Identify predictors from LSMS-style household surveys that (a) belong to categories of covariates used in real-world Proxy Means Tests (PMTs), and (b) are plausibly verifiable — either directly (e.g., by enumerators via observation) or indirectly (e.g., through administrative record linkage).

# Key Notes:
# - Select categories of variables, not individual fields. If a material (e.g., wall material) has been used, treat other similar attributes (e.g., roof material) as valid.
# - Apply skeptical judgment: exclude variables that have been used in PMTs but lack a plausible verification path.

# Include Predictors From These Categories:

# 1. Household Demographics
#    - Counts of members: total, by gender, by age groups (0–4, under 18, 18+, 60+/65+), specially abled.
#    - Household head: age, gender, marital status.
#    - Caste, tribe, or ethnicity.

# 2. Human Capital
#    - Education: of head; max for all adults; max for adult women (in years, levels, or literacy).
#    - Number of children enrolled in school.

# 3. Household Assets
#    - Dwelling: per capita rooms or floor space, materials (floor/wall/roof), homeownership.
#    - Amenities: latrine, water, electricity, gas, drainage, cooking fuel, cable.
#    - Durables: radio, TV, fridge, AC, fan, car, bike, computer, etc.
#    - Productive Assets:
#      - Agricultural: land area, livestock, farm equipment (no crop info).
#      - Non-agricultural: e.g., sewing machine if listed.
#    - Financial: Only if verifiable via government (e.g., Kisan credit card).

# 4. Livelihood Activities
#    - Sector + occupation of household head.
#    - Household-owned enterprise.
#    - Public transfers (if verifiable via records).

# 5. Geographic Indicators
#    - Urban/rural classification.
#    - Administrative division(s).
#    - Distance to facilities/markets; presence of key infrastructure.
#    - Local environmental conditions (e.g., drought history).

# 6. Community Characteristics
#    - Presence of services (healthcare, schools).
#    - Infrastructure (paved roads, banks, admin offices).
#    - Population size/density.

# Exclude These Variables (Not Verifiable at Scale):
# - Dwelling age
# - Food security questions
# - Fertilizer use
# - Internet or mobile phone usage
# - Income or remittances


# Provide an answer for each question from the following. Please include the section name, question code, question, whether it is selected, and a reason.
# """
field_selection_instructions = """
Task: You will receive a 'mapping' object with a list of fields/questions from various gaming data sources. Select fields that should be included as predictors for modeling user behavior, engagement, or churn.

Goal: Identify variables from player statistics, in-game behavior, forums, sentiment analysis, and market data that are likely to be:
(a) predictive of player engagement, churn, or monetization outcomes; and
(b) reliable and scalable — i.e., not dependent on subjective self-reporting or unavailable for large user segments.

Key Notes:
- Prefer variables that are structured, consistently logged, and grounded in observable behaviors or scalable analytics (e.g., telemetry, forum metrics, sentiment models).
- Include representative fields across engagement channels (in-game, social, market).
- Avoid fields that are overly noisy, sparsely populated, or based on unverifiable third-party signals.

Include Predictors From These Categories:

1. Player Demographics & Stats
   - Region or location group.
   - Level or rank.
   - Cumulative session time or average session length.

2. In-Game Interactions
   - Clicks, actions, or movement frequency.
   - Items collected or goals achieved.
   - Time spent in specific modes or environments.

3. Forum & Social Activity
   - Post frequency.
   - Sentiment scores (avg, peak, volatility).
   - Engagement type (e.g., help-seeking vs. opinion-sharing).

4. Market Forecasts & External Signals
   - Region-level forecast scores.
   - Ad or promotion engagement metrics (if present).
   - Timing or seasonality indicators.

5. Aggregate Sentiment & Behavior Signals
   - Mood or sentiment scores from combined sources.
   - Anger/frustration indices.
   - Topic clusters (if derived from structured text analysis).

Exclude These Variables (Not Scalable or Informative):
- Free-text fields without structured processing.
- One-off promotional campaign tags.
- User-entered data that is inconsistently available.
- Fields with excessive missingness or known data quality issues.

Provide an answer for each field in the mapping. Include the section name, question code, question text, whether it is selected, and a clear justification for inclusion or exclusion.
"""


######## ------ PART 3: DATASET TRANSFORMATION (AGGREGATION) ------- #########

# the following was obtained by passing EOP Covariate guide through GPT with the following query: "From this guide, can you extract all information that might be relevant
# to someone who is thinking about what columns need to be aggregated to make a dataset per-household and return just that information? Return in Python string format".
# This step can be modularized when needed.
# aggregation_instructions = """
# Here is a concise extraction of all column types to aggregate at the household level from the rubric, grouped by category:

# Required Special Data (not PMT inputs)
# - Total household consumption (incl. non-spending)
# - Household survey weight / expansion factor

# Demographics
# - Total household size
# - Number of male members
# - Number of female members
# - Number of children (0–17)
# - Number of children aged 0–4
# - Number of adults (18+)
# - Number of elderly (60+ or 65+)
# - Number of specially abled members

# Household Head
# - Age
# - Gender
# - Marital status
# - Ethnicity / tribe / caste

# Human Capital
# - Education level of household head (years or level)
# - Maximum education level among adults
# - Maximum education level among female adults
# - Number of children enrolled in school

# Assets & Housing
# - Homeownership status (e.g., owned vs rented)
# - Per capita number of rooms / floor space
# - Floor material
# - Wall material
# - Roof material
# - Type of latrine
# - Water source
# - Lighting source
# - Drainage system
# - Waste collection method
# - Access to electricity
# - Access to gas
# - Cooking fuel type
# - Cable connection
# - Ownership of:
#   - Consumer durables (TV, radio, fridge, fan, etc.)
#   - Transportation (bike, car, etc.)
#   - Furniture (sofa, bed, etc.)
#   - Devices (computer, etc.)
#   - Agricultural assets (land amount, livestock, farm equipment)
#   - Non-agricultural productive assets (e.g., sewing machine)

# Livelihood
# - Sector of employment of household head
# - Occupation of household head
# - Ownership of household enterprise
# - Receipt of public transfers (verifiable)

# Geographic Info
# - Urban/rural classification
# - Administrative region identifiers
# - Distance to:
#   - District center
#   - Market
#   - Post office
# - Environmental factors (e.g., rainfall, if applicable)

# Community Characteristics
# - Presence of:
#   - Healthcare provider in community (doctor, midwife)
#   - Infrastructure (paved roads, banks, gov. offices)
# - Population size / density of community
# """

# aggregation_instructions = """These are the suggested aggregated columns:
# # Required Special Data
# - total_consumption
# - household_weight

# # Demographics
# - household_size
# - num_male_members
# - num_female_members
# - num_children_0_17
# - num_children_0_4
# - num_adults_18_plus
# - num_elderly_60_plus
# - num_specially_abled

# # Household Head
# - head_age
# - head_gender
# - head_marital_status
# - head_ethnicity_or_caste

# # Human Capital
# - head_education_level
# - max_education_adults
# - max_education_female_adults
# - num_children_enrolled_in_school

# # Assets & Housing
# - homeownership_status
# - per_capita_rooms
# - floor_space
# - floor_material
# - wall_material
# - roof_material
# - latrine_type
# - water_source
# - lighting_source
# - drainage_system
# - waste_collection
# - has_electricity
# - has_gas
# - cooking_fuel_type
# - has_cable_connection
# - owns_tv
# - owns_radio
# - owns_fridge
# - owns_fan
# - owns_ac
# - owns_computer
# - owns_bicycle
# - owns_motorbike
# - owns_car
# - owns_sofa
# - owns_bed
# - land_owned
# - owns_livestock
# - owns_farm_equipment
# - owns_non_agri_productive_assets

# # Livelihood
# - head_employment_sector
# - head_occupation_type
# - owns_enterprise
# - receives_verifiable_transfers

# # Geographic Info
# - is_urban
# - admin_region_code
# - distance_to_district_center
# - distance_to_market
# - distance_to_post_office
# - rainfall_history_indicator

# # Community Characteristics
# - has_doctor_in_community
# - has_midwife_in_community
# - has_paved_roads
# - has_banking_facility
# - has_gov_office
# - community_population
# - community_density

# Columns you will ALWAYS need are:
# - hhid

# The dataset to transform is called generated_dataset.csv.
# """

aggregation_instructions = """These are the suggested aggregated columns for transforming player and game analytics data:

# Core Identifiers
- player_id (required for all aggregation)

# Player Profile
- region
- level
- total_sessions
- avg_session_length
- total_playtime_minutes

# In-Game Behavior
- total_clicks
- total_items_collected
- total_time_spent_seconds
- avg_items_per_session
- avg_click_rate_per_minute

# Forum & Social Activity
- total_forum_posts
- avg_sentiment_score
- sentiment_volatility
- max_anger_index
- avg_help_vs_opinion_ratio

# Market & External Forecasts
- region_forecast_score
- engagement_seasonality_index
- promo_period_flag

# Aggregate Sentiment & Mood
- avg_mood_score
- max_mood_score
- avg_anger_index

# Custom Computed Features
- activity_diversity_index (based on variation across sources)
- sentiment_mismatch_flag (if mood diverges from behavior)

Columns you will ALWAYS need are:
- player_id

The dataset to transform is found at {data_file_path}.
"""
