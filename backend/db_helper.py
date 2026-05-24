import mysql.connector
from contextlib import contextmanager
from logging_setup import setup_logger

logger = setup_logger('db_logger')

@contextmanager
def get_db_cursor(commit=False):
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="expense_manager"
    )

    cursor = connection.cursor(dictionary=True)
    yield  cursor
    if commit:
        connection.commit()
    cursor.close()
    connection.close()


def fetch_expense_for_date(expense_date):
    logger.info(f"fetch_expenses_for_date called with {expense_date}")
    with get_db_cursor() as cursor:
        cursor.execute("select * from expenses where expense_date = %s", (expense_date,))
        expenses = cursor.fetchall()
        return expenses

def insert_expense(expense_date,amount,category,notes):
    logger.info(f"insert_expense called with date: {expense_date}, amount: {amount},"
                f"category: {category}, notes: {notes}")
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            "INSERT INTO expenses (expense_date,amount, category, notes) VALUES (%s, %s, %s, %s)",
            (expense_date,amount,category,notes)
        )

def delete_expense_for_date(expense_date):
    logger.info(f"delete_expense_for_date called with {expense_date}")
    with get_db_cursor(commit=True)as cursor:
        cursor.execute("Delete from expenses where expense_date = %s", (expense_date,))


def fetch_expense_summary(start_date, end_date):
    logger.info(f"fetch_expense_summary called with start: {start_date} end: {end_date}")
    with get_db_cursor() as cursor:
        cursor.execute('''
            Select category, sum(amount) as total
            from expenses where expense_date 
            between %s and %s 
            group by category; ''',
    (start_date,end_date))

        data = cursor.fetchall()
        return data


def fetch_expense_monthwise():
    logger.info(f"fetch_expense_summary called - fetching all months")
    with get_db_cursor() as cursor:
        cursor.execute('''
            Select Date_Format(expense_date, '%M') as month,sum(amount) as total
            from expenses
            group by Date_Format(expense_date, '%M')
            order by month; ''')

        monthly = cursor.fetchall()
        return monthly

if __name__ == "__main__":
    result=fetch_expense_monthwise()
    print(result)