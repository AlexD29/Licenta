.PHONY: run-flask run-react

run-flask:
    python run.py

run-react:
    cd app/react_app && npm start
