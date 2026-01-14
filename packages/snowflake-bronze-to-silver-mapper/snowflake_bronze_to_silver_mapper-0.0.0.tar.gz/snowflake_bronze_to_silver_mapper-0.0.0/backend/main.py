"""
FastAPI Backend for Data Pipeline Manager
Integrated with enhanced transformation functions
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import snowflake.connector
from snowflake.connector import DictCursor
import sqlite3
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Import transformation functions
from transformation_functions import (
    execute_pipeline as execute_transformation,
    apply_transformations,
    preview_transformation,
    validate_transformation_config,
    validate_table_exists,
    TransformationError
)

load_dotenv()

app = FastAPI(title="Data Pipeline API", version="2.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SQLite database path
DB_PATH = os.getenv("DB_PATH", "pipeline_metadata.db")

# ==================== Database Helper Functions ====================

def get_db():
    """Get SQLite database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Initialize SQLite database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create pipelines table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pipelines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            domain TEXT NOT NULL,
            source_table TEXT NOT NULL,
            target_table TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT DEFAULT 'system'
        )
    """)
    
    # Create transformations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transformations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pipeline_id INTEGER NOT NULL,
            sequence_order INTEGER NOT NULL,
            type TEXT NOT NULL,
            config TEXT NOT NULL,
            FOREIGN KEY (pipeline_id) REFERENCES pipelines(id) ON DELETE CASCADE
        )
    """)
    
    # Create pipeline_runs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pipeline_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pipeline_id INTEGER NOT NULL,
            status TEXT NOT NULL,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            rows_processed INTEGER,
            execution_time REAL,
            error_message TEXT,
            generated_sql TEXT,
            complexity_score INTEGER,
            FOREIGN KEY (pipeline_id) REFERENCES pipelines(id)
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully")

# Initialize database on startup
init_db()

# ==================== Pydantic Models ====================

class ColumnMapping(BaseModel):
    from_col: Optional[str] = None
    from_: Optional[str] = None  # Alias for 'from'
    to: str

    class Config:
        fields = {'from_': 'from'}

class Transformation(BaseModel):
    type: str
    mappings: Optional[List[ColumnMapping]] = None
    condition: Optional[str] = None
    join_type: Optional[str] = "INNER"
    selected_columns: Optional[List[str]] = None
    new_column_name: Optional[str] = None
    expression: Optional[str] = None
    output_column: Optional[str] = None
    columns: Optional[List[str]] = None
    direction: Optional[str] = "ASC"

class Pipeline(BaseModel):
    name: str
    domain: str
    source_table: str
    target_table: str
    transformations: List[Transformation]
    description: Optional[str] = None

class PipelineResponse(BaseModel):
    id: int
    name: str
    domain: str
    source_table: str
    target_table: str
    transformations: List[Dict[str, Any]]
    status: str
    created_at: str

class QueryResponse(BaseModel):
    success: bool
    data: Optional[List[Dict[str, Any]]] = None
    row_count: Optional[int] = None
    error: Optional[str] = None

# ==================== Snowflake Connection ====================

def get_snowflake_connection():
    """Create Snowflake connection from environment variables"""
    try:
        conn = snowflake.connector.connect(
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            user=os.getenv("SNOWFLAKE_USERNAME"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
            database=os.getenv("SNOWFLAKE_DATABASE"),
            schema=os.getenv("SNOWFLAKE_SCHEMA")
        )
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Snowflake connection failed: {str(e)}")

# ==================== API Endpoints ====================

@app.get("/")
def read_root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Data Pipeline API",
        "version": "2.0.0",
        "features": [
            "Enhanced transformations",
            "Validation",
            "Preview support",
            "Complexity tracking"
        ]
    }

@app.get("/health")
def health_check():
    """Detailed health status"""
    snowflake_configured = all([
        os.getenv("SNOWFLAKE_ACCOUNT"),
        os.getenv("SNOWFLAKE_USERNAME"),
        os.getenv("SNOWFLAKE_PASSWORD")
    ])
    
    # Test database connection
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM pipelines")
        pipeline_count = cursor.fetchone()[0]
        conn.close()
        db_healthy = True
    except Exception as e:
        db_healthy = False
        pipeline_count = 0
    
    return {
        "status": "healthy",
        "database": "sqlite",
        "database_healthy": db_healthy,
        "snowflake_configured": snowflake_configured,
        "pipeline_count": pipeline_count,
        "db_path": DB_PATH
    }

