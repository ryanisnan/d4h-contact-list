# Installation

Clone this repository

`git clone git@github.com:ryanisnan/d4h-contact-list`

# Set up virtual environment

```
virtualenv -p python3 venv && source venv/bin/activate
pip install -r requirements.txt
```

# Set your D4H API key in your environment

```
echo export D4H_API_KEY=<your_api_key_here> > .env
source .env
```

# Running the project

`python3 run.py`
