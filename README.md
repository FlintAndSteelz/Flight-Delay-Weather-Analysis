# Flight-Delay-Weather-Analysis
Flight Delay and Weather Analysis at JFK Airport


An Exploratory Data Science Project on Flight Delays and Weather Conditions at John F.Kenedy International Airport (JFK)

## 1. Project Overview

This project aims to analyze flight delays at John F.Kenedy International Airport (JFK) and investigate the potential relationships between flight delays and weather conditions 

The project uses historical flight data and weather data to explore delay patterns, identify potential contributing factors, and generate meaningful insights through data analysis and visualization

The project follows a structured Data Science workflow, including data collection, data cleaning, data integration, exploratory data analysis (EDA), and visualization

## 2. Research Objectives

The main objectives of this project are:
- Analyze historical flight delay patterns at JFK Airport
- Examine the distribution and characteristics of flight delays 
- Investigate the relationship between weather conditions and flight delays
- Identify weather conditions that may be associated with increased flight delays
- Present findings through statistical analysis and data visualization 

## 3. Data source 

The project uses two main categories of data: 

### 3.1 Flight Data
- Source: Bureau of Transportation Statistics (BTS)
- Description: Historical flight information, including scheduled and actual departure/arrival information and delay-related variables 
- Storage location: data/raw/bts/

### 3.2 Weather Data

- Source: TODO - Specify the selected weather data provider
- Description: Historical weather observations relevant to JFK Airport
- Storage location: data/raw/bts/ 

Note: Raw datasets are not stored in this GitHub repository. Each team member is responsible for obtaining the required datasets and placing them in the designated directories according the project instructions 

## 4. Project Structure  
The repository is organized as follows:

Flight-Delay-Weather-Analysis/
│
├── data/
│   ├── raw/
│   │   ├── bts/
│   │   └── weather/
│   ├── interim/
│   └── processed/
│
├── ket_qua/
│
├── notebooks/
│
├── src/
│   └── flight_weather/
│       ├── analyzer.py
│       ├── data_cleaner.py
│       ├── data_loader.py
│       ├── data_merger.py
│       ├── data_source.py
│       ├── visualizer.py
│       └── __init__.py
│
├── tai_lieu/
│
├── tests/
│
├── cau_hinh.yaml
├── chay.py
├── PHAN_CONG.md
├── README.md
├── requirements.txt
└── .gitignore


Directory descriptions:

data/raw/ -> stores original flight and weather datasets 

data/interim/ -> stores intermediate data generated during processing

data/processed/ -> stores cleaned and integrated datasets ready for analysis 

ket_qua/ -> stores generated analysis results and visualizations

notebooks/  -> contains Jupyter notebooks for exploration and experimentation

src/  -> contains the main Python source code

tests/  -> contain project tests 

tai_lieu/ -> stores project documentaion and supporting materials 


### Main Python modules

data_source.py  -> handles data source-relate operations

data_loader.py -> loads datasets into the project

data_cleaner.py -> performs data cleaning and preparation

data_merger.py -> integrates flight and weather datasets

analyzer.py -> perform data analysis

visualizer.py -> creates charts and visualizations

chay.py -> main project entry point 


## 5. Technologies and Tools

The project uses the following technologgies:

- Python 3.13.xx
- Git and Github for version control and collaboration
- Jupyter Notebook for data exploration 
- Python libraries listed in requirements.txt

## 6. Installation Guide

Follow these instructions to set up the project on a local personal computer

### Step 1: Clone the repository

Command: 
-> git clone https://github.com/FlintAndSteelz/Flight-Delay-Weather-Analysis.git

Navigate to the project directory:
-> cd Flight-Delay-Weather-Analysis

### Step 2: Create a virtual environment

Make sure Python 3.13.xx is installed 
-> py -3.13 -m venv .venv

### Step 3: Activate the virtual environment 

For Window PowerShell:
-> .\.venv\Scripts\Activate.ps1

### Step 4: install dependencies

-> python -m pip install --upgrade pip
-> python -m pip install -r requirements.txt

## 7. Data Preparation

After setting up the Python environment, prepare the datasets: 

    1. Obtain the required historical flight dataset from BTS
    2. Obtain the corressponding historical weather dataset drom the selected weather provider
    3. Place the flight dataset in:
        -> data/raw/bts/
    4. Place the weather dataset in:
        -> data/raw/weather/
    5. Follow the data preparation instructions and file naming conventions defined by the project

Important: DO NOT upload raw datasets, intermediate datasets, processed datasets, or the virtual environment to GitHub

## 8. Project workflow

THe project follows the general Data Science workflow below: 

1. Data Collection
2. Data Loading
3. Data Cleaning and Preparation
4. Flight and Weather Data Integration
5. Exploratory Data Analysis (EDA)
6. Statistical Analysis 
7. Data visualization
8. Intepretation of Results
9. Final Reporting 

## 9. How to run the project

The main entry point is: 
-> chay.py

The intended execution command is:
-> python chay.py

The execution workflow and required input files will be documented further as the project implemeation is completed

## 10. Team collaboration

This project is developed collaboratively using Git and Github

Team members should follow these guidelines:

1. Pull the latest version of the main branch before starting new work
2. Create a separate branch for each assigned task
3. Never commit or push changes directly to the main branch. All changes must be submitted through feature branches and Pull Requests. Only reviewed and approved changes can be merged into main.
4. Commit changes with cleare and meaningful messages
5. Push completed work to the corresponding feature branch (sub-branch which is created for your own)
6. Create a pull request for code review
7. Merge changes into main only after the review process

*** Some basic git commands:

1/ Update the main branch (pull code mới nhất từ github)
-> git switch main
-> git pull origin main

2/ Create a feature branch (tạo branch riêng để làm việc) 
-> git switch -c feature/your-task-name

3/ Check status
-> git status 

4/ Stage changes (đưa những file đã sửa vào Staging) 
-> git add .

5/ Commit changes (lưu lại những phiên bản thay đổi)
-> git commit -m "Describe your changes"

6/ Push the feature branch (Đẩy branch lên github) 
-> git push -u origin feature/your-task-name 

7/ Create Pull Request for The Leader to accept 

## 11. Team Members
See PHAN_CONG.md for the project team structure, assinged responsibilities, and task distribution

## 12. Project Status

Current status: Project setup and development in progress

The repository structure, development environment, data processing modules, and analysis workflow will be progressively completed and updated throughout the proejct

Repository: https://github.com/FlintAndSteelz/Flight-Delay-Weather-Analysis


Project: Flight Delay & Weather Analysis at JFK Airport



