import vertica_python
import os



class DbConnect:
    """Connect to Vertica Provider cluster"""

    host = os.environ.get("DB_HOST")
    port = int(os.environ.get("DB_PORT"))
    database = os.environ.get("DB_NAME")
    user = os.environ.get("DB_USER")
    password = os.environ.get("DB_PASSWORD")

    default_search_string = """SELECT vo.org_name, u.first_name, u.last_name, u.user_name, u.created_on, u.user_status, 
                            u.modified_on, 
                            SUM(CASE WHEN al.functional_area = 'LOGIN' THEN 1 ELSE 0 END) as Logins,
                            SUM(CASE WHEN (al.functional_area = 'EXPLORE' AND al.action_type = 'SEARCH') 
                              THEN 1 ELSE 0 END) as FastSearch,
                            SUM(CASE WHEN (al.functional_area = 'POWER_SEARCH_DETAIL' AND al.action_type = 'SEARCH') 
                              THEN 1 ELSE 0 END) as PowerSearch,
                            SUM(CASE WHEN (al.functional_area ilike '%engage%' OR al.functional_area ilike '%virtual%') 
                              THEN 1 ELSE 0 END) as VirtualChart 
                            FROM SUPERMART_000.v_explorys_admin_user u 
                            JOIN SUPERMART_000.v_activity_log al 
                            ON al.user_id = u.user_id 
                            JOIN SUPERMART_000.v_organization vo 
                            ON vo.org_id = al.org_id 
                            WHERE vo.org_id = :propOrg
                              AND u.internal_external = 'EXTERNAL' AND (al.logged_on >=:propStart
                              AND al.logged_on <=:propEnd) AND u.user_name ilike :propUser
                              AND u.last_name ilike :propLast
                            GROUP BY 1,2,3,4,5,6,7;"""

    all_org_search_string = """SELECT vo.org_name, u.first_name, u.last_name, u.user_name, u.created_on, u.user_status, 
                                u.modified_on, 
                                SUM(CASE WHEN al.functional_area = 'LOGIN' THEN 1 ELSE 0 END) as Logins,
                                SUM(CASE WHEN (al.functional_area = 'EXPLORE' AND al.action_type = 'SEARCH') 
                                  THEN 1 ELSE 0 END) as FastSearch,
                                SUM(CASE WHEN (al.functional_area = 'POWER_SEARCH_DETAIL' AND al.action_type = 'SEARCH') 
                                  THEN 1 ELSE 0 END) as PowerSearch,
                                SUM(CASE WHEN (al.functional_area ilike '%engage%' OR al.functional_area ilike '%virtual%') 
                                  THEN 1 ELSE 0 END) as VirtualChart 
                                FROM SUPERMART_000.v_explorys_admin_user u 
                                JOIN SUPERMART_000.v_activity_log al 
                                ON al.user_id = u.user_id 
                                JOIN SUPERMART_000.v_organization vo 
                                ON vo.org_id = al.org_id 
                                WHERE vo.org_id IN :propOrg
                                  AND u.internal_external = 'EXTERNAL' AND (al.logged_on >=:propStart
                                  AND al.logged_on <=:propEnd) AND u.user_name ilike :propUser
                                  AND u.last_name ilike :propLast
                                GROUP BY 1,2,3,4,5,6,7;"""



    search_org_string = "SELECT o.org_id, o.org_name FROM SUPERMART_000.v_organization o JOIN SUPERMART_000.v_explorys_admin_user u ON o.org_id = u.org_id WHERE o.org_class = 'PHM' GROUP BY 1,2 ORDER BY 2"

    get_org_number_string = "SELECT o.org_id FROM SUPERMART_000.v_organization o JOIN SUPERMART_000.v_explorys_admin_user u ON o.org_id = u.org_id WHERE o.org_class = 'PHM' GROUP BY 1 ORDER BY 1"

    def open_connection(self):
        connection_info = {
            'host': self.host,
            'port': self.port,
            'user': self.user,
            'password': self.password,
            'database': self.database,
            'read_timeout': 300,
            'connection_timeout': 25
        }
        return vertica_python.connect(**connection_info)

    def close_connection(self, connectionName):
        connectionName.close()

    def search_db(self, form):
        connection = self.open_connection()
        cur = connection.cursor()
        if int(form["org"]) == 0:
            exec_params = self.create_all_orgs_search_params(form)
        else:
            exec_params = self.create_default_search_params(form)
        cur.execute(exec_params[0], exec_params[1])
        result = cur.fetchall()
        self.close_connection(connection)
        result = self.format_result(result)
        return result

    def get_orgs(self):
        connection = self.open_connection()
        cur = connection.cursor()
        cur.execute(self.search_org_string)
        result = cur.fetchall()
        self.close_connection(connection)
        result.insert(0, [0, "All Orgs"])
        return result

    def get_org_numbers(self):
        connection = self.open_connection()
        cur = connection.cursor()
        cur.execute(self.get_org_number_string)
        result = cur.fetchall()
        self.close_connection(connection)
        return result

    def create_default_search_params(self, form):
        org_int = int(form["org"])
        start_str = form["start_date"]
        end_str = form["end_date"]
        user_str = "%" + form["user_name"] + "%"
        last_str = "%" + form["last_name"] + "%"
        select_params = {'propOrg': org_int, 'propStart': start_str,
                         'propEnd': end_str, 'propUser': user_str, 'propLast': last_str}
        search_string = self.default_search_string
        execute_params = [search_string, select_params]
        return execute_params

    def create_all_orgs_search_params(self, form):
        start_str = form["start_date"]
        end_str = form["end_date"]
        user_str = "%" + form["user_name"] + "%"
        last_str = "%" + form["last_name"] + "%"
        org_list = []
        for i in self.get_org_numbers():
            org_list.append(i[0])
        org_tuple = tuple(org_list)
        select_params = {'propOrg': org_tuple, 'propStart': start_str, 'propEnd': end_str,
                         'propUser': user_str, 'propLast': last_str}
        search_string = self.all_org_search_string
        execute_params = [search_string, select_params]
        return execute_params

    def format_result(self, result):
        json_ready_list = []
        for i in result:
            named_list = {"org": i[0], "first": i[1], "last": i[2], "user": i[3], "created": i[4], "status": i[5],
                          "modified": i[6], "logins": i[7], "fast": i[8], "power": i[9], "virtual": i[10]}
            json_ready_list.append(named_list)
        return json_ready_list


def maintain_order(self, n=int, nums=list):
    sorted_nums = nums.sort()
    sliced_nums = sorted_nums[0:n:-1]
    print(sliced_nums)
    nums.sort()