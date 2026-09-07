from kivy.app import App
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from main import Bank, mtext

KV = """
#:import dp kivy.metrics.dp
ScreenManager:
    Home:
    Create:
    UserLogin:
    UserDash:
    StaffLogin:
    StaffDash:

<Button>: size_hint_y: None; height: dp(48); font_size: dp(16)
<TextInput>: size_hint_y: None; height: dp(48); multiline: False; font_size: dp(16)

<Home>:
    name: "home"
    BoxLayout:
        orientation: "vertical"; padding: dp(20); spacing: dp(10)
        Label: text: "SIMPLE BANK"; font_size: dp(28); bold: True
        Button: text: "Create User Account"; on_release: app.go("create")
        Button: text: "User Login"; on_release: app.go("user_login")
        Button: text: "Staff Login"; on_release: app.go("staff_login")
        Button: text: "Exit"; on_release: app.stop

<Create>:
    name: "create"
    BoxLayout:
        orientation: "vertical"; padding: dp(20); spacing: dp(10)
        Label: text: "CREATE ACCOUNT"; font_size: dp(24)
        TextInput: id: name; hint_text: "Full name"
        TextInput: id: pw; hint_text: "Password"; password: True
        Button: text: "Create Account"; on_release: app.create_account(name.text,pw.text)
        Button: text: "Back"; on_release: app.go("home")

<UserLogin>:
    name: "user_login"
    BoxLayout:
        orientation: "vertical"; padding: dp(20); spacing: dp(10)
        Label: text: "USER LOGIN"; font_size: dp(24)
        TextInput: id: acc; hint_text: "Account number"
        TextInput: id: pw; hint_text: "Password"; password: True
        Button: text: "Login"; on_release: app.login_user(acc.text,pw.text)
        Button: text: "Back"; on_release: app.go("home")

<UserDash>:
    name: "user"
    BoxLayout:
        orientation: "vertical"; padding: dp(15); spacing: dp(8)
        Label: id: info; text: ""; font_size: dp(18)
        TextInput: id: receiver; hint_text: "Receiver account"
        TextInput: id: amount; hint_text: "Amount"; input_filter: "float"
        Button: text: "Transfer Money"; on_release: app.transfer(receiver.text,amount.text)
        Button: text: "Refresh"; on_release: app.refresh_user()
        Button: text: "Logout"; on_release: app.logout()

<StaffLogin>:
    name: "staff_login"
    BoxLayout:
        orientation: "vertical"; padding: dp(20); spacing: dp(10)
        Label: text: "STAFF LOGIN"; font_size: dp(24)
        TextInput: id: acc; hint_text: "Staff account"
        TextInput: id: pw; hint_text: "Staff password"; password: True
        Button: text: "Login"; on_release: app.login_staff(acc.text,pw.text)
        Button: text: "Back"; on_release: app.go("home")

<StaffDash>:
    name: "staff"
    BoxLayout:
        orientation: "vertical"; padding: dp(12); spacing: dp(7)
        Label: id: summary; text: ""; font_size: dp(16)
        TextInput: id: account; hint_text: "User account"
        TextInput: id: amount; hint_text: "Amount"; input_filter: "float"
        Button: text: "Deposit"; on_release: app.staff_action("deposit",account.text,amount.text)
        Button: text: "Withdraw"; on_release: app.staff_action("withdraw",account.text,amount.text)
        Button: text: "Give Loan"; on_release: app.staff_action("loan",account.text,amount.text)
        Button: text: "Repay Loan"; on_release: app.staff_action("repay",account.text,amount.text)
        Button: text: "View Users"; on_release: app.view_users()
        Button: text: "View Transactions"; on_release: app.view_transactions()
        Button: text: "Logout"; on_release: app.logout()
"""

class Home(App): pass
class Create(App): pass
class UserLogin(App): pass
class UserDash(App): pass
class StaffLogin(App): pass
class StaffDash(App): pass

class BankApp(App):
    def build(self):
        self.bank=Bank(); self.current_user=None
        return Builder.load_string(KV)
    def go(self,s): self.root.current=s; self.refresh_user() if s=="user" else self.refresh_staff() if s=="staff" else None
    def popup(self,title,msg): Popup(title=title,content=Label(text=msg),size_hint=(.9,.5)).open()
    def create_account(self,n,p):
        try:
            acc=self.bank.create_user(n,p); self.popup("Account Created",f"Your account number:\\n{acc}")
        except Exception as e:self.popup("Error",str(e))
    def login_user(self,a,p):
        r=self.bank.user_login(a.strip(),p)
        if not r:return self.popup("Login Error","Invalid account or password.")
        self.current_user=r; self.go("user")
    def login_staff(self,a,p):
        if not self.bank.staff_login(a.strip(),p):return self.popup("Login Error","Invalid staff login.")
        self.go("staff")
    def refresh_user(self):
        if not self.current_user:return
        u=self.bank.data["users"][self.current_user]
        self.root.get_screen("user").ids.info.text=f"Welcome {u['name']}\\nAccount: {self.current_user}\\nBalance: ₹{mtext(u['balance'])}\\nLoan: ₹{mtext(u['loan']['outstanding'])}"
    def transfer(self,r,a):
        try:self.bank.user_transfer(self.current_user,r,a);self.popup("Success","Transfer completed.");self.refresh_user()
        except Exception as e:self.popup("Transfer Error",str(e))
    def refresh_staff(self):
        s=self.bank.data["staff"]; users=self.bank.data["users"]
        self.root.get_screen("staff").ids.summary.text=f"Staff reserve: ₹{mtext(s['balance'])}\\nUsers: {len(users)}"
    def staff_action(self,action,a,x):
        try:
            getattr(self.bank,{"deposit":"staff_deposit","withdraw":"staff_withdraw","loan":"loan","repay":"repay"}[action])(a,x)
            self.popup("Success","Operation completed.");self.refresh_staff()
        except Exception as e:self.popup("Error",str(e))
    def view_users(self):
        t="\\n".join(f"{u['account_number']} | {u['name']} | ₹{mtext(u['balance'])}" for u in self.bank.data["users"].values()) or "No users."
        self.popup("Users",t)
    def view_transactions(self):
        t="\\n".join(f"{i}. {x['type']} ₹{x['amount']} {x['from']} -> {x['to']}" for i,x in enumerate(self.bank.data["transactions"],1)) or "No transactions."
        self.popup("Transactions",t)
    def logout(self):self.current_user=None;self.go("home")

if __name__=="__main__": BankApp().run()
