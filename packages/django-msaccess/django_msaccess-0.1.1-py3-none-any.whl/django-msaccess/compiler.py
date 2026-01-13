import django

from django.db.models.sql import compiler
from datetime import datetime
if django.VERSION >= (4, 2):
    from django.core.exceptions import EmptyResultSet, FullResultSet

from .debug import _DebugOutput
#import six
#from six.moves import map

REV_ODIR = {
    'ASC': 'DESC',
    'DESC': 'ASC'
}

SQL_SERVER_8_LIMIT_QUERY = \
"""SELECT * FROM (
SELECT TOP %(limit)s *
  FROM (
    %(orig_sql)s
    ORDER BY %(ord)s
  ) AS %(table)s
  ORDER BY %(rev_ord)s
) AS %(table)s
ORDER BY %(ord)s
"""

SQL_SERVER_8_NO_LIMIT_QUERY = \
"""SELECT *
FROM %(table)s
WHERE %(key)s NOT IN (
  %(orig_sql)s
  ORDER BY %(ord)s
)"""

# Strategies for handling limit+offset emulation:
USE_ROW_NUMBER = 0 # For SQL Server >= 2005
USE_TOP_HMARK = 1 # For SQL Server 2000 when both limit and offset are provided
USE_TOP_LMARK = 2 # For SQL Server 2000 when offset but no limit is provided


