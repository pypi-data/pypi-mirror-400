"""
Microsoft Access database backend for Django.
"""

#* from . import __init__ as pkg
#* from . import __debug_output__, __truncate_name__
import sys
pkg = sys.modules[__package__]


from datetime import datetime

try:
    #import pypyodbc as Database
    import pyodbc as Database
except ImportError as e:
    from django.core.exceptions import ImproperlyConfigured
    raise ImproperlyConfigured("Error loading pyodbc module: %s" % e)

import re
m = re.match(r'(\d+)\.(\d+)\.(\d+)(?:-beta(\d+))?', Database.version)
vlist = list(m.groups())
if vlist[3] is None: vlist[3] = '9999'

try:
    from django.db.backends import BaseDatabaseWrapper, BaseDatabaseFeatures, BaseDatabaseValidation
except ImportError:  # these imports have moved in later Django version
    from django.db.backends.base.base import BaseDatabaseWrapper
    from django.db.backends.base.features import BaseDatabaseFeatures
    from django.db.backends.base.validation import BaseDatabaseValidation
from django.db.backends.signals import connection_created
from django.conf import settings

# from access.pyodbc.operations import DatabaseOperations
# from access.pyodbc.client import DatabaseClient
# from access.pyodbc.creation import DatabaseCreation
# from access.pyodbc.introspection import DatabaseIntrospection
from .debug import _DebugOutput
from .operations import DatabaseOperations
from .client import DatabaseClient
from .creation import DatabaseCreation
from .introspection import DatabaseIntrospection
from .schema import DatabaseSchemaEditor


import os
import warnings

DatabaseError = Database.DatabaseError
IntegrityError = Database.IntegrityError

#DRIVER_ACCESS= 'Microsoft Access Driver (*.mdb)'
DRIVER_ACCESS = 'Microsoft Access Driver (*.mdb, *.accdb)'
DRIVER_FREETDS = 'FreeTDS'
DRIVER_SQL_SERVER = 'SQL Server'
DRIVER_SQL_NATIVE_CLIENT = 'SQL Native Client'
DRIVER_MDBTOOLS = 'MDBTools'

IGNORE_SQLStmt = [
 r'If ignored, the fake test will fail.  ALTER TABLE \[django_content_type\] DROP COLUMN \[name\]',
 r'RELEASE SAVEPOINT \[\S+\]',
 r'SAVEPOINT \[\S+\]'
]

IGNORE_SQLStmt_cpl = [re.compile(sql) for sql in IGNORE_SQLStmt]


TruncateName_SQLStmt = [
 {'fmt':r'ALTER TABLE \[([^\[\]]+)\] ADD CONSTRAINT \[([^\[\]]{64})[^\[\]]*\] FOREIGN KEY ([\s\S]+)$',
  'sql':r'ALTER TABLE [\1] ADD CONSTRAINT [\2] FOREIGN KEY \3'},
]

TruncateName_SQLStmt_cpl = [
  re.compile(item['fmt']) for item in TruncateName_SQLStmt
]


from .sql_patch import SELECT_PATCH_0010

# SELECT_PATCH_SQLStmt = [
# [
#   'SELECT_PATCH_0010',
# # 'SELECT [django_admin_log].[user_id], [django_admin_log].[content_type_id], ... [django_content_type].[model] FROM [django_admin_log] INNER JOIN [accounts_user] ON ([django_admin_log].[user_id] = [accounts_user].[id]) LEFT OUTER JOIN [django_content_type] ON ([django_admin_log].[content_type_id] = [django_content_type].[id]) WHERE [django_admin_log].[user_id] = ? ORDER BY [django_admin_log].[action_time] DESC'
#  r'SELECT ((\[\S+\]\.\[\S+\],{0,1}\s*)+) FROM (\[\S+\]) INNER JOIN (\[\S+\]) ON \((\[\S+\]\.\[\S+\] = \[\S+\]\.\[\S+\])\) LEFT OUTER JOIN (\[\S+\]) ON \((\[\S+\]\.\[\S+\] = \[\S+\]\.\[\S+\])\) WHERE ([\S\s]+)$',
# # 'SELECT [django_admin_log].[user_id], [django_admin_log].[content_type_id], ... [django_content_type].[model] FROM ( [django_admin_log] INNER JOIN [accounts_user] ON ([django_admin_log].[user_id] = [accounts_user].[id]) ) LEFT OUTER JOIN [django_content_type] ON ([django_admin_log].[content_type_id] = [django_content_type].[id]) WHERE [django_admin_log].[user_id] = ? ORDER BY [django_admin_log].[action_time] DESC'
# #                                                                                                                   ^^^                                                                                                      ^^^                  
#  r'SELECT \1 FROM ( \3 INNER JOIN \4 ON (\5) ) LEFT OUTER JOIN \6 ON (\7) WHERE \8'
# ],
# [
#   'SELECT_PATCH_0020',
# #sql=SELECT [auth_permission].[id] FROM [auth_permission] INNER JOIN [accounts_user_user_permissions] ON ([auth_permission].[id] = [accounts_user_user_permissions].[permission_id]) INNER JOIN [django_content_type] ON ([auth_permission].[content_type_id] = [django_content_type].[id]) WHERE [accounts_user_user_permissions].[user_id] = ? ORDER BY [django_content_type].[app_label] ASC, [django_content_type].[model] ASC, [auth_permission].[codename] ASC
#  r'SELECT ((\[\S+\]\.\[\S+\],{0,1}\s*)+) FROM (\[\S+\]) INNER JOIN (\[\S+\]) ON \((\[\S+\]\.\[\S+\] = \[\S+\]\.\[\S+\])\) INNER JOIN (\[\S+\]) ON \((\[\S+\]\.\[\S+\] = \[\S+\]\.\[\S+\])\) WHERE ([\S\s]+)$',
# #sql=SELECT [auth_permission].[id] FROM ( [auth_permission] INNER JOIN [accounts_user_user_permissions] ON ([auth_permission].[id] = [accounts_user_user_permissions].[permission_id]) ) INNER JOIN [django_content_type] ON ([auth_permission].[content_type_id] = [django_content_type].[id]) WHERE [accounts_user_user_permissions].[user_id] = ? ORDER BY [django_content_type].[app_label] ASC, [django_content_type].[model] ASC, [auth_permission].[codename] ASC
# #                                      ^^^                                                                                                                                            ^^^                  
#  r'SELECT \1 FROM ( \3 INNER JOIN \4 ON (\5) ) INNER JOIN \6 ON (\7) WHERE \8'
# ],

