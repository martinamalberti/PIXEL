#######################################################
# plotCurrents.py
# Original author: M. Malberti 02/12/2013
# This script plots the analog currents vs Vana iteration.
# It takes as input a txt file with the values of the
# currents for each readout group.
#######################################################
import os
import sys
import ROOT
from ROOT import *
ROOT.gStyle.SetOptStat(1110)
ROOT.gStyle.SetOptTitle(0)

file = open("BmI_T-20deg/currents_BmI_-20deg.log")
#file = open("BmI_T0deg/currents_BmI.log")
currents = [line.replace('Iteration ','').replace(':','').replace('\n','').split(' ') for line in file if 'Iteration' in line]
#print currents

max = len(currents)

# 1-D histogram
hcurrent = []
for iter in range(1,max+1):
    htmp = TH1F("hcurrent%d"%iter,"hcurrent%d"%iter,140,0,7)
    hcurrent.append(htmp)
    for rog in range(1,9):
        hcurrent[iter-1].Fill(float(currents[iter-1][rog]))


# currents vs iteration number
h2 = {}
for rog in range(1,9):
    h2[rog-1] = TH1F("hcurrent_vs_iter_%s"%rog,"hcurrent_vs_iter_%s"%rog,21,-0.5,20.5)
    h2[rog-1].SetLineColor(kBlue+rog%2) 
    for iter in range(1,max+1):
        h2[rog-1].Fill(iter,float(currents[iter-1][rog]))
        

c = TCanvas("c","c")
hcurrent[0].SetLineColor(kRed)
hcurrent[max-1].SetLineColor(kBlue)
hcurrent[max-1].GetXaxis().SetTitle("current/ROG (A)")
hcurrent[max-1].Draw()
hcurrent[0].Draw("sames")
 
cc=TCanvas("cc","cc")
cc.SetGridy()
hdummy =  TH2F("hdummy","", 21,-0.5,20.5,120,2,5)
hdummy.GetXaxis().SetRangeUser(1,max)
hdummy.SetXTitle("iteration")
hdummy.SetYTitle("current/redout group (A)")
hdummy.Draw()
for rog in range(1,9):
    h2[rog-1].Draw("lsame") 

raw_input('ok?')
