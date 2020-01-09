from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from pymongo import MongoClient
import hashlib


Builder.load_file('signin/signin.kv')


class SigninWindow(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def validate_user(self):
        user = self.ids.username_field
        pwd = self.ids.pwd_field
        info = self.ids.info

        username = user.text
        passw = pwd.text

        user.text = pwd.text = ''

        if username == '' or passw == '':
            info.text = "[color=#FF0000]username and/or password is required[/color]"
        else:
            clinet = MongoClient()
            users = clinet.silverpos.users

            user = users.find_one({'user_name':username})
            if user is None:
                info.text = "[color=#FF0000]Invalid username and/or password[/color]"
            else:
                passw = hashlib.sha256(passw.encode()).hexdigest()
                if passw == user["password"]:
                    #info.text = "[color=#00FF00]Logged In Successfully!!![/color]"
                    info.text = ''
                    self.parent.parent.parent.\
                        ids.scrn_op.children[0].ids.loggedin_user.text=username
                    des = user['designation']
                    if des == 'Administrator':
                        self.parent.parent.current = 'scrn_admin'
                    else:
                        self.parent.parent.current = 'scrn_op'
                else:
                    info.text = "[color=#FF0000]Invalid username and/or password[/color]"

            clinet.close()



class SigninApp(App):
    def build(self):
        return SigninWindow()


if __name__ == "__main__":
    sa = SigninApp()
    sa.run()