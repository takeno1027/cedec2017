# -*- coding: utf-8 -*-
"""
Created on Sat Aug  5 01:40:39 2017

@author: tomita
"""

from itertools import chain

class AverageVertexColor(object):
    def __init__(self,vertexColors, connectedVertices, maxDepth = 3, methodType = 0):
        self.vertexColors = vertexColors
        
        self.connectedVertices = connectedVertices
        self.maxDepth = maxDepth
        
        self.methodType = methodType
    
    def traverseAdjacencyListRecursive(self,i,depth,accumulate):
        """
        隣接リストの走査　再帰
        """
        if depth == self.maxDepth:
            return
        
        accumulate.append(i)
        
        for j in self.connectedVertices[i]:
            self.traverseAdjacencyListRecursive(j,depth+1,accumulate)
    
    def traverseAdjacencyListLoop(self,start):
        """
        隣接リストの走査　ループ化
        """
        accumulate = [[start]]
        for i in range(0,self.maxDepth-1):
            tmp = []
            for j in accumulate[i]:
                for k in self.connectedVertices[j]:
                    tmp.append(k)
            
            accumulate.append(tmp)
        
        return list(chain.from_iterable(accumulate))
    
    def traverseAdjacencyListLoop2(self,start):
        """
        隣接リストの走査 内ループをリスト内包表記
        """
        
        accumulate = [[start]]
        
        for i in range(0,self.maxDepth-1):
            accumulate.append([k for j in accumulate[i] for k in self.connectedVertices[j]])
            
        return list(chain.from_iterable(accumulate))
    
    def traverseAdjacencyListLoop3(self,start):
        """
        隣接リストの走査 内ループをリスト内包記法
        dotアクセス（辞書の検索を避ける）
        """
        
        accumulate = [[start]]
        append  = accumulate.append
        maxDepth = self.maxDepth
        connectedVertices = self.connectedVertices
        
        for i in range(0,maxDepth-1):
            append([k for j in accumulate[i] for k in connectedVertices[j]])
        
        return list(chain.from_iterable(accumulate))
    
    
    def traverseAdjacencyListLoopDebug(self,start):
        """
        隣接リストの走査　ループ化 (デバッグ用）
        """
        accumulate = [[start]]
        for i in range(0,self.maxDepth-1):
            tmp = []
            for j in accumulate[i]:
                for k in self.connectedVertices[j]:
                    tmp.append(k)
            
            accumulate.append(tmp)
        
        return accumulate

    def traverseAdjacencyListLoopDebug2(self,start):
        """
        隣接リストの走査　ループ化 (デバッグ用）
        """
        accumulate = [[start]]
        for i in range(0,self.maxDepth-1):
            for j in accumulate[i]:
                tmp = [k for k in self.connectedVertices[j]]
            
            accumulate.append(tmp)
        
        return accumulate
    
    def average(self):
        if self.methodType == 0:
            #print('[averageTraverseAdjacencyListRecursive]'),
            self.averageTraverseAdjacencyListRecursive()

        elif self.methodType == 1:
            #print('[averageTraverseAdjacencyListLoop]'),
            self.averageTraverseAdjacencyListLoop()
            
        elif self.methodType == 2:
            #print('[averageTraverseAdjacencyListLoop2]'),
            self.averageTraverseAdjacencyListLoop2()
        
        elif self.methodType == 3:
            #print('[averageTraverseAdjacencyListLoop3]'),
            self.averageTraverseAdjacencyListLoop3()
        
    #@profile    
    def averageTraverseAdjacencyListRecursive(self):
        resultVertexColors = []
        
        numVertexColors = len(self.vertexColors)
        
        for i in range(0,numVertexColors):
            accumulate = []
            self.traverseAdjacencyListRecursive(i,0,accumulate)
            
            color = [0.0,
                     0.0,
                     0.0,
                     self.vertexColors[i][3]]
        
            for j in accumulate:
                c = self.vertexColors[j]
                
                color[0] += c[0]
                color[1] += c[1]
                color[2] += c[2]
            
            cnt = len(accumulate)
            
            color[0] /= cnt
            color[1] /= cnt
            color[2] /= cnt
            
            resultVertexColors.append(color)
            
        self.vertexColors = resultVertexColors

    def averageTraverseAdjacencyListLoop(self):
        resultVertexColors = []
        
        numVertexColors = len(self.vertexColors)
        
        for i in range(0,numVertexColors):
            accumulate = self.traverseAdjacencyListLoop(i)

            color = [0.0,
                     0.0,
                     0.0,
                     self.vertexColors[i][3]]
        
            for j in accumulate:
                c = self.vertexColors[j]
                
                color[0] += c[0]
                color[1] += c[1]
                color[2] += c[2]
            
            cnt = len(accumulate)
            
            color[0] /= cnt
            color[1] /= cnt
            color[2] /= cnt
            
            resultVertexColors.append(color)

        self.vertexColors = resultVertexColors
        
    #@profile
    def averageTraverseAdjacencyListLoop2(self):
        resultVertexColors = []
        
        numVertexColors = len(self.vertexColors)
        
        for i in range(0,numVertexColors):
            accumulate = self.traverseAdjacencyListLoop2(i)
            
            color = [0.0,
                     0.0,
                     0.0,
                     self.vertexColors[i][3]]
        
            for j in accumulate:
                c = self.vertexColors[j]
                
                color[0] += c[0]
                color[1] += c[1]
                color[2] += c[2]
            
            cnt = len(accumulate)
            
            color[0] /= cnt
            color[1] /= cnt
            color[2] /= cnt
            
            resultVertexColors.append(color)

        self.vertexColors = resultVertexColors
    
    def averageTraverseAdjacencyListLoop3(self):
        class Color(object):
            def __init__(self):
                self.color = [0.0,0.0,0.0,0.0]

            def __add__(self,other):
                pass
        
        resultVertexColors = []
        
        numVertexColors = len(self.vertexColors)
        
        for i in range(0,numVertexColors):
            accumulate = self.traverseAdjacencyListLoop2(i)
            
            color = [0.0,
                     0.0,
                     0.0,
                     self.vertexColors[i][3]]
        
            for j in accumulate:
                c = self.vertexColors[j]
                
                color[0] += c[0]
                color[1] += c[1]
                color[2] += c[2]
            
            cnt = len(accumulate)
            
            color[0] /= cnt
            color[1] /= cnt
            color[2] /= cnt
            
            resultVertexColors.append(color)

        self.vertexColors = resultVertexColors

        
