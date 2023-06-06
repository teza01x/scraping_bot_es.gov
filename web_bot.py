import time
import warnings
import traceback
import telebot
import requests
from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from config import *


class Click_Obj():
    def __init__(self, wait):
        self.wait = wait

    def office(self, office_city):
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, office_city))).click()

    def proc(self, proc):
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, proc))).click()

    def city(self, city):
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, city))).click()

    def submit(self, submit_button):
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, submit_button))).click()


def captcha_post(googlekey):
    url = f'http://2captcha.com/in.php?key={api_key}&method=userrecaptcha&googlekey={googlekey}&pageurl={site_url}'
    return requests.get(url)


def captcha_get(id):
    url = f'http://2captcha.com/res.php?key={api_key}&action=get&id={id}'
    return requests.get(url)


def captcha_api():
    resp_post = captcha_post(gkey)
    if resp_post.text[:2] == "OK":
        time.sleep(15)
        response = captcha_get(resp_post.text[3:])
        while True:
            if response.text != "CAPCHA_NOT_READY":
                break
            time.sleep(5)
            response = captcha_get(resp_post.text[3:])
        captcha_key = response.text[3:]
        return captcha_key


def call_back_detect(browser):
    js_code = """
    function findRecaptchaClients() {
      if (typeof (___grecaptcha_cfg) !== 'undefined') {
        return Object.entries(___grecaptcha_cfg.clients).map(([cid, client]) => {
          const data = { id: cid, version: cid >= 10000 ? 'V3' : 'V2' };
          const objects = Object.entries(client).filter(([_, value]) => value && typeof value === 'object');

          objects.forEach(([toplevelKey, toplevel]) => {
            const found = Object.entries(toplevel).find(([_, value]) => (
              value && typeof value === 'object' && 'sitekey' in value && 'size' in value
            ));

            if (typeof toplevel === 'object' && toplevel instanceof HTMLElement && toplevel['tagName'] === 'DIV'){
                data.pageurl = toplevel.baseURI;
            }

            if (found) {
              const [sublevelKey, sublevel] = found;

              data.sitekey = sublevel.sitekey;
              const callbackKey = data.version === 'V2' ? 'callback' : 'promise-callback';
              const callback = sublevel[callbackKey];
              if (!callback) {
                data.callback = null;
                data.function = null;
              } else {
                data.function = callback;
                const keys = [cid, toplevelKey, sublevelKey, callbackKey].map((key) => `['${key}']`).join('');
                data.callback = `___grecaptcha_cfg.clients${keys}`;
              }
            }
          });
          return data;
        });
      }
      return [];
    }

    return findRecaptchaClients();
    """

    result = browser.execute_script(js_code)
    return result[0]['callback']


def injection(browser, captcha_key, call_back_value):
    captcha_v2 = """
    var element = document.getElementById('publicacionesForm:responseV2');
    element.value = '{capcha_key}';
    """
    grecaptchav2_script = f"{call_back_value}('{captcha_key}')"
    browser.execute_script(captcha_v2.format(capcha_key=captcha_key))
    time.sleep(3)
    browser.execute_script(grecaptchav2_script)


def error_check(browser, office, pais):
    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')

    try:
        error = soup.find('div', class_='buscadorInterno').find('li', class_='msgError').get_text().strip()
        if error:
            print("Офіс: {}\nКраїна: {}\nАктивних процедур не знайдено.".format(office, pais))
            return error
    except:
        try:
            header = soup.find('div', class_='central')
            if header:
                browser.save_screenshot("screenshot.png")
                print("АКТИВНУ ПРОЦЕДУРУ ЗНАЙДЕНО!\nОфіс: {}\nКраїна: {}".format(office, pais))
                print("<Скріншот screenshot.png зроблено>")
                return ''
        except:
            return 'error'


def telegram_bot(browser, error_text, office, pais):
    bot = telebot.TeleBot(telegram_token)
    if len(error_text) > 0:
        pass
    else:
        for chat_id in chat_list:
            bot.send_message(chat_id, "✅ ЗНАЙДЕНО АКТИВНУ ПРОЦЕДУРУ ✅\nОфіс: {}\nКраїна: {}".format(office, pais))
            with open(f'{photo_name}', 'rb') as photo:
                response = requests.post(
                    f'https://api.telegram.org/bot{telegram_token}/sendPhoto',
                    files={'photo': photo},
                    data={'chat_id': chat_id}
                )
        time.sleep(5)
        browser.get(site_url)


def main(wait, browser, city):
    click = Click_Obj(wait)
    click.office(office_city)
    time.sleep(0.5)
    click.proc(proc)
    time.sleep(0.5)
    click.city(city)
    print("<Форму офісної процедури заповнено>")

    pais = browser.find_element(By.CSS_SELECTOR, city).text
    office = browser.find_element(By.CSS_SELECTOR, office_city).text

    time.sleep(1)
    print("<Робота з стороннім API для вирішення reCAPTCHA>")
    captcha_key = captcha_api()

    time.sleep(1)
    call_back_value = call_back_detect(browser)

    time.sleep(1)
    injection(browser, captcha_key, call_back_value)
    print("<Завдання reCAPTCHA вирішено>")

    time.sleep(2)
    click.submit(submit_button)
    print("<Отримуємо відповідь...>")

    time.sleep(5)
    error_text = error_check(browser, office, pais)

    telegram_bot(browser, error_text, office, pais)

    print("Перерва між заповненням форм {} сек.".format(time_break))
    time.sleep(time_break)


if __name__ == "__main__":
    try:
        options = Options()
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        service = Service("chromedriver.exe")
        options.binary_location = chrome_path

        if proxy_use == True:
            proxy = proxy_address
            options.add_argument('--proxy-server=http://%s' % proxy)

        browser = Chrome("chromedriver.exe", service=service, chrome_options=options)
        wait = WebDriverWait(browser, 20)
        browser.maximize_window()

        while True:
            try:
                browser.get(site_url)
                print("<Підключаємось до сайту>")

                if proxy_use == True:
                    input("Введіть пароль та логін від проксі та натисніть 'Enter':")

                time.sleep(10)
                while True:
                    for country in country_list:
                        main(wait, browser, country)

            except Exception as e:
                print("<Помилка 500. Перерва на {} секунд.>".format(error_505))
                time.sleep(error_505)

    except Exception as e:
        traceback_str = traceback.format_exc()
        with open('error_log.txt', 'w') as file:
            file.write(traceback_str)
        print("код: ERROR.\n При роботі програми сталася помилка.\nБудь-ласка, зверніться до програміста за допомогою.")