class SQLCompiler(compiler.SQLCompiler):
    
    def convert_values(self, value, field):
        fnm='[SQLCompiler.convert_values(compiler.py:MS-Access)]'
        _DebugOutput(fnm,f"field={field.get_internal_type()}")
        _DebugOutput(fnm,f"value={value}")

        """
        Coerce the value returned by the database backend into a consistent
        type that is compatible with the field type.

        In our case, cater for the fact that SQL Server < 2008 has no
        separate Date and Time data types.
        TODO: See how we'll handle this for SQL Server >= 2008
        """
        if value is None:
            return None
        if field and field.get_internal_type() == 'DateTimeField':
            return value
        elif field and field.get_internal_type() == 'DateField':
            value = value.date() # extract date
        elif field and field.get_internal_type() == 'TimeField' or (isinstance(value, datetime) and value.year == 1900 and value.month == value.day == 1):
            value = value.time() # extract time
        # Some cases (for example when select_related() is used) aren't
        # caught by the DateField case above and date fields arrive from
        # the DB as datetime instances.
        # Implement a workaround stealing the idea from the Oracle
        # backend. It's not perfect so the same warning applies (i.e. if a
        # query results in valid date+time values with the time part set
        # to midnight, this workaround can surprise us by converting them
        # to the datetime.date Python type).
        elif isinstance(value, datetime) and value.hour == value.minute == value.second == value.microsecond == 0:
            value = value.date()
        # Force floats to the correct type
        elif value is not None and field and field.get_internal_type() == 'FloatField':
            value = float(value)
        return value
        
    def resolve_columns(self, row, fields=()):
        index_start = len(list(self.query.extra_select.keys()))
        values = [self.convert_values(v, None) for v in row[:index_start]]
       #for value, field in map(None, row[index_start:], fields):
        for value, field in zip(row[index_start:], fields):
            values.append(self.convert_values(value, field))
        return tuple(values)

    def modify_query(self, strategy, ordering, out_cols):
        """
        Helper method, called from _as_sql()

        Sets the value of the self._ord and self.default_reverse_ordering
        attributes.
        Can modify the values of the out_cols list argument and the
        self.query.ordering_aliases attribute.
        """
        self.default_reverse_ordering = False
        self._ord = []
        cnt = 0
        extra_select_aliases = [k.strip('[]') for k in list(self.query.extra_select.keys())]
        for ord_spec_item in ordering:
            if ord_spec_item.endswith(' ASC') or ord_spec_item.endswith(' DESC'):
                parts = ord_spec_item.split()
                col, odir = ' '.join(parts[:-1]), parts[-1]
                # if col not in self.query.ordering_aliases and col.strip('[]') not in extra_select_aliases:
                    # if col.isdigit():
                        # cnt += 1
                        # n = int(col)-1
                        # alias = 'OrdAlias%d' % cnt
                        # out_cols[n] = '%s AS [%s]' % (out_cols[n], alias)
                        # self._ord.append((alias, odir))
                    # elif col in out_cols:
                        # if strategy == USE_TOP_HMARK:
                            # cnt += 1
                            # n = out_cols.index(col)
                            # alias = 'OrdAlias%d' % cnt
                            # out_cols[n] = '%s AS %s' % (col, alias)
                            # self._ord.append((alias, odir))
                        # else:
                            # self._ord.append((col, odir))
                    # elif strategy == USE_TOP_HMARK:
                        # # Special case: '_order' column created by Django
                        # # when Meta.order_with_respect_to is used
                        # if col.split('.')[-1] == '[_order]' and odir == 'DESC':
                            # self.default_reverse_ordering = True
                        # cnt += 1
                        # alias = 'OrdAlias%d' % cnt
                        # self._ord.append((alias, odir))
                        # self.query.ordering_aliases.append('%s AS [%s]' % (col, alias))
                    # else:
                        # self._ord.append((col, odir))
                # else:
                    # self._ord.append((col, odir))
                self._ord.append((col, odir))
                if col not in out_cols:
                    out_cols.append(col)

        if strategy == USE_ROW_NUMBER and not self._ord and 'RAND()' in ordering:
            self._ord.append(('RAND()',''))
        if strategy == USE_TOP_HMARK and not self._ord:
            # XXX:
            #meta = self.get_meta()
            meta = self.query.model._meta
            qn = self.quote_name_unless_alias
            pk_col = '%s.%s' % (qn(meta.db_table), qn(meta.pk.db_column or meta.pk.column))
            if pk_col not in out_cols:
                out_cols.append(pk_col)

    def _as_sql(self, strategy):
        """
        Helper method, called from as_sql()
        Similar to django/db/models/sql/query.py:Query.as_sql() but without
        the ordering and limits code.

        Returns SQL that hasn't an order-by clause.
        """
        # get_columns needs to be called before get_ordering to populate
        # _select_alias.
        out_cols = self.get_columns(True)
        ordering, ordering_group_by = self.get_ordering()
        if strategy == USE_ROW_NUMBER:
            if not ordering:
                meta = self.query.get_meta()
                qn = self.quote_name_unless_alias
                # Special case: pk not in out_cols, use random ordering. 
                #
                if '%s.%s' % (qn(meta.db_table), qn(meta.pk.db_column or meta.pk.column)) not in self.get_columns():
                    ordering = ['RAND()']
                    # XXX: Maybe use group_by field for ordering?
                    #if self.group_by:
                        #ordering = ['%s.%s ASC' % (qn(self.group_by[0][0]),qn(self.group_by[0][1]))]
                else:
                    ordering = ['%s.%s ASC' % (qn(meta.db_table), qn(meta.pk.db_column or meta.pk.column))]

        if strategy in (USE_TOP_HMARK, USE_ROW_NUMBER):
            self.modify_query(strategy, ordering, out_cols)

        if strategy == USE_ROW_NUMBER:
            ord = ', '.join(['%s %s' % pair for pair in self._ord])
            self.query.ordering_aliases.append('(ROW_NUMBER() OVER (ORDER BY %s)) AS [rn]' % ord)

        # This must come after 'select' and 'ordering' -- see docstring of
        # get_from_clause() for details.
        from_, f_params = self.get_from_clause()

        qn = self.quote_name_unless_alias
        where, w_params = self.query.where.as_sql(qn, self.connection)
        having, h_params = self.query.having.as_sql(qn, self.connection)
        params = []
        for val in six.itervalues(self.query.extra_select):
            params.extend(val[1])

        result = ['SELECT']
        if self.query.distinct:
            result.append('DISTINCT')

        if strategy == USE_TOP_LMARK:
            # XXX:
            #meta = self.get_meta()
            meta = self.query.model._meta
            result.append('TOP %s %s' % (self.query.low_mark, self.quote_name_unless_alias(meta.pk.db_column or meta.pk.column)))
        else:
            if strategy == USE_TOP_HMARK and self.query.high_mark is not None:
                result.append('TOP %s' % self.query.high_mark)
            result.append(', '.join(out_cols + self.query.ordering_aliases))

        result.append('FROM')
        result.extend(from_)
        params.extend(f_params)

        if where:
            result.append('WHERE %s' % where)
            params.extend(w_params)
        if hasattr(self.query, "extra_where") and self.query.extra_where:
            if not where:
                result.append('WHERE')
            else:
                result.append('AND')
            result.append(' AND '.join(self.query.extra_where))

        grouping, gb_params = self.get_grouping()
        if grouping:
            if ordering:
                # If the backend can't group by PK (i.e., any database
                # other than MySQL), then any fields mentioned in the
                # ordering clause needs to be in the group by clause.
                if not self.connection.features.allows_group_by_pk:
                    for col, col_params in ordering_group_by:
                        if col not in grouping:
                            grouping.append(str(col))
                            gb_params.extend(col_params)
            else:
                ordering = self.connection.ops.force_no_ordering()
            result.append('GROUP BY %s' % ', '.join(grouping))
            params.extend(gb_params)

        if having:
            result.append('HAVING %s' % having)
            params.extend(h_params)

        if hasattr(self.query, "extra_params"):
            params.extend(self.query.extra_params)

        return ' '.join(result), tuple(params)
        
    def __XX__XX__XX__get_from_clause(self):
        fnm='[SQLCompiler.__get_from_clause(compiler.py:MS-Access)]'
        _DebugOutput(fnm,f"class={self.__class__}")
        _DebugOutput(fnm,f"class(query)={self.query.__class__}")
        #print(f'[compiler.py(get_from_clause)]dir(query)={dir(self.query)}')
        _DebugOutput(fnm,f"table_map={self.query.table_map}")
        _DebugOutput(fnm,f"base_table={self.query.base_table}")
        _DebugOutput(fnm,f"alias_map={self.query.alias_map}")

        if not hasattr(self.query, 'tables'):
            _DebugOutput("\n\n"+fnm,"**** not exist 'tables' ****\n\n",force=True)
            #raise ValueError('*** ToDo ***')
        #exit()

        result = []
        qn = self.quote_name_unless_alias
        qn2 = self.connection.ops.quote_name
        first = True
        count_of_open_parens = 0
        _DebugOutput(fnm,f"qn={qn}")
        _DebugOutput(fnm,f"qn2={qn2}")


        #[2025/10/06]Add(if)
        if hasattr(self.query, 'tables'):
            for alias in self.query.tables:
                if not self.query.alias_refcount[alias]:
                    continue
                try:
                    name, alias, join_type, lhs, lhs_col, col, nullable = self.query.alias_map[alias]
                    count_of_open_parens += 1
                except KeyError:
                    continue
                
            for alias in self.query.tables:
                if not self.query.alias_refcount[alias]:
                    continue
                try:
                    name, alias, join_type, lhs, lhs_col, col, nullable = self.query.alias_map[alias]
                except KeyError:
                    # Extra tables can end up in self.tables, but not in the
                    # alias_map if they aren't in a join. That's OK. We skip them.
                    continue
                alias_str = (alias != name and ' %s' % alias or '')
                if join_type and not first:
                                  #INNER JOIN mytable as m ON (test = test.val))
                    result.append('%s %s%s ON (%s.%s = %s.%s))'
                            % (join_type, qn(name), alias_str, qn(lhs),
                               qn2(lhs_col), qn(alias), qn2(col)))
                else:
                    connector = not first and ', ' or ''
                    result.append('%s%s%s%s' % (connector, "("*(count_of_open_parens - 1), qn(name), alias_str))
                first = False
        else:
            #print(f'[compiler.py(get_from_clause)]class={self.__class__}')
            #print(f'[compiler.py(get_from_clause)]class(query)={self.query.__class__}')
            #print(f'[compiler.py(get_from_clause)]dir(query)={dir(self.query)}')
            #raise ValueError('**** "tables" property does not exist. ****')
            _DebugOutput('\n\n'+fnm,'**** "tables" property does not exist. ****\n\n',force=True)
            

        for t in self.query.extra_tables:
            alias, unused = self.query.table_alias(t)
            # Only add the alias if it's not already present (the table_alias()
            # calls increments the refcount, so an alias refcount of one means
            # this is the only reference.
            if alias not in self.query.alias_map or self.query.alias_refcount[alias] == 1:
                connector = not first and ', ' or ''
                result.append('%s%s' % (connector, qn(alias)))
                first = False

        _DebugOutput(fnm,f'result={result}')
        if not result:
            result.append(self.query.base_table)
        _DebugOutput(fnm,f'result={result}')
        #raise ValueError('**** todo ****')
        return result, []
        

    def as_sql(self, with_limits=True, with_col_aliases=False):
        fnm='[SQLCompiler.as_sql(compiler.py:MS-Access)]'
        _DebugOutput(fnm,"----- Outputting arguments. -----")
        _DebugOutput(fnm,f"[1]with_limits={with_limits}")
        _DebugOutput(fnm,f"[2]with_col_aliases={with_col_aliases}")
        """
        Creates the SQL for this query. Returns the SQL string and list of
        parameters.

        If 'with_limits' is False, any limit/offset information is not included
        in the query.
        """
        # The do_offset flag indicates whether we need to construct
        # the SQL needed to use limit/offset w/SQL Server.
        do_offset = False #with_limits and (self.query.high_mark is not None or self.query.low_mark != 0)

        # If no offsets, just return the result of the base class
        # `as_sql`.
        if not do_offset:
            try:
                _DebugOutput(fnm,"[0100]call super(SQLCompiler, self).as_sql()")
             #   ret, params = super(SQLCompiler, self).as_sql(with_limits=False,
             #                                         with_col_aliases=with_col_aliases)
                ret, params = self.BASE_CLASS_as_sql(with_limits=False,
                                                      with_col_aliases=with_col_aliases)

                return ret , params
            except TypeError as e:
                description = str(e)
                _DebugOutput('\n\n'+fnm,f"[1000]Error1={description}\n\n", force=True)

            except Exception as e:
                description = str(e)
                _DebugOutput('\n\n'+fnm,f"[1100]Error2={description}\n\n", force=True)
            return [],[]
            raise Exception('***ERROR***')


            return super(SQLCompiler, self).as_sql(with_limits=False,
                                                      with_col_aliases=with_col_aliases)
        # Shortcut for the corner case when high_mark value is 0:
        if self.query.high_mark == 0:
            return "", ()

        self.pre_sql_setup()
        # XXX:
        #meta = self.get_meta()
        meta = self.query.model._meta
        qn = self.quote_name_unless_alias
        fallback_ordering = '%s.%s' % (qn(meta.db_table), qn(meta.pk.db_column or meta.pk.column))

        # SQL Server 2000, offset+limit case
        if self.connection.ops.sql_server_ver < 2005 and self.query.high_mark is not None:
            orig_sql, params = self._as_sql(USE_TOP_HMARK)
            if self._ord:
                ord = ', '.join(['%s %s' % pair for pair in self._ord])
                rev_ord = ', '.join(['%s %s' % (col, REV_ODIR[odir]) for col, odir in self._ord])
            else:
                if not self.default_reverse_ordering:
                    ord = '%s ASC' % fallback_ordering
                    rev_ord = '%s DESC' % fallback_ordering
                else:
                    ord = '%s DESC' % fallback_ordering
                    rev_ord = '%s ASC' % fallback_ordering
            sql = SQL_SERVER_8_LIMIT_QUERY % {
                'limit': self.query.high_mark - self.query.low_mark,
                'orig_sql': orig_sql,
                'ord': ord,
                'rev_ord': rev_ord,
                # XXX:
                'table': qn(meta.db_table),
            }
            return sql, params

        # SQL Server 2000, offset without limit case
        # get_columns needs to be called before get_ordering to populate
        # select_alias.
        self.get_columns(with_col_aliases)
        ordering, ordering_group_by = self.get_ordering()
        if ordering:
            ord = ', '.join(ordering)
        else:
            # We need to define an ordering clause since none was provided
            ord = fallback_ordering
        orig_sql, params = self._as_sql(USE_TOP_LMARK)
        sql = SQL_SERVER_8_NO_LIMIT_QUERY % {
            'orig_sql': orig_sql,
            'ord': ord,
            'table': qn(meta.db_table),
            'key': qn(meta.pk.db_column or meta.pk.column),
        }
        return sql, params


    def BASE_CLASS_as_sql(self, with_limits=True, with_col_aliases=False):
        fnm='[SQLCompiler.BASE_CLASS_as_sql(compiler.py:MS-Access)]'
        _DebugOutput(fnm,"----- Outputting arguments. -----")
        _DebugOutput(fnm,f"[1]with_limits={with_limits}")
        _DebugOutput(fnm,f"[2]with_col_aliases={with_col_aliases}")
        """
        Create the SQL for this query. Return the SQL string and list of
        parameters.

        If 'with_limits' is False, any limit/offset information is not included
        in the query.
        """
        refcounts_before = self.query.alias_refcount.copy()
        _DebugOutput(fnm,f"refcounts_before={refcounts_before}")
        try:
            _DebugOutput(fnm,"----- [BEFORE]self.pre_sql_setup -----")
            extra_select, order_by, group_by = self.pre_sql_setup()
            _DebugOutput(fnm,f"extra_select={extra_select}")
            _DebugOutput(fnm,f"order_by={order_by}")
            _DebugOutput(fnm,f"group_by={group_by}")
            _DebugOutput(fnm,"----- [AFTER]self.pre_sql_setup -----")

            for_update_part = None
            # Is a LIMIT/OFFSET clause needed?
            with_limit_offset = with_limits and (self.query.high_mark is not None or self.query.low_mark)
            combinator = self.query.combinator
            features = self.connection.features
            _DebugOutput(fnm,"[POS]1000")
            _DebugOutput(fnm,f"with_limit_offset={with_limit_offset}")
            _DebugOutput(fnm,f"combinator={combinator}")
            _DebugOutput(fnm,f"features={features}")

            if combinator:
                if not getattr(features, 'supports_select_{}'.format(combinator)):
                    raise NotSupportedError('{} is not supported on this database backend.'.format(combinator))
                result, params = self.get_combinator_sql(combinator, self.query.combinator_all)
            else:
                distinct_fields, distinct_params = self.get_distinct()
                _DebugOutput(fnm,"[POS]1100")
                _DebugOutput(fnm,f"distinct_fields={distinct_fields}")
                _DebugOutput(fnm,f"distinct_params={distinct_params}")

                # This must come after 'select', 'ordering', and 'distinct'
                # (see docstring of get_from_clause() for details).
                from_, f_params = self.get_from_clause()
                _DebugOutput(fnm,"[POS]1200")
                _DebugOutput(fnm,f"from_={from_}")
                _DebugOutput(fnm,f"f_params={f_params}")
                _DebugOutput(fnm,f"self.where={self.where}")
                _DebugOutput(fnm,f"self.compile={self.BASE_CLASS_compile(self.where)}")

                #
                # I used "mssql-django" as a reference.
                #
                if django.VERSION >= (4, 2):
                    try:
                        where, w_params = self.compile(self.where) if self.where is not None else ("", [])
                    except EmptyResultSet:
                        if self.elide_empty:
                            _DebugOutput(fnm,f"self.elide_empty={self.elide_empty}")
                            _DebugOutput(fnm, "(except EmptyResultSet) raise")
                            #**raise
                        # Use a predicate that's always False.
                        where, w_params = "0 = 1", []
                    except FullResultSet:
                        where, w_params = "", []
                        _DebugOutput(fnm,f"(except FullResultSet)")

                    try:
                        having, h_params = self.compile(self.having) if self.having is not None else ("", [])
                    except FullResultSet:
                        having, h_params = "", []
                else:
                    where, w_params = self.compile(self.where) if self.where is not None else ("", [])
                    having, h_params = self.compile(self.having) if self.having is not None else ("", [])
                params = []
                result = ['SELECT']

                # try:
                #    _DebugOutput(fnm,"[POS]1250")
                #    where, w_params = self.compile(self.where) if self.where is not None else ("", [])
                # except Exception as e:
                #    print("!!!!!!!!!!!!!!!!!ERROR!!!!!!!!!!!!!!!") 
                #    exit()
                # _DebugOutput(fnm,"[POS]1300")

                # having, h_params = self.compile(self.having) if self.having is not None else ("", [])
                _DebugOutput(fnm,"[POS]1400")


                # result = ['SELECT']
                # params = []

                if self.query.distinct:
                    distinct_result, distinct_params = self.connection.ops.distinct_sql(
                        distinct_fields,
                        distinct_params,
                    )
                    _DebugOutput(fnm,"[POS]2000")

                    result += distinct_result
                    params += distinct_params

                out_cols = []
                col_idx = 1
                for _, (s_sql, s_params), alias in self.select + extra_select:
                    if alias:
                        s_sql = '%s AS %s' % (s_sql, self.connection.ops.quote_name(alias))
                        _DebugOutput(fnm,"[POS]2500")

                    elif with_col_aliases:
                        s_sql = '%s AS %s' % (s_sql, 'Col%d' % col_idx)
                        col_idx += 1
                        _DebugOutput(fnm,"[POS]3000")


                    params.extend(s_params)
                    out_cols.append(s_sql)

                result += [', '.join(out_cols), 'FROM', *from_]
                params.extend(f_params)
                _DebugOutput(fnm,"[POS-4000]:call self.query.select_for_update")
                self_query_select_for_update = self.query.select_for_update
                _DebugOutput(fnm,f"[POS-4010]:self.query.select_for_update={self_query_select_for_update}")

                _DebugOutput(fnm,"[POS-4020]:call self.connection.features.has_select_for_update")
                self_connection_features_has_select_for_update = self.connection.features.has_select_for_update
                _DebugOutput(fnm,f"[POS-4030]:self.connection.features.has_select_for_update={self_connection_features_has_select_for_update}")

                if self.query.select_for_update and self.connection.features.has_select_for_update:
                    if self.connection.get_autocommit():
                        raise TransactionManagementError('select_for_update cannot be used outside of a transaction.')

                    if with_limit_offset and not self.connection.features.supports_select_for_update_with_limit:
                        raise NotSupportedError(
                            'LIMIT/OFFSET is not supported with '
                            'select_for_update on this database backend.'
                        )
                    nowait = self.query.select_for_update_nowait
                    skip_locked = self.query.select_for_update_skip_locked
                    of = self.query.select_for_update_of
                    no_key = self.query.select_for_no_key_update
                    # If it's a NOWAIT/SKIP LOCKED/OF/NO KEY query but the
                    # backend doesn't support it, raise NotSupportedError to
                    # prevent a possible deadlock.
                    if nowait and not self.connection.features.has_select_for_update_nowait:
                        raise NotSupportedError('NOWAIT is not supported on this database backend.')
                    elif skip_locked and not self.connection.features.has_select_for_update_skip_locked:
                        raise NotSupportedError('SKIP LOCKED is not supported on this database backend.')
                    elif of and not self.connection.features.has_select_for_update_of:
                        raise NotSupportedError('FOR UPDATE OF is not supported on this database backend.')
                    elif no_key and not self.connection.features.has_select_for_no_key_update:
                        raise NotSupportedError(
                            'FOR NO KEY UPDATE is not supported on this '
                            'database backend.'
                        )
                    for_update_part = self.connection.ops.for_update_sql(
                        nowait=nowait,
                        skip_locked=skip_locked,
                        of=self.get_select_for_update_of_arguments(),
                        no_key=no_key,
                    )



                _DebugOutput(fnm,f"[POS-4100]:for_update_part={for_update_part}")
                _DebugOutput(fnm,f"[POS-4110]:self.connection.features.for_update_after_from={self.connection.features.for_update_after_from}")
                if for_update_part and self.connection.features.for_update_after_from:
                    result.append(for_update_part)


                _DebugOutput(fnm,f"[POS-4200]:where={where}")
                if where:
                    result.append('WHERE %s' % where)
                    params.extend(w_params)

                _DebugOutput(fnm,f"[POS-4300]:result={result}")
                _DebugOutput(fnm,f"[POS-4310]:params={params}")

                grouping = []
                _DebugOutput(fnm,f"[POS-4350]:group_by={group_by}")

                for g_sql, g_params in group_by:
                    grouping.append(g_sql)
                    params.extend(g_params)

                _DebugOutput(fnm,f"[POS-4400]:grouping={grouping}")
                _DebugOutput(fnm,f"[POS-4410]:params={params}")
                _DebugOutput(fnm,f"[POS-4420]:having={having}")

                if grouping:
                    if distinct_fields:
                        raise NotImplementedError('annotate() + distinct(fields) is not implemented.')
                    order_by = order_by or self.connection.ops.force_no_ordering()
                    result.append('GROUP BY %s' % ', '.join(grouping))
                    if self._meta_ordering:
                        order_by = None

                if having:
                    result.append('HAVING %s' % having)
                    params.extend(h_params)

            _DebugOutput(fnm,f"[POS-4480]:self.query class ={self.query.__class__}")
           #_DebugOutput(fnm,f"[POS-4481]:dir(self.query)={dir(self.query)}")

            isExist_explain_query = hasattr(self.query, 'explain_query')
            _DebugOutput(fnm,f"[POS-4482]:isExist_explain_query={isExist_explain_query}")

            if isExist_explain_query:
                _DebugOutput(fnm, "[POS-4500]: 'explain_query' exists")
                if self.query.explain_query:
                    result.insert(0, self.connection.ops.explain_query_prefix(
                        self.query.explain_format,
                        **self.query.explain_options
                    ))
            else:
                _DebugOutput(fnm, "[POS-4510]: 'explain_query' does not exist")

            _DebugOutput(fnm,f"[POS-4550]:order_by={order_by}")
            if order_by:
                ordering = []
                for _, (o_sql, o_params, _) in order_by:
                    ordering.append(o_sql)
                    params.extend(o_params)
                result.append('ORDER BY %s' % ', '.join(ordering))

            _DebugOutput(fnm,f"[POS-4560]:result={result}")


            _DebugOutput(fnm,f"[POS-4600]:with_limit_offset={with_limit_offset}")
            if with_limit_offset:
                result.append(self.connection.ops.limit_offset_sql(self.query.low_mark, self.query.high_mark))

            if for_update_part and not self.connection.features.for_update_after_from:
                result.append(for_update_part)

            if self.query.subquery and extra_select:
                # If the query is used as a subquery, the extra selects would
                # result in more columns than the left-hand side expression is
                # expecting. This can happen when a subquery uses a combination
                # of order_by() and distinct(), forcing the ordering expressions
                # to be selected as well. Wrap the query in another subquery
                # to exclude extraneous selects.
                sub_selects = []
                sub_params = []
                for index, (select, _, alias) in enumerate(self.select, start=1):
                    if not alias and with_col_aliases:
                        alias = 'col%d' % index
                    if alias:
                        sub_selects.append("%s.%s" % (
                            self.connection.ops.quote_name('subquery'),
                            self.connection.ops.quote_name(alias),
                        ))
                    else:
                        select_clone = select.relabeled_clone({select.alias: 'subquery'})
                        subselect, subparams = select_clone.as_sql(self, self.connection)
                        sub_selects.append(subselect)
                        sub_params.extend(subparams)
                return 'SELECT %s FROM (%s) subquery' % (
                    ', '.join(sub_selects),
                    ' '.join(result),
                ), tuple(sub_params + params)

            return ' '.join(result), tuple(params)
        finally:
            # Finally do cleanup - get rid of the joins we created above.
            self.query.reset_refcounts(refcounts_before)

    def BASE_CLASS_compile(self, node):
        fnm='[SQLCompiler.BASE_CLASS_compile(compiler.py:MS-Access)]'
        _DebugOutput(fnm,"----- Outputting arguments. -----")
        _DebugOutput(fnm,f"[1]node={node}")
        _DebugOutput(fnm,f"   node class={node.__class__}")

        vendor_impl = getattr(node, 'as_' + self.connection.vendor, None)
        _DebugOutput(fnm,f"vendor_impl={vendor_impl}")


        if vendor_impl:
            sql, params = vendor_impl(self, self.connection)
            _DebugOutput(fnm,f"sql={sql}")
            _DebugOutput(fnm,f"params={params}")
        else:
            _DebugOutput(fnm,f"node={node}")
            _DebugOutput(fnm,f"node class={node.__class__}")
            _DebugOutput(fnm,f"self.connection class={self.connection.__class__}")
            _DebugOutput(fnm,f"self.connection={self.connection}")


            if django.VERSION >= (4, 2):
                try:
                    _DebugOutput(fnm,"call node.as_sql(self,self.connection)")
                    sql, params = node.as_sql(self,self.connection)
                    _DebugOutput(fnm,f"[django>=4.2]sql={sql}")
                    _DebugOutput(fnm,f"[django>=4.2]params={params}")
                    return sql, params
                except EmptyResultSet:
                    _DebugOutput(fnm,f"[django>=4.2]Received EmptyResultSet !!")
                    _DebugOutput(fnm,f"[django>=4.2]return '0 = 1', [] ")
                    return "0 = 1", []
                except FullResultSet:
                    _DebugOutput(fnm,f"[django>=4.2]Received FullResultSet !!")
                    _DebugOutput(fnm,f"[django>=4.2]return '', [] ")
                    return "", []
                except Exception as e:
                    _DebugOutput("\n\n")
                    _DebugOutput(fnm,"*"*50)
                    _DebugOutput(fnm,f"[django>=4.2:Exception ERROR]Received Exception !!")
                    _DebugOutput(fnm,f"[django>=4.2:Exception ERROR]e={e}")
                    _DebugOutput(fnm,"*"*50)

                raise f"[{fnm}] *** TODO ***"
            else:
                sql, params = node.as_sql(self,self.connection)
            sql, params = node.as_sql(self,self.connection)
            _DebugOutput(fnm,f"sql={sql}")
            _DebugOutput(fnm,f"params={params}")

        return sql, params




