# JdatEditor.py

import os
import re

class JDATBlock:
    def __init__(self, meta, data):
        self.meta = meta
        self.data = data

    def display(self):
        """Affiche le bloc comme dans le shell"""
        print("Bloc JDAT")
        for k,v in self.meta.items():
            print(f"  {k} : {v}")
        for k,v in self.data.items():
            print(f"   - {k} : {v}")
        print()

class ActionContext:
    def __init__(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Fichier JDAT introuvable : {path}")
        self.path = path
        self.blocks = []
        self.action_type = None

    def __enter__(self):
        print(f"[JDAT] Ouverture du fichier : {self.path}")
        self.load()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.action_type == 'edit':
            self.save()
        print(f"[JDAT] Fermeture du fichier : {self.path}")

    def __call__(self, action):
        if action not in ('read', 'edit'):
            raise ValueError(f"Action '{action}' non supportée ! Utilisez 'read' ou 'edit'.")
        self.action_type = action
        print(f"[JDAT] Action choisie : {self.action_type}")
        return self

    def load(self):
        """Lecture des blocs JDAT"""
        self.blocks = []
        with open(self.path, "r", encoding="utf-8") as f:
            content = f.read()

        pattern = r"\(\s*(n:[^\s]+.*)?\{(.*?)\}\s*\)"
        matches = re.findall(pattern, content, re.DOTALL)
        for meta_str, data_str in matches:
            meta = {}
            if meta_str:
                for part in meta_str.strip().split():
                    if ':' in part:
                        k,v = part.split(':',1)
                        m
