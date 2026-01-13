1. Navigate to the folder sample_apps
cd Progress.Observability.Instrumentation/sample_apps

2. Use .env.example file as a template and create .env file in the folder

3. The progress_observability-0.1.0-py3-none-any.whl file will be provided. Place it in the sample_apps folder

4. Install the dependacies 
uv sync
uv pip install --force-reinstall progress_observability-0.1.0-py3-none-any.whl

5. Run the scripts 
uv run test_azure_langchain.py
