## SchlundTech XML Gateway DNS Authenticator plugin for Certbot

The `certbot_dns_schlundtech.dns_schlundtech` plugin automates the process of
completing a ``dns-01`` challenge (`acme.challenges.DNS01`) by creating, and
subsequently removing, TXT records using the SchlundTech XML Gateway API.

### Named Arguments
| | |
| ---: | --- |
| `auth-credentials` | SchlundTech credentials_ INI file. (Required) |
| `auth-propagation-seconds` | The number of seconds to wait for DNS to propagate before asking the ACME server to verify the DNS record. (Default: 60) |

### Credentials
Use of this plugin requires a configuration file containing SchlundTech XML
Gateway API credentials:
* `user`
* `password`
* `context`

```ini
# credentials.ini
certbot_dns_schlundtech:auth_user = 54321
certbot_dns_schlundtech:auth_password = PASSWORD
certbot_dns_schlundtech:auth_context = 10
```

The path to this file can be provided interactively or using the
`--certbot-dns-schlundtech:auth-credentials` command-line argument. Certbot
records the path to this file for use during renewal, but does not store the
file's contents.

**Caution**  
You should protect these credentials. Users who can read this file can use
these credentials to issue some types of API calls on your behalf, limited
by the permissions assigned to the account. Users who can cause Certbot to
run using these credentials can complete a ``dns-01`` challenge to acquire
new certificates or revoke existing certificates for domains these
credentials are authorized to manage.

### Examples
##### To acquire a certificate for `example.com`:
```bash
certbot certonly \
    --server https://acme-v02.api.letsencrypt.org/directory \
    -a certbot-dns-schlundtech:auth \
    --certbot-dns-schlundtech:auth-credentials ~/.secrets/certbot/schlundtech.ini \
    -d example.com
```
##### To acquire a single certificate for both `example.com` and `www.example.com`:
```bash
certbot certonly \
    --server https://acme-v02.api.letsencrypt.org/directory \
    -a certbot-dns-schlundtech:auth \
    --certbot-dns-schlundtech:auth-credentials ~/.secrets/certbot/schlundtech.ini \
    -d example.com \
    -d www.example.com
```
##### To acquire a certificate for `example.com`, waiting 60 seconds for DNS propagation:
```bash
certbot certonly \
    --server https://acme-v02.api.letsencrypt.org/directory \
    -a certbot-dns-schlundtech:auth \
    --certbot-dns-schlundtech:auth-credentials ~/.secrets/certbot/schlundtech.ini \
    --certbot-dns-schlundtech:auth-propagation-seconds 60 \
    -d example.com
```

##### Using docker
Using the provided [Dockerfile](Dockerfile) you can create a docker container based on the original `certbot/certbot`
image plus this plugin.
```bash

```
  
The resulting container image can be run with the options provided above.
```bash
docker run -it --rm \
    -v /etc/letsencrypt:/etc/letsencrypt \
    -v /var/lib/letsencrypt:/var/lib/letsencrypt \
    -v /var/log/letsencrypt:/var/log/letsencrypt \
    -v /tmp:/tmp \
    certbot/dns-schlundtech \
        certonly \
        --server https://acme-v02.api.letsencrypt.org/directory \
        -a certbot-dns-schlundtech:auth \
        --certbot-dns-schlundtech:auth-credentials /etc/letsencrypt/schlundtech.ini \
        -d example.com
```
