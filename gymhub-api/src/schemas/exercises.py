from marshmallow import Schema, fields

class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, description="Nome do exercício")
    muscle_group = fields.Str(required=True, description="Grupo muscular alvo")
    equipment = fields.Str(required=True, description="Equipamento usado (ex.: barra, halteres)")

class ExerciseQuerySchema(Schema):
    q = fields.Str(required=False, description="Busca por nome/grupo/equipamento (icontains)")
    page = fields.Int(required=False, missing=1, description="Página (>=1)")
    page_size = fields.Int(required=False, missing=10, description="Itens por página (<=100)")
