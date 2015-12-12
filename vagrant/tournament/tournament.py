#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
# Author: Rudy Reeves
#

import psycopg2

# Attempts to connect to the DB and returns it and its cursor
def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    try:
        conn = psycopg2.connect("dbname=tournament")
        cursor = conn.cursor()
        return conn, cursor
    except:
        print("Unable to connect to the database.")

# A helper function for executing one PostgreSQL command
def psql_cmd(cmd):
    conn, cursor = connect()
    cursor.execute(cmd)
    conn.commit()
    conn.close()


def deleteMatches():
    """Remove all the match records from the database."""
    psql_cmd("DELETE FROM matches;")


def deletePlayers():
    """Remove all the player records from the database."""
    psql_cmd("DELETE FROM players;")

def countPlayers():
    """Returns the number of players currently registered."""
    conn, cursor = connect()
    cursor.execute("SELECT COUNT(*) FROM players;")
    player_list = cursor.fetchone()
    conn.close()
    return player_list[0]


def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    conn, cursor = connect()
    cursor.execute("INSERT INTO players (name, num_wins, num_matches) VALUES (%s, 0, 0);" # NOQL
              , (name,))
    conn.commit()
    conn.close()

def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    conn, cursor = connect()
    cursor.execute("SELECT * FROM players ORDER BY num_wins")
    players = cursor.fetchall()
    conn.close()
    return players


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    conn, cursor = connect()
    cursor.execute("UPDATE players SET num_wins=num_wins+1 WHERE id=%s", (winner,)) # NOQL
    cursor.execute("UPDATE players SET num_matches=num_matches+1 WHERE id=%s", # NOQL
              (winner,))
    cursor.execute("UPDATE players SET num_matches=num_matches+1 WHERE id=%s", # NOQL
              (loser,))
    conn.commit()
    conn.close()
 
 
def swissPairings():
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    conn, cursor = connect()
    cursor.execute("SELECT * FROM players ORDER BY num_wins")
    players_list = cursor.fetchall()
    result = []

    # Create a list of tuples like [(id1, name1, id2, name2)]
    for i in range(0, len(players_list)-1, 2):
        result.append((players_list[i][0], players_list[i][1],
                       players_list[i+1][0], players_list[i+1][1]))
    conn.close()
    return result

