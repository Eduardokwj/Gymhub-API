from marshmallow import Schema, fields

class WgerSearchSchema(Schema):
    language = fields.Int(required=False, description="ID do idioma (2 = EN, 10 = PT)")
    muscles = fields.Int(required=False, description="ID do músculo")
    equipment = fields.Int(required=False, description="ID do equipamento")
    status = fields.Int(required=False, description="1 = draft, 2 = approved")
    contains = fields.String(required=False, description="Filtra por nome (contém)")
    category = fields.Int(requider=False, description="Categoria (ex.: 10=chest)")
    ordering = fields.String(required=False, description="Ordenação (ex.: name)")
    limit = fields.Int(required=False, description="Quantidade por página (padrão 20)")
    offset = fields.Int(required=False, description="Paginador (começa em 0)")
    raw = fields.String(required=False, description="Debug: use 1 ou true")
