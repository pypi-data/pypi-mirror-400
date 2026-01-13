# SQLFactory

![Pipeline](https://gitlab.com/gcm-cz/sqlfactory/badges/main/pipeline.svg)
![Coverage](https://gitlab.com/gcm-cz/sqlfactory/badges/main/coverage.svg)
![Latest release](https://gitlab.com/gcm-cz/sqlfactory/-/badges/release.svg)

A zero-dependency SQL builder library!

Convenient classes for building SQL queries in Python. Main purpose of this library is to ease construction of SQL
queries in Python code. It is not an ORM (and don't intend to be), just a plain SQL query builder with syntax as
similar to actual SQL as possible.

## Documentation

API documentation with more examples is available at [GitLab Pages](https://gcm-cz.gitlab.io/sqlfactory/).

## Features

- `SELECT` statements
  - Variable select columns
  - Multiple tables
  - Subselects
  - Joins
  - Where condition
  - Group by
  - Having
  - Ordering
  - Limit
  - Common Table Expressions (CTE)
- `INSERT` statements
  - Multiple rows at once
  - Replace
  - On duplicate key update (MySQL / MariaDB specific)
  - `INSERT ... SELECT`
- `UPDATE` statements
  - Variable set of columns to change
  - Where condition
  - Limit
- `DELETE` statements
  - Join
  - Subselects
  - Where condition
  - Order
  - Limit
- `UNION` [`ALL`], `EXCEPT` [`ALL`], `INTERSECT` [`ALL`]
- Multiple SQL dialects support - MySQL / MariaDB, SQLite, PostgreSQL, custom.
  - Can support numeric placeholders (`$1`, `$2`, ...) in custom implementation.

## Basic concepts

- Each component of SQL statement is represented by its own class.
- Each (part of) SQL statement can be used individually or combined with other parts to create more complex SQL statements.
- Each part of statement bundles string representation of given portion of SQL including placeholders with placeholder values.
  These parts are then combined to construct more complex SQL statements up to the executable ones (SELECT, INSERT, UPDATE,
  DELETE, ...).
- When there is no expected return value, `self` is always returned to allow chaining of methods. Chaining of method does not have
  given order, methods can be chained as needed. For example, WHERE does not have to be before LIMIT for SELECT. It is up to the
  library to figure out correct order of parts when building final query.
- `statement.__str__()` method (`str(statement)`) is used to get the final SQL statement.
- `statement.args` property is used to get the values of placeholders.
- `statement.execute()` function is used to execute the statement that could be executed on top of DB-API 2.0 compatible cursor
  (or any object that has execute() method taking string as SQL and variable arguments or tuple of arguments as placeholder values).
- It does not matter whether you are in async or sync code, or what database you are using. SQLFactory is database-agnostic and
    does not care about the underlying database. It only cares about building the SQL statement.
- SQLFactory is not an ORM. It does not map objects to tables or rows. By design.
- SQLFactory utilizes modern Python syntax and type hints, requiring Python 3.11+. It is fully type-safe and works well with
  IDE code completion.
- Developer who knows SQL should understand query written using SQLFactory without explicitly knowing SQLFactory API. Library
  tries to mimic SQL syntax as much as possible.

## Usage

Let's have look at few examples, because examples tell much more than a thousand words:

TL;DR:
```python
sql = Select("column1", "column2", table="books").where(Eq("column1", "value") & In("column2", [1, 2, 3]))

# Will do the args magic for you
sql.execute(cursor)

# OR
cursor.execute(
    str(sql),  # Produces SQL string with value placeholders as %s 
    sql.args   # Returns arguments for the placeholders
)
```

All the following examples are self-contained. You can copy-paste them into your Python code and they will work.

---

Let's see how to build a SELECT statement like this:

```sql
SELECT column1, column2, column3 FROM books WHERE column1 = 'value' AND column2 IN (1, 2, 3);
```

All the following examples are equivalent and produce the same SQL query:

```python
from sqlfactory import SELECT, Table, Select, And, Eq, In

# The most naive and most explicit approach
Select("column1", "column2", "column3", table="books", where=And(Eq("column1", "value"), In("column2", [1, 2, 3])))

# A little more like a SQL:
SELECT("column1", "column2", "column3", table="books")
    .WHERE(Eq("column1", "value") & In("column2", [1, 2, 3]))

# A little more like a python, but still SQL:
books = Table("books")
SELECT(books.column1, books.column2, books.column3, table=books)
    .WHERE((books.column1 == "value") & In(books.column2, [1, 2, 3]))
```

---

Inserts are simple, too:

```sql
INSERT INTO books (column1, column2, column3) VALUES ('value1', 'value2', 'value3'), ('value4', 'value5', 'value6');
```

```python
from sqlfactory import Insert, INSERT, Table

Insert.into("books")("column1", "column2", "column3").VALUES(
    ("value1", "value2", "value3"),
    ("value4", "value5", "value6")
)

# Of course, you can use Table object as well
books = Table("books")
INSERT.INTO(books)(books.column1, books.column2, books.column3).VALUES(
    ("value1", "value2", "value3"),
    ("value4", "value5", "value6")
)

# The INTO is not necessary, you can call INSERT constructor directly:
INSERT("books")("column1", "column2", "column3").VALUES(
    ("value1", "value2", "value3"),
    ("value4", "value5", "value6")
)
```

---

Even updates (and in fact deletes, too):

```sql
UPDATE books SET column1 = 'value1', column2 = 'value2' WHERE column3 = 'value3';
```

```python
from sqlfactory import Update, Table, Eq

Update("books")
    .set("column1", "value1")
    .set("column2", "value2")
    .where(Eq("column3", "value3"))

# Of course, you can use Table object as well
books = Table("books")
Update(books)
    .set(books.column1, "value1")
    .set(books.column2, "value2")
    .where(books.column3 == "value3")
```

It might seem strange to have so many ways to do the same thing, but it's up to you to choose the one that fits your
style the best. The library is designed to be as flexible as possible. You can mix and match different styles in the same
codebase, or even in the same query, if you want, as long as it makes sense to you.

By leveraging Python code in constructing SQL, you can use all sorts of Python features to make building SQL an ease.
Consider list comprehensions for IN statement, building of complex WHERE clauses, dynamic select columns, call UPDATE
only if anything has changed, ... All of that and much more can be done without the hassle of building complex strings
together.

Let's have a look at a few more practical examples:

```python
from sqlfactory import Select, In, Direction, Eq, Column, SelectColumn
from dataclasses import dataclass


@dataclass
class Book:
    id: int
    title: str
    author: str
    year: str


def select_books_by_authors(c: DictCursor, authors: list[str], book_properties: set[str] = None, offset: int = 0,
                            limit: int = 10):
    """
    Returns books written by specific authors. Returns list of books paginated by specified offset and limit, ordered
    by book title and author name.
    """

    if book_properties is None:
        book_properties = {"title", "author", "year"}

    property_column = {
        "title": SelectColumn("books.title", alias="title"),
        "author": SelectColumn("authors.name", alias="author"),
        "year": SelectColumn("books.year", alias="year")
    }

    select = (
        # Map dataclass attributes to SQL columns by using mapping table.
        Select(*[property_column[book_property] for book_property in book_properties], table="books")

        # As Eq expects firt argument to be column and second argument to be value, we need to provide hint, that
        # authors.id is a column, not a value.
        .join("authors", on=Eq("books.author", Column("authors.id")))

        # In is intelligent, it will work even when authors list is empty (will produce False, which in turn will
        # return empty result, as no author has been matched).
        .where(In("authors.name", authors))

        # Multiple ORDER BY columns is supported
        .order_by("title", Direction.ASC)
        .order_by("authors.name", Direction.ASC)

        # Limit and offset are supported as well
        .limit(offset, limit)
    )

    select.execute(c)
    return [Book(**row) for row in c.fetchall()]
```

```python
from sqlfactory import Update, Eq
from dataclasses import dataclass


@dataclass
class BookUpdate:
    id: int
    title: str = None
    author: str = None
    year: int = None


def update_books(c: Cursor, books: list[BookUpdate]):
    """Update multiple books at once. Attributes that has None value won't be modified at all."""
    for book in books:
        update = Update("books", where=Eq("id", book.id))

        if book.title is not None:
            update.set("title", book.title)
        if book.author is not None:
            update.set("author", book.author)
        if book.year is not None:
            update.set("year", book.year)

        # It can even be done as one-liner, but it gets ugly pretty quickly, so it's not recommended for readability:
        # list(map(update.set, [(attr, getattr(book, attr)) for attr in ["title", "author", "year"] if getattr(book, attr) is not None]))

        # Will be executed only if any of the columns should be updated.
        update.execute(c)
```

## SQL Dialect

SQLFactory supports multiple SQL dialects. By default, it uses MySQL / MariaDB dialect, but it can be changed to SQLite,
PostgreSQL, Oracle or custom dialect. Custom dialect can be used to support any database that supports standard SQL, but uses
different placeholders than `%s` (like `$1`, `$2`, ...).

```python
from sqlfactory import PostgreSQLDialect, Statement, Select, Eq, In

# Change the default dialect to PostgreSQL
Statement.default_dialect = PostgreSQLDialect()

# Now, all statements will use PostgreSQL dialect
select = Select("column1", "column2", table="books").where(Eq("column1", "value") & In("column2", [1, 2, 3]))
str(select)  # SELECT "column1", "column2" FROM "books" WHERE "column1" = %s AND "column2" IN (%s, %s, %s)
```

Dialects where placeholders must be numbered are also supported as can be seen in the example `OracleSQLDialect`:

```python
from sqlfactory import OracleSQLDialect, Statement, Select, Eq, In

# Change the default dialect to PostgreSQL
Statement.default_dialect = OracleSQLDialect()

# Now, all statements will use PostgreSQL dialect
select = Select("column1", "column2", table="books").where(Eq("column1", "value") & In("column2", [1, 2, 3]))
str(select)  # SELECT "column1", "column2" FROM "books" WHERE "column1" = :1 AND "column2" IN (:2, :3, :4)
```

However, the library is mainly tested with MySQL / MariaDB dialect, so there might be some issues with other dialects, such
as slightly different syntax or unsupported features. If you find any issue, please report it.

## Installation

Just install it from PyPi and use:

```shell
pip install sqlfactory
```

## Maturity

This library is still very new, but grew from multiple projects where it gradually evolved. So it is already used in
production environment successfully. But as always, bugs are expected to be found. On the other hand, the library
contains large test suite with 100% code coverage, so it should be quite stable. If you find any bug, please report it.

Implemented SQL features are not complete set of what SQL offers, they are added as-needed. Feel free to open a merge
request if you find missing feature that you need.

As we are mainly targeting MySQL / MariaDB, there are some extra features that are on top of SQL standard, that are
implemented in the builder. But the library should work with any database that supports standard SQL, when you won't
use features that are extensions to the SQL standard.

## Contributing

Contributions are always welcome. Just open an issue or a merge request. Keep in mind, that this is not an ORM. So no
sessions, no transactions, no lazy loading, no relations, no schema management, no migrations, no database creation.
