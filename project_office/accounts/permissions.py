from accounts.models import Profile


def get_user_role(user):
    if not user.is_authenticated:
        return None

    if not hasattr(user, "profile"):
        return None

    return user.profile.role


def is_admin(user):
    return (
        user.is_authenticated
        and (
            user.is_superuser
            or get_user_role(user) == Profile.Role.ADMIN
        )
    )


def is_project_manager(user):
    return (
        user.is_authenticated
        and get_user_role(user) == Profile.Role.PROJECT_MANAGER
    )


def is_implementer(user):
    return (
        user.is_authenticated
        and get_user_role(user) == Profile.Role.IMPLEMENTER
    )


def is_engineer(user):
    return (
        user.is_authenticated
        and get_user_role(user) == Profile.Role.ENGINEER
    )


def is_guest(user):
    return (
        user.is_authenticated
        and get_user_role(user) == Profile.Role.GUEST
    )


def can_edit_project(user, project):
    if is_admin(user):
        return True

    if is_project_manager(user) and project.manager_id == user.id:
        return True

    return False


def can_manage_project_contacts(user, project):
    if is_admin(user):
        return True

    if is_project_manager(user) and project.manager_id == user.id:
        return True

    return False


def can_manage_project_equipment(user, project):
    if is_admin(user):
        return True

    if is_project_manager(user) and project.manager_id == user.id:
        return True

    if is_implementer(user):
        return True

    if is_engineer(user):
        return True

    return False


def can_manage_project_software(user, project):
    if is_admin(user):
        return True

    if is_project_manager(user) and project.manager_id == user.id:
        return True

    if is_implementer(user):
        return True

    return False


def can_manage_project_documents(user, project):
    if is_admin(user):
        return True

    if is_project_manager(user) and project.manager_id == user.id:
        return True

    return False

def can_access_production(user):
    if is_admin(user):
        return True

    if is_engineer(user):
        return True

    return False

def can_create_project(user):
    if is_admin(user):
        return True

    if is_project_manager(user):
        return True

    return False

def can_manage_users(user):
    return is_admin(user)

def can_manage_dictionaries(user):
    return is_admin(user)