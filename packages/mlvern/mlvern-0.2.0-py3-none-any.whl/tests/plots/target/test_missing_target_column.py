def test_missing_target_column_should_not_create_target_plots(
    run_eda, mlvern_dir, iris_df
):
    res = run_eda(iris_df, target="not_a_col")
    # ensure no target_vs_features entries
    assert not any("target_vs_features" in p for p in res["plots"])
