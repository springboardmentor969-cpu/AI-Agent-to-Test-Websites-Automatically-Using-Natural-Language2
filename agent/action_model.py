class ActionModel:

    def __init__(self, action, target=None, value=None):
        self.action = action
        self.target = target
        self.value = value

    def to_dict(self):
        return {
            "action": self.action,
            "target": self.target,
            "value": self.value
        }
