"""
Enhanced Transformation Functions for Bronze to Silver Layer
Supports all transformation types with robust error handling and validation
"""

import re
from typing import List, Dict, Any, Tuple, Optional


class TransformationError(Exception):
    """Custom exception for transformation errors"""
    pass


def get_table_columns(cursor, table_name: str, schema: str = None) -> List[str]:
    """
    Get column names from a Snowflake table
    
    Args:
        cursor: Snowflake database cursor
        table_name: Name of the table
        schema: Optional schema name (uses CURRENT_SCHEMA if not provided)
    
    Returns:
        List of column names in lowercase
    
    Raises:
        TransformationError: If table doesn't exist or query fails
    """
    try:
        schema_clause = f"AND TABLE_SCHEMA = '{schema.upper()}'" if schema else "AND TABLE_SCHEMA = CURRENT_SCHEMA()"
        
        query = f"""
        SELECT COLUMN_NAME 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = '{table_name.upper()}'
        {schema_clause}
        ORDER BY ORDINAL_POSITION
        """
        
        print(f"🔍 Querying columns for table: {table_name}")
        result = cursor.execute(query).fetchall()
        
        if not result:
            raise TransformationError(f"Table '{table_name}' not found or has no columns")
        
        columns = [row[0].lower() for row in result]
        print(f"✅ Found {len(columns)} columns: {columns[:5]}{'...' if len(columns) > 5 else ''}")
        return columns
        
    except Exception as e:
        raise TransformationError(f"Failed to get columns for table '{table_name}': {str(e)}")


def validate_table_exists(cursor, table_name: str, schema: str = None) -> bool:
    """
    Check if a table exists in Snowflake
    
    Args:
        cursor: Snowflake database cursor
        table_name: Name of the table to check
        schema: Optional schema name
    
    Returns:
        True if table exists, False otherwise
    """
    try:
        schema_clause = f"AND TABLE_SCHEMA = '{schema.upper()}'" if schema else "AND TABLE_SCHEMA = CURRENT_SCHEMA()"
        
        query = f"""
        SELECT COUNT(*) 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_NAME = '{table_name.upper()}'
        {schema_clause}
        """
        
        result = cursor.execute(query).fetchone()
        exists = result[0] > 0
        
        if exists:
            print(f"✅ Table '{table_name}' exists")
        else:
            print(f"❌ Table '{table_name}' does not exist")
        
        return exists
        
    except Exception as e:
        print(f"⚠️  Warning: Could not verify table existence: {e}")
        return False


def rename_columns(columns: List[str], mapping_columns: List[str]) -> List[str]:
    """
    Rename columns based on mapping configuration
    
    Args:
        columns: List of column names from source table
        mapping_columns: List of mappings in format ["old_col - new_col", ...]
                        Also supports: "old_col, new_col" or "old_col -> new_col"
    
    Returns:
        List of SQL column selections with aliases
    
    Example:
        Input: ["vendor_code", "vendor_name"], ["vendor_code - supplier_id"]
        Output: ["vendor_code AS supplier_id", "vendor_name"]
    """
    # Create mapping dictionary
    column_mapping = {}
    
    for mapping in mapping_columns:
        # Handle multiple separator formats: -, ->, ,
        parts = re.split(r'\s*(?:->|-|,)\s*', mapping.strip())
        
        if len(parts) >= 2:
            old_col = parts[0].strip().lower()
            new_col = parts[1].strip().lower()
            
            # Validate old column exists
            if old_col not in [c.lower() for c in columns]:
                print(f"⚠️  Warning: Source column '{old_col}' not found in table. Available: {columns[:5]}...")
                continue
            
            column_mapping[old_col] = new_col
            print(f"✅ Mapped: '{old_col}' -> '{new_col}'")
        else:
            print(f"⚠️  Warning: Invalid mapping format: '{mapping}'. Expected: 'old_name - new_name'")
    
    # Generate SQL column selections
    sql_columns = []
    for col in columns:
        col_lower = col.lower()
        if col_lower in column_mapping:
            sql_columns.append(f"{col} AS {column_mapping[col_lower]}")
        else:
            sql_columns.append(col)
    
    print(f"✅ Generated {len(sql_columns)} column selections ({len(column_mapping)} renamed)")
    return sql_columns


