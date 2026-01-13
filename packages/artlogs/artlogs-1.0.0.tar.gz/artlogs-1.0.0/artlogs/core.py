import os


class HelpFunction:
    try:
        from colorama import Fore, Style, init, Back
        import os
    except:
        print("Ошибка при импорте Colorama")

    green = Fore.GREEN
    yellow = Fore.YELLOW
    red = Fore.RED
    blue = Fore.BLUE
    white = Fore.WHITE

    back_red = Back.RED

    reset = Style.RESET_ALL


class ArtLogProfile:
    """Класс для работы с одним профилем"""

    def __init__(self, name="user", password="", manager=None):
        self.access = False
        self.h = HelpFunction()
        self.username = ""
        self.password = ""
        self.log_filename = None
        self.mod = "all"  # режим логирования (строка, не метод!)
        self.manager = manager

        # Автоматически создаем/авторизуем профиль
        if name and password:
            self.logUser(name, password, "c" if manager else "i")

    # РАБОТА С ПРОФИЛЕМ
    def logUser(self, name="user", password="0000", flag="c"):
        filename = name.strip() + ".log"

        if flag == "c":
            try:
                with open(filename, "w", encoding="utf-8") as logFile:
                    profile_datas = f"===ArtLogs===\nname={name},\npassword={password},\n===ArtLogs===\n"
                    logFile.write(profile_datas)
            except Exception:
                return "Name is invalid"

            self._log("Успешно создан профиль", "a")
            self.username = name.strip()
            self.password = password.strip()
            self.log_filename = filename
            self.access = True
            return self

        elif flag == "i":
            try:
                with open(filename, "r", encoding="utf-8") as file:
                    content = file.read()
                    name_access = f"name={name.strip()}," in content
                    password_access = f"password={password.strip()}," in content
                    self.username = name.strip()
                    self.password = password.strip()
                    if name_access and password_access:
                        self.access = True
                        self.username = name.strip()
                        self.log_filename = filename
                        self.password = password.strip()
                        self._log(f"Успешно авторизован профиль: {name.strip()}", "a")
                        return self
                    elif not password_access:
                        self._log("Password is invalid", "e")
                        return "Password is invalid"
                    else:
                        self._log("Name and password is invalid", "e")
                        return "Name and password is invalid"
            except FileNotFoundError:
                self._log("Name is invalid (файл не найден)", "e")
                return "Name is invalid"
            except Exception:
                self._log("Name is invalid (ошибка чтения)", "e")
                return "Name is invalid"

    def delUser(self):
        filename = self.username + ".log"
        try:
            self._log(f"Профиль {filename} успешно удалён", "a")
            os.remove(filename)
            return True
        except Exception as e:
            self._log(f"Во время удаления профиля возникла ошибка: {e}", "e")
            return False

    def save_log_data(self, log_context):
        if not self.access:
            print("Ошибка: пользователь не авторизован")
            return False

        try:
            with open(self.log_filename, "a", encoding="utf-8") as logFile:
                logFile.write(log_context + "\n")
            return True
        except Exception as e:
            print(f"Ошибка обработки файла: {e}")
            return False

    # РАБОТА С ЛОГАМИ
    def _log(self, text, flag="i"):
        """Внутренний метод для логирования"""
        log_context = ""

        # Проверяем, разрешен ли данный тип лога в текущем режиме
        if self.mod != "all" and flag != self.mod:
            return "modException"

        if flag == "i":  # information
            log_context = self.h.blue + f"ℹ️{text}ℹ️" + self.h.reset
            print(log_context)
            if self.access:
                self.save_log_data(f"ℹ️{text}ℹ️")
            return True

        elif flag == "a":  # accept
            log_context = self.h.green + f"✅{text}✅" + self.h.reset
            print(log_context)
            if self.access:
                self.save_log_data(f"✅{text}✅")
            return True

        elif flag == "w":  # warning
            log_context = self.h.yellow + f"⚠️{text}⚠️" + self.h.reset
            print(log_context)
            if self.access:
                self.save_log_data(f"⚠️{text}⚠️")
            return True

        elif flag == "e":  # error
            log_context = self.h.red + f"⛔{text}⛔" + self.h.reset
            print(log_context)
            if self.access:
                self.save_log_data(f"⛔{text}⛔")
            return True

        else:  # unknown flag
            if self.mod != "all" and self.mod != "y":
                return "modException"
            log_context = f"??{text}??" + self.h.reset
            print(log_context)
            if self.access:
                self.save_log_data(f"??{text}??")
            return True

    def log(self, text, flag="i"):
        """Публичный метод для логирования"""
        if self.access and self.mod == flag or self.access and self.mod == "all":
            print(f"[{self.username}] ", end="")

        result = self._log(text, flag)

        if result == "modException":
            # Если режим не позволяет этот тип лога, просто ничего не делаем
            # НЕ вызываем _log() снова!
            return False
        return result  # Возвращаем результат _log() (True или modException)

    # ПЕРЕИМЕНОВАЛ метод mod() в set_mod()
    def set_mod(self, flag="all"):
        """Изменить режим логирования"""
        mods = ["i", "a", "w", "e", "all"]
        if flag in mods:
            self._log("Произведена смена режима логирования", "i")
            self.mod = flag
            return True
        else:
            self._log("Неправильно указан флаг режима!", "e")
            return False

    def clear_logs(self):
        filename = self.username+".log"
        password =  self.password
        self._log("Успешно очищен файл логов", "a")
        with open(filename, "w")as file:
            file.write(f"===ArtLogs===\nname={self.username},\npassword={password},\n===ArtLogs===\n")
        return True


class ArtLogs:
    """Менеджер для работы с несколькими профилями"""

    def __init__(self):
        self.profiles = []

    def create_profile(self, name="user", password=""):
        """Создать новый профиль"""
        profile = ArtLogProfile(manager=self)
        result = profile.logUser(name, password, "c")
        if result and isinstance(result, ArtLogProfile):
            self.profiles.append(result)
        return result

    def login_profile(self, name="user", password=""):
        """Авторизовать существующий профиль"""
        profile = ArtLogProfile(manager=self)
        result = profile.logUser(name, password, "i")
        if result and isinstance(result, ArtLogProfile):
            self.profiles.append(result)
        return result

    def logUser(self, name="user", password="", flag="c"):
        """Совместимый метод"""
        if flag == "c":
            return self.create_profile(name, password)
        elif flag == "i":
            return self.login_profile(name, password)