import pandas as pd
from root_cleaning.text_cleaner import clean_text




def test_text_cleaning_basic():
df = pd.DataFrame({"name": [" Alice ", "BOB!!", None]})
cleaned_df, report = clean_text(df)


assert cleaned_df["name"].iloc[0] == "Alice"
assert cleaned_df["name"].iloc[1] == "BOB"
assert cleaned_df["name"].iloc[2] == "Unknown"
assert report["status"] is True
assert report["details"]["text_cleaned"] is True