# [
#   'SELECT_PATCH_0030',
# #sql=SELECT [django_admin_log].[id], ... [django_content_type].[model] FROM [django_admin_log] INNER JOIN [auth_user] ON ([django_admin_log].[user_id] = [auth_user].[id]) LEFT OUTER JOIN [django_content_type] ON ([django_admin_log].[content_type_id] = [django_content_type].[id]) ORDER BY [django_admin_log].[action_time] DESC
# #    SELECT ... FROM ... INNER ... LEFT ...
# #      "WHERE" clause is a non-existent statement.
#  r'SELECT ((\[\S+\]\.\[\S+\],{0,1}\s*)+) FROM (\[\S+\]) INNER JOIN (\[\S+\]) ON \((\[\S+\]\.\[\S+\] = \[\S+\]\.\[\S+\])\) LEFT OUTER JOIN (\[\S+\]) ON \((\[\S+\]\.\[\S+\] = \[\S+\]\.\[\S+\])\) ORDER BY ([\s\S]+)$',

# #SELECT [django_admin_log].[id], ... [django_content_type].[model] FROM (django_admin_log INNER JOIN auth_user ON ([django_admin_log].[user_id] = [auth_user].[id]) ) LEFT JOIN django_content_type ON [django_admin_log].[content_type_id] = [django_content_type].[id] ORDER BY [django_admin_log].[action_time] DESC;
# #                                                                      ^^^                                                                                         ^^^                                                                   
#  r'SELECT \1 FROM ( \3 INNER JOIN \4 ON (\5) ) LEFT OUTER JOIN \6 ON (\7) ORDER BY \8',
# ],


# [
#   'SELECT_PATCH_0040',
# #
# #SELECT [auth_permission].[id] AS [id] FROM [auth_permission]
# # INNER JOIN [auth_user_user_permissions] ON ([auth_permission].[id] = [auth_user_user_permissions].[permission_id]) 
# # INNER JOIN [django_content_type] ON ([auth_permission].[content_type_id] = [django_content_type].[id]) 
# # WHERE [auth_user_user_permissions].[user_id] = ? 
# #ORDER BY [django_content_type].[app_label] ASC, [django_content_type].[model] ASC, [auth_permission].[codename] ASC
# #
#  r'SELECT\s+(.*?)\s+FROM\s+(.*?)\s+INNER JOIN\s+(.*?)\s+ON\s+(.*?)\s+INNER JOIN\s+(.*?)\s+ON\s+(.*?)\s+WHERE\s+(.*?)\s+ORDER BY (.*)$',

# # SELECT ... FROM ( [tbl] INNER JOIN [tbl2] ON ([tbl].[id] = [tbl2].[permission_id]) ) INNER JOIN [tbl3] ON ([tbl1].[content_type_id] = [tbl3].[id]) WHERE [tbl2].[user_id] = ? ORDER BY [tbl3].[app_label] ASC, [tbl3].[model] ASC, [tbl1].[codename] ASC
# #                ^^^                                                                ^^^                  
#  r'SELECT \1 FROM ( \2 INNER JOIN \3 ON \4 ) INNER JOIN \5 ON \6 WHERE \7 ORDER BY \8',
# ],


# ]

# SELECT_PATCH_SQLStmt_cpl = [ [sql_patch[0], re.compile(sql_patch[1],re.IGNORECASE), sql_patch[2]] for sql_patch in SELECT_PATCH_SQLStmt ]

# def patch_select(sql):
#     is_patch= False
#     patch_number=''
#     new_sql=''
#     for patch_list in SELECT_PATCH_SQLStmt_cpl:
#         if re.match( patch_list[1], sql):
#             is_patch= True
#             patch_number= patch_list[0]
#             new_sql= re.sub(patch_list[1], patch_list[2], sql)
#             return (is_patch, patch_number, new_sql)
#     return (False, '', '')


INSERT_PATCH_SQLStmt = [
[
  'INSERT_PATCH_0010',
#sql=INSERT INTO [auth_permission] ([name], [content_type_id], [codename]) VALUES (?, ?, ?), (?, ?, ?), (?, ?, ?), (?, ?, ?)
 r'INSERT INTO \[(\S+)\] \(((\[\S+\],{0,1}\s*)+)\) VALUES ((\((\?,\s){0,}\?\)),\s*){1,}\((\?,\s){0,}\?\)',
#sql=INSERT INTO [auth_permission] ([name], [content_type_id], [codename]) VALUES (?, ?, ?)
#                                                                                ^^^^^^^^^^^
 r'INSERT INTO [\1] (\2) VALUES \5'
],

]