def handle_joins(join_transformations: List[Dict[str, Any]]) -> Tuple[List[str], List[str]]:
    """
    Parse and build JOIN clauses with proper syntax validation
    
    Args:
        join_transformations: List of join configurations with 'condition' and optional 'join_type'
    
    Returns:
        Tuple of (join_clauses, joined_tables)
    
    Example:
        Input: [{"condition": "purchase_order.vendor_code = dim_supplier.supplier_id", "join_type": "LEFT"}]
        Output: (["LEFT JOIN dim_supplier ON purchase_order.vendor_code = dim_supplier.supplier_id"], ["dim_supplier"])
    """
    join_clauses = []
    joined_tables = []
    
    for join_config in join_transformations:
        condition = join_config.get('condition', '').strip()
        join_type = join_config.get('join_type', 'INNER').upper()
        
        if not condition:
            print(f"⚠️  Warning: Empty join condition, skipping")
            continue
        
        # Validate join type
        valid_join_types = ['INNER', 'LEFT', 'RIGHT', 'FULL', 'CROSS']
        if join_type not in valid_join_types:
            print(f"⚠️  Warning: Invalid join type '{join_type}', using INNER")
            join_type = 'INNER'
        
        # Parse condition to extract table name
        # Format: "table1.col = table2.col" or just "condition"
        try:
            if '=' in condition:
                # Extract second table name from condition
                # Example: "purchase_order.vendor_code = dim_supplier.supplier_id"
                parts = condition.split('=')
                right_side = parts[1].strip()
                
                if '.' in right_side:
                    table_name = right_side.split('.')[0].strip()
                    joined_tables.append(table_name)
                    
                    # Build proper JOIN syntax
                    join_clause = f"{join_type} JOIN {table_name} ON {condition}"
                else:
                    # Simple condition without table prefix
                    join_clause = f"{join_type} JOIN {condition}"
            else:
                # Condition without equals (might be subquery or complex join)
                join_clause = f"{join_type} JOIN {condition}"
            
            join_clauses.append(join_clause)
            print(f"✅ Added {join_type} JOIN: {condition}")
            
        except Exception as e:
            print(f"⚠️  Warning: Could not parse join condition '{condition}': {e}")
            # Add as-is if parsing fails
            join_clauses.append(f"{join_type} JOIN {condition}")
    
    return join_clauses, joined_tables


def select_columns(all_columns: List[str], select_columns_list: List[str]) -> List[str]:
    """
    Filter and select specific columns from available columns
    
    Args:
        all_columns: List of all available column names
        select_columns_list: List of columns to select
    
    Returns:
        List of selected column names
    
    Raises:
        TransformationError: If no valid columns found
    """
    if not select_columns_list:
        return all_columns
    
    # Remove duplicates while preserving order
    select_columns_list = list(dict.fromkeys(select_columns_list))
    
    # Convert to lowercase for case-insensitive matching
    all_columns_lower = [col.lower() for col in all_columns]
    select_columns_lower = [col.lower() for col in select_columns_list]
    
    # Find matching columns
    selected = []
    missing = []
    
    for sel_col in select_columns_lower:
        if sel_col in all_columns_lower:
            # Get original case column name
            idx = all_columns_lower.index(sel_col)
            selected.append(all_columns[idx])
        else:
            missing.append(sel_col)
    
    if missing:
        print(f"⚠️  Warning: Columns not found: {missing}")
    
    if not selected:
        raise TransformationError(f"No valid columns selected. Available: {all_columns[:10]}")
    
    print(f"✅ Selected {len(selected)} columns: {selected[:5]}{'...' if len(selected) > 5 else ''}")
    return selected