class SQLInsertCompiler_as_sql_Iterator(object):
    def __init__(self, sql_list):
        self.sql_list = sql_list
        self.current = 0

    def __iter__(self):
        return self

    def __next__(self):
        fnm='[SQLInsertCompiler_as_sql_Iterator.__next__(compiler.y:MS-Access)]'

        if self.current == len(self.sql_list):
            raise StopIteration()
        num = self.current
        self.current += 1
        sql_member=self.sql_list[num]
        sql_str = sql_member[0]
        sql_pam = sql_member[1]

        _DebugOutput(fnm,f"sql={sql_str}")
        _DebugOutput(fnm,f"params={sql_pam}")

        return sql_str, sql_pam




class Error_as_sql_Iterator(object):
    def __init__(self, sql_list):
        self.sql_list = sql_list
        self.current = 0

    def __iter__(self):
        return self

    def __next__(self):
        fnm='[Error_as_sql_Iterator.__next__(compiler.y:MS-Access)]'
        if self.current == len(self.sql_list):
            raise StopIteration()
        num = self.current
        self.current += 1
        sql_member=self.sql_list[num]
        sql_str = sql_member[0]
        sql_pam = sql_member[1]
        _DebugOutput(fnm,f"sql={sql_str}")
        _DebugOutput(fnm,f"params={sql_pam}")
        return sql_str, sql_pam



