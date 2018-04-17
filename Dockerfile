FROM certbot/certbot

COPY . src/certbot-dns-schlundtech

RUN pip install --no-cache-dir --editable src/certbot-dns-schlundtech
