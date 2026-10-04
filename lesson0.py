import requests
BASE_URL = "https://jsonplaceholder.typicode.com/users/"

class UserNotFoundError(Exception):
    pass

class APIError(Exception):
    pass

def fetch_user(url: str, user_id: int) -> dict:
    try:
        response = requests.get(f"{url.rstrip('/')}/{user_id}", timeout=3)

        if response.status_code == 404:
            raise UserNotFoundError(f"User {user_id} was not found.")

        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise APIError(f"Failed to fetch user {user_id}: {e}") from e


def clean_string(value):
    if isinstance(value, str):
        value = value.strip()

        if value:
            return value
    return None

def transform_user(raw_user: dict) -> dict:

    # Email must require to identify a usable user
    email = clean_string(raw_user.get('email'))
    if not email:
        raise ValueError("User is missing the email address")
    
    address = raw_user.get('address') or {}
    company = raw_user.get('company') or {}

    user = {}

    user['name'] = clean_string(raw_user.get('name'))
    user['email'] = email.lower()
    user['city'] = clean_string(address.get('city'))
    user['company'] = clean_string(company.get('name'))

    return user


if __name__ == "__main__":
    try:
        print(transform_user({"email": "a@b.com", "address": "Dhaka"}))
    except UserNotFoundError:
        print("User not found. Please check the user ID.")
    except APIError:
        print("API is unavailable. Please try again late.")
    except ValueError as e:
        print(f"Invalid user data: {e}")
