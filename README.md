# BookingSystemApp
Software engineering group project

## Setting up

> The `python` command should be replaced by `python3` on Mac systems. 

1. Clone this repositiory to your computer
2. Initialize a virtual environment
```
python -m venv venv
```
3. Activate the virtual environment

**Windows:**
```
./venv/Scripts/activate
```
**Mac:**
```
source venv/bin/activate
```

4. Install requirements
```
pip install -r requirements.txt
```
5. Copy the `.env.sample` file to a new `.env` file, and replace the `DB_PASSWORD` variable with the database password.  Then replace the `DATABASE_URI` with the correct database URI.

## Running the project

```
python -m flask --app __init__ run
```