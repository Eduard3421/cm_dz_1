import os
import tarfile
import json
import platform
import subprocess
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext, messagebox


class ShellEmulator:
    def __init__(self, config_path):
        self.load_config(config_path)
        self.current_directory = self.extract_vfs()
        self.init_gui()
        self.run_startup_script()

    def load_config(self, config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
            self.username = config['username']
            self.hostname = config['hostname']
            self.vfs_path = config['vfs_path']
            self.startup_script = config['startup_script']

    def extract_vfs(self):
        # Создаем временную директорию для распаковки VFS
        vfs_dir = '\\tmp\\vfs'
        os.makedirs(vfs_dir, exist_ok=True)

        # Распаковываем tar файл
        with tarfile.open(self.vfs_path, 'r') as tar:
            tar.extractall(path=vfs_dir)

        return vfs_dir

    # def run_startup_script(self):
    #     try:
    #         command = f"bash {self.startup_script}"
    #         output = subprocess.check_output(command, shell=True)
    #         self.output_area.insert(tk.END, output.decode('utf-8') + '\n')
    #         self.output_area.see(tk.END)
    #     except Exception as e:
    #         self.output_area.insert(tk.END, f"Error running startup script: {e}\n")

    def run_startup_script(self):
        try:
            with open(self.startup_script, 'r') as script:
                commands = script.readlines()
                for command in commands:
                    command = command.strip()
                    if command:  # Если команда не пустая
                        output = self.execute_command(command)
                        self.output_area.insert(tk.END, output + '\n')  # Выводим результат выполнения команды
                        self.output_area.see(tk.END)  # Прокручиваем вниз
        except Exception as e:
            self.output_area.insert(tk.END, f"Error running startup script: {e}\n")

    def init_gui(self):
        self.root = tk.Tk()
        self.root.title("Shell Emulator")

        self.output_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD)
        self.output_area.pack(expand=True, fill='both')

        self.input_area = tk.Entry(self.root)
        self.input_area.pack(fill='x')
        self.input_area.bind('<Return>', self.process_command)

    def process_command(self, event):
        command = self.input_area.get()
        self.input_area.delete(0, tk.END)

        if command.strip():
            output = self.execute_command(command.strip())
            if output is not None:
                self.output_area.insert(tk.END, output + '\n')
                self.output_area.see(tk.END)

    def execute_command(self, command):
        user_prompt = f"{self.username}@{self.hostname}:~$ {command}\n"
        self.output_area.insert(tk.END, user_prompt)
        self.output_area.insert(tk.END, command + '\n')
        self.output_area.see(tk.END)
        if command.startswith('cd '):
            return self.change_directory(command[3:])
        elif command == 'ls':
            return self.list_directory()
        elif command == 'uname':
            return f"{platform.system()} {platform.release()}"  #
        elif command == 'date':
            return str(datetime.now())
        elif command == 'exit':
            self.root.quit()
            return None
        else:
            return f"Command not found: {command}"

    def change_directory(self, path):
        new_path = os.path.join(self.current_directory, path.strip())

        if os.path.isdir(new_path):
            os.chdir(new_path)
            self.current_directory = new_path
            return f"Changed directory to {new_path}"

        return "Directory not found."

    def list_directory(self, show_hidden=False):
        try:
            # Получаем список файлов и директорий
            entries = os.listdir(self.current_directory)

            if not show_hidden:
                # Фильтруем скрытые файлы (начинаются с точки)
                entries = [entry for entry in entries if not entry.startswith('.')]

            # Сортируем список
            entries.sort()

            return '\n'.join(entries)  # Возвращаем список в виде строки

        except Exception as e:
            return f"Ошибка при перечислении каталога: {e}"

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    config_file_path = 'C:/Users/Edward/PycharmProjects/conf_man/config.json'
    emulator = ShellEmulator(config_file_path)
    emulator.run()
