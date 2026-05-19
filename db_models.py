from sqlalchemy import Column, Integer, MetaData, String, Table


def get_users_table(metadata: MetaData) -> Table:
    """Define the users table."""
    return Table(
        'users',
        metadata,
        Column('id', Integer, primary_key=True, index=True),
        Column('username', String(50), unique=True, nullable=False),
        Column('email', String(255), unique=True, nullable=False),
    )


def get_products_table(metadata: MetaData) -> Table:
    """Define the products table (example for multiple tables)."""
    return Table(
        'products',
        metadata,
        Column('id', Integer, primary_key=True, index=True),
        Column('name', String(100), nullable=False),
        Column('price', Integer, nullable=False),
    )
