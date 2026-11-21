import ctypes
import time

user32 = ctypes.windll.user32

VK_LWIN = 0x5B
VK_CONTROL = 0x11
VK_LEFT = 0x25
VK_RIGHT = 0x27
VK_D = 0x44

KEYUP = 0x0002


def press(vk):
    user32.keybd_event(vk, 0, 0, 0)


def release(vk):
    user32.keybd_event(vk, 0, KEYUP, 0)


def shortcut(key):
    press(VK_LWIN)
    press(VK_CONTROL)
    press(key)

    time.sleep(0.15)

    release(key)
    release(VK_CONTROL)
    release(VK_LWIN)


if __name__ == "__main__":
    print("1 — Следующий рабочий стол")
    print("2 — Предыдущий рабочий стол")
    print("3 — Создать рабочий стол")

    choice = input("Выбор: ")

    if choice == "1":
        shortcut(VK_RIGHT)
    elif choice == "2":
        shortcut(VK_LEFT)
    elif choice == "3":
        shortcut(VK_D)
    else:
        print("Неверный выбор")