# ==================== Pipeline CRUD Operations ====================

@app.post("/api/pipelines", response_model=PipelineResponse)
def create_pipeline(pipeline: Pipeline, db: sqlite3.Connection = Depends(get_db)):
    """Create a new pipeline configuration with validation"""
    cursor = db.cursor()
    
    try:
        # Validate transformations
        for idx, transform in enumerate(pipeline.transformations):
            is_valid, error_msg = validate_transformation_config(transform.dict())
            if not is_valid:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid transformation at index {idx}: {error_msg}"
                )
        
        # Insert pipeline
        cursor.execute("""
            INSERT INTO pipelines (name, domain, source_table, target_table, description)
            VALUES (?, ?, ?, ?, ?)
        """, (pipeline.name, pipeline.domain, pipeline.source_table, 
              pipeline.target_table, pipeline.description))
        
        pipeline_id = cursor.lastrowid
        
        # Insert transformations
        for idx, transform in enumerate(pipeline.transformations):
            config = transform.dict()
            cursor.execute("""
                INSERT INTO transformations (pipeline_id, sequence_order, type, config)
                VALUES (?, ?, ?, ?)
            """, (pipeline_id, idx, transform.type, json.dumps(config)))
        
        db.commit()
        
        print(f"✅ Pipeline created: {pipeline.name} (ID: {pipeline_id})")
        
        return get_pipeline_by_id(pipeline_id, db)
    
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Pipeline with this name already exists")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/pipelines", response_model=List[PipelineResponse])
def list_pipelines(domain: Optional[str] = None, db: sqlite3.Connection = Depends(get_db)):
    """List all pipelines, optionally filtered by domain"""
    cursor = db.cursor()
    
    if domain:
        cursor.execute("SELECT * FROM pipelines WHERE domain = ? ORDER BY created_at DESC", (domain,))
    else:
        cursor.execute("SELECT * FROM pipelines ORDER BY created_at DESC")
    
    pipelines = []
    for row in cursor.fetchall():
        pipeline = dict(row)
        
        # Get transformations
        cursor.execute("""
            SELECT type, config FROM transformations 
            WHERE pipeline_id = ? ORDER BY sequence_order
        """, (pipeline['id'],))
        
        transformations = []
        for t_row in cursor.fetchall():
            config = json.loads(t_row['config'])
            transformations.append(config)
        
        pipeline['transformations'] = transformations
        pipelines.append(pipeline)
    
    return pipelines

@app.get("/api/pipelines/{pipeline_id}", response_model=PipelineResponse)
def get_pipeline(pipeline_id: int, db: sqlite3.Connection = Depends(get_db)):
    """Get a specific pipeline by ID"""
    return get_pipeline_by_id(pipeline_id, db)

def get_pipeline_by_id(pipeline_id: int, db: sqlite3.Connection):
    """Helper function to get pipeline by ID"""
    cursor = db.cursor()
    cursor.execute("SELECT * FROM pipelines WHERE id = ?", (pipeline_id,))
    row = cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    pipeline = dict(row)
    
    # Get transformations
    cursor.execute("""
        SELECT type, config FROM transformations 
        WHERE pipeline_id = ? ORDER BY sequence_order
    """, (pipeline_id,))
    
    transformations = []
    for t_row in cursor.fetchall():
        config = json.loads(t_row['config'])
        transformations.append(config)
    
    pipeline['transformations'] = transformations
    return pipeline

