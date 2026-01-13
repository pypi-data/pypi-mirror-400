import os

from entity_generator import Column, DataType, EntityGenerator


class TestEntityGenerator:
    def test_init(self):
        # Arrange
        file_path = "tests/data/sample.sql"

        # Act
        generator = EntityGenerator(
            file_path=file_path,
            output_dir="tests/data/entities",
            db_type="sqlite",
        )

        # Assert
        assert generator
        assert generator.db_type == "sqlite"
        assert generator.output_dir == "tests/data/entities"
        assert generator.asts
        assert generator.asts[0].key == "create"

    def test_get_columns(self):
        # Arrange
        file_path = "tests/data/sample.sql"

        # Act
        generator = EntityGenerator(
            file_path=file_path,
            output_dir="tests/data/entities",
            db_type="sqlite",
        )
        columns = generator._get_columns(generator.asts[0].this)

        # Assert
        assert len(columns) == 4
        assert columns == [
            Column(
                name="id",
                data_type=DataType.STRING,
                length=40,
                nullable=False,
                primary_key=True,
                unique=True,
                default=None,
            ),
            Column(
                name="name",
                data_type=DataType.STRING,
                length=100,
                nullable=False,
                primary_key=False,
                unique=False,
                default=None,
            ),
            Column(
                name="email",
                data_type=DataType.STRING,
                length=None,
                nullable=False,
                primary_key=False,
                unique=True,
                default=None,
            ),
            Column(
                name="created_at",
                data_type=DataType.DATETIME,
                length=None,
                nullable=True,
                primary_key=False,
                unique=False,
                default="CURRENT_TIMESTAMP()",
            ),
        ]

    def test__get_tables(self):
        # Arrange
        file_path = "tests/data/sample.sql"

        # Act
        generator = EntityGenerator(
            file_path=file_path,
            output_dir="tests/data/entities",
            db_type="sqlite",
        )
        tables = generator._get_tables()

        # Assert
        assert len(tables) == 2
        assert tables[0].name == "user"
        assert tables[0].columns == [
            Column(
                name="id",
                data_type=DataType.STRING,
                length=40,
                nullable=False,
                primary_key=True,
                unique=True,
                default=None,
            ),
            Column(
                name="name",
                data_type=DataType.STRING,
                length=100,
                nullable=False,
                primary_key=False,
                unique=False,
                default=None,
            ),
            Column(
                name="email",
                data_type=DataType.STRING,
                length=None,
                nullable=False,
                primary_key=False,
                unique=True,
                default=None,
            ),
            Column(
                name="created_at",
                data_type=DataType.DATETIME,
                length=None,
                nullable=True,
                primary_key=False,
                unique=False,
                default="CURRENT_TIMESTAMP()",
            ),
        ]
        assert tables[1].name == "user_password"
        assert tables[1].columns == [
            Column(
                name="id",
                data_type=DataType.STRING,
                length=40,
                nullable=False,
                primary_key=True,
                unique=True,
                default=None,
            ),
            Column(
                name="user_id",
                data_type=DataType.STRING,
                length=40,
                nullable=False,
                primary_key=False,
                unique=False,
                default=None,
            ),
            Column(
                name="password",
                data_type=DataType.STRING,
                length=None,
                nullable=True,
                primary_key=False,
                unique=False,
                default=None,
            ),
            Column(
                name="created_at",
                data_type=DataType.DATETIME,
                length=None,
                nullable=True,
                primary_key=False,
                unique=False,
                default="CURRENT_TIMESTAMP()",
            ),
        ]

    def test_generate_entity_file(self):
        # Arrange
        file_path = "tests/data/sample.sql"

        # Act
        generator = EntityGenerator(
            file_path=file_path,
            output_dir="tests/data/entities",
            db_type="sqlite",
        )
        tables = generator._get_tables()
        generator._generate_entity_file(tables)

        # Assert
        with os.scandir("tests/data/entities") as entries:
            files = [entry.name for entry in entries if entry.is_file()]
        assert "user_entity.py" in files
        assert "user_password_entity.py" in files
