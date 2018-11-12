# -*- coding: utf-8 -*-
from simAnneal import SimAnneal
import numpy as np
from Logger import Logger
import csv

def getConstraintMatrix(): #读取任务间约束数据
    csv_reader = csv.reader(open("data/constraintMat.csv"))
    conMat = []
    index = 0
    for row in csv_reader:
        if index == 0:
            index += 1
            continue
        arr = list(map(int, row[1:]))
        conMat.append(arr)
    return np.array(conMat)

def getTaskTime(): #读取任务拆卸时间
    csv_reader = csv.reader(open("data/taskTime.csv"))
    index = 0
    time = []
    for row in csv_reader:
        if index == 0:
            index += 1
            continue
        time = list(map(int, row))

    return time

def getSeqDependencies(): #读取任务依赖消耗时间
    csv_reader = csv.reader(open("data/seqDependencies.csv"))
    sdMat = []
    index = 0
    for row in csv_reader:
        if index == 0:
            index += 1
            continue
        arr = list(map(int, row[1:]))
        sdMat.append(arr)
    return np.array(sdMat)

def getHazardous(): #读取拆卸危险度
    csv_reader = csv.reader(open("data/hazardous.csv"))
    index = 0
    hazardous = []
    for row in csv_reader:
        if index == 0:
            index += 1
            continue
        hazardous = list(map(int, row))
    print(hazardous)
    return hazardous

def getDemand(): #读取任务需求量
    csv_reader = csv.reader(open("data/demand.csv"))
    index = 0
    demand = []
    for row in csv_reader:
        if index == 0:
            index += 1
            continue
        demand = list(map(int, row))
    print(demand)
    return demand


def writeResult():
    with open("result.txt", 'w') as f:
        f.write("best solution: " + str(Sg) + "\n")
        f.write("need work station number: " + str(len(workTime)) + "\n")
    index = 1
    for f_index in workTime:
        log.logger.info(
            "station No.: " + str(index) + ", station work times: " + str(f_index[0]) + ", taskId: " + str(f_index[1]))
        with open('result.txt', 'a') as f:
            f.write("station No.: " + str(index) + ", station work times: " + str(f_index[0]) + ", taskId: " + str(
                f_index[1]) + "\n")
        index += 1


if __name__ == '__main__':
    log = Logger('all.log', level='debug')
    log.logger.info("SA algo begin...")
    c = 40
    saalgo = SimAnneal(getConstraintMatrix(), getTaskTime(), getSeqDependencies(),
                       c, getHazardous(), getDemand(), log, tlimit=1000)
    Sc = [1, 4, 6, 5, 10, 7, 8, 9, 2, 3] #初始解,按论文说法,初始解可以用启发式方法得到.实际可以人为指定
    Sg = saalgo.solve(Sc)
    workTime = saalgo.calF1(Sg)
    log.logger.info("SA algo end...")
    log.logger.info("best solution: " + str(Sg))
    log.logger.info("need work station number: " + str(len(workTime)) + "\n")
    writeResult()
