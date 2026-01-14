import pandas as pd
from persistency.io import _validate_two_column_input

def test_validate_two_column_input_smoke():
    df = pd.DataFrame({"NBRx": [10, 12], "TRx": [10, 18]})
    out = _validate_two_column_input(df)
    assert list(out.columns) == ["t", "nbrx", "trx"]
    assert out["t"].tolist() == [1, 2]
