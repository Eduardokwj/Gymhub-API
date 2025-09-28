from marshmallow import Schema, fields

class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, description="Título do treino (ex.: Treino A)")
    notes = fields.Str(required=False, allow_none=True, description="Notas do treino")

class WorkoutQuerySchema(Schema):
    q = fields.Str(required=False, description="Busca por título (icontains)")
    page = fields.Int(required=False, missing=1, description="Página (>=1)")
    page_size = fields.Int(required=False, missing=10, description="Itens por página (<=100)")
