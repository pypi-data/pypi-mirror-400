# django-firebird

Firebird database backend for Django.

This package provides a Django database backend for [Firebird](https://firebirdsql.org/),
supporting versions 2.5, 3.0, 4.0, and 5.0+. It uses the
[firebird-driver](https://pypi.org/project/firebird-driver/) library for connectivity.

## Features

| Feature | Firebird 2.5 | Firebird 3.0+ | Firebird 4.0+ | Firebird 5.0+ |
|---------|:------------:|:-------------:|:-------------:|:-------------:|
| Basic ORM operations | Yes | Yes | Yes | Yes |
| Migrations | Yes | Yes | Yes | Yes |
| `inspectdb` command | Yes | Yes | Yes | Yes |
| Native BOOLEAN | No | Yes | Yes | Yes |
| Window functions | No | Yes | Yes | Yes |
| FILTER clause | No | Yes | Yes | Yes |
| Timezone support | No | No | Yes | Yes |
| SKIP LOCKED | No | No | No | Yes |

## Requirements

- Python 3.11+
- Django 5.0, 5.1, or 6.0
- firebird-driver 1.10.0+
- Firebird Server 2.5+

## Installation

```bash
pip install django-firebird
```

## Configuration

Configure your Django `DATABASES` setting:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django_firebird',
        'NAME': '/path/to/database.fdb',
        'USER': 'SYSDBA',
        'PASSWORD': 'masterkey',
    }
}
```

### Remote Database

For remote connections, specify `HOST` and optionally `PORT`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django_firebird',
        'NAME': '/path/to/database.fdb',
        'USER': 'SYSDBA',
        'PASSWORD': 'masterkey',
        'HOST': 'localhost',
        'PORT': '3050',
    }
}
```

### Connection Options

| Option | Description | Default |
|--------|-------------|---------|
| `charset` | Character set for connection | `UTF8` |
| `fb_client_library` | Path to Firebird client library | System default |

```python
DATABASES = {
    'default': {
        'ENGINE': 'django_firebird',
        'NAME': '/path/to/database.fdb',
        'USER': 'SYSDBA',
        'PASSWORD': 'masterkey',
        'OPTIONS': {
            'charset': 'UTF8',
            'fb_client_library': '/usr/lib/libfbclient.so',
        },
    }
}
```

### Timezone Support (Firebird 4.0+)

```python
DATABASES = {
    'default': {
        'ENGINE': 'django_firebird',
        'NAME': '/path/to/database.fdb',
        'USER': 'SYSDBA',
        'PASSWORD': 'masterkey',
        'TIME_ZONE': 'America/New_York',
    }
}
```

## Notes on Django Fields

- **AutoField/BigAutoField**: Uses Firebird generators (sequences) with triggers
- **BooleanField**: Uses native `BOOLEAN` in Firebird 3.0+, `SMALLINT` in 2.5
- **TextField**: Uses `BLOB SUB_TYPE TEXT`
- **JSONField**: Not supported (Firebird has no native JSON type)
- **UUIDField**: Uses `CHAR(36)` storage

## Known Limitations

- **No JSON support**: Firebird does not have a native JSON data type
- **No DISTINCT ON**: Use other approaches for similar functionality
- **Single-row RETURNING**: Bulk inserts with RETURNING not supported
- **DDL auto-commit**: Schema changes cannot be rolled back within a transaction
- **Identifier length**: 31 characters max in Firebird < 4.0, 63 in 4.0+

## Using `inspectdb`

To inspect an existing Firebird database:

```bash
python manage.py inspectdb
```

For better results with foreign key ordering, use the enhanced command:

```bash
python manage.py inspectdb_firebird
```

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

This project is licensed under the BSD-3-Clause License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by [django-cockroachdb](https://github.com/cockroachdb/django-cockroachdb) and [mssql-django](https://github.com/microsoft/mssql-django)
- Built on [firebird-driver](https://github.com/FirebirdSQL/python3-driver)
