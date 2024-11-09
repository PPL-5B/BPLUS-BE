import enum

class TaskStatus(enum.Enum):
    DONE = "DONE"
    TODO = "TODO"

    @classmethod
    def choices(cls):
        return [(key.value, key.value) for key in cls]


class TaskType(enum.Enum):
    POND_QUALITY = "POND_QUALITY"
    FISH_SAMPLING = "FISH_SAMPLING"
    FOOD_SAMPLING = "FOOD_SAMPLING"

    @classmethod
    def choices(cls):
        return [(key.value, key.value) for key in cls]

