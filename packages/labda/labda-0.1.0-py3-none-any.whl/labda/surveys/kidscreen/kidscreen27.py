import logging

import pandas as pd
import pingouin as pg

logger = logging.getLogger(__name__)

SCORES = {
    "KY27PHY1": {
        "domain": "PHY",
        "text": "In general, how would you say your health is?",
        "answers": {"excellent": 3, "very good": 2, "good": 2, "fair": 1, "poor": 1},
        "r": {
            4: -3.986,
            5: -2.752,
            6: -2.145,
            7: -1.722,
            8: -1.377,
            9: -1.07,
            10: -0.778,
            11: -0.487,
            12: -0.187,
            13: 0.128,
            14: 0.463,
            15: 0.824,
            16: 1.221,
            17: 1.671,
            18: 2.21,
            19: 2.926,
            20: 4.232,
        },
    },
    "KY27PHY2": {
        "domain": "PHY",
        "text": "Have you felt fit and well?",
        "answers": {
            "not at all": 1,
            "slightly": 2,
            "moderately": 3,
            "very": 4,
            "extremely": 5,
        },
        "r": {
            4: -4.128,
            5: -2.794,
            6: -2.081,
            7: -1.581,
            8: -1.178,
            9: -0.815,
            10: -0.46,
            11: -0.096,
            12: 0.289,
            13: 0.703,
            14: 1.157,
            15: 1.671,
            16: 2.281,
            17: 3.068,
            18: 4.426,
        },
    },
    "KY27PHY3": {
        "domain": "PHY",
        "text": "Have you been physically active (e.g. running, climbing, biking)?",
        "answers": {
            "not at all": 1,
            "slightly": 2,
            "moderately": 3,
            "very": 4,
            "extremely": 5,
        },
        "r": {
            4: -4.195,
            5: -2.916,
            6: -2.254,
            7: -1.783,
            8: -1.396,
            9: -1.044,
            10: -0.694,
            11: -0.319,
            12: 0.101,
            13: 0.575,
            14: 1.102,
            15: 1.681,
            16: 2.331,
            17: 3.128,
            18: 4.478,
        },
    },
    "KY27PHY4": {
        "domain": "PHY",
        "text": "Have you been able to run well?",
        "answers": {
            "not at all": 1,
            "slightly": 2,
            "moderately": 3,
            "very": 4,
            "extremely": 5,
        },
        "r": {
            4: -4.209,
            5: -2.919,
            6: -2.23,
            7: -1.72,
            8: -1.286,
            9: -0.884,
            10: -0.491,
            11: -0.094,
            12: 0.318,
            13: 0.756,
            14: 1.235,
            15: 1.77,
            16: 2.387,
            17: 3.162,
            18: 4.5,
        },
    },
    "KY27PHY5": {
        "domain": "PHY",
        "text": "Have you felt full of energy?",
        "answers": {
            "never": 1,
            "seldom": 2,
            "quite often": 3,
            "very often": 4,
            "always": 5,
        },
        "r": {
            4: -3.779,
            5: -2.564,
            6: -1.967,
            7: -1.54,
            8: -1.182,
            9: -0.849,
            10: -0.518,
            11: -0.171,
            12: 0.2,
            13: 0.604,
            14: 1.047,
            15: 1.545,
            16: 2.134,
            17: 2.903,
            18: 4.261,
        },
    },
    "KY27PWB1": {
        "domain": "PWB",
        "text": "Has your life been enjoyable?",
        "answers": {
            "not at all": 1,
            "slightly": 2,
            "moderately": 3,
            "very": 4,
            "extremely": 5,
        },
        "r": {
            6: -4.399,
            7: -3.201,
            8: -2.597,
            9: -2.171,
            10: -1.835,
            11: -1.552,
            12: -1.303,
            13: -1.079,
            14: -0.871,
            15: -0.675,
            16: -0.486,
            17: -0.3,
            18: -0.114,
            19: 0.075,
            20: 0.271,
            21: 0.478,
            22: 0.7,
            23: 0.943,
            24: 1.214,
            25: 1.521,
            26: 1.876,
            27: 2.295,
            28: 2.808,
            29: 3.499,
            30: 4.774,
        },
    },
    "KY27PWB2": {
        "domain": "PWB",
        "text": "Have you been in a good mood?",
        "answers": {
            "never": 1,
            "seldom": 2,
            "quite often": 3,
            "very often": 4,
            "always": 5,
        },
        "r": {
            6: -4.154,
            7: -2.99,
            8: -2.418,
            9: -2.024,
            10: -1.715,
            11: -1.457,
            12: -1.23,
            13: -1.024,
            14: -0.832,
            15: -0.649,
            16: -0.472,
            17: -0.296,
            18: -0.119,
            19: 0.061,
            20: 0.249,
            21: 0.447,
            22: 0.659,
            23: 0.891,
            24: 1.147,
            25: 1.435,
            26: 1.766,
            27: 2.156,
            28: 2.635,
            29: 3.291,
            30: 4.532,
        },
    },
    "KY27PWB3": {
        "domain": "PWB",
        "text": "Have you had fun?",
        "answers": {
            "never": 1,
            "seldom": 2,
            "quite often": 3,
            "very often": 4,
            "always": 5,
        },
        "r": {
            6: -4.272,
            7: -3.08,
            8: -2.489,
            9: -2.08,
            10: -1.76,
            11: -1.494,
            12: -1.261,
            13: -1.049,
            14: -0.853,
            15: -0.666,
            16: -0.484,
            17: -0.304,
            18: -0.123,
            19: 0.063,
            20: 0.256,
            21: 0.461,
            22: 0.681,
            23: 0.922,
            24: 1.19,
            25: 1.494,
            26: 1.844,
            27: 2.259,
            28: 2.769,
            29: 3.46,
            30: 4.739,
        },
    },
    "KY27PWB4": {
        "domain": "PWB",
        "text": "Have you felt sad?",
        "answers": {
            "never": 5,
            "seldom": 4,
            "quite often": 3,
            "very often": 2,
            "always": 1,
        },
        "r": {
            6: -4.293,
            7: -3.092,
            8: -2.492,
            9: -2.075,
            10: -1.751,
            11: -1.48,
            12: -1.244,
            13: -1.031,
            14: -0.833,
            15: -0.645,
            16: -0.463,
            17: -0.283,
            18: -0.102,
            19: 0.082,
            20: 0.274,
            21: 0.476,
            22: 0.692,
            23: 0.927,
            24: 1.188,
            25: 1.483,
            26: 1.821,
            27: 2.221,
            28: 2.717,
            29: 3.396,
            30: 4.67,
        },
    },
    "KY27PWB5": {
        "domain": "PWB",
        "text": "Have you felt so bad that you didn't want to do anything?",
        "answers": {
            "never": 5,
            "seldom": 4,
            "quite often": 3,
            "very often": 2,
            "always": 1,
        },
        "r": {
            6: -4.346,
            7: -3.143,
            8: -2.536,
            9: -2.111,
            10: -1.777,
            11: -1.498,
            12: -1.253,
            13: -1.031,
            14: -0.826,
            15: -0.63,
            16: -0.44,
            17: -0.252,
            18: -0.063,
            19: 0.13,
            20: 0.332,
            21: 0.547,
            22: 0.777,
            23: 1.03,
            24: 1.311,
            25: 1.626,
            26: 1.984,
            27: 2.4,
            28: 2.903,
            29: 3.579,
            30: 4.838,
        },
    },
    "KY27PWB6": {
        "domain": "PWB",
        "text": "Have you felt lonely?",
        "answers": {
            "never": 5,
            "seldom": 4,
            "quite often": 3,
            "very often": 2,
            "always": 1,
        },
        "r": {
            6: -4.4,
            7: -3.206,
            8: -2.606,
            9: -2.187,
            10: -1.856,
            11: -1.577,
            12: -1.332,
            13: -1.109,
            14: -0.899,
            15: -0.699,
            16: -0.503,
            17: -0.307,
            18: -0.11,
            19: 0.094,
            20: 0.306,
            21: 0.529,
            22: 0.769,
            23: 1.03,
            24: 1.316,
            25: 1.635,
            26: 1.995,
            27: 2.41,
            28: 2.912,
            29: 3.586,
            30: 4.844,
        },
    },
    "KY27PWB7": {
        "domain": "PWB",
        "text": "Have you been happy with the way you are?",
        "answers": {
            "never": 1,
            "seldom": 2,
            "quite often": 3,
            "very often": 4,
            "always": 5,
        },
        "r": {
            6: -4.367,
            7: -3.172,
            8: -2.573,
            9: -2.157,
            10: -1.831,
            11: -1.559,
            12: -1.321,
            13: -1.107,
            14: -0.907,
            15: -0.718,
            16: -0.535,
            17: -0.354,
            18: -0.173,
            19: 0.013,
            20: 0.206,
            21: 0.411,
            22: 0.633,
            23: 0.876,
            24: 1.149,
            25: 1.459,
            26: 1.818,
            27: 2.243,
            28: 2.763,
            29: 3.462,
            30: 4.745,
        },
    },
    "KY27PAR1": {
        "domain": "PAR",
        "text": "Have you had enough time for yourself?",
        "answers": {
            "never": 1,
            "seldom": 2,
            "quite often": 3,
            "very often": 4,
            "always": 5,
        },
        "r": {
            6: -3.852,
            7: -2.677,
            8: -2.097,
            9: -1.697,
            10: -1.387,
            11: -1.131,
            12: -0.911,
            13: -0.717,
            14: -0.542,
            15: -0.38,
            16: -0.228,
            17: -0.083,
            18: 0.058,
            19: 0.197,
            20: 0.336,
            21: 0.478,
            22: 0.625,
            23: 0.781,
            24: 0.951,
            25: 1.141,
            26: 1.362,
            27: 1.632,
            28: 1.987,
            29: 2.521,
            30: 3.651,
        },
    },
    "KY27PAR2": {
        "domain": "PAR",
        "text": "Have you been able to do the things that you want to do in your free time?",
        "answers": {
            "never": 1,
            "seldom": 2,
            "quite often": 3,
            "very often": 4,
            "always": 5,
        },
        "r": {
            6: -3.89,
            7: -2.697,
            8: -2.099,
            9: -1.683,
            10: -1.361,
            11: -1.096,
            12: -0.871,
            13: -0.673,
            14: -0.496,
            15: -0.332,
            16: -0.18,
            17: -0.034,
            18: 0.107,
            19: 0.247,
            20: 0.387,
            21: 0.53,
            22: 0.679,
            23: 0.837,
            24: 1.01,
            25: 1.204,
            26: 1.429,
            27: 1.706,
            28: 2.069,
            29: 2.611,
            30: 3.75,
        },
    },
    "KY27PAR3": {
        "domain": "PAR",
        "text": "Have your parent(s) had enough time for you?",
        "answers": {
            "never": 1,
            "seldom": 2,
            "quite often": 3,
            "very often": 4,
            "always": 5,
        },
        "r": {
            6: -3.907,
            7: -2.724,
            8: -2.134,
            9: -1.724,
            10: -1.404,
            11: -1.14,
            12: -0.913,
            13: -0.712,
            14: -0.53,
            15: -0.362,
            16: -0.204,
            17: -0.054,
            18: 0.091,
            19: 0.235,
            20: 0.379,
            21: 0.525,
            22: 0.677,
            23: 0.839,
            24: 1.015,
            25: 1.212,
            26: 1.441,
            27: 1.72,
            28: 2.086,
            29: 2.63,
            30: 3.77,
        },
    },
    "KY27PAR4": {
        "domain": "PAR",
        "text": "Have your parent(s) treated you fairly?",
        "answers": {
            "never": 1,
            "seldom": 2,
            "quite often": 3,
            "very often": 4,
            "always": 5,
        },
        "r": {
            6: -3.831,
            7: -2.665,
            8: -2.091,
            9: -1.696,
            10: -1.39,
            11: -1.137,
            12: -0.92,
            13: -0.727,
            14: -0.553,
            15: -0.392,
            16: -0.241,
            17: -0.096,
            18: 0.045,
            19: 0.183,
            20: 0.322,
            21: 0.463,
            22: 0.61,
            23: 0.766,
            24: 0.935,
            25: 1.124,
            26: 1.344,
            27: 1.613,
            28: 1.966,
            29: 2.496,
            30: 3.621,
        },
    },
    "KY27PAR5": {
        "domain": "PAR",
        "text": "Have you been able to talk to your parent(s) when you wanted to?",
        "answers": {
            "never": 1,
            "seldom": 2,
            "quite often": 3,
            "very often": 4,
            "always": 5,
        },
        "r": {
            6: -3.865,
            7: -2.692,
            8: -2.113,
            9: -1.713,
            10: -1.403,
            11: -1.147,
            12: -0.928,
            13: -0.733,
            14: -0.557,
            15: -0.395,
            16: -0.242,
            17: -0.096,
            18: 0.045,
            19: 0.184,
            20: 0.324,
            21: 0.466,
            22: 0.613,
            23: 0.769,
            24: 0.939,
            25: 1.128,
            26: 1.348,
            27: 1.615,
            28: 1.967,
            29: 2.495,
            30: 3.616,
        },
    },
    "KY27PAR6": {
        "domain": "PAR",
        "text": "Have you had enough money to do the same things as your friends?",
        "answers": {
            "never": 1,
            "seldom": 2,
            "quite often": 3,
            "very often": 4,
            "always": 5,
        },
        "r": {
            6: -3.984,
            7: -2.807,
            8: -2.221,
            9: -1.815,
            10: -1.497,
            11: -1.233,
            12: -1.006,
            13: -0.805,
            14: -0.622,
            15: -0.454,
            16: -0.295,
            17: -0.144,
            18: 0.003,
            19: 0.148,
            20: 0.293,
            21: 0.442,
            22: 0.596,
            23: 0.76,
            24: 0.938,
            25: 1.138,
            26: 1.371,
            27: 1.654,
            28: 2.025,
            29: 2.576,
            30: 3.722,
        },
    },
    "KY27PAR7": {
        "domain": "PAR",
        "text": "Have you had enough money for your expenses?",
        "answers": {
            "never": 1,
            "seldom": 2,
            "quite often": 3,
            "very often": 4,
            "always": 5,
        },
        "r": {
            6: -3.983,
            7: -2.805,
            8: -2.219,
            9: -1.812,
            10: -1.493,
            11: -1.229,
            12: -1,
            13: -0.798,
            14: -0.614,
            15: -0.444,
            16: -0.284,
            17: -0.13,
            18: 0.019,
            19: 0.166,
            20: 0.314,
            21: 0.465,
            22: 0.621,
            23: 0.788,
            24: 0.969,
            25: 1.17,
            26: 1.404,
            27: 1.689,
            28: 2.06,
            29: 2.609,
            30: 3.754,
        },
    },
    "KY27SOC1": {
        "domain": "SOC",
        "text": "Have you spent time with your friends?",
        "answers": {
            "never": 1,
            "seldom": 2,
            "quite often": 3,
            "very often": 4,
            "always": 5,
        },
        "r": {
            3: -3.711,
            4: -2.474,
            5: -1.813,
            6: -1.312,
            7: -0.88,
            8: -0.476,
            9: -0.079,
            10: 0.327,
            11: 0.757,
            12: 1.227,
            13: 1.77,
            14: 2.475,
            15: 3.754,
        },
    },
    "KY27SOC2": {
        "domain": "SOC",
        "text": "Have you had fun with your friends?",
        "answers": {
            "never": 1,
            "seldom": 2,
            "quite often": 3,
            "very often": 4,
            "always": 5,
        },
        "r": {
            3: -3.756,
            4: -2.473,
            5: -1.77,
            6: -1.231,
            7: -0.767,
            8: -0.339,
            9: 0.075,
            10: 0.494,
            11: 0.938,
            12: 1.43,
            13: 2.008,
            14: 2.758,
            15: 4.09,
        },
    },
    "KY27SOC3": {
        "domain": "SOC",
        "text": "Have you and your friends helped each other?",
        "answers": {
            "never": 1,
            "seldom": 2,
            "quite often": 3,
            "very often": 4,
            "always": 5,
        },
        "r": {
            3: -3.826,
            4: -2.557,
            5: -1.869,
            6: -1.348,
            7: -0.904,
            8: -0.496,
            9: -0.1,
            10: 0.303,
            11: 0.736,
            12: 1.222,
            13: 1.804,
            14: 2.574,
            15: 3.941,
        },
    },
    "KY27SOC4": {
        "domain": "SOC",
        "text": "Have you been able to rely on your friends?",
        "answers": {
            "never": 1,
            "seldom": 2,
            "quite often": 3,
            "very often": 4,
            "always": 5,
        },
        "r": {
            3: -3.827,
            4: -2.564,
            5: -1.881,
            6: -1.364,
            7: -0.92,
            8: -0.509,
            9: -0.104,
            10: 0.314,
            11: 0.768,
            12: 1.283,
            13: 1.892,
            14: 2.675,
            15: 4.035,
        },
    },
    "KY27SCH1": {
        "domain": "SCH",
        "text": "Have you been happy at school?",
        "answers": {
            "not at all": 1,
            "slightly": 2,
            "moderately": 3,
            "very": 4,
            "extremely": 5,
        },
        "r": {
            3: -4.046,
            4: -2.779,
            5: -2.118,
            6: -1.626,
            7: -1.193,
            8: -0.768,
            9: -0.317,
            10: 0.18,
            11: 0.731,
            12: 1.351,
            13: 2.059,
            14: 2.911,
            15: 4.301,
        },
    },
    "KY27SCH2": {
        "domain": "SCH",
        "text": "Have you got on well at school?",
        "answers": {
            "not at all": 1,
            "slightly": 2,
            "moderately": 3,
            "very": 4,
            "extremely": 5,
        },
        "r": {
            3: -3.978,
            4: -2.664,
            5: -1.965,
            6: -1.452,
            7: -1.018,
            8: -0.607,
            9: -0.182,
            10: 0.287,
            11: 0.82,
            12: 1.429,
            13: 2.131,
            14: 2.982,
            15: 4.373,
        },
    },
    "KY27SCH3": {
        "domain": "SCH",
        "text": "Have you been able to pay attention?",
        "answers": {
            "never": 1,
            "seldom": 2,
            "quite often": 3,
            "very often": 4,
            "always": 5,
        },
        "r": {
            3: -3.496,
            4: -2.379,
            5: -1.807,
            6: -1.375,
            7: -0.99,
            8: -0.61,
            9: -0.204,
            10: 0.257,
            11: 0.79,
            12: 1.4,
            13: 2.098,
            14: 2.942,
            15: 4.329,
        },
    },
    "KY27SCH4": {
        "domain": "SCH",
        "text": "Have you got along well with your teachers?",
        "answers": {
            "never": 1,
            "seldom": 2,
            "quite often": 3,
            "very often": 4,
            "always": 5,
        },
        "r": {
            3: -3.84,
            4: -2.547,
            5: -1.898,
            6: -1.426,
            7: -1.017,
            8: -0.618,
            9: -0.192,
            10: 0.297,
            11: 0.876,
            12: 1.551,
            13: 2.3,
            14: 3.154,
            15: 4.524,
        },
    },
}

