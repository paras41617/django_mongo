from .models import user_collection

def generate_unique_username(email):
    # Function to generate a unique username based on the email
    username = email.split("@")[0]
    return username

def validate_credentials(username, password):
    # Query MongoDB to find a user with the provided username
    user = user_collection.find_one({"username": username})

    if user:
        # Check if the provided password matches the stored password
        if user.get("password") == password:
            return True  # Credentials are valid
    return False  # Credentials are invalid
