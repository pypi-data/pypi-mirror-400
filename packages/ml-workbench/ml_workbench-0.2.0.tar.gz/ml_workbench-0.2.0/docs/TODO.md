# In dataset config
- [x] remove "column" option in dataset configuration
- [x] add "columns" specification
- [x] add "__all__" specification


# Experiment Runner:
### Immediate
- [x] Add mlflow to dependencies: `uv add mlflow`
- [x] Test with actual Databricks MLFlow
- [x] Test with multiple models simultaneously
- [ ] Add more comprehensive integration tests
- [ ] Create separate transformers/pipelines for _TREE_TYPES and _SCALE_FRIENDLY estimators

### Future
- [ ] Implement hyperparameter tuning execution
- [ ] Add cross-validation support
- [x] Create CLI interface for running experiments
- [ ] Add progress bars for long operations
- [ ] Implement caching for intermediate results
- [ ] Add parallel execution for multiple models
- [ ] Create model comparison reports
- [ ] Add SHAP value integration
- [ ] Support custom transformers
- [ ] Package as a PIP package
- [ ] Implement configuration for ColumnTransformer (data pipeline definition) 
- [ ] Default ColumnTransformer for various types of sklearn estimators 
