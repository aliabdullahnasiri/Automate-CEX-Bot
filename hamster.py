import requests

from functions import json_decode_error_handler, round_num, send_email


class Hamster(requests.Session):

    def __init__(self, token: str) -> None:
        super().__init__()
        self.token = token

    @json_decode_error_handler
    def get_user_info(self) -> dict:
        # get user information
        response: requests.Response = self.post(
            "https://api.hamsterkombat.io/auth/me-telegram",
            headers={
                "Authorization": f"Bearer {self.token}",
            },
        )

        return response.json()

    @json_decode_error_handler
    def get_telegram_user_info(self) -> dict:
        user_info = self.get_user_info()

        # get telegram user information from user info
        telegram_user = user_info.get("telegramUser", {})

        return telegram_user

    @json_decode_error_handler
    def collect_passive_earn(self) -> dict:

        response: requests.Response = self.post(
            "https://api.hamsterkombat.io/clicker/sync",
            headers={
                "Authorization": f"Bearer {self.token}",
            },
        )

        data = response.json()
        clickser_user = data.get("clickerUser")
        last_passive_earn = clickser_user.get("lastPassiveEarn")
        balance_coins = clickser_user.get("balanceCoins")

        telegram_user_info = self.get_telegram_user_info()

        return {
            "lastPassiveEarn": round_num(int(last_passive_earn)),
            "balanceCoins": round_num(int(balance_coins)),
            **telegram_user_info,
        }


def hamster():
    with open(".hamster-tokens.txt", "rt", encoding="UTF-8") as f:
        tokens = [line.strip() for line in f.readlines()]

        for token in tokens:
            hamster = Hamster(token)
            data = hamster.collect_passive_earn()

            string = ""
            for key, value in data.items():
                string += f"{key}: {value}\n"

            string += "\n\n\n"

            send_email(f"Collect Passive Earn", string)


if __name__ == "__main__":
    hamster()
