from apps.accounts.models import Role


class RoleSelector:

    @staticmethod
    def list_roles():
        return Role.objects.all()

    @staticmethod
    def get_role(role_id):
        return Role.objects.filter(id=role_id).first()

    @staticmethod
    def get_role_by_name(name):
        return Role.objects.filter(name=name).first()