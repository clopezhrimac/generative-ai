from vertexai.generative_models import FunctionDeclaration
import google.auth
import google.auth.transport.requests
import requests

def set_light_values(brightness, color_temp):
    """Set the brightness and color temperature of a room light. (mock API).

    Args:
        brightness: Light level from 0 to 100. Zero is off and 100 is full brightness
        color_temp: Color temperature of the light fixture, which can be `daylight`, `cool` or `warm`.

    Returns:
        A dictionary containing the set brightness and color temperature.
    """
    return {
        "brightness": brightness,
        "colorTemperature": color_temp
    }

function_declaration = FunctionDeclaration(
    name="set_light_values",
    description="Set the brightness and color temperature of a room light.",
    parameters={
        "type": "object",
        "properties": {
            "brightness": {
                "type": "number",
                "description": "Light level from 0 to 100. Zero is off and 100 is full brightness.",
            },
            "color_temp": {
                "type": "string",
                "description": "Color temperature of the light fixture, which can be `daylight`, `cool` or `warm`.",
            },
        },
        "required": [
            "brightness",
            "color_temp",
        ],
    },
)

def permanence_model(prompt):
    # Simulación de llamada al modelo de permanencia
    if "permanencia" in prompt.lower():
        return "permanencia: 6, prima_estimada: 1520, calificacion: 4"
    else:
        return "No se encontró información para la pregunta."

permanence_func = FunctionDeclaration(
    name="permanence_model",
    description="Obtener información sobre permanencia, prima estimada y calificación.",
    parameters={
        "type": "object",
        "properties": {
            "prompt": {
                "type": "string",
                "description": "Pregunta del usuario para obtener información.",
            }
        },
        "required": [
            "prompt",
        ],
    },
)

def get_access_token():
    # Carga las credenciales usando la variable de entorno GOOGLE_APPLICATION_CREDENTIALS
    credentials, project = google.auth.default()
    credentials.refresh(google.auth.transport.requests.Request())
    return credentials.token

def call_cloud_run_api(cuc):
    url = "https://api-tecnica-digital-analytics-impl-v1-uwr3p4egga-uk.a.run.app/utilitarios/nse"
    bearer_token = "eyJhbGciOiJSUzI1NiIsImtpZCI6Ijg3YmJlMDgxNWIwNjRlNmQ0NDljYWM5OTlmMGU1MGU3MmEzZTQzNzQiLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiIzMjU1NTk0MDU1OS5hcHBzLmdvb2dsZXVzZXJjb250ZW50LmNvbSIsImF6cCI6InNhLWFpZmFjdG9yeS1waXBlbGluZXNAcnMtbnByZC1kbGstaWEtZGV2LWFpZi1kM2Q5LmlhbS5nc2VydmljZWFjY291bnQuY29tIiwiZW1haWwiOiJzYS1haWZhY3RvcnktcGlwZWxpbmVzQHJzLW5wcmQtZGxrLWlhLWRldi1haWYtZDNkOS5pYW0uZ3NlcnZpY2VhY2NvdW50LmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJleHAiOjE3MjA1NDg4OTUsImlhdCI6MTcyMDU0NTI5NSwiaXNzIjoiaHR0cHM6Ly9hY2NvdW50cy5nb29nbGUuY29tIiwic3ViIjoiMTE3OTIxNDIyMDM5MjcxOTc2Njg5In0.dSKXz50lKCOhsUzG_JMkReLJSATvuhht6mhKL35IBdOswOjIV0SOkQCTbQ-vBtJF3aJBVnejqh7SSk9SsXZtgV3tnquSEbR2sFLfQdkZ4cq5hXvb7-_RM573ByrZKQmaqoslfvlChC0OtlzxNAIwN1sJ8vjJ1NnxPXZKzA-pr4jHsb5kOjhwubSe_2IgARPFuq_M0L_4Gdr-HsVrvjeAMuigHDAjZIEoNL2D77dQeY4XbNUSRqCOv12IUAawTPe7yC5hUNJCxuwJAwkUJJnmm0p8gbQJfuMF7-ISw7_4YMxE0D4Bm9PxC7BHg_qwhOYXOf4cQfjKXw43Vc8hLfVSXg"
    # bearer_token = get_access_token()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {bearer_token}"
        }
    
    payload = {
        "trace": {
            "traceId": "6b10480f-af20-4676-a8e0-1df84dd7cdb6",
            "consumerId": "RIMAC_Leads",
            "serviceId": "TEST",
            "moduleId": "ID_RIMAC",
            "channelCode": "WEB"
        },
        "payload": {
            "cuc": cuc
        }
    }
    response = requests.post(url, json=payload, headers=headers)
    print(f'API Response: {response}')
    return response.json()

query_api_func = FunctionDeclaration(
    name="call_cloud_run_api",
    description="Obtener informacion de nse usando identificador cuc.",
    parameters={
        "type": "object",
        "properties": {
            "cuc": {
                "type": "string", 
                "description": "El id unico de usuario."
            }
        },
        "required": [
            "cuc",
        ],
    }
)