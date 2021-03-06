# -*- coding: utf-8 -*-
# ELEKTRONN2 Toolkit
# Copyright (c) 2016 Philipp J. Schubert
# All rights reserved

save_path = '~/elektronn2_examples/'
save_name = "piano_lstm_sgd"

preview_data_path = None
preview_kwargs    = dict(export_class='all', max_z_pred=5)
initial_prev_h   = 0.5
prev_save_h      = 1.0
data_class = 'PianoData'
background_processes = 2

n_steps=10000
max_runtime = 4 * 24 * 3600 # in seconds
history_freq = 200
monitor_batch_size = 20
optimiser = 'Adam'
data_batch_args = {}
data_init_kwargs = {}
optimiser_params = dict(lr=2e-4, mom=0.9, beta2=0.99, wd=0.5e-3)
batch_size = 20


def create_model():
    from elektronn2 import neuromancer

    in_sh = (20, 20, 58)
    inp = neuromancer.Input(in_sh, 'r,b,f', name='raw')
    inp0, _ = neuromancer.split(inp, 'r', index=1, strip_singleton_dims=True)
    init_memory = neuromancer.InitialState_like(inp0, override_f=1000, init_kwargs=dict(mode='fix-uni', scale=0.1))
    out = neuromancer.LSTM(inp0, init_memory, 500)
    out = neuromancer.Scan(out, init_memory, in_iterate=inp,
                           in_iterate_0=inp0, n_steps=20, last_only=True)
    out = neuromancer.Perceptron(out, 2*58, 'lin')
    out = neuromancer.Softmax(out, n_indep=58)
    target = neuromancer.Input_like(out, override_f=1, name='target')
    weights = neuromancer.ValueNode((116, ), 'f', value=(0.2, 1.8))
    loss = neuromancer.MultinoulliNLL(out, target, target_is_sparse=True,
                                      class_weights=weights, name='nll')
    # Objective
    loss = neuromancer.AggregateLoss(loss)
    # Monitoring  / Debug outputs
    errors = neuromancer.Errors(out, target, target_is_sparse=True)

    model = neuromancer.model_manager.getmodel()
    model.designate_nodes(input_node=inp, target_node=target, loss_node=loss,
                          prediction_node=out, prediction_ext=[loss, errors, out])
    return model

if __name__ == "__main__":
    import traceback
    model = create_model()


    try:
        model.test_run_prediction()
    except Exception as e:
        traceback.print_exc()
        print("Test run failed. In case your GPU ran out of memory the \
               principal setup might still be working")

    try:
        from elektronn2.utils.d3viz import visualise_model
        visualise_model(model, 'model-graph')
        import webbrowser
        webbrowser.open('model-graph.png')
        webbrowser.open('model-graph.html')
    except Exception as e:
        traceback.print_exc()
        print("Could not print model model graph. Is pydot/graphviz properly installed?")




