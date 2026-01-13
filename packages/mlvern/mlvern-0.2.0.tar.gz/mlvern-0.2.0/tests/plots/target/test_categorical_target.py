from pathlib import Path


def test_target_vs_feature_categorical(run_eda, mlvern_dir, iris_df):
    df = iris_df.copy()
    df["target"] = df["target"].astype(str)
    res = run_eda(df, target="target")
    expected = (Path(mlvern_dir)
                / "plots" / "eda" / "target_vs_features"
                / "sepal length (cm)_vs_target.png")
    assert str(expected) in res["plots"]
    assert expected.exists()
