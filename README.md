# cs-price-tracker
A unified price tracker deployed online to track real time price differences between float and steam


## Building the docker image for dev vs prod

For the development environment, this will override the environment variable for the type of environment, it will use the databse docker thats launched in the production version
```bash
ENV=development python3 wsgi.py
```

Running the production environment in headless mode
```bash
docker compose up -d
```

Building the environment, don't rebuild the database because it will destroy the current database
```bash
docker compose build
```

Replacing the build with a new one, image name is specific like web or db if you just want that one
```bash
docker compose up -d {image_name if specified} --force-recreate
```