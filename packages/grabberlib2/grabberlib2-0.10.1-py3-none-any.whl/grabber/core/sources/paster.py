import sys

import requests


def retrieve_paster_contents(paster_ids: list[str]) -> list[str]:
    contents: list[str] = []

    for paste_id in paster_ids:
        try:
            response = requests.get(
                f"https://paster.so/api/v3/pastes/markdown/{paste_id}",
                headers={"Content-Type": "application/json"},
            )
            response_data: dict[str, dict[str, str]] = response.json()

            if "data" in response_data and "content" in response_data["data"]:
                content: str = response_data["data"]["content"].replace("\n", "")
                contents.append(content)
            else:
                print("Response did not contain a URL:", response_data)
        except requests.exceptions.RequestException as e:
            print("Error making the request:", e)
    return contents


def main():
    args = sys.argv[1:]
    contents = retrieve_paster_contents(args)
    for content in contents:
        print(f"Content: {content}\n\n")


if __name__ == "__main__":
    main()
