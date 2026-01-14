from .qrl import (
    monte_carlo_code,
    td_code,
    complete_policy_iteration_code,
    complete_value_iteration_code,
    tensor_operations_code,
    perceptron_operations_code,
    perceptron_manual_code,
    ADALINE_complete_code,
    MLP_complete_code,
    MLP_titanic_houses_code,
    CNN_og_code,
    CNN_modified_code,
    CNN_filters_code,

)
from .qan import (
    undercomplete_ae_code,
    denoising_ae_code,
    convolutional_ae_code,
    simple_rnn_code,
    rnn_imdb_code,
    lstm_vs_rnn_code,
    lstm_next_word_code,
    gan_code,
    dcgan_code,
    
)

from .qsp2 import (
    sp_lstm_code,
    sp_cnn_code,
    sp_hmm_code,
    sp_rule_code,
)

from .qkr import (
    kr_swi_code,
    kr_fuzzy_uni_code,
    kr_fuzzy_fan_code,
    kr_bay_engine_code,
    kr_bay_flu_code,
    kr_lab12_code,
)

from .qrl2 import (
    q_learning_code,
    sarsa_code,
    mc_is_code,
    qlearning_tdcontrol_code,
    linear_approximation_code,
    non_linear_approximation_nn_code,
    batch_monte_carlo_code,
    batch_td_code,
    batch_td_lambda_code,
    dqn_batch_code,

)

from .qsp import (
    mfcc_manual_vs_auto_code,
    analysis_formants_harmonics_code,
    generate_consonants_code,
    quiz_code,
    lab2_code,
    oel1_code,
    mfcc_from_scratch_code,
    mfcc_feature_extraction_code,
    mfcc_file_features_code,


)

from .utils import display_snippet, save_snippet

__all__ = [
    "monte_carlo_code",
    "td_code",
    "complete_policy_iteration_code",
    "complete_value_iteration_code",
    "display_snippet",
    "save_snippet",
    "tensor_operations_code",
    "perceptron_operations_code",
    "perceptron_manual_code",
    "ADALINE_complete_code",
    "MLP_complete_code",
    "MLP_titanic_houses_code",
    "CNN_og_code",
    "CNN_modified_code",
    "CNN_filters_code",
    "mfcc_manual_vs_auto_code",
    "analysis_formants_harmonics_code",
    "generate_consonants_code",
    "quiz_code",
    "lab2_code",
    "oel1_code",
    "mfcc_from_scratch_code",
    "mfcc_feature_extraction_code",
    "mfcc_file_features_code",
    "q_learning_code",
    "sarsa_code",
    "mc_is_code",
    "qlearning_tdcontrol_code",
    "linear_approximation_code",
    "non_linear_approximation_nn_code",
    "batch_monte_carlo_code",
    "batch_td_code",
    "batch_td_lambda_code",
    "dqn_batch_code",
    "undercomplete_ae_code",
    "denoising_ae_code",
    "convolutional_ae_code",
    "simple_rnn_code",
    "rnn_imdb_code",
    "lstm_vs_rnn_code",
    "lstm_next_word_code",
    "gan_code",
    "dcgan_code",
    "sp_lstm_code",
    "sp_cnn_code",
    "sp_hmm_code",
    "sp_rule_code",
    "kr_swi_code",
    "kr_fuzzy_uni_code",
    "kr_fuzzy_fan_code",
    "kr_bay_engine_code",
    "kr_bay_flu_code",
    "kr_lab12_code",
]