def derived_column(column_name: str, expression: str, validate: bool = True) -> str:
    """
    Create a derived column with SQL expression
    
    Args:
        column_name: Name of the output column
        expression: SQL expression to calculate the derived value
        validate: Whether to validate the expression (basic check)
    
    Returns:
        SQL string for the derived column
    
    Example:
        Input: "full_name", "CONCAT(first_name, ' ', last_name)"
        Output: "CONCAT(first_name, ' ', last_name) AS full_name"
    """
    if not column_name or not expression:
        raise TransformationError("Both column_name and expression are required")
    
    # Basic validation
    if validate:
        dangerous_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE']
        expr_upper = expression.upper()
        for keyword in dangerous_keywords:
            if keyword in expr_upper:
                raise TransformationError(f"Dangerous SQL keyword '{keyword}' detected in expression")
    
    sql_expression = f"{expression} AS {column_name}"
    print(f"✅ Created derived column: '{column_name}' = {expression}")
    return sql_expression


def conditional_flag(column_name: str, condition: str) -> str:
    """
    Create a conditional flag column (boolean: TRUE/FALSE or 0/1)
    
    Args:
        column_name: Name of the output flag column
        condition: SQL condition to evaluate
    
    Returns:
        SQL CASE statement for the conditional flag
    
    Example:
        Input: "is_active", "status = 'active'"
        Output: "CASE WHEN status = 'active' THEN TRUE ELSE FALSE END AS is_active"
    """
    if not column_name or not condition:
        raise TransformationError("Both column_name and condition are required")
    
    sql_case = f"CASE WHEN {condition} THEN TRUE ELSE FALSE END AS {column_name}"
    print(f"✅ Created conditional flag: '{column_name}' based on: {condition}")
    return sql_case


def aggregate_column(column_name: str, aggregation: str, group_by_columns: List[str] = None) -> str:
    """
    Create an aggregated column
    
    Args:
        column_name: Name of the column to aggregate
        aggregation: Aggregation function (SUM, AVG, COUNT, MIN, MAX)
        group_by_columns: Optional list of columns to group by
    
    Returns:
        SQL aggregation expression
    
    Example:
        Input: "amount", "SUM", ["customer_id"]
        Output: "SUM(amount) AS total_amount"
    """
    valid_aggs = ['SUM', 'AVG', 'COUNT', 'MIN', 'MAX', 'STDDEV', 'VARIANCE']
    agg_upper = aggregation.upper()
    
    if agg_upper not in valid_aggs:
        raise TransformationError(f"Invalid aggregation '{aggregation}'. Valid: {valid_aggs}")
    
    if agg_upper == 'COUNT':
        # COUNT can be COUNT(*) or COUNT(column)
        agg_expr = f"COUNT({column_name if column_name != '*' else '*'})"
    else:
        agg_expr = f"{agg_upper}({column_name})"
    
    output_name = f"{agg_upper.lower()}_{column_name}".replace('*', 'all')
    sql_expr = f"{agg_expr} AS {output_name}"
    
    print(f"✅ Created aggregation: {sql_expr}")
    return sql_expr


