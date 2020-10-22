# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/06_model_evaluation.ipynb (unless otherwise specified).

__all__ = ['show_loss_accurracy_plots', 'evaluate_model']

# Cell
from tensorflow.keras.models import load_model
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import average_precision_score,precision_recall_curve
#funcsigs replaces the (deprecated?) sklearn signature
from funcsigs import signature
#from sklearn.utils.fixes import signature
from sklearn.metrics import roc_curve
from sklearn.metrics import roc_auc_score

def show_loss_accurracy_plots(history):
    #Evaluation
    acc = history['accuracy']
    val_acc = history['val_accuracy']
    loss = history['loss']
    val_loss = history['val_loss']

    epochs2 = range(len(acc))

    plt.plot(epochs2, acc, 'b', label='Training')
    plt.plot(epochs2, val_acc, 'r', label='Validation')
    plt.title('Training and validation accuracy')
    plt.ylabel('acc')
    plt.xlabel('epoch')
    plt.legend()

    plt.figure()

    plt.plot(epochs2, loss, 'b', label='Training')
    plt.plot(epochs2, val_loss, 'r', label='Validation')
    plt.title('Training and validation loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend()

    plt.show()

# Cell
def evaluate_model(criticality_network_load,corpora_test_x,target_test_y):
    score = criticality_network_load.evaluate(corpora_test_x, target_test_y, verbose=1)
    print('Test loss:', score[0])
    print('Test accuracy:', score[1])
    history_predict = criticality_network_load.predict(x=corpora_test_x)
    history_predict

    inferred_data = pd.DataFrame(history_predict,columns=list('AB'))
    target_data = pd.DataFrame(target_test_y,columns=list('LN'))
    data = target_data.join(inferred_data)

    y_true = list(data['L'])
    y_score= list(data['A'])
    average_precision = average_precision_score(y_true, y_score)

    print('Average precision-recall score: {0:0.2f}'.format(average_precision))

    #ROC Curve (all our samples are balanced)
    auc = roc_auc_score(y_true, y_score)
    print('AUC: %.3f' % auc)