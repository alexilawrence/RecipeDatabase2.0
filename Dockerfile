# Python image to use.
FROM python:3.12-alpine

# Set the working directory to /app
WORKDIR /RecipeDatabase2.0

# copy the requirements file used for dependencies
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Copy the rest of the working directory contents into the container at /app
COPY . .

# Run app.py when the container launches
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "recipeDBMain:app"]
