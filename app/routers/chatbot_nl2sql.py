from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.database import get_db
from app.schemas.chat import ChatRequest
from app.services.nl2sql_engine import get_db_schema, generate_sql, format_answer, fuzzy_correct_query

router = APIRouter(prefix="/chatbot", tags=["Chatbot NL2SQL"])


@router.post("/ask")
def ask_db(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Natural-language-to-SQL endpoint.
    Send any question → AI writes SQL → executes against DB → AI formats answer.
    """
    query = (request.query or "").strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    # 1. Get schema — full for powerful models, compact for Groq fallback
    try:
        schema_full    = get_db_schema(db, compact=False)
        schema_compact = get_db_schema(db, compact=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Schema fetch failed: {e}")

    # 2. Fuzzy-correct any misspelled entity names before SQL generation
    query = fuzzy_correct_query(query, db)

    # 3. Generate SQL
    try:
        sql = generate_sql(query, schema_full, schema_compact)
    except ValueError:
        return {
            "answer": "Yeh question mujhe samajh nahi aaya ya database mein iska data nahi hai. Thoda aur clearly poochho?",
            "sql": None,
            "rows": [],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SQL generation failed: {e}")

    # 4. Execute SQL — if it fails, let the AI fix it once and retry
    try:
        result  = db.execute(text(sql))
        columns = list(result.keys())
        rows    = [list(row) for row in result.fetchall()]
    except Exception as first_error:
        try:
            sql     = generate_sql(query, schema_full, schema_compact,
                                   previous_sql=sql, sql_error=str(first_error))
            result  = db.execute(text(sql))
            columns = list(result.keys())
            rows    = [list(row) for row in result.fetchall()]
        except Exception:
            return {
                "answer": "Yeh query samajh nahi aaya. Thoda aur clearly poochho?",
                "sql": sql,
                "rows": [],
            }

    # 5. Format answer
    try:
        answer = format_answer(query, rows, columns)
    except Exception:
        answer = f"Results ({len(rows)} rows): " + str(rows[:10])

    rows_as_dicts = [dict(zip(columns, row)) for row in rows[:50]]
    return {
        "answer":     answer,
        "sql":        sql,
        "rows":       rows_as_dicts,
        "columns":    columns,
        "total_rows": len(rows),
    }
