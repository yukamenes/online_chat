from customtkinter import *
from socket import *
import threading


class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        self.geometry("400x400")

        self.menu_frame = CTkFrame(self, width = 30, height=300)
        self.menu_frame.pack_propagate(0)
        self.menu_frame.place(x = 0, y = 0) 

        self.is_show_menu = False
        self.animation_speed = -7

        self.btn = CTkButton(self, text = ">", width = 30, command=self.open_closed_menu)
        self.btn.place(x = 0, y = 0)

        self.chat_field = CTkTextbox(self, font = ("Arial", 20, "bold"), state = "disabled")
        self.chat_field.place(x = 0, y = 0)

        self.message_entry = CTkEntry(self, placeholder_text="Type your message:", height=40)
        self.message_entry.place(x = 0, y = 0)

        self.send_button = CTkButton(self, text=">", width = 70, height=40, command = self.send_message)
        self.send_button.place(x = 0, y = 0)

        set_appearance_mode("system")

        self.sound_pack = False

        self.username = "yulia" 
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(("localhost", 8080))
            hello = f"{self.username} приєднався до чату!"
            self.sock.send(hello.encode("utf-8"))
        except Exception as e:
            print(f"Не вдалось підключитись до сервера: {e}")
        
        threading.Thread(target=self.receive_message, daemon=True).start()



        self.adaptive_ui()
    def change_username(self):
        new_username = self.entry.get()
        old_username = self.username
        if new_username:
            self.username = new_username
            notification = f"{old_username} change nickname to {new_username}"
            try:
                self.sock.send(notification.encode())
            except Exception as e:
                print(f"Error - {e}")
    
    def receive_message(self):
        while 1:
            try:
                data = self.sock.recv(4096)
                if not data:
                    break
                message = data.decode()
                self.chat_field.configure(state = "normal")
                self.chat_field.insert(END, message + "\n")
                self.chat_field.see(END)
                self.chat_field.configure(state = "disabled")
                if self.sound_pack:
                    self.bell()
            except Exception as e:
                print(f"Error - {e}")
        
        self.sock.close()



    def send_message(self):
        message = self.message_entry.get()
        if message:
            full_message = f"{self.username} : {message}"
            try:
                self.sock.send(full_message.encode())
                self.chat_field.configure(state = "normal")
                self.chat_field.insert(END, full_message + "\n")
                self.chat_field.see(END)
                self.chat_field.configure(state = "disabled")
                self.message_entry.delete(0, END)
            except Exception as e:
                print(f"Error - {e}")


    def adaptive_ui(self):
        self.menu_frame.configure(height = self.winfo_height())

        self.chat_field.place(x = self.menu_frame.winfo_width())

        self.chat_field.configure(
            width = self.winfo_width() - self.menu_frame.winfo_width() - 20,
            height = self.winfo_height() - 40
        )

        self.send_button.place(x = self.winfo_width() - self.send_button.winfo_width(),
                               y = self.winfo_height() - 40)

        self.message_entry.place(x = self.menu_frame.winfo_width(),
                                 y = self.send_button.winfo_y())
        self.message_entry.configure(width = self.winfo_width() - self.menu_frame.winfo_width() - self.send_button.winfo_width())

        self.after(10, self.adaptive_ui)
        

    def open_closed_menu(self):
        if self.is_show_menu:
            self.is_show_menu = False
            self.animation_speed *= -1
            self.btn.configure(text = ">")
            self.show_menu()
        else:
            self.is_show_menu = True
            self.animation_speed *= -1
            self.btn.configure(text = "<")
            self.show_menu()

            self.label = CTkLabel(self.menu_frame, text = "Type your username:")
            self.label.pack(pady = 30)

            self.entry = CTkEntry(self.menu_frame)
            self.entry.pack()
            
            self.save_button = CTkButton(self.menu_frame, text = "Save", command = self.change_username)
            self.save_button.pack(pady = 5)

            self.app_label = CTkLabel(self.menu_frame, text = "Select theme:")
            self.app_label.pack(pady = 5)

            self.app_menu = CTkOptionMenu(self.menu_frame, values=["System", "Light", "Dark"], command=self.change_theme)
            self.app_menu.pack()

            self.font_label = CTkLabel(self.menu_frame, text = "Select Font Size:")
            self.font_label.pack(pady = 5)

            self.font_slider = CTkSlider(self.menu_frame, from_ = 10, to = 30, command = self.change_font)
            self.font_slider.set(20)
            self.font_slider.pack()

            self.save_chat_but = CTkButton(self.menu_frame, text = "Save chat", command=self.save_chat)
            self.save_chat_but.pack(pady = 5)

            self.sound_var = Variable(value = 0)
            self.sound_checkbox = CTkCheckBox(self.menu_frame, text = "Enable Sound on Message", variable=self.sound_var, command = self.update_sound)
            self.sound_checkbox.pack(pady = 5)
    
    def show_menu(self):
        self.menu_frame.configure(width = self.menu_frame.winfo_width() + self.animation_speed)

        if not self.menu_frame.winfo_width() >= 200 and self.is_show_menu:
            self.after(10, self.show_menu)
        elif self.menu_frame.winfo_width() >= 40 and not self.is_show_menu:
            self.after(10, self.show_menu) 
            if self.label and self.entry and self.save_button and self.app_label and self.app_menu and self.font_label and self.font_slider and self.save_chat_but and self.sound_checkbox:
                self.label.destroy()
                self.entry.destroy() 
                self.save_button.destroy() 
                self.app_label.destroy()
                self.app_menu.destroy()
                self.font_label.destroy()
                self.font_slider.destroy()
                self.save_chat_but.destroy()
                self.sound_checkbox.destroy()
    
    def change_theme(self, mode): # mode = "Dark" -> dark
        set_appearance_mode(mode.lower())
    
    def change_font(self, value):
        self.chat_field.configure(font = ("Arial", int(value), "bold"))

    def save_chat(self):
        with open("chat_log.txt", "w") as file:
            file.write(self.chat_field.get("1.0", END))
    
    def update_sound(self):
        self.sound_pack = bool(self.sound_var.get())

    


win = MainWindow()
win.mainloop()