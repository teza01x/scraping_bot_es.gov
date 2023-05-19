# Якщо будете використовувати проксі то ставте True та заповнюйте proxy_address
# False - означає що проксі не використовується
proxy_use = False
proxy_address = ''  # host:port

# перерва (у секундах) між поданням заявок щоб обійти серверне блокування запиту. Краще ставити більше 120 сек
time_break = 120

# перерва (у секундах) через помилку 505 (тобто занадто часті запити)
error_505 = 600

# у графі chrome_path вкажіть шлях до вашого браузера хром, як вказано нижче
# зазвичай ця директорія використовується за замовчуванням
chrome_path = "" # path to your google

site_url = 'https://sedeclave.dgt.gob.es/WEB_NCIT_CONSULTA/solicitarCita.faces'
api_key = '' # api captcha
gkey = '6LeK_-kZAAAAAEqP9TZnX-js2ldWjNxNnvReXsOY'
telegram_token = '' # telegram bot token
photo_name = 'screenshot.png'

# для отримання повідомлень потрібно авторизуватись у своєму боті
# це список id людей яким будуть приходити повідомлення у телеграм, змініть на своє (обовя'язково вказувати в лапках '')
chat_list = []


# офіс у якому записуються на прийом (обовя'язково вказувати в лапках '')
office_city = '#publicacionesForm\:oficina > optgroup:nth-child(4) > option:nth-child(2)'

# процедура (обовя'язково вказувати в лапках '')
proc = '#publicacionesForm\:tipoTramite > option:nth-child(4)'

submit_button = '#publicacionesForm\:j_id70 > input'

# перелік країн у графі País (*), вписуйте кожну країну в лапках та через кому, непотрібні - видаляйте
country_list = ['#publicacionesForm\:pais > option:nth-child(4)', '#publicacionesForm\:pais > option:nth-child(8)']

