import logging

import pandas as pd
import pingouin as pg

SCORES = {
    "PHY1": {
        "domain": "Physical Functioning",
        "text": "It is hard for me to walk more than one block",
    },
    "PHY2": {
        "domain": "Physical Functioning",
        "text": "It is hard for me to run",
    },
    "PHY3": {
        "domain": "Physical Functioning",
        "text": "It is hard for me to do sports activity or exercise",
    },
    "PHY4": {
        "domain": "Physical Functioning",
        "text": "It is hard for me to lift something heavy",
    },
    "PHY5": {
        "domain": "Physical Functioning",
        "text": "It is hard for me to take a bath or shower by myself",
    },
    "PHY6": {
        "domain": "Physical Functioning",
        "text": "It is hard for me to do chores around the house",
    },
    "PHY7": {
        "domain": "Physical Functioning",
        "text": "I hurt or ache",
    },
    "PHY8": {
        "domain": "Physical Functioning",
        "text": "I have low energy",
    },
    "EMO1": {
        "domain": "Emotional Functioning",
        "text": "I feel afraid or scared",
    },
    "EMO2": {
        "domain": "Emotional Functioning",
        "text": "I feel sad or blue",
    },
    "EMO3": {
        "domain": "Emotional Functioning",
        "text": "I feel angry",
    },
    "EMO4": {
        "domain": "Emotional Functioning",
        "text": "I have trouble sleeping",
    },
    "EMO5": {
        "domain": "Emotional Functioning",
        "text": "I worry about what will happen to me",
    },
    "SOC1": {
        "domain": "Social Functioning",
        "text": "I have trouble getting along with other kids",
    },
    "SOC2": {
        "domain": "Social Functioning",
        "text": "Other kids do not want to be my friend",
    },
    "SOC3": {
        "domain": "Social Functioning",
        "text": "Other kids tease me",
    },
    "SOC4": {
        "domain": "Social Functioning",
        "text": "I cannot do things that other kids my age can do",
    },
    "SOC5": {
        "domain": "Social Functioning",
        "text": "It is hard to keep up when I play with other kids",
    },
    "SCH1": {
        "domain": "School Functioning",
        "text": "It is hard to pay attention in class",
    },
    "SCH2": {
        "domain": "School Functioning",
        "text": "I forget things",
    },
    "SCH3": {
        "domain": "School Functioning",
        "text": "I have trouble keeping up with my schoolwork",
    },
    "SCH4": {
        "domain": "School Functioning",
        "text": "I miss school because of not feeling well",
    },
    "SCH5": {
        "domain": "School Functioning",
        "text": "I miss school to go to the doctor or hospital",
    },
}

NORMALIZED_SCORES = {
    "Never": 100,
    "Almost never": 75,
    "Sometimes": 50,
    "Often": 25,
    "Almost always": 0,
}

DOMAINS = [
    "Physical Functioning",
    "Emotional Functioning",
    "Social Functioning",
    "School Functioning",
]


logger = logging.getLogger(__name__)


def get_domain_questions(domain):
    return {key: value for key, value in SCORES.items() if value["domain"] == domain}


def get_question_scores(answers, questions):
    scores = {}

    for id in questions.keys():
        answer = answers.get(id, None)

        if answer:
            score = NORMALIZED_SCORES[answer]
        else:
            score = None

        scores[id] = score

    return scores


def get_domain_scores(answers, domain):
    questions = get_domain_questions(domain)
    n_questions = len(questions)
    min_questions = n_questions / 2

    scores = get_question_scores(answers, questions)
    n_scores = sum(x is not None for x in scores.values())

    if n_scores < min_questions:
        scores[domain] = None
        logger.warning(
            f"Domain '{domain}' score cannot be calculated, not enough questions answered."
        )
    else:
        score_sum = sum(x for x in scores.values() if x is not None)
        scores[domain] = score_sum / n_scores

        if n_scores == n_questions:
            logger.info(
                f"Domain '{domain}' score calculated with all questions answered."
            )
        else:
            missing_question = next(
                (key for key, value in scores.items() if value is None), None
            )
            logger.warning(
                f"Domain '{domain}' score calculated with one question missing: '{missing_question}'."
            )

    return scores


def get_score(answers):
    scores = {}

    for domain in DOMAINS:
        domain_scores = get_domain_scores(answers, domain)
        scores.update(domain_scores)

    emo = scores["Emotional Functioning"]
    soc = scores["Social Functioning"]
    sch = scores["School Functioning"]
    phy = scores["Physical Functioning"]

    if emo is not None and soc is not None and sch is not None:
        scores["Psychosocial Health"] = emo + soc + sch

    if phy is not None:
        scores["Physical Health"] = phy

    if emo is not None and soc is not None and sch is not None and phy is not None:
        scores["Total Score"] = emo + soc + sch + phy

    return scores


def get_scores(df: pd.DataFrame) -> pd.DataFrame:
    scored = {}
    index_name = df.index.name

    for index, answers in df.to_dict(orient="index").items():
        scores = get_score(answers)
        scored[index] = scores

    df = pd.DataFrame.from_dict(scored, orient="index")
    df.index.name = index_name
    df = df.apply(pd.to_numeric, errors="coerce", downcast="unsigned")

    return df.round(3)


def get_alphas(df: pd.DataFrame) -> pd.DataFrame:
    alphas = {}

    for domain in DOMAINS:
        alpha, ci = None, (None, None)
        questions = list(get_domain_questions(domain).keys())
        temp = df[questions]

        questions = temp.isnull().all(axis=0)
        empty = questions[questions].index.tolist()

        if empty:
            n_empty = len(empty)
            if n_empty == 1:
                logger.warning(
                    f"Domain '{domain}' has empty questions {empty}, removing them and calculating cronbach alpha."
                )
                temp = temp.drop(columns=empty)

                alpha, ci = pg.cronbach_alpha(temp)
            else:
                logger.warning(
                    f"Domain '{domain}' has multiple empty questions {empty}, cronbach alpha cannot be calculated."
                )
        else:
            alpha, ci = pg.cronbach_alpha(temp)
            logger.info(
                f"Domain '{domain}' has all questions answered, cronbach alpha calculated."
            )

        alphas[domain] = {"alpha": alpha, "ci_low": ci[0], "ci_high": ci[1]}

    df = pd.DataFrame.from_dict(alphas, orient="index")
    df.index.name = "Domain"
    df = df.apply(pd.to_numeric, errors="coerce", downcast="unsigned").round(4)

    return df


def questions() -> list[str]:
    return list(SCORES.keys())


def domains() -> list[str]:
    return DOMAINS
