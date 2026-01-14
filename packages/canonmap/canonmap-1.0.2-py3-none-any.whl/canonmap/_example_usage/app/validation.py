from typing import Union, Literal, Any
from pydantic import BaseModel, PositiveInt, Field, ConfigDict

class ImportTableBody(BaseModel):
  file_path: str
  table_name: str | None = None
  if_table_exists: Literal["append","replace","fail"] = "append"

class TableFieldObj(BaseModel):
    table_name: str
    field_name: str

TableFieldIn = Union[str, TableFieldObj]

class CreateHelperFieldsBody(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "table_fields": [
                    "table_name.field_name",
                    {"table_name": "table_name", "field_name": "field_name"}
                ],
                "all_transforms": True,
                "transform_type": "initialism",
                "if_helper_exists": "error",
                "chunk_size": 10000,
                "parallel": False
            }
        }
    )
    
    table_fields: list[TableFieldIn] = Field(
        ...,
        description="List of table/field references. Each item can be a string in format 'table.field' or 'table:field', or an object with table_name and field_name."
    )
    all_transforms: bool = True
    transform_type: Literal["initialism","phonetic","soundex"] | None = None
    if_helper_exists: Literal["replace","append","error","skip","fill_empty"] = "error"
    chunk_size: PositiveInt = 10000
    parallel: bool = False

class ExecuteQueryBody(BaseModel):
  query: str
  params: list[Any] | None = None
  allow_writes: bool = False

class TransactionStatement(BaseModel):
  query: str
  params: list[Any] | None = None


class TransactionBody(BaseModel):
  statements: list[TransactionStatement]

class AddPrimaryKeyBody(BaseModel):
  table_name: str
  columns: list[str]
  replace: bool = False

class DropPrimaryKeyBody(BaseModel):
  table_name: str

class AddForeignKeyBody(BaseModel):
  table_name: str
  columns: list[str]
  ref_table: str
  ref_columns: list[str]
  constraint_name: str | None = None
  on_delete: Literal["CASCADE","SET NULL","RESTRICT","NO ACTION"] | None = None
  on_update: Literal["CASCADE","SET NULL","RESTRICT","NO ACTION"] | None = None
  replace: bool = False


class CreateTableBody(BaseModel):
  table_name: str
  fields_ddl: str
  if_not_exists: bool = True
  temporary: bool = False
  table_options: str | None = None

class CreateFieldBody(BaseModel):
  table_name: str
  field_name: str
  field_ddl: str | None = None
  if_field_exists: Literal["error","skip","replace"] = "error"
  first: bool = False
  after: str | None = None
  sample_values: list[Any] | None = None

class CreateAutoIncrementPKBody(BaseModel):
  table_name: str
  field_name: str = "id"
  replace: bool = False
  unsigned: bool = True
  start_with: int | None = None

class DropForeignKeyBody(BaseModel):
  table_name: str
  constraint_name: str
 
class CreateDatabaseBody(BaseModel):
  database_name: str
  if_not_exists: bool = True
  charset: str | None = None
  collate: str | None = None