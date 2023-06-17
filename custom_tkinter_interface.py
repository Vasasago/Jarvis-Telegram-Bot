import os
import subprocess
import sys
import time
import tkinter as tk
import webbrowser
from threading import Thread
import PIL
import customtkinter
import requests
from PIL import ImageTk
from PIL.Image import Image
import create_bot
from tkinter.filedialog import askdirectory
import tts

"""ИНИЦИАЛИЗИРУЕМ ПЕРЕМЕННЫЕ"""

config = create_bot.config
console = create_bot.console
active_frame = 'settings_frame'
errors = 0
is_check_bot_running = True
is_start = True
start_bot_thread = None


"""КЛАССЫ"""

class checker_settings:
    @staticmethod
    def check_bot_token(token: str) -> bool:
        try:
            url = f'https://api.telegram.org/bot{token}/getMe'
            response = requests.get(url)
            if response.status_code == 200:
                create_bot.console += f'set bot token: {token}\n'
                return True
            else:
                return False
        except Exception:
            return False

    @staticmethod
    def check_commands_path(path: str) -> bool:
        # Проверка, есть ли папка commands в конце пути
        all_path = os.path.join(path, 'commands')
        if os.path.isdir(all_path) or path.split('/')[-1] == 'commands':
            create_bot.console += f'set cmd path: {path}/commands.\n'  # Установка пути команд
            create_bot.root_folder = path + '/commands'
            return True
        else:
            return False

    @staticmethod
    def check_downloads_path(path: str) -> bool:
        # Проверка, есть ли папка downloads в конце пути
        all_path = os.path.join(path, 'downloads')
        if os.path.isdir(all_path) or path.split('/')[-1].lower() == 'downloads' or path.split('\\')[
            -1].lower() == 'downloads':
            create_bot.console += f'set downloads path: {path}/downloads\n'  # Установка пути загрузок
        return True

    @staticmethod
    def check_openai(token: str) -> bool:
        try:
            url = 'https://api.openai.com/v1/dashboard/billing/subscription'
            headers = {
                'Authorization': f'Bearer {token}',
            }
            response = requests.get(url, headers=headers)
        except Exception:
            return False
        if response.status_code == 200:
            create_bot.console += f'set openai token: {token}\n'  # Установка токена OpenAI
            create_bot.chatgpt_token = token
            return True
        else:
            return False
class main_funcs:
    def start(self):
        if self.check_internet_connection():
            from handlers import commands_hands, callbacks_messages_hands, files_hands
            commands_hands.copy_bot()
            callbacks_messages_hands.copy_bot()
            files_hands.copy_bot()

    def update_scrollbar(self):
        global console
        if console != create_bot.console:
            tk_textbox.configure(state='normal')
            tk_textbox.delete("1.0", tk.END)
            tk_textbox.insert(tk.INSERT, create_bot.console)
            tk_textbox.yview_moveto(1.0)
            console = create_bot.console
            tk_textbox.configure(state='disabled')

        console_frame.after(1000, self.update_scrollbar)

    @staticmethod
    def stop_bot():
        global start_bot_thread
        try:
            if create_bot.flag and start_bot_thread is not None:
                import bot_telegram

                bot_telegram.stop_bot()
                bot_telegram.new_loop.stop()
                start_bot_thread.join()

            check_bot.configure(text='Бот отключен')
        except:
            pass

    @staticmethod
    def check_internet_connection():
        global errors, is_start
        try:
            subprocess.check_output(["ping", "-n", "1", "www.google.com"], timeout=5)
            return True
        except Exception:
            errors = errors + 1
            if errors >= 2 or is_start:
                is_start = False
                return False
            else:
                return True

    def check_bot_fun(self):
        while True:
            global is_check_bot_running, errors
            # Проверяем флаг, чтобы определить, нужно ли выполнять функцию
            flag = self.check_internet_connection()
            if flag:
                # Подключение к интернету есть, запуск бота
                if create_bot.bot_token is not None and create_bot.bot_token != '':
                    if is_check_bot_running:
                        errors = 0
                        check_bot.select()
                        buttons.key_bot(True)
                        self.start()

                    check_bot.configure(state='enabled')
                    check_connection_label.configure(text='подключено к интернету', text_color='green')
                    check_connection_label.place(x=0, y=360)
            else:
                # Подключение к интернету отсутствует
                self.stop_bot()
                check_bot.deselect()
                check_bot.configure(state='disabled')
                check_bot.configure(text='Бот отключен')
                check_connection_label.configure(text='подключение к интернету отсутствует', text_color='red3')
                check_connection_label.place(x=0, y=360)

            # Планируем следующее выполнение функции через 5 секунд
            time.sleep(5)

    def start_check_bot_thread(self):
        thread = Thread(target=self.check_bot_fun)
        thread.start()

