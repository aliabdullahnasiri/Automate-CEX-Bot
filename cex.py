import json
import re
import time
from typing import Literal

import requests

from functions import json_decode_error_handler, fragment2dct, send_email


class CEX(requests.Session):

    def __init__(self):
        # initialize the super class
        super().__init__()

        # get auth data from file
        with open(".cex-auth-data.txt", "rt") as f:
            self.auth_data_lst = [line.strip() for line in f.readlines()]

    def get_user_info(self, auth_data: str) -> dict:
        fragment = fragment2dct(auth_data)
        user = fragment.get("user", {})
        user_id = user.get("id")

        data = {
            "devAuthData": user_id,
            "authData": auth_data,
            "data": {},
            "platform": "android",
        }

        response = self.post(
            "https://cexp.cex.io/api/getUserInfo",
            data=json.dumps(data),
            headers={
                "Content-Type": "application/json",
            },
        )

        print(
            f"In `get_user_info` the post request status code was {response.status_code}."
        )
        return response.json() if response.status_code == 200 else {}

    def get_users_info(self):
        outputs = []
        for auth_data in self.auth_data_lst:
            user_info: dict = self.get_user_info(auth_data)

            outputs.append(user_info)

        return outputs

    def get_user_telegram_id(self, auth_data: str) -> int:
        user_info = self.get_user_info(auth_data)
        user_data = user_info.get("data", {})

        user_telegram_id = user_data.get("userTelegramId")

        return user_telegram_id

    def claim_taps(self):
        outputs = []
        for auth_data in self.auth_data_lst:
            user_info = self.get_user_info(auth_data)
            user_data = user_info.get("data", {})
            available_taps = user_data.get("availableTaps")

            if not available_taps:
                outputs.append("No enough taps available, please invite more friends.")
                continue

            data = {
                "devAuthData": self.get_user_telegram_id(auth_data),
                "authData": auth_data,
                "data": {"taps": available_taps},
            }

            response = self.post(
                "https://cexp.cex.io/api/claimTaps",
                data=json.dumps(data),
                headers={"Content-Type": "application/json"},
            )

            if response.status_code == 200:
                outputs.append(response.json())

        def mapper(output):
            if isinstance(output, dict):
                return {
                    "balance": output.get("data", {}).get("balance"),
                    "first_name": output.get("data", {}).get("first_name"),
                    "last_name": output.get("data", {}).get("last_name"),
                    "userTelegramId": output.get("data", {}).get("userTelegramId"),
                }
            else:
                return output

        outputs = list(map(mapper, outputs))

        return outputs

    def start_farming(self):
        outputs = []
        for auth_data in self.auth_data_lst:

            user_info = self.get_user_info(auth_data)
            user_data = user_info.get("data", {})

            if (
                user_data.get("farmStartedAt")
                and not user_data.get("farmReward", "") == "0.0"
            ):
                outputs.append(f"Farm is already started.")
                continue

            data = {
                "devAuthData": self.get_user_telegram_id(auth_data),
                "authData": auth_data,
                "data": {},
            }

            response = self.post(
                "https://cexp.cex.io/api/startFarm",
                data=json.dumps(data),
                headers={"Content-Type": "application/json"},
            )

            if response.status_code == 200:
                outputs.append(response.json())

        # return outputs
        return outputs

    def claim_farming(self):
        outputs = []
        for auth_data in self.auth_data_lst:
            user_info = self.get_user_info(auth_data)
            user_data = user_info.get("data", {})
            # farm_started_at = user_data.get("farmStartedAt")
            farm_reward = user_data.get("farmReward")
            min_random_farm_reward = user_data.get("minRandomFarmReward", 400)
            max_random_farm_reward = user_data.get("maxRandomFarmReward", 800)

            if min_random_farm_reward < float(farm_reward) < max_random_farm_reward:
                data = {
                    "devAuthData": self.get_user_telegram_id(auth_data),
                    "authData": auth_data,
                    "data": {},
                }

                response = self.post(
                    "https://cexp.cex.io/api/claimFarm",
                    data=json.dumps(data),
                    headers={
                        "Content-Type": "application/json",
                    },
                )

                if response.status_code == 200:
                    outputs.append(response.json())
            else:
                outputs.append(
                    {
                        "status": "error",
                        "msg": f"Not enough farm reward: {farm_reward}",
                    }
                )

        return outputs

    def get_tasks(
        self,
        auth_data: str,
        state: Literal["NONE", "ReadyToCheck", "ReadyToClaim", "Claimed"] = "NONE",
    ):
        user_info = self.get_user_info(auth_data)
        user_data = user_info.get("data", {})
        tasks = user_data.get("tasks", [])

        return {
            key: value for key, value in tasks.items() if value.get("state") == state
        }

    def start_tasks(self):
        outputs = []
        for auth_data in self.auth_data_lst:
            tasks = self.get_tasks(auth_data)

            for id in tasks.keys():

                if "invite" in id:
                    continue

                data = {
                    "devAuthData": self.get_user_telegram_id(auth_data),
                    "authData": auth_data,
                    "data": {"taskId": id},
                }

                response = self.post(
                    "https://cexp.cex.io/api/startTask",
                    data=json.dumps(data),
                    headers={
                        "Content-Type": "application/json",
                    },
                )

                if response.status_code == 200:
                    result = response.json()
                    outputs.append(result)

        return outputs

    def check_tasks(self):
        outputs = []
        for auth_data in self.auth_data_lst:
            tasks = self.get_tasks(auth_data, "ReadyToCheck")

            for id in tasks.keys():
                data = {
                    "devAuthData": self.get_user_telegram_id(auth_data),
                    "authData": auth_data,
                    "data": {"taskId": id},
                }

                response = self.post(
                    "https://cexp.cex.io/api/checkTask",
                    data=json.dumps(data),
                    headers={
                        "Content-Type": "application/json",
                    },
                )

                if response.status_code == 200:
                    outputs.append(response.json())

        return outputs

    def claim_tasks(self):
        outputs = []
        for auth_data in self.auth_data_lst:
            tasks = self.get_tasks(auth_data, "ReadyToClaim")

            for id in tasks.keys():
                data = {
                    "devAuthData": self.get_user_telegram_id(auth_data),
                    "authData": auth_data,
                    "data": {"taskId": id},
                }

                response = self.post(
                    "https://cexp.cex.io/api/claimTask",
                    data=json.dumps(data),
                    headers={
                        "Content-Type": "application/json",
                    },
                )

                if response.status_code == 200:
                    outputs.append(response.json())

        return outputs


def main():
    cex = CEX()

    print("Claim Taps...")
    cex.claim_taps()

    print("Start farming...")
    cex.start_farming()

    print("Claim farming...")
    cex.claim_farming()

    print("Start farming...")
    cex.start_farming()

    print("Start tasks...")
    cex.start_tasks()

    print("Check tasks...")
    cex.check_tasks()

    print("Claim tasks...")
    cex.claim_tasks()

    print("Getting users information...")
    users_info = cex.get_users_info()

    string = ""
    for user_info in users_info:
        user_data = user_info.get("data", {})

        user_data.pop("tasks")
        user_data.pop("inviteUrl")
        user_data.pop("shareDetails")

        string += "\n".join([f"{key}: {value}" for key, value in user_data.items()])
        string += "\n\n\n"

    send_email("CEX.IO Power Tap", string)


if __name__ == "__main__":
    main()