INSERT_PATCH_SQLStmt_cpl = [ [sql_patch[0], re.compile(sql_patch[1],re.IGNORECASE), sql_patch[2]] for sql_patch in INSERT_PATCH_SQLStmt ]

def divide_value_parameters(dim, params):
    """
    Splits the tuple params into tuples of the specified dim size and returns them as a list.
    If there are insufficient elements, fill with None.

    Args:
        dim (int): The size of the tuple to split.
        params (params): Tuple to be split.

    Returns:
        list: A list of split tuples.
    """
    if dim <= 0:
        # If dim is less than or equal to 0, return an empty list or consider error handling.
        # This returns an empty list.
        return []

    ary = []
    n = len(params)

    # Create a tuple for each dim size.
    for i in range(0, n, dim):
        # Get dim-sized chunks in a slice.
        chunk = params[i:i + dim]

        # If it is less than the dim size, fill it with None.
        if len(chunk) < dim:
            padding_needed = dim - len(chunk)
            # Create a tuple of None and join
            padded_chunk = chunk + (None,) * padding_needed
        else:
            padded_chunk = chunk

        # Add to results list
        ary.append(padded_chunk)

    return ary


def patch_insert(sql, params):
    is_patch= False
    patch_number=''
    divided_q_count=0
    new_params=[]
    new_sql=''
    for patch_list in INSERT_PATCH_SQLStmt_cpl:
        ret = re.match( patch_list[1], sql)
        if ret:
            is_patch= True
            patch_number= patch_list[0]
            new_sql= re.sub(patch_list[1], patch_list[2], sql)
            if patch_number=='INSERT_PATCH_0010':
                st = ret.group(5)
                divided_q_count = st.count('?')
                new_params = divide_value_parameters(divided_q_count, params)
            return (is_patch, patch_number, divided_q_count, new_params, new_sql)
    return (False, '', 0, [], '')    


# Pattern to find the "innermost" CASE WHEN ... END.
# By ensuring that no CASE is included before END, processing is performed from the inside out.
INNER_CASE_RE = re.compile(
    r"CASE\s+WHEN\s+((?:(?!CASE).)*?)\s+END", 
    re.IGNORECASE | re.DOTALL
)

def convert_nested_case_to_iif(text):
    current_text = text
    
    while True:
        # 1. Check if current text contains a CASE statement.
        match = INNER_CASE_RE.search(current_text)
        if not match:
            break  # If CASE is not found, exit
            
        # 2. Replace only the "innermost one" found.
        # Here we call the multi-WHEN logic we created last time (described below).
        replaced_fragment = process_single_case(match.group(1))
        
        # 3. Update by replacing part of a string.
        # Replace the part from match.start() to match.end() with replaced_fragment.
        current_text = (
            current_text[:match.start()] + 
            replaced_fragment + 
            current_text[match.end():]
        )
        
    return current_text

def process_single_case(content):
    """Auxiliary function that takes the "contents" of CASE WHEN and END and converts them to IIF"""
    # Extracting the ELSE clause.
    parts = re.split(r"\s+ELSE\s+", content, flags=re.IGNORECASE)
    else_value = parts[1].strip() if len(parts) > 1 else "NULL"
    when_then_part = parts[0]
    
    # Extracting WHEN ~ THEN pairs.
    items = re.findall(r"(.*?)\s+THEN\s+(.*?)(?:\s+WHEN\s+|$)", when_then_part, re.IGNORECASE)
    
    # Assembling the IIF from behind.
    result = else_value
    for condition, value in reversed(items):
        result = f"IIF({condition.strip()}, {value.strip()}, {result})"
    return result





class DatabaseFeatures(BaseDatabaseFeatures):
    uses_custom_query_class = True
    can_use_chunked_reads = False
    #uses_savepoints = True


