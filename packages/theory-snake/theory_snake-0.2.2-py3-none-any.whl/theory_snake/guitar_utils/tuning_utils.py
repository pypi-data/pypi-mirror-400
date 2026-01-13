from ..consts import COMMON_TUNNINGS,Notes

def select_tuning(tuning:str='Standard'):
    if tuning not in COMMON_TUNNINGS:
        try:
            if "," in tuning:
                tuning_list = tuning.split(",")
            else:
                tuning_list = tuning.split(" ")
            for note in tuning_list:
                if note not in Notes:
                    raise ValueError("Invalid note in custom tuning")
            return tuning_list
        except Exception as e:
            raise ValueError("Invalid tuning format") from e
    else:
        return COMMON_TUNNINGS[tuning]


