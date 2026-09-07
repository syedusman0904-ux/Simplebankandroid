import json, os, secrets, hashlib
from decimal import Decimal
from kivy.app import App

APP_DIR = App.get_running_app().user_data_dir if App.get_running_app() else "."
DATA_FILE = os.path.join(APP_DIR, "bank_data.json")

def money(v): return Decimal(str(v)).quantize(Decimal("0.01"))
def mtext(v): return f"{money(v):.2f}"

def hash_password(password, salt=None):
    salt = salt or secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120000).hex()
    return salt, h

def verify_password(password, salt, expected):
    _, actual = hash_password(password, salt)
    return secrets.compare_digest(actual, expected)

class Bank:
    def __init__(self): self.data = self.load()

    def load(self):
        os.makedirs(APP_DIR, exist_ok=True)
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f: return json.load(f)
            except Exception: pass
        salt, ph = hash_password("syedu2")
        data = {"staff":{"account_number":"su2608","balance":"0.00","password_salt":salt,"password_hash":ph},
                "users":{}, "transactions":[]}
        self.save(data); return data

    def save(self, data=None):
        if data is not None: self.data = data
        tmp = DATA_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f: json.dump(self.data, f, indent=2)
        os.replace(tmp, DATA_FILE)

    def tx(self, typ, amount, sender=None, receiver=None, note=""):
        self.data["transactions"].append({"type":typ,"amount":mtext(amount),"from":sender,"to":receiver,"note":note})

    def create_user(self, name, password):
        if not name.strip(): raise ValueError("Name is required.")
        if len(password) < 4: raise ValueError("Password must be at least 4 characters.")
        while True:
            acc = "US" + secrets.token_hex(4).upper()
            if acc not in self.data["users"]: break
        salt, ph = hash_password(password)
        self.data["users"][acc] = {"account_number":acc,"name":name.strip(),"balance":"0.00",
            "password_salt":salt,"password_hash":ph,"loan":{"principal":"0.00","outstanding":"0.00"}}
        self.save(); return acc

    def user_login(self, acc, password):
        u = self.data["users"].get(acc.upper())
        return acc.upper() if u and verify_password(password,u["password_salt"],u["password_hash"]) else None

    def staff_login(self, acc, password):
        s=self.data["staff"]
        return acc=="su2608" and verify_password(password,s["password_salt"],s["password_hash"])

    def user_transfer(self, sender, receiver, amount):
        amount=money(amount); receiver=receiver.upper()
        a=self.data["users"].get(sender); b=self.data["users"].get(receiver)
        if not b: raise ValueError("Receiver account not found.")
        if sender==receiver: raise ValueError("Cannot transfer to your own account.")
        if money(a["balance"])<amount: raise ValueError("Insufficient balance.")
        a["balance"]=mtext(money(a["balance"])-amount); b["balance"]=mtext(money(b["balance"])+amount)
        self.tx("TRANSFER",amount,sender,receiver,"User transfer"); self.save()

    def staff_deposit(self, acc, amount):
        amount=money(amount); u=self.data["users"].get(acc.upper())
        if not u: raise ValueError("User account not found.")
        if money(self.data["staff"]["balance"])<amount: raise ValueError("Staff reserve has insufficient money.")
        self.data["staff"]["balance"]=mtext(money(self.data["staff"]["balance"])-amount)
        u["balance"]=mtext(money(u["balance"])+amount); self.tx("STAFF_DEPOSIT",amount,"su2608",acc.upper(),"Staff deposit"); self.save()

    def staff_withdraw(self, acc, amount):
        amount=money(amount); u=self.data["users"].get(acc.upper())
        if not u: raise ValueError("User account not found.")
        if money(u["balance"])<amount: raise ValueError("User has insufficient balance.")
        u["balance"]=mtext(money(u["balance"])-amount)
        self.data["staff"]["balance"]=mtext(money(self.data["staff"]["balance"])+amount)
        self.tx("STAFF_WITHDRAW",amount,acc.upper(),"su2608","Staff withdrawal"); self.save()

    def loan(self, acc, amount):
        amount=money(amount); u=self.data["users"].get(acc.upper())
        if not u: raise ValueError("User account not found.")
        if money(self.data["staff"]["balance"])<amount: raise ValueError("Staff reserve has insufficient money.")
        self.data["staff"]["balance"]=mtext(money(self.data["staff"]["balance"])-amount)
        u["balance"]=mtext(money(u["balance"])+amount)
        u["loan"]["principal"]=mtext(money(u["loan"]["principal"])+amount)
        u["loan"]["outstanding"]=mtext(money(u["loan"]["outstanding"])+amount)
        self.tx("LOAN",amount,"su2608",acc.upper(),"Staff loan"); self.save()

    def repay(self, acc, amount):
        amount=money(amount); u=self.data["users"].get(acc.upper())
        if not u: raise ValueError("User account not found.")
        out=money(u["loan"]["outstanding"])
        if out<=0: raise ValueError("No outstanding loan.")
        if amount>out: raise ValueError("Repayment is greater than loan outstanding.")
        if money(u["balance"])<amount: raise ValueError("User has insufficient balance.")
        u["balance"]=mtext(money(u["balance"])-amount); u["loan"]["outstanding"]=mtext(out-amount)
        self.data["staff"]["balance"]=mtext(money(self.data["staff"]["balance"])+amount)
        self.tx("LOAN_REPAYMENT",amount,acc.upper(),"su2608","Loan repayment"); self.save()
