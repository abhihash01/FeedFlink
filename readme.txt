Uncompress the directory and navigate to it.
After uncompressing make sure the trained_models directory is present in it already that contains the files for processing and the trained models for categories.

First we need to install the requirements. 

pip install -r requirements.txt


We need the nltk wordnet and lexicon for text processing. 

So run 
python download_nltk_data.python

Once this is run, the nltk directory is created and stored in the project root which would contain the wordnet and lexicon. 


Create a news api key and add it in the .env file. Already added an exitent api here.

Setup the secrets for kafka ui in the kafka-ui directory- config.yml file. Have previously set username for "username" and "password" for password.

Now setting up user information for the airflow user that will be used for setting up airflow. The username, firstname, lastname, email and password needs to be set. All of these are in the secrets folder. 
Defaults: Username:"username", firstname:"firstname", lastname: "lastname", email: "user@email.com", password: "password"

Now we run

docker compose up airflow-init -d

This runs the docker initialisation container that creates the airflow user and sets up password and other information for it. 

Now we run

docker compose up -d

To check status at all times:

kafka-ui: http://localhost:7070/ - user the default "username", "password"

spark-ui: http://localhost:9090/ - requires no password

airflow-websersver: http://localhost:8080/ - use the default "username", "password"

This will fire up all the required containers like spark-master, spark-worker, airflow-webserver, airflow-worker, redis, mongodb, zookeeper, kafka ui and our news client. 


Now to create topics, we need to enter the kafka broker container and create the topics. For this we docker

docker exec -it kafka-broker1 bash -c "./scripts/.create_topics.sh"


Once this is done, we can enter the topics subsection in the kafka ui and look at the topics. 5 topics - NewsTopic1, NewsTopic2, NewsTopic3,NewsTopic4, NewsTopic5 is created. 


Now to run all these, we access the airflow web server. First we see all our dags dag_generation, dag_transformation, dag_suggestion, dag_engagement. 

We have to establish the spark connection to airflow for running the spark streams. So we go to adming and setup new connection. 

The field attributes for this would be  connection-id: spark-connection, Connection-Type: Spark, Host: spark://spark-master and Port: 7077

Now we have to toggle all the DAGS to active state. 

Now trigger the dag_news_generation dag. This will do the fetching of news and dump it in the NewsTopic1. We can cross verify this by entering the kafka ui and looking for the messages in the NewsTopic1

Next we trigger the dag_news_transformation. This will do the filtering of news and store them in MongoDB. This DAG also does the modelling, prediciton and classification of the categories. 
We can cross check filtered news in NewsTopic2 and predictable set of news items in NewsTopic3. 

Cross check the filtered content in MongoDB by accessing the filtered news table in MongoDB.

docker exec -it mongodb mongo --eval "db.filtered_news.countDocuments()"



Now create user on 

http://localhost:8501/

Now trigger the news_suggestion dag again to have the relevant news available. 

On the user window, we can interact with the news articles and all of this will be published into the NewsTopic5. 

Cross verify contnet on mongo by running db.users.find()

Now we can store the interactions in the storage by triggering the dag_engagement which can be cross verified from the mongodb.

Fin



