import psycopg2

from app.config import settings


def fetch_ventas_data():
    """Obtiene los datos de ventas reales desde PostgreSQL usando psycopg2.

    Los parámetros de conexión provienen de la configuración del proyecto
    (variables POSTGRES_* de .env).
    Los errores de PostgreSQL se propagan al llamador, no se ocultan.
    """
    conn = psycopg2.connect(
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        dbname=settings.POSTGRES_DB,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        client_encoding="utf8",
    )
    try:
        cur = conn.cursor()
        try:
            cur.execute("SELECT producto, categoria, region, ventas FROM ventas ORDER BY id;")
            rows = cur.fetchall()
        finally:
            cur.close()

        data = [
            {
                "producto": row[0],
                "categoria": row[1],
                "region": row[2],
                "ventas": row[3],
            }
            for row in rows
        ]
        return data
    finally:
        conn.close()
