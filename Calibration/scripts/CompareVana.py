#######################################################
# CompareVana.py
# Original author: M. Malberti 02/12/2013
# This script takes as input two dac dirs and 
# compares the values of a chosen dac parameter roc 
# by roc. The parameter can be chosen, default is Vana.
#######################################################

import os
import sys
import ROOT
from ROOT import *
import itertools

def ReadDacSettings(dir,dac):
    files = [file for file in os.listdir(dir)]
    # fill dictionary with key = roc, value = vana 
    vanadict = {}
    for f in files:
        file = open(dir+'/'+f)
        # group dac settings via a separator - the group separator is ROC
        for key,group in itertools.groupby(file,isa_group_separator):
            for item in group:
                if key:
                    roc,name = item.split()
                else:
                    if dac in item:
                        vana,value = item.split()
#                        print roc,name
#                        print vana,value
                        vanadict[name] = value
    return vanadict
        
def isa_group_separator(line):
    return 'ROC:' in line


def MakeScatterPlot(d1,d2,par,min,max):
    nbins = int(max - min)/2
    h = TH2F("h","h",nbins,min,max,nbins,min,max)
    title = '%s (T = 0#circC)'%par
    h.SetXTitle(title)
    title = '%s (T = -20#circC)'%par
    h.SetYTitle(title)
    h.SetMarkerColor(kBlack)
    h.SetLineColor(kBlack)
    h.SetMarkerStyle(20)
    h.SetMarkerSize(0.1)
    
    for roc in d1:
        v1 = float(d1[roc])
        v2 = float(d2[roc])
        #if ('PLQ2' in roc):
        h.Fill(v1,v2)
        
    tp,fun = MakeFit(h)    
    return h,tp,fun


def MakeFit(h):
    tp = h.ProfileX()
    tp.SetLineColor(kRed)
    tp.SetMarkerColor(kRed)
    tp.SetMarkerSize(0.5)
    
    average = int(h.GetMean())
    print 'Average %s = %d'%(options.parameter,average)
    formula = "%d+[0]+[1]*(x-%d)"%(average,average)
    f1 = TF1("f1",formula,options.min,options.max)
    f1.SetLineStyle(2)
    f1.SetLineWidth(1)
    f1.SetLineColor(kRed)
    tp.Fit("f1","S")
    print '%s = %d at %s = %d'%(options.parameter,f1.Eval(average-2*h.GetRMS()), options.parameter,average-2*h.GetRMS())
    print '%s = %d at %s = %d'%(options.parameter,f1.Eval(average), options.parameter,average)
    print '%s = %d at %s = %d'%(options.parameter,f1.Eval(average+2*h.GetRMS()), options.parameter,average+2*h.GetRMS())
    
    return tp, f1

from optparse import OptionParser
parser = OptionParser()
parser.add_option("--dac1",dest="dac1",type="string",default="PCDE_BmI/dac/67",help="Name of first dac dir")
parser.add_option("--dac2",dest="dac2",type="string",default="PCDE_BmI/dac/91",help="Name of second dac dir")
parser.add_option("-p","--parameter",dest="parameter",type="string",default="Vana",help="Name of dac. Default is Vana")
parser.add_option("--min",dest="min",type="float",default=80,help="Minimum value of dac")
parser.add_option("--max",dest="max",type="float",default=200,help="Maximum value of dac")

(options,args)=parser.parse_args()

ROOT.gStyle.SetOptStat(1110)
ROOT.gStyle.SetOptFit(111)
ROOT.gStyle.SetOptTitle(0)
ROOT.gStyle.SetTitleXOffset(1.2)
ROOT.gStyle.SetTitleYOffset(1.3)
ROOT.gStyle.SetStatX(0.89);
ROOT.gStyle.SetStatY(0.4);
ROOT.gStyle.SetStatH(0.125);


vana1 = ReadDacSettings(options.dac1,options.parameter)
vana2 = ReadDacSettings(options.dac2,options.parameter)



h,tp,f1 = MakeScatterPlot(vana1,vana2,options.parameter,options.min,options.max)

c=TCanvas("c","c",500,500)
c.SetGridy()
c.SetGridx()
h.Draw("box")
tp.Draw("same")
f1.Draw("same")
    
f2 = TF1("f2","x",0,options.max)
f2.SetLineStyle(3)
f2.SetLineWidth(1)
f2.SetLineColor(kBlack)
f2.Draw("same")

raw_input('ok?')

cname = '%sComparison'%options.parameter
c.SaveAs(cname+'.png')    
c.SaveAs(cname+'.pdf')    
