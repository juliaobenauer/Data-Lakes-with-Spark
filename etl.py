import configparser
import os
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import TimestampType, DateType, IntegerType
from pyspark.sql.window import Window
from datetime import datetime

config = configparser.ConfigParser()
config.read('dl.cfg')

os.environ['AWS_ACCESS_KEY_ID']=config['AWS']['AWS_ACCESS_KEY_ID']
os.environ['AWS_SECRET_ACCESS_KEY']=config['AWS']['AWS_SECRET_ACCESS_KEY']

def create_spark_session():
    # broadcastTimeout statement added based on https://knowledge.udacity.com/questions/312437
    spark = SparkSession \
        .builder \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:2.7.0") \
        .config("spark.sql.broadcastTimeout", "36000") \
        .getOrCreate()
    return spark


def process_song_data(spark, input_data, output_data):
    """
    Read song data from S3.
    Create the songs_table and artists_table.
    Load data back to S3.
    """
    # get filepath to song data file
    song_data = os.path.join(input_data, 'song_data', '*', '*', '*')

    # read song data file
    df = spark.read.json(song_data)

    # extract columns to create songs table
    songs_table = df.select(['song_id', 'title', 'artist_id', 'year', 'duration'])

    # write songs table to parquet files partitioned by year and artist
    songs_table.write.parquet(os.path.join(output_data, 'songs'), partitionBy=['year', 'artist_id'])

    # extract columns to create artists table
    columns = ['artist_name', 'artist_location', 'artist_latitude', 'artist_longitude']
    columns = [col + ' as ' + col.replace('artist_', '') for col in columns]
    artists_table = df.selectExpr('artist_id', *columns)

    # write artists table to parquet files
    artists_table.write.parquet(os.path.join(output_data, 'artists'))


def process_log_data(spark, input_data, output_data):
    """
    Read log data from S3.
    Create the users table, songplays_table and time_table.
    Load data back to S3.
    """
    # get filepath to log data file
    log_data = os.path.join(input_data, 'log_data', '*', '*')

    # read log data file
    df = spark.read.json(log_data)
    df = df.withColumn('user_id', df.userId.cast(IntegerType()))

    # filter by actions for song plays
    df = df.where(df.page == 'NextSong')

    # extract columns for users table
    users_table = df.selectExpr(['user_id', 'firstName as first_name', 'lastName as last_name', 'gender', 'level', 'ts'])
    users_window = Window.partitionBy('user_id').orderBy(F.desc('ts'))
    users_table = users_table.withColumn('row_number', F.row_number().over(users_window))
    users_table = users_table.where(users_table.row_number == 1).drop('ts', 'row_number')

    # write users table to parquet files
    users_table.write.parquet(os.path.join(output_data, 'users'))

    # create timestamp column from original timestamp column
    get_timestamp = F.udf(lambda ts: datetime.fromtimestamp(ts/1000).isoformat())
    df = df.withColumn('start_time', get_timestamp('ts').cast(TimestampType()))

    # extract columns to create time table
    time_table = df.select('start_time')
    time_table = time_table.withColumn('hour', F.hour('start_time'))
    time_table = time_table.withColumn('day', F.dayofmonth('start_time'))
    time_table = time_table.withColumn('week', F.weekofyear('start_time'))
    time_table = time_table.withColumn('month', F.month('start_time'))
    time_table = time_table.withColumn('year', F.year('start_time'))
    time_table = time_table.withColumn('weekday', F.dayofweek('start_time'))

    # write time table to parquet files partitioned by year and month
    time_table.write.parquet(os.path.join(output_data, 'time'), partitionBy=['year', 'month'])

    # read in song data to use for songplays table
    song_df = spark.read.json(os.path.join(input_data, 'song_data', '*', '*', '*'))

    # extract columns from joined song and log datasets to create songplays table
    df = df.orderBy('ts')
    df = df.withColumn('songplay_id', F.monotonically_increasing_id())
    song_df.createOrReplaceTempView('songs')
    df.createOrReplaceTempView('events')

    songplays_table = spark.sql("""
        SELECT
            e.songplay_id,
            e.start_time,
            e.user_id,
            e.level,
            s.song_id,
            s.artist_id,
            e.sessionId as session_id,
            e.location,
            e.userAgent as user_agent,
            year(e.start_time) as year,
            month(e.start_time) as month
        FROM events AS e
        LEFT JOIN songs AS s ON
            e.song = s.title AND
            e.artist = s.artist_name AND
            ABS(e.length - s.duration) < 2
    """)

    # write songplays table to parquet files partitioned by year and month
    songplays_table.write.parquet(os.path.join(output_data, 'songplays'), partitionBy=['year', 'month'])


def main():
    """
    Extracts songs and events data from S3.
    Transform data into fact and dimension tables using Spark.
    Load tables into S3 in parquet format.
    """
    spark = create_spark_session()
    input_data = 's3a://udacity-dend/'
    output_data = '<add URI of target S3 bucket here>'

    process_song_data(spark, input_data, output_data)
    process_log_data(spark, input_data, output_data)
    spark.stop()


if __name__ == '__main__':
    main()