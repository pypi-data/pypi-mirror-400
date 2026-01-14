from os.path import join
import paramiko
import pyodbc
import json
from datetime import datetime, date
from decimal import Decimal

class getUserInfoForUser():

    def getAllUsers(self, wantJson: bool = False):
        """
        Fetches all user information from the database.

        This function queries the database to retrieve user information and returns the results
        either as a list of tuples or as a JSON-formatted string, depending on the value
        of the `wantJson` parameter. If no data is found, an error message is returned instead.

        :param wantJson: Determines the format of the output. If True, the result
                         will be returned as a JSON-formatted string. If False, the
                         result will be returned as a list of tuples.
        :type wantJson: bool
        :return: The user information retrieved from the database. The format of
                 the result depends on the value of the `wantJson` parameter. If
                 no data is found, an error message is returned instead.
        :rtype: Union[list[tuple], str, None]
        """
        sql_query = "SELECT * FROM qsys2.user_info"

        def json_serial(obj):
            if hasattr(obj, 'isoformat'):
                return obj.isoformat()
            return str(obj)

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql_query)
                rows = cursor.fetchall()

                if not rows:
                    error_msg = {'error': 'No data found'}
                    return json.dumps(error_msg, indent=4) if wantJson else [("error", "No data found")]

                # Get column names
                columns = [column[0] for column in cursor.description]

                if wantJson:
                    # Create a LIST of dictionaries
                    results = [dict(zip(columns, r)) for r in rows]
                    return json.dumps(results, indent=4, default=json_serial)

                return rows  # Returns the list of tuples

        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def getSingleUserInformation(self, username: str, wantJson: bool = False):

        if not username:
          raise ValueError("A username is required.")

        sql_query = f"SELECT * FROM qsys2.user_info WHERE AUTHORIZATION_NAME = upper('{username}')"

        def json_serial(obj):
            # Handle datetime and Decimal (common in DB2)
            if hasattr(obj, 'isoformat'):
                return obj.isoformat()
            return str(obj)

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql_query)
                row = cursor.fetchone()  # Since you only expect one user

                if not row:
                    error_msg = {'error': 'No data found for User: ' + username}
                    return json.dumps(error_msg, indent=4) if wantJson else ("error", error_msg['error'])

                # DYNAMICALLY get column names from the database itself
                columns = [column[0] for column in cursor.description]
                row_dict = dict(zip(columns, row))

                if wantJson:
                    return json.dumps(row_dict, indent=4, default=json_serial)
                return row  # Returns the tuple

        except Exception as e:
            print(f"An error occurred: {e}")
            return None