from .constants import ATARI_SCORES


def refine_environment_name(environment_name: str):
    if environment_name.startswith("ALE/"):
        return environment_name[4:]

    return environment_name


def check_environment_statistics(environment_name: str):
    if environment_name not in ATARI_SCORES:
        raise RuntimeError(
            f"We couldn't find the statistics regarding atari environment {environment_name}."
        )


def get_human_score(environment_name: str) -> float:
    environment_name = refine_environment_name(environment_name)
    check_environment_statistics(environment_name)
    return ATARI_SCORES.get(environment_name)[1]


def get_random_score(environment_name: str) -> float:
    environment_name = refine_environment_name(environment_name)
    check_environment_statistics(environment_name)
    return ATARI_SCORES.get(environment_name)[0]


def calculate_hns(environment_name: str, agent_score: float) -> float:
    human_score = get_human_score(environment_name)
    random_score = get_random_score(environment_name)
    return (agent_score - random_score) / (human_score - random_score)
