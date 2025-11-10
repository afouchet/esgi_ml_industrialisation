from time import sleep
from unittest.mock import patch

from td5.chatbot import ChatBot


def test_run_sql_query__to_validate_action():
    bot = ChatBot()

    # Insert query
    sql_insert = """INSERT INTO purchases (user_id, drug_id, quantity, unit_price, total_amount, purchase_date, prescription_number, prescribing_doctor, pharmacy_location, insurance_claim_id, payment_method, transaction_id, delivery_address, delivery_status, tracking_number, notes)
VALUES (2, 2, 10, 0.01, 0.1, '2025-07-01', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'pending', NULL, NULL);"""
    reply = bot.run_sql_query(sql_insert, user_id=1)

    assert reply == f"Waiting human validation to execute: {sql_insert}"
    assert bot._queries_to_validate == [sql_insert]

    # read query
    sql_select = """SELECT d.drug_name 
FROM drugs d
WHERE d.requires_prescription = 0;"""

    reply = bot.run_sql_query(sql_select, user_id=1)

    # Robust to various way to linebreak
    reply = reply.replace("\r", "\n")
    assert reply == "drug_name\nAcetaminophen\nIbuprofen\nOmeprazole\n"
    assert bot._queries_to_validate == [sql_insert]

    # update query
    sql_update = "UPDATE drugs SET requires_prescription = 0 WHERE drug_name = 'Oxycodone';"

    reply = bot.run_sql_query(sql_update, user_id=1)

    assert reply == f"Waiting human validation to execute: {sql_update}"
    assert bot._queries_to_validate == [sql_insert, sql_update]


def tst_run_sql_query__created_undo_actions__insert():
    # !! NOTE !! use td5/sql_undoer.py to build the undo query
    sql = """INSERT INTO purchases (user_id, drug_id, quantity, unit_price, total_amount, purchase_date)
VALUES (2, 2, 10, 0.01, 0.1, '2025-07-01');"""
    sql_undo = "DELETE FROM purchases WHERE user_id = 2 AND drug_id = 2 AND quantity = 10 AND unit_price = 0.01 AND total_amount = 0.1 AND purchase_date = '2025-07-01'"

    bot = ChatBot()

    bot.run_sql_query(sql, user_id=1, admin=True)

    assert bot._queries_ran == [sql]
    assert bot._queries_to_undo == [sql_undo]


def tst_run_sql_query__undo_action():
    """
    Previous tests "knew implementation details"
    (that, when you run a query, the bot._queries_ran and bot._queries_to_undo
    would be changed.

    Design a new test ignoring implementation details.
    The test would just know that we have the following API
    - bot.get_table(table_name) -> return full table
    - bot.run_sql_query(sql_query) -> runs the query
    - bot.list_ran_queries() -> return dictionnary {query_id: sql_query that was ran}
    - bot.undo_query(query_id) -> undo the action done by "query_id"
    """
    raise NotImplementedError("TO DO")


@patch("td5.chatbot.sqlite3.connect")
def tst_run_sql_query__filter_user_scope(sql_connection):
    """
    When running a select query on a table with user_id,
    Add the filter where user_id = {user_id}

    Mocking the SQL connection to assert that, on calls to a table
    with user_id, the filter "user_id = {user_id}" was added
    """
    sql_connection().cursor().fetchall.return_value = [[]]
    sql_connection().cursor().description = []

    # Purchases is a table with user_id
    sql_select = "SELECT * FROM purchases;"
    user_id = 10

    bot = ChatBot()

    bot.run_sql_query(sql_select, user_id)

    sql_connection().cursor().execute.assert_called_with(
        "SELECT * FROM purchases WHERE  user_id = 10;"
    )

    # Drugs is a table with no user_id
    sql_select = "SELECT * FROM drugs;"

    bot.run_sql_query(sql_select, user_id)

    sql_connection().cursor().execute.assert_called_with("SELECT * FROM drugs;")

    # Select with join
    sql_select = """SELECT 
    p.purchase_id, 
    p.purchase_date, 
    p.total_amount,
    p.delivery_address,
    u.credit_card_number
FROM purchases p
JOIN users u ON p.user_id = u.user_id;"""

    bot.run_sql_query(sql_select, user_id)

    sql_connection().cursor().execute.assert_called_with(
        """SELECT 
    p.purchase_id, 
    p.purchase_date, 
    p.total_amount,
    p.delivery_address,
    u.credit_card_number
FROM purchases p
JOIN users u ON p.user_id = u.user_id WHERE p.user_id = 10;"""
    )

    # No "user_id = 2" to add, becase it's already there
    sql_select = "SELECT * FROM purchases WHERE  user_id = 10;"

    bot.run_sql_query(sql_select, user_id)

    sql_connection().cursor().execute.assert_called_with(sql_select)


def tst_run_sql_query__autovalid_update():
    """User can change his/her information, no need ot validate
    even if that's an update operation"""
    # update query
    sql_update = "UPDATE users SET phone = +33612345678 WHERE user_id = 2;"

    bot = ChatBot()

    bot.run_sql_query(sql_update, user_id=2)

    assert bot._queries_to_validate == []

def tst_add_lag():
    """
    If a user spams our API, we want to add lag, with the following rules:
    - if >= 5 calls in past second, add lag of 1
    - if >= 10 calls in past 10 second, add lag of 10
    """

    bot = ChatBot()

    sql_query = "SELECT * FROM drugs;"
    user_id = 42

    for i in range(4):
        bot.run_sql_query(sql_query, user_id)

    # 5th query gets you lag
    bot.run_sql_query(sql_query, user_id)
    assert bot.add_lag(user_id) == 1

    sleep(1)

    assert bot.add_lag(user_id) == 0

    for i in range(10):
        bot.run_sql_query(sql_query, user_id)

    assert bot.add_lag(user_id) == 10