@app.put("/api/pipelines/{pipeline_id}")
def update_pipeline(pipeline_id: int, pipeline: Pipeline, db: sqlite3.Connection = Depends(get_db)):
    """Update an existing pipeline"""
    cursor = db.cursor()
    
    try:
        # Validate transformations
        for idx, transform in enumerate(pipeline.transformations):
            is_valid, error_msg = validate_transformation_config(transform.dict())
            if not is_valid:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid transformation at index {idx}: {error_msg}"
                )
        
        # Update pipeline
        cursor.execute("""
            UPDATE pipelines 
            SET name = ?, domain = ?, source_table = ?, target_table = ?, 
                description = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (pipeline.name, pipeline.domain, pipeline.source_table, 
              pipeline.target_table, pipeline.description, pipeline_id))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Pipeline not found")
        
        # Delete old transformations
        cursor.execute("DELETE FROM transformations WHERE pipeline_id = ?", (pipeline_id,))
        
        # Insert new transformations
        for idx, transform in enumerate(pipeline.transformations):
            config = transform.dict()
            cursor.execute("""
                INSERT INTO transformations (pipeline_id, sequence_order, type, config)
                VALUES (?, ?, ?, ?)
            """, (pipeline_id, idx, transform.type, json.dumps(config)))
        
        db.commit()
        
        print(f"✅ Pipeline updated: {pipeline.name} (ID: {pipeline_id})")
        
        return {"message": "Pipeline updated successfully"}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/pipelines/{pipeline_id}")
def delete_pipeline(pipeline_id: int, db: sqlite3.Connection = Depends(get_db)):
    """Delete a pipeline"""
    cursor = db.cursor()
    cursor.execute("DELETE FROM pipelines WHERE id = ?", (pipeline_id,))
    
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    db.commit()
    
    print(f"✅ Pipeline deleted: ID {pipeline_id}")
    
    return {"message": "Pipeline deleted successfully"}

# ==================== Pipeline Execution (Enhanced) ====================

@app.post("/api/pipelines/{pipeline_id}/execute")
def execute_pipeline(pipeline_id: int, db: sqlite3.Connection = Depends(get_db)):
    """
    Execute a pipeline using enhanced transformation functions
    This now includes validation, error handling, and performance tracking
    """
    
    print(f"\n{'='*60}")
    print(f"🚀 Executing Pipeline ID: {pipeline_id}")
    print(f"{'='*60}")
    
    # Get pipeline configuration
    pipeline = get_pipeline_by_id(pipeline_id, db)
    
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO pipeline_runs (pipeline_id, status)
        VALUES (?, 'running')
    """, (pipeline_id,))
    run_id = cursor.lastrowid
    db.commit()
    
    sf_conn = None
    try:
        # Connect to Snowflake
        sf_conn = get_snowflake_connection()
        sf_cursor = sf_conn.cursor()
        
        # Validate source table exists
        if not validate_table_exists(sf_cursor, pipeline['source_table']):
            raise TransformationError(
                f"Source table '{pipeline['source_table']}' does not exist in Snowflake. "
                f"Please create it first or update the pipeline configuration."
            )
        
        # 🔥 EXECUTE USING ENHANCED TRANSFORMATION FUNCTIONS 🔥
        result = execute_transformation(
            cursor=sf_cursor,
            source_table=pipeline['source_table'],
            target_table=pipeline['target_table'],
            transformations=pipeline['transformations'],
            schema=os.getenv("SNOWFLAKE_SCHEMA"),
            dry_run=False
        )
        
        if not result['success']:
            raise TransformationError(result.get('error', 'Unknown error'))
        
        # Update run status with detailed metrics
        cursor.execute("""
            UPDATE pipeline_runs 
            SET status = 'completed', 
                completed_at = CURRENT_TIMESTAMP, 
                rows_processed = ?,
                execution_time = ?,
                generated_sql = ?,
                complexity_score = ?
            WHERE id = ?
        """, (
            result['rows_processed'],
            result['execution_time'],
            result['sql'],
            result.get('complexity', 0),
            run_id
        ))
        db.commit()
        
        print(f"\n✅ Pipeline execution completed successfully!")
        print(f"📊 Rows processed: {result['rows_processed']:,}")
        print(f"⏱️  Execution time: {result['execution_time']}s")
        print(f"{'='*60}\n")
        
        return {
            "success": True,
            "run_id": run_id,
            "rows_processed": result['rows_processed'],
            "execution_time": result['execution_time'],
            "complexity_score": result.get('complexity', 0),
            "message": f"Pipeline executed successfully. {result['rows_processed']:,} rows processed in {result['execution_time']}s.",
            "generated_sql": result['sql']
        }
    
    except TransformationError as te:
        # Handle transformation-specific errors
        error_message = str(te)
        cursor.execute("""
            UPDATE pipeline_runs 
            SET status = 'failed', 
                completed_at = CURRENT_TIMESTAMP, 
                error_message = ?
            WHERE id = ?
        """, (error_message, run_id))
        db.commit()
        
        print(f"\n❌ Pipeline execution failed: {error_message}\n")
        
        raise HTTPException(status_code=400, detail=f"Pipeline execution failed: {error_message}")
    
    except Exception as e:
        # Handle general errors
        error_message = str(e)
        cursor.execute("""
            UPDATE pipeline_runs 
            SET status = 'failed', 
                completed_at = CURRENT_TIMESTAMP, 
                error_message = ?
            WHERE id = ?
        """, (error_message, run_id))
        db.commit()
        
        print(f"\n❌ Pipeline execution failed: {error_message}\n")
        
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {error_message}")
    
    finally:
        if sf_conn:
            sf_conn.close()

