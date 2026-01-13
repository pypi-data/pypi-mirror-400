class ForgejoRouter:
    def db_for_read(self, model, **hints):
        """
        Attempts to read auth and contenttypes models go to auth_db.
        """
        if model._meta.app_label == __package__:
            return __package__
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == __package__:
            return __package__
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == __package__:
            return False
        return None
