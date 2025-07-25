# mini-max (Work in Progress)
MiniMax is an open-sourced droid built to accelerate research and engineering tasks through intelligent experimentation and rapid prototyping.

## Table of Contents

1. [Usage](#Usage)
1. [Requirements](#requirements)
1. [Development](#development)
    1. [Installing Dependencies](#installing-dependencies)
    1. [Defining and Running Experiments](#defining-and-running-experiments)
    1. [Front End UI Prototyping](#front-end-ui-prototyping)
    1. [Serving FastApi Locally](#serving-fastapi-locally)
    1. [Testing](#testing)
    1. [Code Formatting](#code-formatting)
1. [Outcomes](#outcomes)
1. [Architecture](#architecture)
1. [Roadmap](#roadmap)

## Usage
>MiniMax is a research and engineering assistant, bridging the gap between software and the physical world. This repo is intended to be a base prototyping and research setup for sensor data collection, Exploratory Data Analysis, model development, inference on edge, and intelligent analysis for a variety of use cases. It is not intended for production, just a lower friction env for prototyping and research. There's an offline mode that opperates without wifi, and an optional online mode that leverages more powerful LLMs.

## Requirements

- Python 3.11.10 or higher
- Pip 24.2 or higher
- Uv 0.7.13 or higher

## Development

## Configure .env

To use the optional online mode, create a `.env` file in your root dir.
```
touch .env
```

Then store your api keys there
```
OPENAI_API_KEY=you_know_the_drill
...
```

### Installing Dependencies

From within the root directory:

```
uv sync
```

or 
```
uv pip install ".[jetson]"
```

To create an ipykernel associated with this projects virtual env:
```
uv run python -m ipykernel install --user --name="gm_$(basename $(pwd))" --display-name="gm_$(basename $(pwd))"
```

### Defining and Running Experiments

From within the root directory:

```
uv run jupyter lab
```

**Research**
Experiments are organized locally under the `/experiments` dir. There you will see an `example` folder that contains a summary.ipynb file, and an `observations` folder that contains all the notebooks for my Exploratory Data Analysis and Model Development Iterations.

### Front End UI Prototyping

For development, I'm storing base ui templates in a folder titled `streamlit`. To serve locally, run the following command on the UI you want to serve
Example:
```
uv run streamlit run ./streamlit/text/simple_chat_app.py
```

Other options include:
1. `uv run streamlit run ./streamlit/text/fastapi_chat_app.py`
1. `uv run streamlit run ./streamlit/image/image_classify_app.py`

**Note**
### Serving FastApi Locally

From within the root directory:

```
uv run fastapi dev app/main.py
```

## Running MiniMax via cli
```
minimax start
```
or pass a router.csv file with question, answer, action for offline mode.
```
minimax start --init_file "./new_text.csv"
```

## Run without installing the cli
```
python minimax/cli.py start
```


### Testing

From within the root directory:

```
uv run pytest tests
```

### Code Formatting

For this project I'm using the popular [Python Black Code Formatting](https://github.com/psf/black).

### Outcomes

1. Collect sensor data
1. Run Exploratory Data Analysis
1. Run Model Development Experiments
1. Prototype frontend UIs quickly
1. Leverage lightweight model servering api
1. Prototype with sensors and effectors
1. Leverate LLMs for intelligent analysis and chat wholistically with the droid

### Architecture

- Jetson Orin: For hosting the droid
- FastApi: For inference api
- LanceDB: For vector database and offline mode.
- LangGraph: For agentic control
- Streamlit: For rapid front end prototyping


### Roadmap

- TBD