SUMMARY_TEMPLATE = """Analiza la siguiente conversación y genera un resumen ejecutivo con los puntos clave.

DATOS DEL CANDIDATO:
{user_data}

INFORMACIÓN DEL PUESTO ASIGNADO:
{position_info}

HISTORIAL DE LA CONVERSACIÓN:
{conversation_history}

INSTRUCCIONES:
1. Genera un resumen conciso de la interacción
2. Extrae los puntos clave sobre el candidato
3. Resume las preguntas y respuestas sobre el puesto/empresa
4. Proporciona recomendaciones basadas en el perfil del candidato y el puesto asignado

El resumen debe seguir este formato:

RESUMEN EJECUTIVO:
[Resumen conciso de la interacción]

DATOS DEL CANDIDATO:
- Nombre: [nombre]
- Edad: [edad]
- Horario preferido: [preferencia de horario]

PUESTO ASIGNADO:
- Equipo: [nombre del equipo]
- Puesto: [título del puesto]
- Líder: [nombre del líder]

INTERÉS Y PREGUNTAS:
[Resume las preguntas realizadas por el candidato y su interés mostrado]

OBSERVACIONES:
[Observaciones sobre la interacción, actitud, claridad de comunicación, etc.]

RECOMENDACIONES:
[Recomendaciones específicas basadas en el perfil del candidato y el puesto asignado]""" 