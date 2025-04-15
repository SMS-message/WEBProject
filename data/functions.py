import sqlite3
from typing import List, Tuple


def user_table_exists(user_id: int, path_to_db: str):
    con = sqlite3.connect(path_to_db)
    cur = con.cursor()

    try:
        cur.execute(f"SELECT ID FROM User_{user_id}")
    except sqlite3.OperationalError as error:
        if "no such table" in error.args[0]:
            return False
    return True


def create_user_table(user_id: int, path_to_db:str):
    con = sqlite3.connect(path_to_db)
    cur = con.cursor()

    cur.execute(f"""
                    CREATE TABLE User_{user_id} (
                        ID     INTEGER PRIMARY KEY,
                        viewed INTEGER DEFAULT (0) 
                    );
                    """)
    con.commit()

    cur.execute(f"""
                    INSERT INTO User_{user_id} (
                                          ID
                                      )
                                      SELECT ID
                                        FROM Videos;""")
    con.commit()


def make_queue(user_id: int, path_to_db: str) -> List[int]:
    con = sqlite3.connect(path_to_db)
    cur = con.cursor()

    res = tuple(cur.execute(f"""SELECT ID
                          FROM User_{user_id}
                         WHERE viewed = 0;"""))
    if res:
        return refactor_result(res)
    res = tuple(cur.execute(f"""SELECT ID
                                  FROM User_{user_id}
                                 WHERE ID IN (
                                           SELECT ID
                                             FROM Videos
                                            WHERE dislikes == 0
                                       );
                                """))
    if res:
        return refactor_result(res)

    res = tuple(cur.execute(f"""SELECT ID
                                  FROM User_{user_id}
                                 WHERE ID IN (
                                           SELECT ID
                                             FROM Videos
                                            WHERE likes >= dislikes
                                       );
                                    """))
    if res:
        return refactor_result(res)

    res = tuple(cur.execute(f"""SELECT ID
                                      FROM User_{user_id}"""))
    return refactor_result(res)


def update_user_table(user_id: int, path_do_db: str):
    con = sqlite3.connect(path_do_db)
    cur = con.cursor()

    cur.execute(f"""
                    INSERT INTO User_{user_id} (
                               ID
                           )
                           SELECT ID
                             FROM Videos
                            WHERE ID NOT IN (
                                      SELECT ID
                                        FROM User_{user_id}
                                  );
                    """)
    con.commit()


def refactor_result(res: Tuple[Tuple[int]]) -> List[int]:
    result = []
    for elem in res:
        result.append(elem[0])

    return result
