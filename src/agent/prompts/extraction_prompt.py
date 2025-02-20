EXTRACTION_TEMPLATE = """Extrae ÚNICAMENTE la información que esté EXPLÍCITAMENTE mencionada en el mensaje del usuario.

INFORMACIÓN A EXTRAER:
- Nombre de la persona (si se menciona explícitamente)
- Edad (si se menciona explícitamente en números)
- Horario preferido (si se menciona explícitamente "mañana" o "tarde")

REGLAS ESTRICTAS:
- SOLO extrae información que esté EXPLÍCITAMENTE mencionada
- NO infiereas, NO asumas, NO inventes NINGUNA información
- Si un dato no está explícitamente mencionado, déjalo como null
- Si hay ambigüedad, déjalo como null

REGLAS POR CAMPO:
- Nombre:
  * Solo extrae si la persona dice explícitamente su nombre
  * Debe ser mencionado como "me llamo X", "soy X", "mi nombre es X"
  * Si no cumple estos formatos, deja como null

- Edad:
  * Solo extrae si la persona menciona explícitamente su edad
  * Debe ser un número seguido de "años" o similar
  * Si no es mencionado así, deja como null

- Horario:
  * Solo extrae si la persona dice explícitamente "mañana" o "tarde"
  * Debe ser mencionado como preferencia de horario
  * Si hay ambigüedad, deja como null

MENSAJE DEL USUARIO:
{input}

{format_instructions}
""" 