from sqlalchemy import create_engine, text


def main():
    # future means using 2.0 style
    engine = create_engine("sqlite+pysqlite:///:memory:", echo=True, future=True)
    with engine.connect() as conn:
        result = conn.execute(text("select 'hello world'"))
        print(result.all())

    with engine.connect() as conn:
        conn.execute(text("CREATE TABLE some_table (x int, y int)"))
        conn.execute(text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
                     [{"x": 1, "y": 1},
                      {"x": 2, "y": 4}])
        conn.commit()


if __name__ == '__main__':
    main()