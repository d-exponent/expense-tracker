# TODO: Undo in production
def dev_error_tracer(message):
    """
    Prints verbose messages
    Will be made into a stupid function in production
    """
    print(f"🧰🧰🧰🧰🧰 {message}\n")


class UserErrorMessages:
    already_exists = "This user already exists."
    does_not_exist = "The user does not exist."
    no_users = "There are no users"
