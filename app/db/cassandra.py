import os

from cassandra.cluster import Cluster
from cassandra.query import dict_factory


CASSANDRA_CONNECTION_PONITS = ["127.0.0.1"]
CASSANDRA_PORT = 9042
CASSANDRA_KEYSPACE = "app_auth"

cluster = None
session = None

def get_cassandra_session():
    global cluster
    global session

    if session:
        return session

    cluster = Cluster(
        contact_points=CASSANDRA_CONNECTION_PONITS,
        port=CASSANDRA_PORT,
    )

    session = cluster.connect()

    session.execute(
        """
        CREATE KEYSPACE IF NOT EXISTS app_auth 
        WITH replication = {
         'class': 'SimpleStrategy', 
         'replication_factor': 1 
         }
        """
    )

    session.set_keyspace(CASSANDRA_KEYSPACE)
    session.row_factory = dict_factory

    create_table(session)
    return session


def create_table(session):
    session.execute(
        """
        CREATE TABLE IF NOT EXISTS user_by_email (
        email text primary key,
        id uuid,
        full_name_en text,
        full_name_ch text,
        hashed_password text,
        is_active boolean,
        is_verified boolean,
        created_at timestamp,
        updated_at timestamp)
        """
    )

    session.execute(
        """
        CREATE TABLE IF NOT EXISTS user_by_id
        (
            id uuid PRIMARY KEY,
            email text,
            full_name_en text,
            full_name_ch text,
            hashed_password text,
            is_active boolean
            is_verified boolean 
            created_at timestamp,
            updated_at timestamp
        )
        """
    )

    session.execute(
        """
        CREATE TABLE IF NOT EXISTS user_by_created_at
        (
         created_at timestamp,
         id uuid,
         email text,
         full_name_en text,
         full_name_ch text,
         hashed_password text,
         is_active boolean,
         is_verified boolean, 
         updated_at timestamp)"""
    )

def close_cassandra_connection():
    global cluster
    if cluster:
        cluster.shutdown()

