from datasanity import analyze_csv

def test_basic():
    import pandas as pd
    df = pd.DataFrame({"x": [1,2,3,4], "y":[10,20,30,40]})
    df.to_csv("tmp.csv", index=False)

    r = analyze_csv("tmp.csv")
    assert r["rows"] == 4
    assert "missing_pct" in r
