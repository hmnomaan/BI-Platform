import pandas as pd
from bi_dashboard.factory import build_chart


def test_build_line_chart():
    df = pd.DataFrame({"date": ["2023-01-01", "2023-01-02"], "sales": [100, 200]})
    cfg = {"type": "line", "x": "date", "y": "sales", "title": "S"}
    fig = build_chart(cfg, df)
    assert fig is not None


def test_build_pie_chart():
    df = pd.DataFrame({"cat": ["A", "B"], "val": [1, 2]})
    cfg = {"type": "pie", "names": "cat", "values": "val"}
    fig = build_chart(cfg, df)
    assert fig is not None