@app.post("/api/pipelines/{pipeline_id}/preview")
def preview_pipeline(pipeline_id: int, limit: int = 10, db: sqlite3.Connection = Depends(get_db)):
    """
    Preview pipeline results without creating target table
    Useful for testing transformations
    """
    
    pipeline = get_pipeline_by_id(pipeline_id, db)
    
    sf_conn = None
    try:
        sf_conn = get_snowflake_connection()
        sf_cursor = sf_conn.cursor()
        
        # Validate source table exists
        if not validate_table_exists(sf_cursor, pipeline['source_table']):
            raise TransformationError(f"Source table '{pipeline['source_table']}' does not exist")
        
        # Get preview data
        preview_data = preview_transformation(
            cursor=sf_cursor,
            source_table=pipeline['source_table'],
            transformations=pipeline['transformations'],
            limit=limit
        )
        
        return {
            "success": True,
            "preview_data": preview_data,
            "row_count": len(preview_data),
            "message": f"Preview generated for {len(preview_data)} sample rows"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Preview failed: {str(e)}")
    
    finally:
        if sf_conn:
            sf_conn.close()

@app.post("/api/pipelines/{pipeline_id}/validate")
def validate_pipeline(pipeline_id: int, db: sqlite3.Connection = Depends(get_db)):
    """
    Validate pipeline configuration without executing
    Checks table existence and transformation validity
    """
    
    pipeline = get_pipeline_by_id(pipeline_id, db)
    
    validation_results = {
        "valid": True,
        "errors": [],
        "warnings": []
    }
    
    sf_conn = None
    try:
        # Validate transformations
        for idx, transform in enumerate(pipeline['transformations']):
            is_valid, error_msg = validate_transformation_config(transform)
            if not is_valid:
                validation_results['valid'] = False
                validation_results['errors'].append(f"Transformation {idx+1}: {error_msg}")
        
        # Check Snowflake connection and tables
        try:
            sf_conn = get_snowflake_connection()
            sf_cursor = sf_conn.cursor()
            
            # Check source table
            if not validate_table_exists(sf_cursor, pipeline['source_table']):
                validation_results['errors'].append(
                    f"Source table '{pipeline['source_table']}' does not exist in Snowflake"
                )
                validation_results['valid'] = False
            
            # Warning if target table already exists
            if validate_table_exists(sf_cursor, pipeline['target_table']):
                validation_results['warnings'].append(
                    f"Target table '{pipeline['target_table']}' already exists and will be replaced"
                )
        
        except Exception as e:
            validation_results['errors'].append(f"Snowflake validation failed: {str(e)}")
            validation_results['valid'] = False
        
        return validation_results
    
    finally:
        if sf_conn:
            sf_conn.close()

@app.get("/api/pipelines/{pipeline_id}/runs")
def get_pipeline_runs(pipeline_id: int, limit: int = 10, db: sqlite3.Connection = Depends(get_db)):
    """Get execution history for a pipeline with enhanced metrics"""
    cursor = db.cursor()
    cursor.execute("""
        SELECT * FROM pipeline_runs 
        WHERE pipeline_id = ? 
        ORDER BY started_at DESC 
        LIMIT ?
    """, (pipeline_id, limit))
    
    runs = [dict(row) for row in cursor.fetchall()]
    return runs

# ==================== Export Config.json ====================

@app.get("/api/pipelines/export/config")
def export_config_json(db: sqlite3.Connection = Depends(get_db)):
    """Export all pipelines to config.json format"""
    
    pipelines_list = list_pipelines(db=db)
    
    config = {
        "metadata": {
            "version": "2.0.0",
            "created_by": "Data Pipeline API",
            "created_date": datetime.now().strftime("%Y-%m-%d"),
            "last_modified": datetime.now().strftime("%Y-%m-%d"),
            "description": "Data transformation pipeline configuration with enhanced transformations",
            "environment": "production"
        },
        "pipelines": []
    }
    
    for pipeline in pipelines_list:
        pipeline_config = {
            "name": pipeline['name'],
            "domain": pipeline['domain'],
            "source_table": pipeline['source_table'],
            "target_table": pipeline['target_table'],
            "transformations": pipeline['transformations'],
            "status": pipeline['status']
        }
        config['pipelines'].append(pipeline_config)
    
    print(f"✅ Exported {len(pipelines_list)} pipelines to config format")
    
    return config

# ==================== Snowflake Query Endpoints ====================

@app.post("/api/snowflake/query", response_model=QueryResponse)
def execute_snowflake_query(query: str):
    """Execute arbitrary SQL query in Snowflake"""
    conn = None
    try:
        conn = get_snowflake_connection()
        cursor = conn.cursor(DictCursor)
        cursor.execute(query)
        results = cursor.fetchall()
        
        return QueryResponse(
            success=True,
            data=results,
            row_count=len(results)
        )
    except Exception as e:
        return QueryResponse(success=False, error=str(e))
    finally:
        if conn:
            conn.close()

@app.get("/api/snowflake/tables")
def list_snowflake_tables(schema: Optional[str] = None):
    """List all tables in Snowflake"""
    conn = None
    try:
        conn = get_snowflake_connection()
        cursor = conn.cursor(DictCursor)
        
        if schema:
            query = f"SHOW TABLES IN SCHEMA {schema}"
        else:
            query = "SHOW TABLES"
        
        cursor.execute(query)
        tables = cursor.fetchall()
        
        return {"success": True, "tables": tables, "count": len(tables)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()

@app.get("/api/snowflake/table/{table_name}/columns")
def get_table_columns_endpoint(table_name: str):
    """Get columns for a specific table"""
    conn = None
    try:
        conn = get_snowflake_connection()
        cursor = conn.cursor()
        
        from transformation_functions import get_table_columns
        columns = get_table_columns(cursor, table_name)
        
        return {
            "success": True,
            "table_name": table_name,
            "columns": columns,
            "column_count": len(columns)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()

# ==================== Statistics & Monitoring ====================

@app.get("/api/statistics")
def get_statistics(db: sqlite3.Connection = Depends(get_db)):
    """Get overall system statistics"""
    cursor = db.cursor()
    
    # Total pipelines
    cursor.execute("SELECT COUNT(*) FROM pipelines")
    total_pipelines = cursor.fetchone()[0]
    
    # Total runs
    cursor.execute("SELECT COUNT(*) FROM pipeline_runs")
    total_runs = cursor.fetchone()[0]
    
    # Success rate
    cursor.execute("SELECT COUNT(*) FROM pipeline_runs WHERE status = 'completed'")
    successful_runs = cursor.fetchone()[0]
    
    success_rate = (successful_runs / total_runs * 100) if total_runs > 0 else 0
    
    # Average execution time
    cursor.execute("SELECT AVG(execution_time) FROM pipeline_runs WHERE status = 'completed'")
    avg_execution_time = cursor.fetchone()[0] or 0
    
    # Total rows processed
    cursor.execute("SELECT SUM(rows_processed) FROM pipeline_runs WHERE status = 'completed'")
    total_rows_processed = cursor.fetchone()[0] or 0
    
    # Recent failures
    cursor.execute("""
        SELECT p.name, pr.error_message, pr.started_at
        FROM pipeline_runs pr
        JOIN pipelines p ON pr.pipeline_id = p.id
        WHERE pr.status = 'failed'
        ORDER BY pr.started_at DESC
        LIMIT 5
    """)
    recent_failures = [dict(row) for row in cursor.fetchall()]
    
    return {
        "total_pipelines": total_pipelines,
        "total_runs": total_runs,
        "successful_runs": successful_runs,
        "success_rate": round(success_rate, 2),
        "avg_execution_time": round(avg_execution_time, 2),
        "total_rows_processed": total_rows_processed,
        "recent_failures": recent_failures
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)