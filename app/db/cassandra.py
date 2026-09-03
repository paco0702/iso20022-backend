import os

from cassandra.cluster import Cluster
from cassandra.query import dict_factory

CASSANDRA_CONNECTION_POINTS = ["127.0.0.1"]
CASSANDRA_PORT = 9042
CASSANDRA_KEYSPACE = "myapp"

cluster = None
session = None


def get_cassandra_session():
    global cluster
    global session

    if session:
        return session

    cluster = Cluster(
        contact_points=CASSANDRA_CONNECTION_POINTS,
        port=CASSANDRA_PORT,
    )

    session = cluster.connect()

    session.execute(
        """
        CREATE KEYSPACE IF NOT EXISTS myapp
        WITH replication = {
         'class': 'SimpleStrategy', 
         'replication_factor': 1 
         }
        """
    )

    session.set_keyspace(CASSANDRA_KEYSPACE)
    session.row_factory = dict_factory

    create_table(session)
    print("Created tables.")
    return session


def create_table(session):
    session.execute(
        """
        CREATE TABLE IF NOT EXISTS user_by_email
        (
            email text PRIMARY KEY,
            id uuid,
            full_name_en text,
            full_name_ch text,
            hashed_password text,
            is_active boolean,
            is_verified boolean,
            created_at timestamp,
            updated_at timestamp
        )
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
            is_active boolean,
            is_verified boolean,
            created_at timestamp,
            updated_at timestamp
        )
        """
    )

    session.execute(
        """
        CREATE TABLE IF NOT EXISTS user_repair_tasks (
            user_id uuid,
            task_type text,
            email text,
            full_name_en text,
            full_name_ch text,
            created_at timestamp,
            reason text,
            attempts int,
            last_error text,
            PRIMARY KEY (user_id, task_type)
        )
        """
    )


def close_cassandra_connection():
    global cluster
    global session

    if session:
        session.shutdown()
        session = None

    if cluster:
        cluster.shutdown()
        cluster = None
