from customtkinter import *
from socket import *
import threading

class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        self.geometry("720x420")
        self.title("LogiTalk")

        self.menu_frame = CTkFrame(self, width=30, height=420)
        self.menu_frame.pack_propagate(False)
        self.menu_frame.place(x=0, y=0)

        self.is_show_menu = False
        self.speed_animation_menu = -5

        self.btn = CTkButton(self, text=">", width=30, height=30,
                             command=self.toggle_show_menu)
        self.btn.place(x=0, y=0)

        self.chat_field = CTkTextbox(self, font=("Arial", 15, "bold"), state="disabled")
        self.chat_field.place(x=0, y=0)

        self.message_entry = CTkEntry(self, placeholder_text="Enter your message", height=40)
        self.message_entry.place(x=0, y=0)

        self.send_button = CTkButton(self, text=">", width=50, height=40, 
                                     command=self.send_message)
        self.send_button.place(x=0, y=0)

        self.username = "Biba"

        # Підключення до сервера 
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(("0.tcp.eu.ngrok.io", 10453)) 
            hello = f"TEXT@{self.username}@[SYSTEM MESSAGE] {self.username} приєднався до чату!\n"
            self.sock.sendall(hello.encode('utf-8')) # На всяк кодування нехай буде (розпізнає кирилицю, емодзі)
            threading.Thread(target=self.recv_message, daemon=True).start()
        except Exception as e:
            print(f"Failed to connect: {e}")
            self.add_message(f"Не вдалося підключитися: {e}")

        self.adaptive_ui()

    def recv_message(self):
        """Постійно слухає сервер і отримує дані"""
        buffer = ""                                  

        while True:
            try:
                chunk = self.sock.recv(4096)           
                if not chunk:                           
                    break
                
                buffer += chunk.decode('utf-8', errors='ignore')  # Декодуємо з обробкою помилок (ігноримо їх)

                # Обробляємо всі повні рядки
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)   # Відділяємо один рядок
                    self.handle_line(line.strip())         # Передаємо на обробку

            except Exception as e:
                print(f"Помилка при отриманні даних: {e}")
                break

        if self.sock:
            self.sock.close()

    def handle_line(self, line):
        """Розбирає одне повідомлення від сервера"""
        if not line:
            return

        # Приклад line: "TEXT@Biba@Привіт всім!"
        parts = line.split("@", 3)          # Розділяємо максимум на 4 частини

        if not parts:
            return

        msg_type = parts[0]

        if msg_type == "TEXT":
            if len(parts) >= 3:
                author = parts[1]
                message = parts[2]
                self.add_message(f"{author}: {message}")
        else:
            # Невідомий тип — просто виводимо як є
            self.add_message(line)

    def add_message(self, text):
        """Додає повідомлення в чат і прокручує вниз"""
        self.chat_field.configure(state="normal")
        self.chat_field.insert(END, text + "\n")
        self.chat_field.see(END)                  
        self.chat_field.configure(state="disabled")

    def send_message(self):
        """Відправляє повідомлення"""
        message = self.message_entry.get().strip()   # Видаляємо пробіли з обох боків
        if message:
            self.add_message(f"{self.username}: {message}")   # Показуємо своє повідомлення
            data = f"TEXT@{self.username}@{message}\n"
            try:
                self.sock.sendall(data.encode('utf-8'))
            except Exception as e:
                print(f"Помилка відправки: {e}")
        self.message_entry.delete(0, END)

    def adaptive_ui(self):
        """Оновлює розташування елементів при зміні розміру вікна"""
        self.menu_frame.configure(height=self.winfo_height())
        
        self.chat_field.place(x=self.menu_frame.winfo_width())
        self.chat_field.configure(
            width=self.winfo_width() - self.menu_frame.winfo_width(),
            height=self.winfo_height() - 50
        )
        
        self.send_button.place(x=self.winfo_width() - 55, y=self.winfo_height() - 45)
        self.message_entry.place(x=self.menu_frame.winfo_width(), y=self.send_button.winfo_y())
        self.message_entry.configure(
            width=self.winfo_width() - self.menu_frame.winfo_width() - self.send_button.winfo_width() - 10
        )

        self.after(50, self.adaptive_ui)   # Повторюємо кожні 50 мс

    def toggle_show_menu(self):
        if self.is_show_menu:
            self.is_show_menu = False
            self.speed_animation_menu *= -1
            self.btn.configure(text=">")
            self.show_menu()
        else:
            self.is_show_menu = True
            self.speed_animation_menu *= -1
            self.btn.configure(text="<")
            self.show_menu()

            self.entry = CTkEntry(self.menu_frame)
            self.entry.pack(pady=10, padx=5)

    def show_menu(self):
        current_width = self.menu_frame.winfo_width()
        self.menu_frame.configure(width=current_width + self.speed_animation_menu)

        if self.is_show_menu and current_width < 200:
            self.after(10, self.show_menu)
        elif not self.is_show_menu and current_width > 30:
            self.after(10, self.show_menu)
            # Безпечне видалення нашого елемента
            if hasattr(self, 'entry') and self.entry is not None:
                self.entry.destroy()


win = MainWindow()
win.mainloop()