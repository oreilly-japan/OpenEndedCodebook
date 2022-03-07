
num_processes   = 4
seed            = 1

steps           = 128
num_mini_batch  = 4
epochs          = 8
learning_rate   = 3e-4
gamma           = 0.99
clip_range      = 0.3
ent_coef        = 0.01

learning_steps  = 50

policy_kwargs   = {
    'log_std_init'  : 0.0,
    'ortho_init'    : True,
    'squash_output' : False,
}
