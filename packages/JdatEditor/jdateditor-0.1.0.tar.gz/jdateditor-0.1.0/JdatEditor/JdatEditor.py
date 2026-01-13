# JdatEditor.py

class ActionContext:
    def __init__(self, path):
        self.path = path
        self.action_type = None

    def __enter__(self):
        print(f"[JDAT] Ouverture du fichier : {self.path}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"[JDAT] Fermeture du fichier : {self.path}")

    def __call__(self, action):
        if action not in ('read', 'edit'):
            raise ValueError(f"Action '{action}' non supportée ! Utilisez 'read' ou 'edit'.")
        self.action_type = action
        print(f"[JDAT] Action choisie : {self.action_type}")
        return self  # permet éventuellement le chaînage si besoin

# Fonction principale exposée
def action(path):
    return ActionContext(path)
