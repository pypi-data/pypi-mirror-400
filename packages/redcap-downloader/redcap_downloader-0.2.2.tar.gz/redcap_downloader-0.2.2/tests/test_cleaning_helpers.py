import pandas as pd

from redcap_downloader.data_cleaning.helpers import drop_empty_columns, merge_duplicate_columns, replace_strings


class TestCleaningHelpers:
    def test_drop_empty_columns(self):
        df = pd.DataFrame({
            'A': [1, 2, 3],
            'B': [None, None, None],
            'C': [4, 5, 6]
        })
        result = drop_empty_columns(df)
        expected = pd.DataFrame({
            'A': [1, 2, 3],
            'C': [4, 5, 6]
        })
        pd.testing.assert_frame_equal(result, expected)

    def test_merge_duplicate_columns(self):
        df = pd.DataFrame({
            'A': ['1', None, '3'],
            'C': [None, '2', None],
            'B': ['4', '5', '6']
        }).rename(columns={'C': 'A'})
        result = merge_duplicate_columns(df)
        expected = pd.DataFrame({
            'A': ['1', '2', '3'],
            'B': ['4', '5', '6']
        })
        pd.testing.assert_frame_equal(result, expected)

    def test_replace_strings(self):
        series = pd.Series(['apple', 'banana', 'cherry'])
        replacements = {'apple': 'orange', 'banana': 'grape'}
        result = replace_strings(series, replacements)
        expected = pd.Series(['orange', 'grape', 'cherry'])
        pd.testing.assert_series_equal(result, expected)
