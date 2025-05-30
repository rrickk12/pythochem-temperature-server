# Usa uma imagem leve do Python
FROM python:3.11-slim

# Define diretório de trabalho
WORKDIR /app

# Copia o projeto todo para dentro do container
COPY . /app

# Instala dependências
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta padrão do Flask (ajuste se usar outra)
EXPOSE 8080

# Define variável de ambiente para Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_PORT=8080
ENV FLASK_ENV=production

# Comando para rodar o Flask via gunicorn (recomendado para produção)
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