DOMAINS = {
    "PHY": {
        "name": "Physical Well-being",
        "t": (1.2203, 1.45408),
        "r": {
            5: -4.287,
            6: -3.040,
            7: -2.405,
            8: -1.960,
            9: -1.605,
            10: -1.296,
            11: -1.011,
            12: -0.735,
            13: -0.456,
            14: -0.168,
            15: 0.134,
            16: 0.454,
            17: 0.796,
            18: 1.166,
            19: 1.574,
            20: 2.035,
            21: 2.582,
            22: 3.299,
            23: 4.594,
        },
    },
    "PWB": {
        "name": "Psychological Well-being",
        "t": (1.6950, 1.35642),
        "r": {
            7: -4.472,
            8: -3.292,
            9: -2.705,
            10: -2.299,
            11: -1.982,
            12: -1.718,
            13: -1.489,
            14: -1.284,
            15: -1.096,
            16: -0.920,
            17: -0.752,
            18: -0.590,
            19: -0.431,
            20: -0.273,
            21: -0.114,
            22: 0.049,
            23: 0.216,
            24: 0.391,
            25: 0.576,
            26: 0.774,
            27: 0.989,
            28: 1.224,
            29: 1.485,
            30: 1.778,
            31: 2.112,
            32: 2.504,
            33: 2.985,
            34: 3.642,
            35: 4.886,
        },
    },
    "PAR": {
        "name": "Parent Realtions & Home Life",
        "t": (1.1982, 1.08822),
        "r": {
            7: -4.053,
            8: -2.887,
            9: -2.312,
            10: -1.915,
            11: -1.607,
            12: -1.353,
            13: -1.136,
            14: -0.944,
            15: -0.772,
            16: -0.614,
            17: -0.468,
            18: -0.330,
            19: -0.199,
            20: -0.072,
            21: 0.052,
            22: 0.174,
            23: 0.297,
            24: 0.421,
            25: 0.548,
            26: 0.681,
            27: 0.821,
            28: 0.973,
            29: 1.140,
            30: 1.330,
            31: 1.552,
            32: 1.824,
            33: 2.184,
            34: 2.721,
            35: 3.852,
        },
    },
    "SOC": {
        "name": "Social Support & Peers",
        "t": (1.7749, 1.50386),
        "r": {
            4: -4.054,
            5: -2.832,
            6: -2.193,
            7: -1.725,
            8: -1.335,
            9: -0.989,
            10: -0.667,
            11: -0.358,
            12: -0.051,
            13: 0.261,
            14: 0.586,
            15: 0.932,
            16: 1.313,
            17: 1.744,
            18: 2.261,
            19: 2.953,
            20: 4.232,
        },
    },
    "SCH": {
        "name": "School Environment",
        "t": (1.2774, 1.60553),
        "r": {
            4: -4.136,
            5: -2.906,
            6: -2.286,
            7: -1.846,
            8: -1.485,
            9: -1.161,
            10: -0.852,
            11: -0.540,
            12: -0.212,
            13: 0.144,
            14: 0.536,
            15: 0.970,
            16: 1.450,
            17: 1.984,
            18: 2.588,
            19: 3.339,
            20: 4.649,
        },
    },
}


