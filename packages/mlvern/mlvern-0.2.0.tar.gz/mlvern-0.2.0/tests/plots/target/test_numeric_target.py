import os
from pathlib import Path

from mlvern.visual.eda import basic_eda


def test_target_vs_feature_numeric(run_eda, mlvern_dir, iris_df):
    res = run_eda(iris_df, target="target")
    # numeric target will produce xy scatter per numeric feature
    expected = (Path(mlvern_dir) / "plots" / "eda"
                / "target_vs_features" / "sepal length (cm)_vs_target.png")
    assert str(expected) in res["plots"]
    assert expected.exists()


def test_numeric_target(tmp_mlvern_dir, sample_df):
    out = basic_eda(
        sample_df,
        output_dir="unused",
        mlvern_dir=tmp_mlvern_dir,
        target="target",
    )
    plots = out["plots"]
    # Expect target_vs_features plots for numeric columns
    assert any("_vs_target.png" in p for p in plots)
    for p in [p for p in plots if p.endswith("_vs_target.png")]:
        assert os.path.isfile(p)
