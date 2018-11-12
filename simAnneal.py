# -*- coding: utf-8 -*-
import random
from time import time
import math
from random import choice

class SimAnneal(object):#模拟退火类
    '''
    Simulated annealing algorithm
    '''
    def __init__(self, constraintMatrix, time, sd, c, hazardous, demand, log, tlimit=500, temperature0=200000, temFinal=1e-8):
        '''
        :param constraintMatrix: 优先既约束矩阵
        :param time: 任务时间
        :param sd: 时间增量矩阵
        :param c: 工作站周期
        :param hazardous: 任务危险矩阵
        :param demand: 任务的需求量
        :param tlimit: 算法执行时间
        :param temperature0: initial temperature
        :param temDelta: step factor for decreasing temperature
        :param temFinal: the final temperature
        '''
        self.constraintMatrix = constraintMatrix
        self.time = time
        self.sd  = sd
        self.c = c
        self.hazardous = hazardous
        self.demand = demand
        self.log = log #打日志用的
        self.tlimit = tlimit  #论文中的时间限制
        self.temperature0 = temperature0 #初始温度
        self.temFinal = temFinal #最终温度

    def calF1(self, Sg): #计算目标值f1
        '''
        :param Sg: 当前迭代解
        :return 各站工作时间
        '''
        stationWorkTime = []
        tmpTime = 0
        times = 0
        taskList = []
        for i in range(len(Sg)):
            times += self.time[Sg[i] - 1]
            if self.checkSeqDep(self.sd[:, Sg[i] - 1]):
                sdtime = self.getSeqDepTime(Sg[0:i], self.sd[:, Sg[i] - 1])
                times += sdtime
            if tmpTime + times <= self.c:
                taskList.append(Sg[i])
                tmpTime += times
                times = 0
                continue
            else:
                stationWorkTime.append([tmpTime, taskList])
                tmpTime = times
                times = 0
                taskList = []
                taskList.append(Sg[i])
        stationWorkTime.append([tmpTime, taskList])
        # print("stationWokrTime: ", stationWorkTime)

        return stationWorkTime

    def checkSeqDep(self, sdList):
        for s in sdList:
            if s != 0:
                return True
        return False

    def getSeqDepTime(self, sgSublist, sdList):
        sdtime = 0
        for i in range(len(sdList)):
            if (i+1) not in sgSublist:
                sdtime += sdList[i]
        return sdtime


    def calF2(self, stationWorkTime, c):#计算目标值f2
        '''
        :param stationWorkTime: 各站工作时间
        :return: f2
        '''
        f2 = 0
        for t in stationWorkTime:
            f2 += math.pow(c-t[0], 2)

        return f2

    def calF3(self, Sg):#计算目标值f3
        '''
        :param Sg: 当前迭代解
        :return: f3
        '''
        f3 = 0
        for i in range(0, len(Sg)):
            f3 += (i+1) * self.hazardous[Sg[i]-1]

        return f3

    def calF4(self, Sg):#计算目标值f4
        '''
        :param Sg: 当前迭代解
        :return: f4
        '''
        f4 = 0
        for i in range(0, len(Sg)):
            f4 += (i+1) * self.demand[Sg[i]-1]

        return f4

    def SWAP(self, Sc, stationWorkTime, pre, suc):
        '''
        :param Sc: curent solution Sc
        :return: neighbour solution Sg
        '''
        # for i in range(1, len(stationWorkTime)):
        #     for j in range(0, i):
        #         Sg = self.swapOpreation(Sc, stationWorkTime[i][1], stationWorkTime[j][1])
        #         if Sg is not None:
        #             return Sg
        Sg = self.swapOpreation(Sc, stationWorkTime[suc][1], stationWorkTime[pre][1])
        return Sg

    def swapOpreation(self, Sc, sucTaskList, preTaskList):
        '''
        :param Sc:  curent solution Sc
        :param sucTaskList: 后继站中的任务列表
        :param preTaskList: 前驱站中的任务列表
        :return: neighbour solution Sg
        '''
        times = 0
        while(1):
            sucIndex = choice(sucTaskList) - 1
            preIndex = choice(preTaskList) - 1
            Sg = Sc.copy()
            tmp = Sg[sucIndex]
            Sg[sucIndex] = Sg[preIndex]
            Sg[preIndex] = tmp
            count = 0
            for checkIdex in range(preIndex + 1, sucIndex + 1):
                if self.checkConstraint(Sc[checkIdex], Sc[preIndex]) and self.checkConstraint(Sc[sucIndex], Sc[checkIdex]):
                    count += 1
                    continue
            if count == (sucIndex - preIndex):
                return Sg
            times += 1
            if times == 100:
                return None

    def checkConstraint(self, precursor, succeed):
        '''
        :param precursor:  前驱
        :param succeed:  后继
        :return:
        '''
        if precursor == succeed:
            return True
        preList = {precursor}
        tmpPreList = {precursor}

        while 1:
            taskIdList = set()
            for pre in tmpPreList:
                index = 0
                for val in self.constraintMatrix[:, pre-1]:
                    index += 1
                    if val == 1:
                        taskIdList.add(index)
                        preList.add(index)
            if not taskIdList:
                break
            else:
                tmpPreList = taskIdList

        return succeed not in preList


    def INSERT(self, Sc, stationWorkTime, preStion, sucStion):
        # for i in range(1, len(stationWorkTime)):
        #     for j in range(0, i):
        #         Sg = self.insertOpreation(Sc, stationWorkTime[i][1], stationWorkTime[j][1])
        #         if Sg is not None:
        #             return Sg
        Sg = self.insertOpreation(Sc, stationWorkTime[sucStion][1], stationWorkTime[preStion][1])
        return Sg

    def insertOpreation(self, Sc, sucTaskList, preTaskList):
        '''
        :param Sc:  curent solution Sc
        :param sucTaskList: 后继站中的任务列表
        :param preTaskList: 前驱站中的任务列表
        :return: neighbour solution Sg
        '''
        times = 0
        while(1):
            sucIndex = choice(sucTaskList) - 1
            preIndex = choice(preTaskList) - 1
            Sg = Sc.copy()
            tmp = Sg[sucIndex]
            Sg.pop(sucIndex)
            Sg.insert(preIndex, tmp)
            count = 0
            for checkIdex in range(preIndex, sucIndex):
                if self.checkConstraint(Sc[sucIndex], Sc[checkIdex]):
                    count += 1
                    continue
            if count == (sucIndex - preIndex):
                return Sg
            times += 1
            if times == 100:
                return None

    def solve(self, Sc):
        '''
        :param Sc: old solution
        :return:
        '''
        t_start = time()
        g = 1 #迭代次数
        T0 = self.temperature0 #初始温度
        Tg = T0 #每轮迭代温度

        while Tg > self.temFinal: #循环迭代
            workTime = self.calF1(Sc) #计算目标值f1
            preStion = random.randint(0, len(workTime) - 1) #随机获取需要swap或insert的两个站
            sucStoin = random.randint(0, len(workTime) - 1)
            while sucStoin <= preStion: #确保swap或insert的两个站先后顺序
                preStion = random.randint(0, len(workTime) - 1)
                sucStoin = random.randint(0, len(workTime) - 1)
            tmpS = Sc.copy()
            op = random.random()
            if op < 0.5: #论文核心算法, 随机对上一轮迭代的解进行swap或inset操作
                Sg = self.SWAP(tmpS, workTime, preStion, sucStoin)
                if Sg is None:
                    self.log.logger.info("swap is None")
                else:
                    self.log.logger.info("swap, " + str(Sg) + str(len(self.calF1(Sg))))
            else:
                Sg = self.INSERT(tmpS, workTime, preStion, sucStoin)
                if Sg is None:
                    self.log.logger.info("insert is None")
                else:
                    self.log.logger.info("insert, " + str(Sg) + str(len(self.calF1(Sg))))
            if Sg is None: #若一次swap或insert操作不能得到一个解则再次更换preStion,sucStoin值,直到得到一个解
                # (由于有优先级约束,所以可能swap或inset操作得不到满足约束的解)
                t_end = time()
                if (t_end - t_start) > self.tlimit:
                    break
                continue

            self.log.logger.info("new Sg: " + str(Sg) + str(len(self.calF1(Sg))))
            dE = self.calde(Sg, Sc) #根据论文方法计算Delta(即dE),目标值有f1到f4依次比较
            self.log.logger.info('dE:' + str(dE))
            if dE <= 0: #如果当前解Sg优于历史最优解Sc,则更新Sc
                Sc = Sg.copy()
            else:#否则, 按一定概率接纳当前解Sg,此处模拟退火核心,一定概率接受次优的Sg,能跳出局部最优解
                if math.exp(-self.caldEByF2(Sg, Sc) / Tg) > 0.9:
                    self.log.logger.info('accept Sg:' + str(Sg))
                    Sc = Sg.copy()
            # update the current temperature
            # Tg = self.temperature0 / (1 + math.log(g))
            self.log.logger.info("accept new Sg: " + str(Sg) + str(len(self.calF1(Sg))))
            Tg *= 0.98 #更新温度
            g += 1 #更新迭代
            t_end = time() #检查运行时间是否超过阈值
            # if (t_end - t_start) > self.tlimit:
            #     break
            self.log.logger.info('end once......')
        return Sc

    def calde(self, Sg, Sc):
        sgf1 = self.calF1(Sg)
        scf1 = self.calF1(Sc)
        self.log.logger.info('sgf1:' + str(sgf1) + str(len(sgf1)) + ' '+ str(Sg) + ' scf1:' + str(scf1) + str(len(scf1)) + ' ' + str(Sc))
        if len(sgf1) != len(scf1):
            return len(sgf1) - len(scf1)

        sgf2 = self.calF2(sgf1, self.c)
        scf2 = self.calF2(scf1, self.c)
        self.log.logger.info('sgf2:' + str(sgf2) + ' '+ str(Sg) + ' scf2:' + str(scf2) + ' ' + str(Sc))
        if sgf2 != scf2:
            return sgf2 - scf2

        sgf3 = self.calF3(Sg)
        scf3 = self.calF3(Sc)
        self.log.logger.info('sgf3:' + str(sgf3) + ' '+ str(Sg) + ' scf3:' + str(scf3) + ' ' + str(Sc))
        if sgf3 != scf3:
            return sgf3 - scf3

        sgf4 = self.calF4(Sg)
        scf4 = self.calF4(Sc)
        self.log.logger.info('sgf4:' + str(sgf4) + ' '+ str(Sg) + ' scf4:' + str(scf4) + ' ' + str(Sc))
        return sgf4 - scf4

    def caldEByF2(self, Sg, Sc):
        sgf1 = self.calF1(Sg)
        scf1 = self.calF1(Sc)
        sgf2 = self.calF2(sgf1, self.c)
        scf2 = self.calF2(scf1, self.c)
        return sgf2 - scf2

















