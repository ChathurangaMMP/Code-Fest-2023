# CodeFest - 2023

## Install dependencies

```
cd codefest/
pip install -r requirements.txt
```

## Run the program

To run the program, we only need to run the **fastapi_app.py** file. Use following command to run the file.

```
cd codefest/main_program/
python -m uvicorn fastapi_app:app --app-dir . --port 5000 --host 127.0.0.1 --access-log --reload
```