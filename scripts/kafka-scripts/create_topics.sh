#!/bin/bash
replication_factor=1

/usr/bin/kafka-topics --bootstrap-server localhost:9092 --create --topic NewsTopic1 --partitions 5 --config retention.ms=$((30 * 3600 * 1000)) --if-not-exists  
/usr/bin/kafka-topics --bootstrap-server localhost:9092 --create --topic NewsTopic2 --partitions 5 --config retention.ms=$((30 * 3600 * 1000)) --if-not-exists  
/usr/bin/kafka-topics --bootstrap-server localhost:9092 --create --topic NewsTopic3 --partitions 5 --config retention.ms=$((30 * 3600 * 1000)) --if-not-exists  
/usr/bin/kafka-topics --bootstrap-server localhost:9092 --create --topic NewsTopic4 --partitions 5 --config retention.ms=$((30 * 3600 * 1000)) --if-not-exists  
/usr/bin/kafka-topics --bootstrap-server localhost:9092 --create --topic NewsTopic5 --partitions 5 --config retention.ms=$((30 * 3600 * 1000)) --if-not-exists  