class SQLInsertCompiler(compiler.SQLInsertCompiler, SQLCompiler):
    def as_sql(self):
        fnm='[SQLInsertCompiler.as_sql(compiler.y:MS-Access)]'

        #[("INSERT INTO table ...", (1, 2, 3, 4))]
        #[("INSERT ... (%s, %s)", (1, 2)), ("INSERT ... (%s, %s, %s)", (10, 20, 30)), ...]
        try:
            ret = super(SQLInsertCompiler, self).as_sql()
            _DebugOutput(fnm,f"ret={ret}")
            return SQLInsertCompiler_as_sql_Iterator(ret)
        except AttributeError as e:
            description = str(e)
            _DebugOutput('\n\n'+fnm,f"Error1={description}\n\n",force=True)
            return Error_as_sql_Iterator([('','')])
        except ValueError as e:
            description = str(e)
            _DebugOutput('\n\n'+fnm,f"Error2={description}\n\n",force=True)
            return Error_as_sql_Iterator([('','')])
        except Exception as e:
            description = str(e)
            _DebugOutput('\n\n'+fnm,f"Error3={description}\n\n",force=True)
            return Error_as_sql_Iterator([('','')])
        
        print(fnm,'*' * 30)
        print(fnm,' ToDo '*4)
        print(fnm,'*' * 30)
        raise ValueError('*** ToDo ***') 



        if(len(tp)==1):
            sql=tp[0]
            params=None
        if(len(tp)==2):
            sql=tp[0]
            params=tp[1]

        #[SQLInsertCompiler(as_sql)]sql=('INSERT INTO [django_migrations] ([app], [name], [applied]) VALUES (%s, %s, %s)', ['contenttypes', '0001_initial', '2025-10-07 13:57:13.812697+00:00'])
        #[SQLInsertCompiler(as_sql)]params=None
        print(f'[SQLInsertCompiler(as_sql)]sql={sql}')
        print(f'[SQLInsertCompiler(as_sql)]params={params}')

        meta = self.query.get_meta()
        quoted_table = self.connection.ops.quote_name(meta.db_table)

        print(f'[SQLInsertCompiler(as_sql)]type(self.query)={type(self.query)}')
       #print(f'[compiler(as_sql)]dir(self.query)={dir(self.query)}')
       #print(f'[compiler(as_sql)]vars(self.query)={vars(self.query)}')
        print(f'[SQLInsertCompiler(as_sql)]meta.pk.attname={meta.pk.attname}')
        print(f'[SQLInsertCompiler(as_sql)]meta.pk.__class__.__name__={meta.pk.__class__.__name__}')

        # if meta.pk.attname in self.query.columns and meta.pk.__class__.__name__ == "AutoField":
        #     if len(self.query.columns) == 1 and not params:
        #         sql = "INSERT INTO %s DEFAULT VALUES" % quoted_table
        #     else:
        #         sql = "SET IDENTITY_INSERT %s ON;\n%s;\nSET IDENTITY_INSERT %s OFF" % \
        #             (quoted_table, sql, quoted_table)

        # return sql, params
        return SQLInsertCompiler_as_sql_Iterator(sql, params)


