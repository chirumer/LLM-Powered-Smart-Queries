## Deprecated epxeriments summary:

version_1
-> creating text embeds
-> cosine similarity search amongst the embeds

version_2
-> comparing JSON, Text, Per Field chunking

version_3
-> embeds update module

version_4
-> schema selection

version_5
-> smart query implementation


## Current Approach:
Step 1 -> Use text embedding to retrieve top N schema
Step 2 -> Query GPT-3.5 to select relevant schema [Use few shot prompting]
Step 3 -> Query GPT-3.5 with (Relevant schema + Query)
Step 4 -> Execute the SQL query suggested by GPT-3.5