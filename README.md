## Creating a local virtualenv
create a virtual environment and activate it
`python -m venv .venv && source .venv/bin/activate `

## Install 

`pip install pytest`
`pip install pytest sqlalchemy`
`pip install -r requirements.txt` # you can bring in the requirements
`pip install -e src/`

## Running the pytest
`pytest tests/unit`
`pytest tests/integration`
`pytest tests/e2e`