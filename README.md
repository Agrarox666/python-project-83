# Page Analyzer (educational project)
Hexlet tests and linter status: [![Actions Status](https://github.com/Agrarox666/python-project-83/workflows/hexlet-check/badge.svg)](https://github.com/Agrarox666/python-project-83/actions)
Code cleanliness: [![Maintainability](https://api.codeclimate.com/v1/badges/2d6bb0c4fabd2caa7a0d/maintainability)](https://codeclimate.com/github/Agrarox666/python-project-83/maintainability)

Try it: https://firstpageanalyzer74.onrender.com

## Contents
- [Requirements](#requirements)
- [Packages](#packages)
- [Installation](#installation)
- [Quick start](#quick-start)

## Requirements
1. Git
2. Linux-like OS or WSL (on Windows)
3. Python ^3.10
4. PostgreSQL ^14.0

## Packages
1. Flask v2.3.3 https://flask.palletsprojects.com/en/3.0.x/
2. Requests v2.31.0 https://requests.readthedocs.io/en/latest/
3. Gunicorn v20.1.0 https://docs.gunicorn.org/en/latest/
4. Psycopg v2.9.9

## Installation
1. Clone this repository to your computer by command:
```sh
   git clone git@github.com:Agrarox666/python-project-83.git
```

## Quick start
1. Install poetry and db (postgresql) on your PC and by command (from the main directory):
```sh
   make build
```
2. Start gunicorn server by command:
```sh
   make start
```
A simple page analyzer is running on your computer and ready to go!

 