class DatabaseWrapper(BaseDatabaseWrapper):
    # drv_name = None
    driver_needs_utf8 = None
    vendor = 'msaccess'
    display_name = 'MSAccess'

    #sqlite -> Access
    #https://learn.microsoft.com/ja-jp/office/client-developer/access/desktop-database-reference/create-table-statement-microsoft-access-sql
    data_types = {
        'AutoField': 'COUNTER',
        'BigAutoField': 'COUNTER',
        'BinaryField': 'IMAGE',
        'BooleanField': 'BIT',
        'CharField': 'varchar(%(max_length)s)',
        'DateField': 'DATETIME',
        'DateTimeField': 'datetime',
        'DecimalField': 'MONEY',
        'DurationField': 'INTEGER',
        'FileField': 'varchar(%(max_length)s)',
        'FilePathField': 'varchar(%(max_length)s)',
        'FloatField': 'FLOAT',
        'IntegerField': 'integer',
        'BigIntegerField': 'integer',
        'IPAddressField': 'varchar(15)',
        'GenericIPAddressField': 'varchar(39)',
        'JSONField': 'MEMO',
        'NullBooleanField': 'integer',
        'OneToOneField': 'integer',

        # 'PositiveBigIntegerField': 'bigint unsigned',
        # 'PositiveIntegerField': 'integer unsigned',
        # 'PositiveSmallIntegerField': 'smallint unsigned',
         'PositiveBigIntegerField': 'integer',
         'PositiveIntegerField': 'integer',
         'PositiveSmallIntegerField': 'integer',


        'SlugField': 'varchar(%(max_length)s)',
        'SmallAutoField': 'COUNTER',
        'SmallIntegerField': 'integer',
        'TextField': 'memo',
        'TimeField': 'datetime',
        'UUIDField': 'UNIQUEIDENTIFIER',

        
    }

    data_type_check_constraints = {
     #**   'PositiveBigIntegerField': '"%(column)s" >= 0',
        'JSONField': '(JSON_VALID("%(column)s") OR "%(column)s" IS NULL)',
     #**   'PositiveIntegerField': '"%(column)s" >= 0',

     #[action_flag] integer NOT NULL CHECK ("action_flag" >= 0),
     #**   'PositiveSmallIntegerField': '"%(column)s" >= 0',
     
    }

    data_types_suffix = {
      #   'AutoField': 'AUTOINCREMENT',
      #   'BigAutoField': 'AUTOINCREMENT',
      #   'SmallAutoField': 'AUTOINCREMENT',
    }


    operators = {
            'exact': '= %s',
            'iexact': "= UCASE(%s)",
            'contains': "LIKE %s ", #ESCAPE '\\' COLLATE " + collation,
            'icontains': "LIKE UCASE(%s) ", #ESCAPE '\\' COLLATE "+ collation,
            'gt': '> %s',
            'gte': '>= %s',
            'lt': '< %s',
            'lte': '<= %s',
            'startswith': "LIKE %s ", #ESCAPE '\\' COLLATE " + collation,
            'endswith': "LIKE %s ", #ESCAPE '\\' COLLATE " + collation,
            'istartswith': "LIKE UCASE(%s) ", #ESCAPE '\\' COLLATE " + collation,
            'iendswith': "LIKE UCASE(%s) ", #ESCAPE '\\' COLLATE " + collation,

            # TODO: remove, keep native T-SQL LIKE wildcards support
            # or use a "compatibility layer" and replace '*' with '%'
            # and '.' with '_'
            'regex': 'LIKE %s COLLATE ',
            'iregex': 'LIKE %s COLLATE ',

            # TODO: freetext, full-text contains...
    }

    pattern_esc = r"REPLACE(REPLACE(REPLACE({}, '\', '\\'), '%%', '\%%'), '_', '\_')"
    pattern_ops = {
        'contains': r"LIKE '%%' || {} || '%%' ESCAPE '\'",
        'icontains': r"LIKE '%%' || UPPER({}) || '%%' ESCAPE '\'",
        'startswith': r"LIKE {} || '%%' ESCAPE '\'",
        'istartswith': r"LIKE UPPER({}) || '%%' ESCAPE '\'",
        'endswith': r"LIKE '%%' || {} ESCAPE '\'",
        'iendswith': r"LIKE '%%' || UPPER({}) ESCAPE '\'",
    }

    Database = Database
    SchemaEditorClass = DatabaseSchemaEditor
    # Classes instantiated in __init__().
    client_class = DatabaseClient
    creation_class = DatabaseCreation
    features_class = DatabaseFeatures
    introspection_class = DatabaseIntrospection
    ops_class = DatabaseOperations

    def __init__(self, *args, **kwargs):
         import sys
         #print(f"*args: {args}", file=sys.stderr)
         #print(f"**kwargs: {kwargs}", file=sys.stderr)

         super(DatabaseWrapper, self).__init__(*args, **kwargs)

         self._set_configuration(self.settings_dict)
         #print(f"debug flag={self._debug_flag}")
         #print(f"debug flag={pkg.__debug_output__}")

         self.features = DatabaseFeatures(self)
         self.ops = DatabaseOperations(self)
         self.client = DatabaseClient(self)
         self.creation = DatabaseCreation(self)
         self.introspection = DatabaseIntrospection(self)
         self.validation = BaseDatabaseValidation(self)
         self.connection = None

    def _set_configuration(self, settings_dict):
        #print(f"[_set_configuration]settings_dict={settings_dict}")
        #sd = self._merge_settings(self._fixup_settings_dict(settings_dict))

        if not ('PATH' in settings_dict):
            from django.core.exceptions import ImproperlyConfigured
            raise ImproperlyConfigured('You need to specify PATH(File path for file extension name accdb) in your Django settings file.')

       #if not sd['name']:
        if not settings_dict['PATH']:
            from django.core.exceptions import ImproperlyConfigured
            raise ImproperlyConfigured('You need to specify PATH(File path for file extension name accdb) in your Django settings file.')
        #self._setup_operators(sd)
        # self.settings_dict = sd

        self._debug_flag = False
        if 'DEBUG' in settings_dict:
            if settings_dict['DEBUG']:
                pkg.__debug_output__ = True
                self._debug_flag = True

        self._truncate_name = False
        if 'TRUNCATENAME' in settings_dict:
            if settings_dict['TRUNCATENAME']:
                pkg.__truncate_name__ = True
                self._truncate_name = True





    # def _fixup_settings_dict(self, sd):
    #     new_d = {}
    #    #for k, v in six.iteritems(sd):
    #     for k, v in sd.items():
    #         if k.startswith('DATABASE_'):
    #             k = k.partition('_')[2]
    #         new_d[k] = v
    #     return new_d

    def _parse_driver(self, driver):
        shortcuts = {
            None: self._guess_driver(),
            'access': DRIVER_ACCESS,
            'sql': DRIVER_SQL_SERVER,
            'freetds': DRIVER_FREETDS,
            'mdbtools': DRIVER_MDBTOOLS,
        }
        return shortcuts.get(driver, driver)

    def _guess_driver(self):
        return DRIVER_ACCESS

    # def _merge_settings(self, settings_dict):
    #     default_settings = dict(
    #         #Standard Django settings first
    #         USER=None,
    #         PASSWORD=None,
    #         #Host and port, if applicable
    #         HOST=None,
    #         PORT=None,
    #         #Database name, if applicable
    #         NAME=None,
    #     )
    #     settings = dict(default_settings, **settings_dict)
    #     default_options = dict(
    #         MARS_Connection=False,
    #         datefirst=7,
    #         unicode_results=False,
    #         autocommit=False,
    #         dsn=None,
    #         host_is_server=False,
    #         collation='Latin1_General_CI_AS',
    #         extra_params={},
    #     )
    #     settings['OPTIONS'] = dict(default_options, **settings.get('OPTIONS', {}))
    #     settings['OPTIONS']['driver'] = self._parse_driver(settings['OPTIONS'].get('driver', None))
    #     rename = dict(
    #         USER='user',
    #         PASSWORD='password',
    #         HOST='host',
    #         PORT='port',
    #         NAME='name',
    #         OPTIONS='options',
    #     )
    #    #for k, v in six.iteritems(rename):
    #     for k, v in rename.items():
    #         settings[v] = settings[k]
    #         del settings[k]
    #     return settings

    def _get_connstring_data(self):
        fnm='[DatabaseWrapper._get_connstring_data(base.py:MS-Access)]'
        sd = self.settings_dict
        sd_keys = sd.keys()
        cd = dict()
        _DebugOutput(fnm,f"sd={sd}")

        cd['DRIVER']=sd['ODBC']+';DBQ='+sd['PATH']
        if ('UID' in sd_keys) and (sd['UID'] is not None):
            cd['UID']=sd['UID']
        if ('PWD' in sd_keys) and (sd['PWD'] is not None):
            cd['PWD']=sd['PWD']

        _DebugOutput(fnm,f"cd={cd}")
        return cd


        #if sd['options']['dsn']:
        if sd['options']['dsn']:
            cd['DSN'] = sd['options']['dsn']
        else:
            cd['DRIVER'] = '{%s}'%(sd['options']['driver'])
            if sd['options']['driver'] == DRIVER_ACCESS:
                #Access can't do network, so NAME should be the filename
                cd['DBQ'] = sd['name']
            else:
                if os.name == 'nt' or (sd['options']['driver'] == 'FreeTDS' and sd['options']['host_is_server']):
                    host = sd['host']
                    if sd['port']:
                        host += ',%s'%(sd['port'])
                        cd['SERVER'] = host
                    else:
                        cd['SERVERNAME'] = host
        if sd['user'] is not None:
            cd['UID']=sd['user']
        if sd['password'] is not None:
            cd['PWD']=sd['password']
        if sd['user'] is True:
            if sd['options']['driver'] in (DRIVER_SQL_SERVER, DRIVER_SQL_NATIVE_CLIENT):
                cd['Trusted_Connection'] = 'yes'
            else:
                cd['Integrated Security'] = 'SSPI'

        if sd['options']['driver'] != DRIVER_ACCESS:
            cd['DATABASE'] = sd['name']

        if sd['options']['MARS_Connection']:
            cd['MARS_Connection']='yes'

        if sd['options']['extra_params']:
            cd.update(sd['options']['extra_params'])

        return cd

    def _get_new_connection_kwargs(self):
        return dict()
    
        z = dict(
            autocommit = self.settings_dict['options']['autocommit'],
        )
        if self.settings_dict['options']['unicode_results']:
            z['unicode_results'] = True
        return z

    def _open_new_connection(self):
        fnm='[DatabaseWrapper._open_new_connection(base.py:MS-Access)]'
       #connstr = ';'.join(('%s=%s'%(k, v) for k, v in six.iteritems(self._get_connstring_data())))
        connstr = ';'.join(('%s=%s'%(k, v) for k, v in self._get_connstring_data().items()))
        kwargs = self._get_new_connection_kwargs()
        #print(f"[_open_new_connection]conn={connstr}")
        _DebugOutput(fnm,f"conn={connstr}")

        conn = Database.connect(connstr, **kwargs)
        #print(f"[_open_new_connection]conn={conn}")
        _DebugOutput(fnm,f"conn={conn}")

        self._on_connection_created(conn)
        return conn

    def _on_connection_created(self, conn):
        return
        # Set date format for the connection. Also, make sure Sunday is
        # considered the first day of the week (to be consistent with the
        # Django convention for the 'week_day' Django lookup) if the user
        # hasn't told us otherwise
        #cursor.execute("SET DATEFORMAT ymd; SET DATEFIRST %s" % self.datefirst)
        #if self.ops._get_sql_server_ver(self.connection) < 2005:
        #    self.creation.data_types['TextField'] = 'ntext'

        #if self.driver_needs_utf8 is None:
        #    self.driver_needs_utf8 = True
        #    self.drv_name = self.connection.getinfo(Database.SQL_DRIVER_NAME).upper()
        #    if self.drv_name in ('SQLSRV32.DLL', 'SQLNCLI.DLL', 'SQLNCLI10.DLL'):
        #        self.driver_needs_utf8 = False

            # http://msdn.microsoft.com/en-us/library/ms131686.aspx
            #if self.ops._get_sql_server_ver(self.connection) >= 2005 and self.drv_name in ('SQLNCLI.DLL', 'SQLNCLI10.DLL') and self.MARS_Connection:
                # How to to activate it: Add 'MARS_Connection': True
                # to the DATABASE_OPTIONS dictionary setting
                #self.features.can_use_chunked_reads = True

        # FreeTDS can't execute some sql queries like CREATE DATABASE etc.
        # in multi-statement, so we need to commit the above SQL sentence(s)
        # to avoid this
        #if self.drv_name.startswith('LIBTDSODBC') and not self.connection.autocommit:
            #self.connection.commit()

    def _cursor(self):
        fnm='[DatabaseWrapper._cursor(base.py:MS-Access)]'
        if self.connection is None:
            _DebugOutput(fnm,"connection is None")

            self.connection = self._open_new_connection()
            _DebugOutput(fnm,f"connection={self.connection}")
            _DebugOutput(fnm,f"__class__={self.__class__}")

            connection_created.send(sender=self.__class__)

        cursor = self.connection.cursor()
        _DebugOutput(fnm,f"cursor={cursor}")
        _DebugOutput(fnm,f"driver_needs_utf8={self.driver_needs_utf8}")
        return CursorWrapper(cursor, self.driver_needs_utf8)

