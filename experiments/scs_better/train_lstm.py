import torch

from txai.utils.predictors.loss import Poly1CrossEntropyLoss
from txai.trainers.train_transformer import train
from txai.models.encoders.simple import LSTM
from txai.utils.data import process_Synth
from txai.utils.predictors import eval_mvts_transformer
from txai.synth_data.simple_spike import SpikeTrainDataset

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

clf_criterion = Poly1CrossEntropyLoss(
    num_classes = 4,
    epsilon = 1.0,
    weight = None,
    reduction = 'mean'
)

for i in range(1, 6):
    D = process_Synth(split_no = i, device = device, base_path = '/TimeX/datasets/SeqCombSingle/')
    train_loader = torch.utils.data.DataLoader(D['train_loader'], batch_size = 64, shuffle = True)

    val, test = D['val'], D['test']

    model = LSTM(
        d_inp = val[0].shape[-1],
        n_classes = 4,
    )

    model.to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr = 1e-4)
    
    spath = 'models/Scomb_lstm_split={}.pt'.format(i)

    model, loss, auc = train(
        model,
        train_loader,
        val_tuple = val, 
        n_classes = 4,
        num_epochs = 200,
        save_path = spath,
        optimizer = optimizer,
        show_sizes = False,
        use_scheduler = False,
        validate_by_step = None,
    )
    
    model_sdict_cpu = {k:v.cpu() for k, v in  model.state_dict().items()}
    torch.save(model_sdict_cpu, spath)

    f1 = eval_mvts_transformer(test, model)
    print('Test F1: {:.4f}'.format(f1))