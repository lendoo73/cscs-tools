class Version:
    def __init__(self, version_dict):
        self.major = int(version_dict["major"])
        self.minor = int(version_dict["minor"])
        self.patch = int(version_dict["patch"])
        self.inherit = bool(version_dict["inherit"])

    def set(self, type, value):
        value = int(value)
        if type in ["M", "Major", "major"]:
            self.major = value
        if type in ["m", "minor"]:
            self.minor = value
        if type in ["p", "patch"]:
            self.patch = value
        if type in ["i", "inherit"]:
            self.inherit = bool(int(value))

    def increase(self, type):
        if type in ["M", "Major", "major"]:
            self.major += 1
        if type in ["m", "minor"]:
            self.minor += 1
        if type in ["p", "patch"]:
            self.patch += 1
        if type in ["i", "inherit"]:
            self.inherit = not self.inherit

    def str_repr(self):
        return f"{self.major}.{self.minor}.{self.patch} inherit: {self.inherit}"