def get_question_score(input, question):
    score = None
    answers = question["answers"]

    if input:
        score = answers[input] if input in answers else None

    return score


def get_question_scores(answers, questions):
    scores = {}

    for id, question in questions.items():
        answer = answers.get(id, None)
        score = get_question_score(answer, question)

        scores[id] = score

    return scores


def get_domain_questions(domain):
    return {key: value for key, value in SCORES.items() if value["domain"] == domain}


def get_domain_scores(answers, domain):
    questions = get_domain_questions(domain)
    n_questions = len(questions)
    min_questions = n_questions - 1

    scores = get_question_scores(answers, questions)
    n_scores = sum(x is not None for x in scores.values())

    if n_scores < min_questions:
        scores[f"{domain}_R"] = None
        scores[f"{domain}_T"] = None
        logger.warning(
            f"Domain '{domain}' score cannot be calculated, not enough questions answered."
        )
    else:
        score_sum = sum(x for x in scores.values() if x is not None)

        if n_scores == min_questions:
            missing_question = next(
                (key for key, value in scores.items() if value is None), None
            )
            r_value = SCORES[missing_question]["r"][score_sum]  # type: ignore

            logger.warning(
                f"Domain '{domain}' score calculated with one question missing: '{missing_question}'."
            )

        else:
            r_value = DOMAINS[domain]["r"][score_sum]
            logger.info(
                f"Domain '{domain}' score calculated with all questions answered."
            )

        t_value = (
            (r_value - DOMAINS[domain]["t"][0]) / DOMAINS[domain]["t"][1]
        ) * 10 + 50
        scores[f"{domain}_R"] = r_value
        scores[f"{domain}_T"] = t_value

    return scores


def get_score(answers):
    domains = ["PHY", "PWB", "PAR", "SOC", "SCH"]
    scores = {}

    for domain in domains:
        domain_scores = get_domain_scores(answers, domain)
        scores.update(domain_scores)

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
    domains = ["PHY", "PWB", "PAR", "SOC", "SCH"]
    alphas = {}

    for domain in domains:
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
    return list(DOMAINS.keys())
