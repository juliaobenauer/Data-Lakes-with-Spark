# Project: Data Lakes with Spark

## 1. Introduction

A music streaming startup, Sparkify, has grown their user base and song database even more and want to move their data warehouse to a data lake. Their data resides in S3, in a directory of JSON logs on user activity on the app, as well as a directory with JSON metadata on the songs in their app.

As their data engineer, you are tasked with building an ETL pipeline that extracts their data from S3, processes them using Spark, and loads the data back into S3 as a set of dimensional tables. This will allow their analytics team to continue finding insights in what songs their users are listening to.

You'll be able to test your database and ETL pipeline by running queries given to you by the analytics team from Sparkify and compare your results with their expected results.

## 2. Project Description

In this project, you'll apply what you've learned on Spark and data lakes to build an ETL pipeline for a data lake hosted on S3. To complete the project, you will need to load data from S3, process the data into analytics tables using Spark, and load them back into S3. You'll deploy this Spark process on a cluster using AWS.

## 3. Schema for Song Play Analysis

### 3.1. Fact Table

1. songplays - records in log data associated with song plays i.e. records with page NextSong
    - songplay_id, start_time, user_id, level, song_id, artist_id, session_id, location, user_agent

### 3.2. Dimension Tables

1. users - users in the app
    - user_id, first_name, last_name, gender, level
2. songs - songs in music database
    - song_id, title, artist_id, year, duration
3. artists - artists in music database
    - artist_id, name, location, lattitude, longitude
4. time - timestamps of records in songplays broken down into specific units
    - start_time, hour, day, week, month, year, weekday

### 4. Project Files

- etl.py: reads data from S3, processes that data using Spark, and writes them back to S3
- dl.cfg: contains AWS credentials
- README.md: provides discussion on process and decisions

## 5. How the ETL pipeline was set up  
Building an ETL pipeline that 
- first extracts data from S3  
- then processes them using Spark, and loads the data back into S3 as a set of dimensional tables  
Tables are loaded into S3 in parquet format.  

## 6. How to run scripts

1. Set environment variables `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in `dl.cfg`.  
2. Connect to the destination S3 bucket and replace the output_data variable in the main() function with the S3 bucket URI.    
3. Run the ETL pipeline using `python etl.py`  

## 7. Disclaimer
Data and project information were kindly provided by [Udacity](https://www.udacity.com/).