def test_profile():
    """
    timeモジュールを使った単純な処理時間の計測
    """
    
    import sys
    import os
    import pickle
    
    import time
    
    try:    
        data = pickle.load(open(os.path.join(os.path.dirname(__file__),'vertexColor.bin'),'rb'))
    except ValueError:
        # githubにアップするときに、うっかりバイナリをテキスト転送されたファイルを読む場合
        with open(os.path.join(os.path.dirname(__file__),'vertexColor.bin'),'r') as fin:
            data = pickle.loads("\n".join([line.strip() for line in fin]))
    
    vertexColors = data['vertexColors']
    connectedVertices = data['connectedVertices']
    
    maxDepth = 5
    
    averageVertexColor = AverageVertexColor(vertexColors,connectedVertices,maxDepth,methodType = 0)
    
    tm = time.time()
    
    averageVertexColor.average()
    
    print('%f sec' % (time.time() - tm))

def test_cProfile():
    """
    cProfilemモジュールを使った関数ごとの呼び出し時間計測
    """

    
    import sys
    import os
    import pickle
    
    import cProfile
    import pstats
    
    try:    
        data = pickle.load(open(os.path.join(os.path.dirname(__file__),'vertexColor.bin'),'rb'))
    except ValueError:
        # githubにアップするときに、うっかりバイナリをテキスト転送されたファイルを読む場合
        with open(os.path.join(os.path.dirname(__file__),'vertexColor.bin'),'r') as fin:
            data = pickle.loads("\n".join([line.strip() for line in fin]))
    
    vertexColors = data['vertexColors']
    connectedVertices = data['connectedVertices']
    
    maxDepth = 5
    
    averageVertexColor = AverageVertexColor(vertexColors,connectedVertices,maxDepth,methodType = 0)
    
    profile = cProfile.Profile()
    profile.enable()
    
    averageVertexColor.average()
    
    profile.disable()
    ps = pstats.Stats(profile)
    ps.sort_stats("time")
    ps.print_stats()
    

def test_line_profile():
    """
    line_profileを使ったソースコードの行単位での計測
    AverageVertexColorクラスの計測したい関数のデコレーター@profileのコメントアウトを外してくださ
    """
    
    test_profile()

def test_dis():
    import dis
    
    dis.dis(AverageVertexColor.traverseAdjacencyListLoop3)
    
    
if __name__ == '__main__':
    #test_dis()
    #test_profile()
    test_cProfile()
    
    
    
    
    
    
    
