import os
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np
import torch

DATASET = 'toy'
ROOT_DIR = os.path.abspath("./")
COLOR = ('lightcoral', 'royalblue', 'limegreen', 'gold', 'darkorchid', 'aqua', 'tomato', 'deeppink', 'teal')


class default_plt:
    def __init__(self, savePath, xlabel='', ylabel='', mode='png', isGray=False, isLegend=True, isGrid=True):
        self.savePath = savePath
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.mode = mode
        self.isGray = isGray
        self.isLegend = isLegend
        self.isGrid = isGrid

    def __enter__(self):
        fig = plt.figure(0, figsize=(8, 7), dpi=600)
        self.ax = fig.subplots()
        self.ax.cla()
        if not self.isGray:
            self.ax.patch.set_facecolor("w")
        self.ax.tick_params(labelsize=15)
        self.ax.set_xlabel(self.xlabel, fontdict={'weight': 'normal', 'size': 15})
        self.ax.set_ylabel(self.ylabel, fontdict={'weight': 'normal', 'size': 15})
        if self.isGrid:
            self.ax.grid(color="#EAEAEA", linewidth=1)
        return self.ax

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.isLegend:
            box = self.ax.get_position()
            self.ax.set_position([box.x0, box.y0, box.width, box.height*0.95])
            self.ax.legend(prop={'weight': 'normal', 'size': 14}, loc='lower left', bbox_to_anchor=(0, 1.02, 1, 0.2), ncol=3, mode="expand")

        plt.savefig(self.savePath, dpi=600, format=f'{self.mode}')
        plt.clf()
        plt.close()


def default(savePath, xlabel='', ylabel='', mode='png', isGray=False, isLegend=True, isGrid=True):
    return default_plt(savePath, xlabel, ylabel, mode, isGray, isLegend, isGrid)


def lab():
    labDict = {}
    DatasetDir = os.path.join(ROOT_DIR, 'cache', DATASET)
    saveDir = os.path.join(DatasetDir, "All")
    if not os.path.exists(saveDir):
        os.makedirs(saveDir)
    for tag in os.listdir(DatasetDir):
        if tag == "All":
            continue
        labDict[tag] = {}
        datasetPath = os.path.join(DatasetDir, tag, 'dataset.pkl')
        dataset = torch.load(datasetPath)
        drawDataSet(dataset, os.path.join(DatasetDir, tag))
        labDir = os.path.join(DatasetDir, tag, 'lab')
        for epochFold in os.listdir(labDir):
            epoch = float(epochFold[4:])
            pklDict = torch.load(os.path.join(labDir, epochFold, 'dataSave.pkl'))
            labDict[tag][epoch] = pklDict

    saveRegionEpochTabel(labDict, saveDir)
    drawRegionEpochPlot(labDict, saveDir)
    drawRegionAccPlot(labDict, saveDir)
    drawEpochAccPlot(labDict, saveDir)


def saveRegionEpochTabel(labDict: Dict, saveDir):
    savePath = os.path.join(saveDir, "regionEpoch.csv")
    strBuff = ''
    head = None
    for tag, epochDict in labDict.items():
        tag1 = tag.split('-')[-1].replace(',', '-')
        body = [tag1, ]
        dataList = []
        for epoch, fileDict in epochDict.items():
            data = [epoch, fileDict['regionNum']]
            dataList.append(data)
        dataList = np.array(dataList)
        a = dataList[:, 0]
        index = np.lexsort((a,))
        dataList = dataList[index]
        regionList = list(map(str, dataList[:, 1].astype(np.int16).tolist()))
        body.extend(regionList)
        bodyStr = ','.join(body)
        if head is None:
            epochList = list(map(str, dataList[:, 0].tolist()))
            head = ['model/epoch', ]
            head.extend(epochList)
            headStr = ','.join(head)
            strBuff = strBuff + headStr + '\r\n'
        strBuff = strBuff + bodyStr + '\r\n'
    with open(savePath, 'w') as w:
        w.write(strBuff)
        w.close()


def drawRegionEpochPlot(labDict: Dict, saveDir):
    savePath = os.path.join(saveDir, "regionEpoch.png")
    with default(savePath, 'Epoch', 'Number of Rgions') as ax:
        i = 0
        for tag, epochDict in labDict.items():
            tag1 = tag.split('-')[-1]
            dataList = []
            for epoch, fileDict in epochDict.items():
                data = [epoch, fileDict['regionNum']]
                dataList.append(data)
            dataList = np.array(dataList)
            a = dataList[:, 0]
            index = np.lexsort((a,))
            dataList = dataList[index]
            ax.plot(dataList[:, 0], dataList[:, 1], label=tag1, color=COLOR[i])
            ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
            i += 1


def drawRegionAccPlot(labDict: Dict, saveDir):
    savePath = os.path.join(saveDir, "regionAcc.png")
    with default(savePath, 'Accuracy', 'Number of Rgions') as ax:
        i = 0
        for tag, epochDict in labDict.items():
            tag1 = tag.split('-')[-1]
            dataList = []
            for _, fileDict in epochDict.items():
                acc = fileDict['accuracy']
                if isinstance(acc, torch.Tensor):
                    acc = acc.cpu().numpy()
                data = [acc, fileDict['regionNum']]
                dataList.append(data)
            dataList = np.array(dataList)
            a = dataList[:, 0]
            index = np.lexsort((a,))
            dataList = dataList[index]
            ax.plot(dataList[:, 0], dataList[:, 1], label=tag1, color=COLOR[i])
            ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
            # ax.set_xlim(0.965, 0.98)
            i += 1


def drawEpochAccPlot(labDict: Dict, saveDir):
    savePath = os.path.join(saveDir, "EpochAcc.png")
    with default(savePath, 'Epoch', 'Accuracy') as ax:
        i = 0
        for tag, epochDict in labDict.items():
            tag1 = tag.split('-')[-1]
            dataList = []
            for epoch, fileDict in epochDict.items():
                acc = fileDict['accuracy']
                if isinstance(acc, torch.Tensor):
                    acc = acc.cpu().numpy()
                data = [epoch, acc]
                dataList.append(data)
            dataList = np.array(dataList)
            a = dataList[:, 0]
            index = np.lexsort((a,))
            dataList = dataList[index]
            ax.plot(dataList[:, 0], dataList[:, 1], label=tag1, color=COLOR[i])

            i += 1


def drawDataSet(dataset, saveDir):
    savePath = os.path.join(saveDir, "distribution.png")
    x, y, isNorm, n_classes = dataset['x'], dataset['y'], dataset['isNorm'], dataset['n_classes']
    x = norm(x) if isNorm else x
    with default(savePath, 'x1', 'x2', isLegend=False, isGrid=False) as ax:
        ax.set_xlim(-1, 1)
        ax.set_ylim(-1, 1)
        for i in range(n_classes):
            ax.scatter(x[y == i, 0], x[y == i, 1], color=COLOR[i])


def norm(x):
    x = (x - np.min(x)) / (np.max(x) - np.min(x))
    x = (x - x.mean(0, keepdims=True)) / ((x.std(0, keepdims=True) + 1e-16))
    x /= np.max(np.abs(x))
    return x


if __name__ == "__main__":
    lab()