def apply_transformations(
    cursor,
    source_table: str,
    target_table: str,
    transformations: List[Dict[str, Any]],
    schema: str = None
) -> Tuple[str, int]:
    """
    Apply all transformations and generate final SQL
    
    Args:
        cursor: Snowflake database cursor
        source_table: Name of the source (bronze) table
        target_table: Name of the target (silver) table
        transformations: List of transformation configurations
        schema: Optional schema name
    
    Returns:
        Tuple of (generated_sql, estimated_complexity)
    
    Raises:
        TransformationError: If transformations fail
    """
    print(f"\n{'='*60}")
    print(f"🔄 Starting transformation: {source_table} → {target_table}")
    print(f"{'='*60}")
    
    # Validate source table exists
    if not validate_table_exists(cursor, source_table, schema):
        raise TransformationError(f"Source table '{source_table}' does not exist")
    
    # Get source columns
    try:
        columns = get_table_columns(cursor, source_table, schema)
    except Exception as e:
        raise TransformationError(f"Failed to get columns: {str(e)}")
    
    # Initialize SQL components
    select_columns_list = []
    additional_columns = []
    join_clauses = []
    where_clauses = []
    group_by_columns = []
    having_clauses = []
    order_by_columns = []
    
    # Track transformation complexity
    complexity_score = 0
    
    # Process each transformation in order
    for idx, transformation in enumerate(transformations, 1):
        trans_type = transformation.get('type', '').lower()
        print(f"\n📋 Transformation {idx}: {trans_type}")
        
        try:
            if trans_type == 'rename_columns':
                # Handle rename columns
                mappings = []
                if 'mappings' in transformation:
                    for mapping in transformation['mappings']:
                        from_col = mapping.get('from_col') or mapping.get('from')
                        to_col = mapping.get('to')
                        if from_col and to_col:
                            mappings.append(f"{from_col} - {to_col}")
                
                if mappings:
                    select_columns_list = rename_columns(columns, mappings)
                    complexity_score += 1
                else:
                    print(f"⚠️  No mappings provided for rename_columns")
            
            elif trans_type == 'join':
                # Handle joins
                condition = transformation.get('condition')
                join_type = transformation.get('join_type', 'INNER')
                
                if condition:
                    joins, tables = handle_joins([{
                        'condition': condition,
                        'join_type': join_type
                    }])
                    join_clauses.extend(joins)
                    complexity_score += 3  # Joins add significant complexity
                else:
                    print(f"⚠️  No condition provided for join")
            
            elif trans_type == 'select':
                # Handle column selection
                selected = transformation.get('selected_columns', [])
                if selected:
                    select_columns_list = select_columns(columns, selected)
                    complexity_score += 1
                else:
                    print(f"⚠️  No columns specified for select")
            
            elif trans_type == 'derived_column':
                # Handle derived columns
                expression = transformation.get('expression')
                new_col = transformation.get('new_column_name')
                
                if expression and new_col:
                    additional_columns.append(derived_column(new_col, expression))
                    complexity_score += 2
                else:
                    print(f"⚠️  Missing expression or column name for derived_column")
            
            elif trans_type == 'conditional_flag':
                # Handle conditional flags
                condition = transformation.get('condition')
                output_col = transformation.get('output_column')
                
                if condition and output_col:
                    additional_columns.append(conditional_flag(output_col, condition))
                    complexity_score += 2
                else:
                    print(f"⚠️  Missing condition or output column for conditional_flag")
            
            elif trans_type == 'where':
                # Handle WHERE clauses
                condition = transformation.get('condition')
                if condition:
                    where_clauses.append(condition)
                    print(f"✅ Added WHERE condition: {condition}")
                    complexity_score += 1
            
            elif trans_type == 'group_by':
                # Handle GROUP BY
                columns_to_group = transformation.get('columns', [])
                if columns_to_group:
                    group_by_columns.extend(columns_to_group)
                    print(f"✅ Added GROUP BY: {columns_to_group}")
                    complexity_score += 2
            
            elif trans_type == 'order_by':
                # Handle ORDER BY
                columns_to_order = transformation.get('columns', [])
                direction = transformation.get('direction', 'ASC').upper()
                
                if columns_to_order:
                    for col in columns_to_order:
                        order_by_columns.append(f"{col} {direction}")
                    print(f"✅ Added ORDER BY: {columns_to_order} {direction}")
                    complexity_score += 1
            
            else:
                print(f"⚠️  Unknown transformation type: '{trans_type}'")
        
        except Exception as e:
            print(f"❌ Error in transformation {idx} ({trans_type}): {str(e)}")
            raise TransformationError(f"Transformation {idx} failed: {str(e)}")
    
    # Build final column list
    if not select_columns_list:
        select_columns_list = columns
    
    # Add additional derived/flag columns
    all_columns = select_columns_list + additional_columns
    
    if not all_columns:
        raise TransformationError("No columns selected for output")
    
    # Build SQL statement
    columns_sql = ",\n    ".join(all_columns)
    
    sql = f"""CREATE OR REPLACE TABLE {target_table} AS
SELECT 
    {columns_sql}
FROM {source_table}"""
    
    # Add JOIN clauses
    if join_clauses:
        sql += "\n" + "\n".join(join_clauses)
    
    # Add WHERE clauses
    if where_clauses:
        sql += f"\nWHERE {' AND '.join(where_clauses)}"
    
    # Add GROUP BY
    if group_by_columns:
        sql += f"\nGROUP BY {', '.join(group_by_columns)}"
    
    # Add HAVING
    if having_clauses:
        sql += f"\nHAVING {' AND '.join(having_clauses)}"
    
    # Add ORDER BY
    if order_by_columns:
        sql += f"\nORDER BY {', '.join(order_by_columns)}"
    
    print(f"\n{'='*60}")
    print(f"✅ SQL generation complete")
    print(f"📊 Complexity score: {complexity_score}")
    print(f"📝 Columns: {len(all_columns)}, Joins: {len(join_clauses)}, Filters: {len(where_clauses)}")
    print(f"{'='*60}\n")
    
    return sql, complexity_score