class buttons:
    @staticmethod
    def select_folder_commands():
        commands_path = askdirectory(title='Выбор папки с командами')
        if commands_path != '':
            commands_path_entry.delete(0, customtkinter.END)
            commands_path_entry.insert(0, commands_path)

    @staticmethod
    def select_folder_downloads():
        downloads_path = askdirectory(title='Выбор папки загрузок')
        if downloads_path != '':
            downloads_path_entry.delete(0, customtkinter.END)
            downloads_path_entry.insert(0, downloads_path)

    @staticmethod
    def animate_color(entry_enter, color):
        start_color = "#8B008B"  # Начальный цвет (magenta4)
        end_color = color  # #00FF00 зеленый  #FF0000 красный
        duration = 300  # Продолжительность анимации (в миллисекундах)
        steps = 10  # Количество шагов анимации

        # Вычисление изменения цвета для каждого шага
        r_step = (int(end_color[1:3], 16) - int(start_color[1:3], 16)) // steps
        g_step = (int(end_color[3:5], 16) - int(start_color[3:5], 16)) // steps
        b_step = (int(end_color[5:7], 16) - int(start_color[5:7], 16)) // steps

        # Функция, которая будет вызываться на каждом шаге анимации
        def update_color(step):
            r = int(start_color[1:3], 16) + r_step * step
            g = int(start_color[3:5], 16) + g_step * step
            b = int(start_color[5:7], 16) + b_step * step
            color = f"#{r:02X}{g:02X}{b:02X}"
            color = color.replace('-', '0')
            entry_enter.configure(border_color=color)
            if step < steps:
                entry_enter.after(duration // steps, update_color, step + 1)
            else:
                pass

        update_color(0)

    @staticmethod
    def reverse_color(entry_enter):
        start_color = entry_enter.cget("border_color")
        end_color = "#8B008B"  # magenta4
        duration = 500  # Продолжительность анимации (в миллисекундах)
        steps = 10  # Количество шагов анимации

        # Вычисление изменения цвета для каждого шага
        r_step = (int(end_color[1:3], 16) - int(start_color[1:3], 16)) // steps
        g_step = (int(end_color[3:5], 16) - int(start_color[3:5], 16)) // steps
        b_step = (int(end_color[5:7], 16) - int(start_color[5:7], 16)) // steps

        # Функция, которая будет вызываться на каждом шаге анимации
        def update_color(step):
            r = int(start_color[1:3], 16) + r_step * step
            g = int(start_color[3:5], 16) + g_step * step
            b = int(start_color[5:7], 16) + b_step * step
            color = f"#{r:02X}{g:02X}{b:02X}"
            color = color.replace('-', '0')
            entry_enter.configure(border_color=color)
            if step < steps:
                entry_enter.after(duration // steps, update_color, step + 1)
            else:
                pass

        update_color(0)

    # Функция для сохранения изменений
    def save_changes(self):
        def reverse_entries_colors():
            try:
                self.reverse_color(bot_token_entry)
            except Exception:
                pass
            try:
                self.reverse_color(openai_token_entry)
            except Exception:
                pass
            try:
                self.reverse_color(commands_path_entry)
            except Exception:
                pass
            try:
                self.reverse_color(downloads_path_entry)
            except Exception:
                pass

        # Получение значений из полей ввода
        bot_token = bot_token_entry.get()
        openai_token = openai_token_entry.get()
        commands_path = commands_path_entry.get()
        downloads_path = downloads_path_entry.get()


        if bot_token != create_bot.bot_token:
            if checker_settings.check_bot_token(bot_token):
                create_bot.bot_token = bot_token
                config.set('tg-bot', 'bot_token', f'{bot_token}')
                self.animate_color(bot_token_entry, "#00FF00")
                create_bot.create()
                check_bot.configure(state='enabled')
                check_bot.select()
                self.key_bot(True)
                main.start()
            else:
                bot_token_entry.delete(0, customtkinter.END)
                bot_token_entry.insert(0, create_bot.bot_token)
                bot_token_entry.place(x=10, y=100)
                self.animate_color(bot_token_entry, "#FF0000")

        if openai_token != create_bot.chatgpt_token:
            if checker_settings.check_openai(openai_token):
                create_bot.chatgpt_token = openai_token
                config.set('tg-bot', 'chatgpt_token', f'{openai_token}')
                self.animate_color(openai_token_entry, "#00FF00")
            else:
                openai_token_entry.delete(0, customtkinter.END)
                openai_token_entry.insert(0, create_bot.chatgpt_token)
                openai_token_entry.place(x=10, y=170)
                self.animate_color(openai_token_entry, "#FF0000")

        if commands_path != create_bot.root_folder:
            if checker_settings.check_commands_path(commands_path):
                create_bot.root_folder = commands_path
                config.set('tg-bot', 'commands_folder', f'{commands_path}')
                self.animate_color(commands_path_entry, "#00FF00")
            else:
                commands_path_entry.delete(0, customtkinter.END)
                commands_path_entry.insert(0, commands_folder)
                commands_path_entry.place(x=10, y=240)
                self.animate_color(commands_path_entry, "#FF0000")

        if downloads_path != create_bot.script_path:
            if checker_settings.check_downloads_path(downloads_path):

                all_path = os.path.join(downloads_path, 'downloads')
                if downloads_path.split('/')[-1].lower() == 'downloads' or\
                        downloads_path.split('\\')[-1].lower() == 'downloads':
                    create_bot.script_path = downloads_path
                elif os.path.isdir(all_path):
                    create_bot.script_path = downloads_path + '/downloads'
                else:
                    os.makedirs(all_path, exist_ok=True)  # Создание папки, если она не существует
                    create_bot.script_path = all_path

                config.set('tg-bot', 'downloads_path', f'{create_bot.script_path}')
                downloads_path_entry.delete(0, customtkinter.END)
                downloads_path_entry.insert(0, create_bot.script_path)
                self.animate_color(downloads_path_entry, "#00FF00")

        with open('config.ini', 'w') as configfile:
            config.write(configfile)

        settings_frame.after(800, reverse_entries_colors)

    def default_settings(self):
        def reverse_entries_colors():
            try:
                self.reverse_color(commands_path_entry)
            except Exception:
                pass
            try:
                self.reverse_color(downloads_path_entry)
            except Exception:
                pass

        commands_path = os.path.dirname(os.path.abspath(sys.argv[0])) + f'/commands'
        downloads_path = os.path.dirname(os.path.abspath(sys.argv[0])) + f'/downloads'

        if commands_path != create_bot.root_folder:
            commands_path_entry.delete(0, customtkinter.END)
            commands_path_entry.insert(0, commands_path)
            commands_path_entry.place(x=10, y=240)
            config.set('tg-bot', 'commands_folder', f'{commands_path}')
            self.animate_color(commands_path_entry, "#00FF00")

        if downloads_path != create_bot.script_path:
            downloads_path_entry.delete(0, customtkinter.END)
            downloads_path_entry.insert(0, downloads_path)
            downloads_path_entry.place(x=10, y=310)
            config.set('tg-bot', 'downloads_path', f'{downloads_path}')
            self.animate_color(downloads_path_entry, "#00FF00")

        settings_frame.after(800, reverse_entries_colors)

        with open('config.ini', 'w') as configfile:
            config.write(configfile)

    @staticmethod
    def close_window():
        try:
            if main.check_internet_connection():
                global start_bot_thread
                import bot_telegram

                if start_bot_thread is not None and start_bot_thread.is_alive():
                    bot_telegram.stop_bot()
                    bot_telegram.new_loop.stop()
                    start_bot_thread.join()
                    root.destroy()

            else:
                root.destroy()
        except:
            pass

        subprocess.Popen('off.exe')

    @staticmethod
    def settings():
        global active_frame

        console_frame.place_forget()
        settings_frame.place(x=0, y=0)

        active_frame = 'settings_frame'

        settings_btn.configure(text_color='magenta3')

        progressbar_set.place(x=140, y=47)
        progressbar_set.set(1)
        progressbar_set.update()

        console_btn.configure(text_color='white')
        progressbar_con.place_forget()

    @staticmethod
    def console():
        global active_frame

        settings_frame.place_forget()
        console_frame.place(x=0, y=60)

        active_frame = 'console_frame'

        console_btn.configure(text_color='magenta3')

        progressbar_con.place(x=285, y=47)
        progressbar_con.set(1)
        progressbar_con.update()

        settings_btn.configure(text_color='white')
        progressbar_set.place_forget()

    @staticmethod
    def on_enter_settings_button(event):
        try:
            if active_frame != 'settings_frame':
                settings_btn.configure(text_color='magenta3')
                progressbar_set.place(x=140, y=47)
                value = progressbar_set.get()
                if value == 1:
                    progressbar_set.set(0)
                    value = 0

                # Обновление прогрессбара с небольшой задержкой
                while True:
                    progressbar_set.set(value + 0.05)
                    progressbar_set.update()
                    time.sleep(0.01)
                    value = progressbar_set.get()
                    if value >= 0.98:
                        progressbar_set.set(1)
                        progressbar_set.update()
                        break
        except Exception:
            pass

    @staticmethod
    def on_leave_settings_button(event):
        try:
            global active_frame
            if active_frame == 'settings_frame':
                settings_btn.configure(text_color='magenta3')
                progressbar_set.place(x=140, y=47)
                progressbar_set.set(1)
                progressbar_set.update()

                console_btn.configure(text_color='white')
                progressbar_con.place_forget()
            else:
                settings_btn.configure(text_color='white')

                value = progressbar_set.get()

                while True:
                    if active_frame != 'settings_frame' and settings_btn.cget('text_color') != 'magenta3':
                        progressbar_set.set(value - 0.05)
                        progressbar_set.update()
                        time.sleep(0.01)
                        value = progressbar_set.get()
                        if value <= 0:
                            progressbar_set.place_forget()
                            break
                    else:
                        break

        except Exception:
            pass

    @staticmethod
    def on_enter_console_button(event):
        try:
            if active_frame != 'console_frame':
                console_btn.configure(text_color='magenta3')
                progressbar_con.place(x=285, y=47)

                value = progressbar_con.get()
                if value == 1:
                    progressbar_con.set(0)
                    value = 0

                # Обновление прогрессбара с небольшой задержкой
                while True:
                    progressbar_con.set(value + 0.05)
                    progressbar_con.update()
                    time.sleep(0.01)
                    value = progressbar_con.get()
                    if value >= 0.98:
                        progressbar_con.set(1)
                        progressbar_con.update()
                        break

        except Exception:
            pass

    @staticmethod
    def on_leave_console_button(event):
        try:
            global active_frame
            if active_frame == 'console_frame':
                console_btn.configure(text_color='magenta3')
                progressbar_con.place(x=285, y=47)
                progressbar_con.set(1)
                progressbar_con.update()

                settings_btn.configure(text_color='white')
                progressbar_set.place_forget()
            else:
                console_btn.configure(text_color='white')
                value = progressbar_con.get()

                while True:
                    if active_frame != 'console_frame' and console_btn.cget('text_color') != 'magenta3':
                        progressbar_con.set(value - 0.05)
                        progressbar_con.update()
                        time.sleep(0.01)
                        value = progressbar_con.get()
                        if value <= 0:
                            progressbar_con.place_forget()
                            break
                    else:
                        break

        except Exception:
            pass

    @staticmethod
    def on_enter_select_commands_button(event):
        select_commands_button.configure(text_color='orange1')

    @staticmethod
    def on_leave_select_commands_button(event):
        select_commands_button.configure(text_color='yellow')

    @staticmethod
    def on_enter_select_downloads_button(event):
        select_downloads_button.configure(text_color='orange1')

    @staticmethod
    def on_leave_select_downloads_button(event):
        select_downloads_button.configure(text_color='yellow')

    @staticmethod
    def on_enter_telegram_button(event):
        telegram.configure(text_color='magenta1')

    @staticmethod
    def on_leave_telegram_button(event):
        telegram.configure(text_color='magenta3')

    @staticmethod
    def key_bot(flag=False):
        global start_bot_thread, is_check_bot_running
        try:
            if check_bot.get() == 1 or flag and create_bot.bot_token is not None and create_bot.bot_token != '':

                if flag is False:
                    is_check_bot_running = True

                check_bot.configure(text='Бот запущен')
                if start_bot_thread is None or not start_bot_thread.is_alive():
                    if main.check_internet_connection():
                        import bot_telegram
                        start_bot_thread = Thread(target=bot_telegram.start)
                        start_bot_thread.start()
            else:
                if flag is False:
                    is_check_bot_running = False

                check_bot.configure(text='Отключение...')
                check_bot.configure(state='disabled')
                main.update_scrollbar()
                if start_bot_thread is not None and start_bot_thread.is_alive():
                    # Запустить остановку бота и ожидание завершения потока в отдельном потоке
                    stop_thread = Thread(target=main.stop_bot)
                    stop_thread.start()
        except:
            pass

    @staticmethod
    def open_log():
        log_file = os.path.dirname(os.path.abspath(sys.argv[0])) + '\\logs_from_bot.log'
        os.startfile(log_file)

    @staticmethod
    def clear():
        create_bot.console = ''

    @staticmethod
    def go_telegram():
        webbrowser.open(url='https://t.me/jarvis_bot_by_vassago')


"""ИНИЦИАЛИЗИРУЕМ КЛАССЫ"""


checker_settings = checker_settings()
main = main_funcs()
buttons = buttons()


"""СОЗДАЕМ ОКНО"""

# Создание графического интерфейса
customtkinter.set_appearance_mode('dark')
customtkinter.set_default_color_theme('dark-blue')

customtkinter.deactivate_automatic_dpi_awareness()


root = customtkinter.CTk()
root.title(f"Jarvis Telegram Bot | User ID: {create_bot.user_id}")
root.geometry("400x520")
root.resizable(False, False)  # Запрет изменения размера окна
root.iconbitmap("icons\\h.ico")

"""СОЗДАЕМ ФРЕЙМ КОНСОЛИ И ДОБАВЛЯЕМ НА НЕГО ЭЛЕМЕНТЫ"""

console_frame = customtkinter.CTkFrame(root)

console_frame.configure(width=400, height=400, fg_color='gray10')


# Создание текстового поля
tk_textbox = tk.Text(console_frame, highlightthickness=0, selectbackground='magenta2', selectforeground='blue',
                     fg='gray80', bg='gray10', wrap='word', height=17, width=43)
tk_textbox.place(x=-1, y=3)

# Создание скроллбара
ctk_textbox_scrollbar = customtkinter.CTkScrollbar(console_frame, command=tk_textbox.yview, height=310,
                                                   bg_color='gray10', fg_color='gray10', button_color='magenta4',
                                                   button_hover_color='magenta3')
ctk_textbox_scrollbar.place(x=385, y=4)

# Текст на скроллбар
tk_textbox.configure(yscrollcommand=ctk_textbox_scrollbar.set, font=('Arial Black', 10))

tk_textbox.insert('1.0', create_bot.console)

log_button = customtkinter.CTkButton(console_frame, text="ОТКРЫТЬ ЛОГ", width=10, font=('Arial Black', 10),
                                     bg_color='gray10', fg_color='gray20', hover_color='gray15',
                                     border_color='gray10', command=buttons.open_log)
log_button.place(x=280, y=320)

clear_console = customtkinter.CTkButton(console_frame, text='ОЧИСТИТЬ', width=10, font=('Arial Black', 10),
                                        bg_color='gray10', fg_color='gray20', hover_color='gray15',
                                        border_color='gray10', command=buttons.clear)
clear_console.place(x=190, y=320)


check_bot = customtkinter.CTkSwitch(console_frame, text='Бот отключен', text_color='gray90',
                                    progress_color='magenta4', command=buttons.key_bot)
check_bot.place(x=30, y=320)

check_connection_label = customtkinter.CTkLabel(console_frame, text='идет загрузка...',
                                                text_color='gray50', bg_color='gray15', height=0, width=400)
check_connection_label.place(x=0, y=360)


"""СОЗДАЕМ ФРЕЙМ НАСТРОЕК И ДОБАВЛЯЕМ НА НЕГО ЭЛЕМЕНТЫ"""

settings_frame = customtkinter.CTkFrame(root, width=400, height=460, fg_color='gray10')
settings_frame.place(x=0, y=0)


save_button = customtkinter.CTkButton(settings_frame, text="СОХРАНИТЬ", width=380, font=('Arial Black', 10),
                                      fg_color='magenta4', hover_color='DarkOrchid4', text_color='white',
                                      command=buttons.save_changes)
save_button.place(x=10, y=360)

default_settings_button = customtkinter.CTkButton(settings_frame, text="ВЕРНУТЬ ПО-УМОЛЧАНИЮ", width=380,
                                                  font=('Arial Black', 10), fg_color='gray20', hover_color='gray15',
                                                  text_color='white', command=buttons.default_settings)
default_settings_button.place(x=10, y=400)


bot_token_label = customtkinter.CTkLabel(settings_frame, text="Токен бота:", font=('Trebuchet MS', 15))
bot_token_label.place(x=10, y=70)

bot_token_entry = customtkinter.CTkEntry(settings_frame, width=380, border_color='magenta4', fg_color='black',
                                         placeholder_text='Токен не найден', placeholder_text_color='gray60',
                                         text_color='white')
bot_token_entry.place(x=10, y=100)


openai_token_label = customtkinter.CTkLabel(settings_frame, text="Токен OpenAI:", font=('Trebuchet MS', 15))
openai_token_label.place(x=10, y=140)

openai_token_entry = customtkinter.CTkEntry(settings_frame, width=380, border_color='magenta4', fg_color='black',
                                            placeholder_text='Токен не найден',
                                            placeholder_text_color='gray60', text_color='white')
openai_token_entry.place(x=10, y=170)


commands_path_label = customtkinter.CTkLabel(settings_frame, text="Путь к командам:", font=('Trebuchet MS', 15))
commands_path_label.place(x=10, y=210)
commands_path_entry = customtkinter.CTkEntry(settings_frame, width=380, border_color='magenta4', fg_color='black',
                                             placeholder_text_color='gray40', text_color='white')
commands_path_entry.place(x=10, y=240)

select_commands_button = customtkinter.CTkButton(settings_frame, text='📂', width=0, height=0, font=('Arial Black', 15),
                                                 text_color='yellow', bg_color='gray10',
                                                 fg_color='gray10', hover_color='gray10',
                                                 command=buttons.select_folder_commands)
select_commands_button.place(x=360, y=210)


downloads_path_label = customtkinter.CTkLabel(settings_frame, text="Путь к загрузкам:", font=('Trebuchet MS', 15))
downloads_path_label.place(x=10, y=280)
downloads_path_entry = customtkinter.CTkEntry(settings_frame, width=380, border_color='magenta4', fg_color='black',
                                              placeholder_text_color='gray40', text_color='white')
downloads_path_entry.insert(0, create_bot.script_path)
downloads_path_entry.place(x=10, y=310)

select_downloads_button = customtkinter.CTkButton(settings_frame, text='📂', width=0, height=0, font=('Arial Black', 15),
                                                 text_color='yellow', bg_color='gray10',
                                                 fg_color='gray10', hover_color='gray10',
                                                 command=buttons.select_folder_downloads)
select_downloads_button.place(x=360, y=280)


"""СОЗДАЕМ КАНВАС И ДОБАВЛЯЕМ НА НЕГО ЭЛЕМЕНТЫ"""

canvas = customtkinter.CTkCanvas(root, width=400, height=60, bg='gray5', highlightbackground='gray5')
canvas.place(x=0, y=0)


# Создание Canvas с фоном прозрачного цвета для логотипа
canvas_image = customtkinter.CTkCanvas(root, width=60, height=60, bg='gray5', highlightthickness=0)
canvas_image.place(x=0, y=0)


image = PIL.Image.open("icons\\img.png")
image = image.resize((60, 60))  # Измените размер изображения по своему усмотрению
photo = ImageTk.PhotoImage(image)

# Вставка логотипа на Canvas
image_label = canvas_image.create_image(0, 0, anchor=customtkinter.NW, image=photo)


name = customtkinter.CTkLabel(canvas, text=f'JARVIS', text_color='gray80', font=('Arial Black', 15))
name1 = customtkinter.CTkLabel(canvas, text=f'BOT', text_color='gray80', font=('Arial Black', 15))
version = customtkinter.CTkLabel(canvas, text=f'V{create_bot.bot_version}', text_color='gray60', height=5)
name.place(x=65, y=0)
name1.place(x=65, y=20)
version.place(x=65, y=45)

progressbar_set = customtkinter.CTkProgressBar(root, width=120, height=5, progress_color='magenta3',
                                               fg_color='gray5', bg_color='gray5', indeterminate_speed=1)

progressbar_set.place(x=140, y=47)
progressbar_set.set(1)
progressbar_set.update()

progressbar_con = customtkinter.CTkProgressBar(root, width=100, height=5, progress_color='magenta3',
                                               fg_color='gray5', bg_color='gray5', indeterminate_speed=1)

settings_btn = customtkinter.CTkButton(root, text="⚙️ НАСТРОЙКИ", width=10, font=('Trebuchet MS', 17),
                                       fg_color='gray5', bg_color='gray5', hover_color='gray5',
                                       text_color='white', command=buttons.settings)
settings_btn.place(x=130, y=20)

settings_btn.configure(text_color='magenta3')

console_btn = customtkinter.CTkButton(root, text="🖥 КОНСОЛЬ", width=10, font=('Trebuchet MS', 17), fg_color='gray5',
                                      bg_color='gray5', hover_color='gray5', text_color='white', command=buttons.console)
console_btn.place(x=275, y=20)


"""ПОДПИСИ"""

author = customtkinter.CTkLabel(root, text="Автор проекта: Vassago | Evgeny Punk",
                                              text_color='gray50')
author.place(x=90, y=450)

image = PIL.Image.open("icons\\telegram.png")
telegram_image = customtkinter.CTkImage(light_image=image)

telegram = customtkinter.CTkButton(root, text="Наш телеграм канал",
                                text_color='magenta3', bg_color='gray10',
                                   fg_color='gray10', hover_color='gray10', image=telegram_image, command=buttons.go_telegram)
telegram.place(x=115, y=480)


"""БИНДЫ"""

# Кнопка настройки
settings_btn.bind('<Enter>', buttons.on_enter_settings_button)  # Обработчик события наведения
settings_btn.bind('<Leave>', buttons.on_leave_settings_button)  # Обработчик события покидания

# Кнопка консоль
console_btn.bind('<Enter>', buttons.on_enter_console_button)
console_btn.bind('<Leave>', buttons.on_leave_console_button)

# Кнопка выбора папки команд
select_commands_button.bind('<Enter>', buttons.on_enter_select_commands_button)
select_commands_button.bind('<Leave>', buttons.on_leave_select_commands_button)

# Кнопка выбора папки загрузок
select_downloads_button.bind('<Enter>', buttons.on_enter_select_downloads_button)
select_downloads_button.bind('<Leave>', buttons.on_leave_select_downloads_button)

# Кнопка перехода в телеграм канал
telegram.bind('<Enter>', buttons.on_enter_telegram_button)
telegram.bind('<Leave>', buttons.on_leave_telegram_button)


"""УСЛОВИЯ"""

if create_bot.bot_token != '' and create_bot.bot_token is not None:
    bot_token_entry.insert(0, create_bot.bot_token)

if create_bot.chatgpt_token != '' and create_bot.chatgpt_token is not None:
    openai_token_entry.insert(0, create_bot.chatgpt_token)

if create_bot.root_folder == 'commands':
    commands_folder = os.path.dirname(os.path.abspath(sys.argv[0])) + f'\\{create_bot.root_folder}'
    commands_path_entry.insert(0, commands_folder)
else:
    commands_folder = create_bot.root_folder
    commands_path_entry.insert(0, commands_folder)


"""ПРОТОКОЛЫ"""

root.protocol("WM_DELETE_WINDOW", buttons.close_window)


"""СТАРТУЕМ"""

# Проверка установки Silero TTS и инициализация модели
tts.start_tts()

# Запускаем проверку соединения и первоначальное выполнение функции в отдельном потоке
main.start_check_bot_thread()

# Запускаем обновление консоли
main.update_scrollbar()

# Запуск главного цикла приложения
root.mainloop()