class CursorWrapper(object):
    """
    A wrapper around the pyodbc's cursor that takes in account a) some pyodbc
    DB-API 2.0 implementation and b) some common ODBC driver particularities.
    """
    def __init__(self, cursor, driver_needs_utf8):
        fnm='[CursorWrapper.__init__(base.py:MS-Access)]'
        self.cursor = cursor
        self.driver_needs_utf8 = driver_needs_utf8
        self.last_sql = ''
        self.last_params = ()
        #print(f"[CursorWrapper.__init__] *** return ***")
        _DebugOutput(fnm,f" *** return ***")


    def format_sql(self, sql, n_params=None):
        fnm='[CursorWrapper.format_sql(base.py:MS-Access)]'
       #if self.driver_needs_utf8 and isinstance(sql, six.text_type):
        if self.driver_needs_utf8 and isinstance(sql, str):
            # FreeTDS (and other ODBC drivers?) doesn't support Unicode
            # yet, so we need to encode the SQL clause itself in utf-8
            sql = sql.encode('utf-8')
        # pyodbc uses '?' instead of '%s' as parameter placeholder.
        if n_params is not None:
            sql = sql % tuple('?' * n_params)
        else:
            if '%s' in sql:
                sql = sql.replace('%s', '?')
        #print(f"[CursorWrapper.format_sql]sql={sql}")
        _DebugOutput(fnm,f"sql={sql}")
        return sql

    def format_params(self, params):
        fnm='[CursorWrapper.format_params(base.py:MS-Access)]'

        if params is None:
            return tuple([])
        
        fp = []
        for p in params:
            #print(f"[format_params]p={p} isinstance(p, str)={isinstance(p, str)}")
            _DebugOutput(fnm,f"p={p} isinstance(p, str)={isinstance(p, str)}")

            if isinstance(p, str):
                try:
                    #2025-10-04 07:42:35.088840+00:00
                    dt = datetime.strptime(p, '%Y-%m-%d %H:%M:%S.%f%z')
                    fp.append(dt)
                    continue

                    # dt= datetime.strptime(p, '%Y-%m-%d %H:%M:%S.%f%z')
                    # parts = p.split('.')
                    # result_split = parts[0]
                    # p_str= '#' + result_split + '#'
                    # p_str= datetime(2025, 10, 4, 8, 52, 20)
                    # fp.append(p_str)
                    # continue
                except:
                    pass

            if isinstance(p, str):
                try:
                    #2025-10-04 07:42:35+00:00
                    dt = datetime.strptime(p, '%Y-%m-%d %H:%M:%S%z')
                    fp.append(dt)
                    continue
                except:
                    pass





           #if isinstance(p, six.text_type):
            # if isinstance(p, datetime):
            #     print(f"[format_params]datetime={p}")
            #     p_str= '#' + p.strftime('%Y-%m-%d %H:%M:%S') + '#'
            #     fp.append(p_str)
            #     continue

            if isinstance(p, str):
                if self.driver_needs_utf8:
                    # FreeTDS (and other ODBC drivers?) doesn't support Unicode
                    # yet, so we need to encode parameters in utf-8
                    fp.append(p.encode('utf-8'))
                else:
                    fp.append(p)
            elif isinstance(p, str):
                if self.driver_needs_utf8:
                    # TODO: use system encoding when calling decode()?
                    fp.append(p.decode('utf-8').encode('utf-8'))
                else:
                    fp.append(p)
            elif isinstance(p, type(True)):
                if p:
                    fp.append(-1)
                else:
                    fp.append(0)
            elif type(p) == type(1):
                #print(f"[format_params]type(p):{type(p)} == type(1)")
                _DebugOutput(fnm,f"type(p):{type(p)} == type(1)")
                fp.append(int(p))
            else:
                fp.append(p)
        #print(f"[CursorWrapper.format_params]---return---:fp={fp}")
        _DebugOutput(fnm,f"---return---:fp={fp}")
        return tuple(fp)

    def execute(self, sql, params=()):
        fnm='[CursorWrapper.execute(base.py:MS-Access)]'
        #print(f"----[START][CursorWrapper.execute]----")
        #print(f"[CursorWrapper.execute]sql={sql}")
        #print(f"[CursorWrapper.execute]params={params}")
        _DebugOutput(fnm,f"----[START][CursorWrapper.execute]----")
        _DebugOutput(fnm,f"sql={sql}")
        _DebugOutput(fnm,f"params={params}")

        for reobj in IGNORE_SQLStmt_cpl:
            if reobj.match(sql):
                print('\n\n')
                print('v'*60)
                print(' '*20+'Ignore SQL Statement.')
                print(' '*14 +'[CursorWrapper.execute(base.py)]')
                print('^'*60)
                print(f'[EXECUTE_SQL]sql={sql}')
                print('This SQL statement cannot be executed in Microsoft Access.')
                print('The execution of this SQL statement will be ignored.')
                print('\n\n')
                return
            

        need_commit = True
        if len(sql) > 5:
           str = sql[:6].upper()
           if str == 'SELECT':
                need_commit = False
                # is_patch, patch_number, new_sql = patch_select(sql)
                success, rebuilt, data = SELECT_PATCH_0010(sql)
                patch_number='SELECT_PATCH_0010'
                if success:
                    _DebugOutput(fnm,'\n\n')
                    _DebugOutput(fnm,'******************************')
                    _DebugOutput(fnm,'      [PATCH]  SELECT         ')
                    _DebugOutput(fnm,'[CursorWrapper.execute(base.py)]')
                    _DebugOutput(fnm,'******************************')
                    _DebugOutput(fnm,'The SELECT statement has been modified to be executable in Microsoft Access.')
                    _DebugOutput(fnm,f'[Patch Number] {patch_number}')
                    _DebugOutput(fnm,f'[Original SQL] {sql}')
                    _DebugOutput(fnm,f'[ Patched SQL] {rebuilt}')
                    sql = rebuilt


        #print(f"[CursorWrapper.execute]need_commit={need_commit}")
        _DebugOutput(fnm,f"need_commit={need_commit}")

        self.last_sql = sql
       #sql = self.format_sql(sql, len(params))
        sql = self.format_sql(sql, None if params is None else len(params))
        #print(f"[CursorWrapper.execute]sql(2)={sql}")
        _DebugOutput(fnm,f"sql(2)={sql}")
        params = self.format_params(params)


        self.last_params = params
        #print("\n")
        #print(f"[CursorWrapper.execute]sql={sql}")
        #print(f"[CursorWrapper.execute]params={params}")
        #print(f"----[CALL][self.cursor.execute]----")
        _DebugOutput(fnm, "\n")
        _DebugOutput(fnm,f"sql={sql}")
        _DebugOutput(fnm,f"params={params}")
        _DebugOutput(fnm, "----[CALL][self.cursor.execute]----")

        if len(sql) > 11:
            str = sql[:12].upper()
            if str == 'INSERT INTO ':
                is_patch, patch_number, divided_q_count, new_params, new_sql = (
                  patch_insert(sql, params) )
                if is_patch and patch_number=='INSERT_PATCH_0010':
                    _DebugOutput(fnm,'\n\n')
                    _DebugOutput(fnm,'******************************')
                    _DebugOutput(fnm,'      [PATCH]  INSERT         ')
                    _DebugOutput(fnm,'[CursorWrapper.execute(base.py)]')
                    _DebugOutput(fnm,'******************************')
                    _DebugOutput(fnm,'The INSERT statement has been modified to be executable in Microsoft Access.')
                    _DebugOutput(fnm,'Multiple records cannot be registered with one insert statement.')
                    _DebugOutput(fnm,'Register ONE RECORD at a time.')
                    _DebugOutput(fnm,f'[Patch Number] {patch_number}')
                    _DebugOutput(fnm,f'[Original SQL] {sql}')
                    _DebugOutput(fnm,f'[ Patched SQL] {new_sql}')
                    _DebugOutput(fnm,f'[Original PARAM] {params}')
                    _DebugOutput(fnm,f'[ Patched PARAM] {new_params}')
                    for param in new_params:
                        ret=""
                        try:
                            _DebugOutput(fnm,f"[EXECUTE_SQL]sql={new_sql}")
                            _DebugOutput(fnm,f"[EXECUTE_PAM]params={param}")
                            ret = self.cursor.execute(new_sql, param)
                            self.connection.commit()
                        except Database.Error as e:
                            print(f"\n\n*** [ODBC ERROR(1)] ***\n[CursorWrapper.execute(base.py)]\nsql={sql}\nparams={params}\n{e}\n\n")
                    return ret

        #
        # convert from 'CASE WHEN'.
        #
        # SELECT COUNT(CASE WHEN [auth_user].[is_staff] THEN [auth_user].[id] ELSE NULL END) AS [true__c],
        #        COUNT(CASE WHEN NOT [auth_user].[is_staff] THEN [auth_user].[id] ELSE NULL END) AS [false__c],
        #        COUNT(CASE WHEN [auth_user].[is_staff] IS NULL THEN [auth_user].[id] ELSE NULL END) AS [null__c]
        # FROM [auth_user]
        #
        newsql = convert_nested_case_to_iif(sql)
        if newsql != sql:
            _DebugOutput(fnm,f"[Convert_CaseWhen]originalSQL={sql}")
            _DebugOutput(fnm,f"[Convert_CaseWhen] convertSQL={newsql}")
            sql = newsql



        truncate_flag = False
        idx = 0
        if pkg.__truncate_name__:
            for item in TruncateName_SQLStmt_cpl:
                if item.match(sql):
                    trunc_sql =item.sub(TruncateName_SQLStmt[idx]['sql'], sql)
                    truncate_flag = True
                    break
                else:
                    idx = idx + 1
                    continue
            if truncate_flag:
                _DebugOutput("\n\n----- truncate name -----")
                _DebugOutput(fnm,"Microsoft Access constraint name length is maximum 64 characters.")
                _DebugOutput(fnm,"Names longer than 64 characters will be truncated.")
                _DebugOutput(fnm,f"original sql={sql}")
                _DebugOutput(fnm,f"truncate sql={trunc_sql}")
                _DebugOutput("-"*25)
                _DebugOutput("\n")
                sql=trunc_sql

       #return self.cursor.execute(sql, params)
        ret=""
        try:
            _DebugOutput(fnm,f"[EXECUTE_SQL]sql={sql}")
            _DebugOutput(fnm,f"[EXECUTE_PAM]params={params}")
            ret = self.cursor.execute(sql, params)
        except Database.Error as e:
            print(f"\n\n*** [ODBC ERROR(2)] ***\n[CursorWrapper.execute(base.py)]\nsql={sql}\nparams={params}\n{e}\n\n")

        #print(f"[CursorWrapper.execute]ret={ret}")
        _DebugOutput(fnm,f"ret={ret}")

        if need_commit:
            self.connection.commit()
            #print(f"----[COMMIT][self.cursor.execute]----")
            _DebugOutput(fnm, "----[COMMIT][self.cursor.execute]----")
        return ret

    def executemany(self, sql, params_list):
        fnm='[CursorWrapper.executemany(base.py:MS-Access)]'
        #print("\n")
        #print(f"[CursorWrapper.executemany]sql={sql}")
        #print(f"[CursorWrapper.executemany]params_list={params_list}")
        #print(f"----[CALL][self.cursor.executemany]----")
        _DebugOutput(fnm, "\n")
        _DebugOutput(fnm,f"sql={sql}")
        _DebugOutput(fnm,f"params_list={params_list}")
        _DebugOutput(fnm, "----[CALL][self.cursor.executemany]----")

        sql = self.format_sql(sql)
        # pyodbc's cursor.executemany() doesn't support an empty param_list
        if not params_list:
            if '?' in sql:
                return
        else:
            raw_pll = params_list
            params_list = [self.format_params(p) for p in raw_pll]
       #return self.cursor.executemany(sql, params_list)

        _DebugOutput(fnm,f"[EXECUTE_SQL]sql={sql}")
        _DebugOutput(fnm,f"[EXECUTE_PAM]params={params_list}")
        ret = self.cursor.executemany(sql, params_list)
        self.connection.commit()
        return ret


    def format_results(self, rows):
        """
        Decode data coming from the database if needed and convert rows to tuples
        (pyodbc Rows are not sliceable).
        """
        if not self.driver_needs_utf8:
            return tuple(rows)
        # FreeTDS (and other ODBC drivers?) doesn't support Unicode
        # yet, so we need to decode utf-8 data coming from the DB
        fr = []
        for row in rows:
            if isinstance(row, str):
                fr.append(row.decode('utf-8'))
            else:
                fr.append(row)
        return tuple(fr)

    def fetchone(self):
        row = self.cursor.fetchone()
        if row is not None:
            return self.format_results(row)
        return row

    def fetchmany(self, chunk):
        fnm='[CursorWrapper.fetchmany(base.py:MS-Access)]'
        #print(f"fetchmany(self, chunk):chunk={chunk}")
        _DebugOutput(fnm,f"chunk={chunk}")

        column_definition = self.cursor.description
        #print(f"column_definition={column_definition}")
        _DebugOutput(fnm,f"column_definition={column_definition}")


        result=[]
        for row in self.cursor.fetchmany(chunk):
            result.append(self.format_results(row))
        #print(f"result={result}")
        _DebugOutput(fnm,f"result={result}")
        return result            


        result=[]
        for iii in range(chunk):
            row = self.cursor.fetchone()
            print(f"cnt={iii} row={row}")
            if row is not None:
                result.append(self.format_results(row))
        return result            


        return [self.format_results(row) for row in self.cursor.fetchmany(chunk)]

    def fetchall(self):
        return [self.format_results(row) for row in self.cursor.fetchall()]

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return self.__dict__[attr]
        return getattr(self.cursor, attr)

    def __iter__(self):
        return iter(self.cursor)



    def __enter__(self):
        fnm='[CursorWrapper.__enter__(base.py:MS-Access)]'
        #print(f"[CursorWrapper.__enter__]")
        #print("Entering the context...")
        _DebugOutput(fnm,f"Entering the context...")
        return self  # オブジェクト自体を返す

    def __exit__(self, exc_type, exc_val, exc_tb):
        fnm='[CursorWrapper.__exit__(base.py:MS-Access)]'
        #print(f"[CursorWrapper.__exit__]")
        #print("Exiting the context...")
        _DebugOutput(fnm,f"Exiting the context...")
        # エラー処理を行うことも可能


    def close(self):
        fnm='[CursorWrapper.close(base.py:MS-Access)]'
        tl='[CursorWrapper.close]:'
        try:
            self.cursor.close()
            _DebugOutput(fnm,"********************")
            _DebugOutput(fnm,"   cursor close     ")
            _DebugOutput(fnm,"********************")
            return
        except Database.Error as e:
            #print(f"{tl} The cursor has already been closed.\n{e}\n")
            _DebugOutput(fnm,"The cursor has already been closed.")
            _DebugOutput(fnm,f"e={e}")
            return