class SQLDeleteCompiler(compiler.SQLDeleteCompiler, SQLCompiler):
    def as_sql(self):
        fnm='[SQLDeleteCompiler.as_sql(compiler.py:MS-Access)]'
        sql, params = super(SQLDeleteCompiler, self).as_sql()
        _DebugOutput(fnm,f"sql={sql}")
        _DebugOutput(fnm,f"params={params}")
        return sql, params


class SQLUpdateCompiler(compiler.SQLUpdateCompiler, SQLCompiler):
    def as_sql(self):
        fnm='[SQLUpdateCompiler.as_sql(compiler.py:MS-Access)]'
        sql, params = super(SQLUpdateCompiler, self).as_sql()
        _DebugOutput(fnm,f"sql={sql}")
        _DebugOutput(fnm,f"params={params}")
        return sql, params


class SQLAggregateCompiler(compiler.SQLAggregateCompiler, SQLCompiler):
    def as_sql(self):
        fnm='[SQLAggregateCompiler.as_sql(compiler.py:MS-Access)]'
        sql, params = super(SQLAggregateCompiler, self).as_sql()
        _DebugOutput(fnm,f"sql={sql}")
        _DebugOutput(fnm,f"params={params}")
        return sql, params


# class SQLDateCompiler(compiler.SQLDateCompiler, SQLCompiler):
#     pass
# class SQLDateCompiler(compiler.SQLDateCompiler, SQLCompiler):
#     pass
