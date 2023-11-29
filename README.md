# Fast API Project

REST API implementation for a basic social network.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
  - [Database schema](#database-schema)
- [Getting Started](#getting-started)
  - [Installation](#installation)
  - [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [License](#license)


## Introduction

[Ongoing unfinished project - the current version is for demonstration purposes only]

This project simulates a REST API implementation for a simple social network. This project is based on the [freeCodeCamp's Python API Development course](https://www.freecodecamp.org/news/creating-apis-with-python-free-19-hour-course/), and its purpose is to become acquainted with a series of concepts and tools such as:

- REST API architecture.
- MySQL database setup and integration.
- Database modelling tools: SQLALchemy and Alembic.
- Unit testing with Pytest.
- CI integration with GitHUb actions (and Jenkins).
- App deployment with Heroku.
- Containerization with Docker.



## Features

Current:

- Python Fast API as the core of the API implementation.
- Pydantic validation for serialization and deserialization processes.  
- Default password hashing.
- JWT token authentication.
- MySQL database setup.
- Database model and tables set via SQLAlchemy.
- Alembic for database related migrations.
- CORS implementation.
- Unit testing with Pytest.

Future:

- Production deployment with Heroku.
- Containerization with Docker of app and database.
- Continuous integration (CI) with GitHub Actions.


These tables are stored as CSV files in the 'data_sets' folder.

### Database schema

The database schema, `social_network`, has currently, the following tables:

- `users`
- `posts`
- `votes`
- `social_groups`
- `group_members`

The data for these tables has been generated through multiples sources: 
- List of posts (`title`) taken from the Data Science Stack Exchange database.
- Random processes, e.g. post upvotes.
- Users names via [randomwordgenerator](https://randomwordgenerator.com/name.php)
- Social groups information generated via ChatGPT.

![erd_social_network](/img/social_network_erd.png)

## Getting Started

[]

### Prerequisites

Support platforms for the project:

- Install [poetry](https://python-poetry.org/) to isolate the required dependencies into a virtual environment (requirements.txt also available).
- Install [MySQL](https://dev.mysql.com/downloads/mysql/)
- Use [MySQL Workbench](https://dev.mysql.com/downloads/workbench/) to create a MySQL server create and access the project's database. 
- Experiment and test the app with [Postman](https://www.postman.com/downloads/).

### Installation

- Generate a virtual environment and install requirements with poetry (Linux):
    - $ `cd [projects_directory]`
    - $ `poetry install`

- Install MySQL

- Create a MySQL server via CLI or MySQL Workbench UI by setting (these are the same values that must be set in the .env file, to the exception of the 'Connection Name'):
    - Connection Name
    - Connection Method
    - Hostname
    - Port
    - Username
    - Password
    - Default Schema

### Configuration

#### Setting the environment variables

Env file environmental variables are set and validated via Pydantic in 'version_12/src/env_models_12.py'. `config_path` is an environment variable with the path to the folder containing the project .env file; `dotenv_path` is the full path for the .env file. Variables that must be set:

For database connection:

    `USER_NAME`
    `SECRET_KEY`
    `PORT`
    `HOST`
    `DATABASE`


For authorization token creation:

    `AUTH_SECRET_KEY`
    `AUTH_ALGORITHM`
    `AUTH_ACCESS_TOKEN_EXPIRE_MINUTES`

## Usage

Examples of HTTP requests endpoints and purposes:

- Create/post a user's session: "localhost:8000/login"

- Get user information by user ID; e.g. get user 1 : "localhost:8000/users/id/1"
- Get user information by user name; e.g. get user Kim Kent : "localhost:8000/users/name/kim_kent"
- Delete user via, e.g.:
    - ID: "localhost:8000/users/id/1"
    - Name:  "localhost:8000/users/name/kim_kent"

- Get users posts: "localhost:8000/posts/my_posts"
- Get any post by its ID; e.g. get post 1: "localhost:8000/posts/1"
- Post a post: "localhost:8000/posts"


- Get user's social groups that he/she is member or admin of:  "localhost:8000/social_groups/my_social_groups"
- Create/post a social group (only for logged in users): "localhost:8000/social_groups"

- Post a upvote or a downvote: "localhost:8000/votes"

## API Documentation

Fast API / OpenAPI generates two different interactive API documentation UI versions that can be accessed via the following end points (change port according to the one set in the .env file): 

    - Swagger UI: `localhost:8000/docs`
    - ReDoc UI: `localhost:8000/redoc`

## License

MIT license.


