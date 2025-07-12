import sqlite3, logging, traceback
from flask import session, jsonify
from datetime import datetime, timedelta

# Define a connection to the database
def connect_db():
    return sqlite3.connect('murilex.db')

# Create tables if they don't exist
def get_artist_data_by_id(artist_id):
    conn = None

    try:
        with connect_db() as conn:
            cursor = conn.cursor()

            artist_data = {}
            song_data = []
            album_data = []
            catalogue_data = {}
            song_watchlist_count = {}
            album_watchlist_count = {}
            catalogue_watchlist_count = {}

            if artist_id is not None:
                cursor.execute("""SELECT
                                name,
                                image,
                                category_id,
                                language,
                                country,
                                price
                            FROM artist
                            WHERE id = ?""", (artist_id,))
                artist_raw = cursor.fetchone()
                if artist_raw:
                    artist_data = {
                        'name': artist_raw[0],
                        'image': artist_raw[1],
                        'category': artist_raw[2],
                        'language': artist_raw[3],
                        'country': artist_raw[4],
                        'price': artist_raw[5]
                    }

                cursor.execute("""SELECT
                                id AS song_id,
                                name AS song_name,
                                image AS song_image,
                                albumname AS song_albumname,
                                price AS song_price,
                                availability AS song_availability
                            FROM song
                            WHERE artist_id = ?""", (artist_id,))
                songs_raw = cursor.fetchall()
                song_data = [
                    {
                        'id': song_raw[0],
                        'name': song_raw[1],
                        'image': song_raw[2],
                        'albumname': song_raw[3],
                        'price': song_raw[4],
                        'availability': song_raw[5]
                    }
                    for song_raw in songs_raw
                ]

                cursor.execute("""SELECT
                                id AS album_id,
                                name AS album_name,
                                image AS album_image,
                                price AS album_price,
                                availability AS album_availability
                            FROM album
                            WHERE artist_id = ?""", (artist_id,))
                albums_raw = cursor.fetchall()
                album_data = [
                    {
                        'id': album_raw[0],
                        'name': album_raw[1],
                        'image': album_raw[2],
                        'price': album_raw[3],
                        'availability': album_raw[4]
                    }
                    for album_raw in albums_raw
                ]

                cursor.execute("""SELECT
                                id AS catalogue_id,
                                price AS catalogue_price,
                                shares AS catalogue_shares
                            FROM catalogue
                            WHERE artist_id = ?""", (artist_id,))
                catalogue_raw = cursor.fetchone()

                if catalogue_raw:
                    catalogue_data = {
                        'id': catalogue_raw[0],
                        'price': catalogue_raw[1],
                        'shares': catalogue_raw[2]
                    }

                user_id = session.get('user_id')

                for item in song_data:
                    cursor.execute('SELECT COUNT(*) FROM watchlist WHERE user_id = ? AND item_id = ? AND item_type = ?',
                                (user_id, item['id'], "song"))
                    count = cursor.fetchone()[0]
                    song_watchlist_count[item['id']] = count

                for item in album_data:
                    cursor.execute('SELECT COUNT(*) FROM watchlist WHERE user_id = ? AND item_id = ? AND item_type = ?',
                                (user_id, item['id'], "album"))
                    count = cursor.fetchone()[0]
                    album_watchlist_count[item['id']] = count

                if catalogue_data:
                    cursor.execute('SELECT COUNT(*) FROM watchlist WHERE user_id = ? AND item_id = ? AND item_type = ?',
                                (user_id, catalogue_data['id'], "catalogue"))
                    count = cursor.fetchone()[0]
                    catalogue_watchlist_count[catalogue_data['id']] = count

            return artist_data, song_data, album_data, catalogue_data, song_watchlist_count, album_watchlist_count, catalogue_watchlist_count

    except Exception as error:
        logging.error("Error in get_artist_data_by_id: %s", error)
        if conn:
            conn.rollback()

    finally:
        if conn:
            conn.close()