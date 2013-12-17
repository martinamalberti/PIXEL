#######################################################################
# PixelAliveAnalysisForThr.py
# Original author : M . Malberti 17/12/2013
#
#######################################################################

import os
import sys
from ROOT import *
import itertools



pixelAnalysisExe   = './bin/linux/x86_64_slc5/PixelAnalysis.exe'
config             = 'configuration/PixelAliveAnalysis.xml'
#rundir             = os.environ['POS_OUTPUT_DIRS']
#dacdir             = os.environ['PIXELCONFIGURATIONBASE']+'/dac'

rundir             = './'
dacdir             = '/Users/malberti/Work/CMS/PIXEL/Calibrations/PCDE_BmI/dac'


def RunPixelAliveAnalysis(run):
    currentdir = os.getcwd() 
    cmd = '%s %s %d'%(pixelAnalysisExe, config, run)
    os.system(cmd) 


def CheckEfficiency(run, outfilename):
    
    maxeff = 100
    maxDeadPixels = 10
    numPixels = 4160
    numFailingRocs = 0

    # prepare output file where ROCs failing PixelAlive will be written
    outfile = open(outfilename,'w')

    # open PixelAlive root file to be analyzed
    #path = '%s/Run_%d/Run_%d/%s' % (rundir,runfolder(run),run)
    #files = [ file for file in os.listdir('%d'%path) if 'PixelAlive_Fed_' in file]
    #if len(files!=1):
    #    sys.exit('PixelAlive root file NOT found !!!')
    #file = TFile( '%s/Run_%d/Run_%d/%s' % (rundir,runfolder(run),run,files[0]) )
    file = TFile('PixelAlive_Fed_37-38_Run_1171.root')
    
    FPix.cd()
   
    for obj0 in gDirectory.GetListOfKeys(): #FPix_BmI
        if obj0.IsFolder():
            obj0.ReadObj().cd()

            for obj1 in gDirectory.GetListOfKeys(): # DISK folder 
                if obj1.IsFolder():
                    obj1.ReadObj().cd()

                    for obj2 in gDirectory.GetListOfKeys(): ## BLD folder
                        if  obj2.IsFolder():
                            obj2.ReadObj().cd()

                            for obj3 in gDirectory.GetListOfKeys(): ## PNL folder
                                if  obj3.IsFolder():
                                    obj3.ReadObj().cd()

                                    for obj4 in gDirectory.GetListOfKeys(): ## PLQ folder
                                        if  obj4.IsFolder():
                                            obj4.ReadObj().cd()

                                            for obj5 in gDirectory.GetListOfKeys(): ## ROC folder: find one TH2F for each ROC
                                                histo = obj5.ReadObj()
                                                hname   = histo.GetName()
                                                xBins   = histo.GetNbinsX()
                                                yBins   = histo.GetNbinsY()
 
                                                # count dead pixels in each roc
                                                numDeadPixels=0
                                                for x in range(1,xBins):
                                                    for y in range(1,yBins):
                                                        if histo.GetBinContent(x,y) < maxeff:
                                                            numDeadPixels=numDeadPixels+1;
                                                if (numDeadPixels > maxDeadPixels):
                                                    numFailingRocs=numFailingRocs+1
                                                    rocname = hname.replace('(inv)','')
                                                    print '%s - Number of dead pixels = %d' %(rocname,numDeadPixels)
                                                    outfile.write('%s\n'%rocname)

    print 'Number of failing ROCs = %d'% numFailingRocs
    outfile.close()
    


def ChangeVcThr(run,dac,failed):

    currentdir = os.getcwd()

    #read file containing the list of rocs that failed the PixelAlive
    ffailed = open(failed,'r')
    failedrocs = [line.replace('\n','') for line in ffailed]
    print failedrocs
    
    #prepare dir for new dac settings
    tmpdir = 'new'
    cmd = 'mkdir %s'%tmpdir
    os.system(cmd)
    
    #take dac settings used for the previous PixelAlive run
    cmd = 'cp  %s/%s/*.dat ./'%(dacdir,dac)
    os.system(cmd)

    #change VcThr: if ROC passed PixelAlive then VcThr+2, if failed VcThr-4
    files = [file for file in os.listdir('./') if 'ROC_DAC_module' in file]
    for f in files:
        fileold = open(f)
        filenew = open('%s/%s'%(tmpdir,f),'w')
        # group dac settings via a separator - the group separator is ROC
        for key,group in itertools.groupby(fileold,isa_group_separator):
            for item in group:
                if key:
                    roc,name = item.split()
                    filenew.write(item)
                elif 'VcThr' in item:
                    vcthr,value = item.split()
                    if name in failedrocs:
                        newvalue = int(value)-4 
                    else: 
                        newvalue = int(value)+2
                    filenew.write('VcThr:         %d\n'%newvalue)
                else:
                    filenew.write(item)
        fileold.close()
        filenew.close()


def isa_group_separator(line):
    return 'ROC:' in line



def MakeNewDacSettings():
    currentdir = os.getcwd()

    cmd = 'cd %s'%dacdir
    os.chdir('%s'%dacdir)
        
    # make list of subdirectories in dac/ directory    
    subdirs = [ int(x) for x in os.walk('.').next()[1] ]
    subdirs.sort()
    print 'Last dac dir : ', subdirs[-1]    
    lastsettings = subdirs[-1]
    newsettings = subdirs[-1]+1
    cmd = 'cp -r %d %d'%(lastsettings,newsettings)
    os.system(cmd)
 
    cmd = 'cd %s'%currentdir
    os.chdir('%s'%currentdir)

    cmd = 'cp new/ROC_DAC_module_FPix*dat %s/%d'%(dacdir,newsettings)    
    os.system(cmd)
        
    cmd = 'PixelConfigDBCmd.exe --insertVersionAlias dac %d Default'%newsettings
    print cmd
#    os.system(cmd)




from optparse import OptionParser
parser = OptionParser()
parser.add_option("-r","--run",dest="run",type="int",help="Run number")
parser.add_option("-d","--dac",dest="dac",type="string",help="dac")
parser.add_option("-o","--output",dest="output",type="string",help="Name of the output file")
(options,args)=parser.parse_args()

if not options.run or not options.dac or not options.output:
    sys.exit('Usage: PixelAliveAnalysisForThr -r <run> -d <dac> -o <outfile> \n Exiting.')

# --- analyze PixelAlive run
RunPixelAliveAnalysis(options.run)

# --- check the efficiecny of all ROCS and make a list of failed rocs (i.e. rocs with more than 10 dead pixels)
CheckEfficiency(options.run,options.output)

# --- prepare new dac settings by changing VcThr
ChangeVcThr(options.run,options.dac,options.output)
MakeNewDacSettings()



