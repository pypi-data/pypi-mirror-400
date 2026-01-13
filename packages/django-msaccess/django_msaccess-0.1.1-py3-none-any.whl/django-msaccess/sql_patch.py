#
#/////////////////////////////////////////////////////////////////////////
#
# Apply a patch to the SQL statement that caused the error notification
#    from the ODBC system.
#        
#/////////////////////////////////////////////////////////////////////////
#
import re

#Symbol that represents the start of a name
START_CHAR = '['
ESC_START_CHAR = re.escape(START_CHAR)

#End of name symbol
END_CHAR = ']'
ESC_END_CHAR = re.escape(END_CHAR)

NAME_PATTERN = rf'(?:{ESC_START_CHAR}[^{ESC_END_CHAR}]+{ESC_END_CHAR}|\S+)'
JOIN_TYPES = r"INNER|LEFT\s+OUTER|RIGHT\s+OUTER"
#
#//////////////////////////////////
#[SQLPatch ID]:SELECT_PATCH_0010
#//////////////////////////////////
#[SQL statements that cannot be executed in the ACCESS ODBC system]
#  SELECT column-name-list FROM [django_admin_log] INNER JOIN [accounts_user] ON ([django_admin_log].[user_id] = [accounts_user].[id]) LEFT OUTER JOIN [django_content_type] ON ([django_admin_log].[content_type_id] = [django_content_type].[id]) WHERE ... ORDER BY ...
#
#[SQL statements that have been modified to be executable]
#  SELECT column-name-list FROM ( [django_admin_log] INNER JOIN [accounts_user] ON ([django_admin_log].[user_id] = [accounts_user].[id]) ) LEFT OUTER JOIN [django_content_type] ON ([django_admin_log].[content_type_id] = [django_content_type].[id]) WHERE ... ORDER BY ...
#                              ^^^                                                                                                      ^^^                  
# The FROM clause must be immediately followed by parentheses.
# The first join clause must be enclosed in parentheses.
#
SELECT_PATCH_0010_regex = rf"""
  ^SELECT\s+(?P<columns>.+?)
    \s+FROM\s+(?P<table_name>{NAME_PATTERN})
    \s+(?P<join1_type>{JOIN_TYPES})\s+JOIN\s+(?P<join1_cond>.+?)
    \s+(?P<join2_type>{JOIN_TYPES})\s+JOIN\s+(?P<join2_cond>.+?)
    (?:\s+WHERE\s+(?P<where_clause>.+?))?
    (?:\s+ORDER\s+BY\s+(?P<order_by_clause>.+?))?
    $
"""
SELECT_PATCH_0010_cpl = re.compile(SELECT_PATCH_0010_regex,
                            re.IGNORECASE | re.VERBOSE | re.DOTALL)

def SELECT_PATCH_0010(input_sql):
    match = SELECT_PATCH_0010_cpl.match(input_sql.strip())
    if not match:
        return False, "Parsing failed (pattern not matched)", None

    p = match.groupdict()
    
    # Reconstructing SQL statements
    reconstructed = (
        f"SELECT {p['columns']} FROM ( {p['table_name']} "
        f" {p['join1_type']} JOIN {p['join1_cond']} )"
        f" {p['join2_type']} JOIN {p['join2_cond']}  "
    )
    
    # Add any part in order
    if p['where_clause']:
        reconstructed += f" WHERE {p['where_clause']}"
    if p['order_by_clause']:
        reconstructed += f" ORDER BY {p['order_by_clause']}"
    
    return True, reconstructed, p


#//////////////////////////////
if __name__ == '__main__':
#//////////////////////////////
    print("*"*30)
    print("       SELECT_PATCH_0010")
    print("*"*30)
    test_select_0010 = [
        'SELECT shop_id, COUNT(*) FROM Shops INNER JOIN Staffs ON s1=s2 LEFT OUTER JOIN Sales ON s2=s3',
        'SELECT category, price FROM Products INNER JOIN Tags ON t1=t2 INNER JOIN Stock ON s1=s2 ORDER BY price DESC',
        'SELECT dept_id, salary FROM Dept INNER JOIN Emp ON e1=e2 INNER JOIN Project ON p1=p2 where salary > 50000',
        'SELECT a, b FROM T1 INNER JOIN T2 ON a=b INNER JOIN T3 ON b=c WHERE a > 10 ORDER BY a ASC'
    ]
    print(f"{'Status':<4} | {'Extraction summary'}")
    print("-" * 60)
    for sql in test_select_0010:
        success, rebuilt, data = SELECT_PATCH_0010(sql)
        status = "✅OK" if success else "❌NG"
        summary = f"WHERE BY: {data['where_clause'] or '❌'} / ORDER BY: {data['order_by_clause'] or '❌'}"
        print(f"{status:<4} | {summary}")
        if success:
            print(f"{rebuilt}\n")
            for key, val in data.items():
                if val: print(f"  {key}: {val}")
            print("-"*30,"\n")



