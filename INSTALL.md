Hay dos formas de ejecutar el agente, de forma local (recomendada para mejor rendimiento del hardware tanto en el modelo como en los dispositivos de entrada y salida de audio) o a través de Docker.

## Dependecias comunes
Es necesario tener Ollama (https://ollama.com/) instalado y disponible en el host con el modelo mistral instalado.

Para comprobar que ollama está instalado y funcionando:
````
ollama -v
output: ollama version is 0.5.7

ollama serve
````

Para instalar el modelo mistral:
````
ollama pull mistral
````

También es necesario ffmpeg:
````
brew install ffmpeg  # En macOS
sudo apt install ffmpeg  # En Linux

````

## Instalación local

1. Crear el entorno virtual:
```bash
python3.11 -m venv venv
source venv/bin/activate
```

2. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

3. Ejecutar el agente:
```bash
python run.py
```



## Instalación con Docker
Para la construcción de la imágen:
````
make build
````

Para ejecutar el contenedor:
````
make run
```