def execute_pipeline(
    cursor,
    source_table: str,
    target_table: str,
    transformations: List[Dict[str, Any]],
    schema: str = None,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Execute complete pipeline transformation
    
    Args:
        cursor: Snowflake database cursor
        source_table: Source table name
        target_table: Target table name
        transformations: List of transformations to apply
        schema: Optional schema name
        dry_run: If True, generate SQL but don't execute
    
    Returns:
        Dictionary with execution results
    """
    result = {
        'success': False,
        'sql': None,
        'rows_processed': 0,
        'execution_time': 0,
        'error': None
    }
    
    try:
        import time
        start_time = time.time()
        
        # Generate SQL
        sql, complexity = apply_transformations(
            cursor,
            source_table,
            target_table,
            transformations,
            schema
        )
        
        result['sql'] = sql
        result['complexity'] = complexity
        
        if dry_run:
            print("🔍 DRY RUN - SQL generated but not executed")
            result['success'] = True
            result['dry_run'] = True
            return result
        
        # Execute SQL
        print(f"⏳ Executing transformation SQL...")
        cursor.execute(sql)
        
        # Get row count
        count_query = f"SELECT COUNT(*) FROM {target_table}"
        count_result = cursor.execute(count_query).fetchone()
        rows_processed = count_result[0] if count_result else 0
        
        execution_time = time.time() - start_time
        
        result['success'] = True
        result['rows_processed'] = rows_processed
        result['execution_time'] = round(execution_time, 2)
        
        print(f"✅ Transformation complete!")
        print(f"📊 Rows processed: {rows_processed:,}")
        print(f"⏱️  Execution time: {execution_time:.2f}s")
        
    except Exception as e:
        result['error'] = str(e)
        print(f"❌ Pipeline execution failed: {str(e)}")
    
    return result


# Utility functions

def validate_transformation_config(transformation: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate a transformation configuration
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    trans_type = transformation.get('type')
    
    if not trans_type:
        return False, "Transformation type is required"
    
    # Type-specific validation
    if trans_type == 'rename_columns':
        if 'mappings' not in transformation:
            return False, "rename_columns requires 'mappings'"
    
    elif trans_type == 'join':
        if 'condition' not in transformation:
            return False, "join requires 'condition'"
    
    elif trans_type == 'derived_column':
        if 'expression' not in transformation or 'new_column_name' not in transformation:
            return False, "derived_column requires 'expression' and 'new_column_name'"
    
    return True, ""


def preview_transformation(
    cursor,
    source_table: str,
    transformations: List[Dict[str, Any]],
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Preview transformation results without creating target table
    
    Args:
        cursor: Snowflake cursor
        source_table: Source table name
        transformations: List of transformations
        limit: Number of rows to preview
    
    Returns:
        List of sample rows
    """
    # Generate SQL without CREATE TABLE
    columns = get_table_columns(cursor, source_table)
    
    # Simplified transformation for preview
    select_cols = []
    for t in transformations:
        if t['type'] == 'rename_columns' and 'mappings' in t:
            for m in t['mappings']:
                from_col = m.get('from_col') or m.get('from')
                to_col = m.get('to')
                if from_col and to_col:
                    select_cols.append(f"{from_col} AS {to_col}")
    
    if not select_cols:
        select_cols = columns
    
    preview_sql = f"SELECT {', '.join(select_cols)} FROM {source_table} LIMIT {limit}"
    
    result = cursor.execute(preview_sql).fetchall()
    return [dict(row) for row in result]