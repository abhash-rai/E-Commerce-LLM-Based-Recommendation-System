# E-Commerce LLM Based Recommendation System

Stores e-commerce data (go to [sql_models.py](./db/sql_models.py) for detailed schema) in a sqlite database using SQLModel (main sql component is [sql_db.py](./db/sql_db.py)). Whenever a product is inserted into database using [sql_db.py](./db/sql_db.py), its corresponding product text vector embedding along with product id (for product searching) is stored automatically in Qdrant vector database. FastAPI server [run.py](./run.py) utilizes [sql_db.py](./db/sql_db.py) for fetching and inserting data into database and llm component [llm.py](./llm/llm.py) utilizes [sql_db.py](./db/sql_db.py) for query generation and csv dataset generation for fine tuning of `Google FLAN-T5` (go to [fine-tuning.ipynb](./llm/fine-tuning.ipynb)). 

# Prerequisites

- You must have `Git` installed on your system.
- You must have `Python 3` installed on your system.
- You must have `Docker Desktop` (for hosing qdrant server) installed on your system. Download page: [here](https://www.docker.com/products/docker-desktop/)
- You must have `cuda` installed on your system for llm fine tuning. Find out which is the latest version of CUDA that pytorch supports at: [pytorch.org](https://pytorch.org/) and install that version of cuda. Please refer to [cudas installation guide](https://github.com/entbappy/Setup-NVIDIA-GPU-for-Deep-Learning) for step by step guide for installation.

# Step 1: Clone the repo into your local machine:

Ensure git is installed on your system. Then, open terminal and enter:
```
git clone https://github.com/abhash-rai/E-Commerce-LLM-Based-Recommendation-System.git
```

Open project directory:
```
cd E-Commerce-LLM-Based-Recommendation-System
```

Keep note of the `full path` to the project directory as it will be required in step 2.

# Step 2: Running Qdrant server on Docker

Install docker desktop and check docker installation:
```
docker --version
```

If you get docker version and build text then, enter (make sure Docker Desktop is open and running in your system):
```
docker pull qdrant/qdrant
```

Run qdrant server on docker with below command but replace `<PathToLocalRepo>` portion with the `full path` of the project directory noted in `step 1`:
```
docker run -d --name qdrant -p 6333:6333 -v <PathToLocalRepo>/db/qdrant_storage:/qdrant/storage qdrant/qdrant
```

# Step 3: Creating virtual environment and installing dependencies

Install `virtualenv` library using pip:
```
pip install virtualenv
```

I found python3.12 works well along with the required dependencies so create virtual environment named `.venv` with the same python version:
```
virtualenv -p python3.12 .venv
```

Activate the virtual environment:
```
.venv\Scripts\activate
```

Install dependencies:
```
pip install -r requirements.txt
```

Final dependency to install is pytorch. Before that make sure you know your system OS and installed cudas version. You can check installed cudas version by entering:
```
nvcc --version
```

Find out which is the versions of CUDA that pytorch supports at: [pytorch.org](https://pytorch.org/) and see if one of those version is the one you installed on your system. If there is no match then, you need to reinstall cuda to a version that pytorch supports.

Go to same [pytorch.org](https://pytorch.org/) site and scroll down to 'Install PyTorch' section and select relevant options to get pytorch installation command for your system. For my windows OS with CUDA 12.4 command was (yours might be different according to your system):
```
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```

# Step 4: (Optional) Populate database with synthetic data

You can start experimenting with synthetic data which is not necessary but recommended for trying out. To populate synthetic data run below command, which will create sqlite database and vectore collection for products automatically:
```
python populate_synthetic_db.py
```

# Step 5: Fine Tune LLM

Open [fine-tuning.ipynb](./llm/fine-tuning.ipynb)) in VS Code and select the previously generated virtual environment `.venv` as the kernel. Then, run each cell of the notebook which will ultimately generate csv dataset for fine tuning, tune `Google FLAN-T5` llm model, and save the fine tuned model locally for generating recommendations.

# Step 6: Run the server

[run.py](./run.py) has already builtin functionality to run fastapi server with uvicorn. So, run command:
```
python run.py
```

Wait a while until server is fully loaded, then to try out the APIs go to: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs). There are 3 APIs for searching products, recommending product to a customer, and storing recommendation feedback.

You can modify [run.py](./run.py) and [sql_db.py](./db/sql_db.py) to add endpoints to perform CRUD operations on every models detailed in [sql_models.py](./db/sql_models.py) to make a full fledged server.
