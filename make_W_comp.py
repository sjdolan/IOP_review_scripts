import ROOT
from ROOT import gStyle, TGaxis, TPad, TLine, gROOT, TH1, TColor, TCanvas, TFile, TH1D, gPad, TLegend, kWhite, gDirectory
from glob import glob

## No need to see the plots appear here
gROOT.SetBatch(1)
gStyle.SetLineWidth(3)
gStyle.SetOptStat(0)
gStyle.SetOptTitle(0)
gStyle.SetOptFit(0)
TGaxis.SetMaxDigits(4)
gStyle.SetLineStyleString(11,"40 20 40 20")
gStyle.SetLineStyleString(12,"20 10 20 10")

gStyle.SetTextSize(0.05)
gStyle.SetLabelSize(0.05,"xyzt")
gStyle.SetTitleSize(0.05,"xyzt")

gStyle.SetPadTickX(1)
gStyle.SetPadTickY(1)
gStyle.SetNdivisions(505, "XY")

gROOT .ForceStyle()

TH1.SetDefaultSumw2()
gStyle.SetLineWidth(3)

## Sort out the position of the y axis exponent...
TGaxis.SetExponentOffset(-0.06, 0., "y")

## Make some colorblind friendly objects
## From: https://personal.sron.nl/~pault/#sec:qualitative

kkBlue = TColor.GetFreeColorIndex()
ckBlue = TColor(kkBlue,   0./255., 119./255., 187./255., "kkBlue", 1.0)

kkCyan    = TColor.GetFreeColorIndex()
ckCyan = TColor(kkCyan,  51./255., 187./255., 238./255., "kkCyan", 1.0)

kkTeal    = TColor.GetFreeColorIndex()
ckTeal = TColor(kkTeal,   0./255., 153./255., 136./255., "kkTeal", 1.0)

kkOrange  = TColor.GetFreeColorIndex()
ckOrange = TColor(kkOrange, 238./255., 119./255.,  51./255., "kkOrange", 1.0)

kkRed     = TColor.GetFreeColorIndex()
ckRed = TColor(kkRed, 204./255.,  51./255.,  17./255., "kkRed", 1.0)

kkMagenta = TColor.GetFreeColorIndex()
ckMagenta = TColor(kkMagenta, 238./255.,  51/255., 119./255., "kkMagenta", 1.0)

kkGray = TColor.GetFreeColorIndex()
ckGray = TColor(kkGray, 187./255., 187./255., 187./255., "kkGray", 1.0)

# kkBlue    = TColor(9000,   0/255., 119/255., 187/255.)
# kkCyan    = TColor(9001,  51/255., 187/255., 238/255.)
# kkTeal    = TColor(9002,   0/255., 153/255., 136/255.)
# kkOrange  = TColor(9003, 238/255., 119/255.,  51/255.)
# kkRed     = TColor(9004, 204/255.,  51/255.,  17/255.)
# kkMagenta = TColor(9005, 238/255.,  51/255., 119/255.)
# kkGray    = TColor(9006, 187/255., 187/255., 187/255.)

can = TCanvas("can", "can", 600, 1000)
can .cd()

def get_chain(inputFileNames, max_files=999):

    print("Found", inputFileNames)
    inFile   = ROOT.TFile(glob(inputFileNames)[0], "READ")
    inFlux   = None
    inEvt    = None
    treeName = None
    nFiles   = 0

    for key in inFile.GetListOfKeys():
        if "FLUX" in key.GetName():
            inFlux = inFile.Get(key.GetName())
            inFlux .SetDirectory(0)
        if "VARS" in key.GetName():
            treeName = key.GetName()
    
    inFile .Close()
    
    inTree = ROOT.TChain(treeName)
    for inputFileName in glob(inputFileNames):

        nFiles += 1
        if nFiles > max_files: break
        
        inTree.Add(inputFileName)

        ## Add the histograms up
        inFile   = ROOT.TFile(inputFileName, "READ")
        for key in inFile.GetListOfKeys():
            if "EVT" not in key.GetName(): continue
            tempEvt = inFile.Get(key.GetName())
            if not inEvt:
                inEvt = tempEvt
                inEvt .SetDirectory(0)
            else: inEvt.Add(tempEvt)
        inFile.Close()    

    print("Found", inTree.GetEntries(), "events in chain")

    return inTree, inFlux, inEvt, nFiles

def make_generator_comp(outPlotName, inFileList, nameList, colzList, \
                        plotVar="q0", binning="100,0,5", cut="cc==1", \
                        labels="q_{0} (GeV); d#sigma/dq_{0} (#times 10^{-38} cm^{2}/nucleon)",
                        isShape=False, maxVal=None):
    isLog = False
    histList = []
    ratList  = []
    
    can     .cd()
    top_pad = TPad("top_pad", "top_pad", 0, 0.4, 1, 1)
    top_pad .Draw()
    bot_pad = TPad("bot_pad", "bot_pad", 0, 0, 1, 0.4)
    bot_pad .Draw()
    top_pad .cd()
    ratio = 0.6/0.4

    titleSize = 0.05
    labelSize = 0.04
    
    ## Loop over the input files and make the histograms
    for inFileName in inFileList:

        ## Modify to use glob
        inTree, inFlux, inEvt, nFiles = get_chain(inFileName)
        
        inTree.Draw(plotVar+">>this_hist("+binning+")", "("+cut+")*fScaleFactor")
        thisHist = gDirectory.Get("this_hist")
        thisHist .SetDirectory(0)

        ## Deal with different numbers of files
        thisHist.Scale(1./nFiles)

        ## Allow for shape option
        if isShape: thisHist .Scale(1/thisHist.Integral())

        ## Retain for use
        thisHist .SetNameTitle("thisHist", "thisHist;"+labels)
        histList .append(thisHist)

    ## Sort out the ratio hists
    nomHist = histList[0].Clone()
    for hist in histList:
        rat_hist = hist.Clone()
        rat_hist .Divide(nomHist)
        ratList  .append(rat_hist)
        
    ## Get the maximum value
    if not maxVal:
        maxVal   = 0
        for hist in histList:
            if hist.GetMaximum() > maxVal:
                maxVal = hist.GetMaximum()        
        maxVal = maxVal*1.1
        
    ## Actually draw the histograms
    histList[0].Draw("HIST")
    histList[0].SetMaximum(maxVal)

    ## Unify title/label sizes
    histList[0] .GetYaxis().SetTitleSize(titleSize)
    histList[0] .GetYaxis().SetLabelSize(labelSize)
    histList[0] .GetYaxis().SetTitleOffset(1.4)
    
    ## Suppress x axis title and labels
    histList[0] .GetXaxis().SetTitle("")
    histList[0] .GetXaxis().SetTitleSize(0.0)
    histList[0] .GetXaxis().SetLabelSize(0.0)
    
    if not isLog: histList[0].SetMinimum(0)
    for x in reversed(range(len(histList))):
        histList[x].SetLineWidth(3)
        histList[x].SetLineColor(colzList[x])
        histList[x].Draw("HIST SAME")

    
    ## Now make a legend
    dim = [0.2, 0.85, 0.98, 1.00]
    leg = TLegend(dim[0], dim[1], dim[2], dim[3], "", "NDC")
    leg .SetShadowColor(0)
    leg .SetFillColor(0)
    leg .SetLineWidth(0)
    leg .SetTextSize(0.036)
    leg .SetNColumns(3)
    leg .SetLineColor(kWhite)
    for hist in range(len(histList)):
        leg .AddEntry(histList[hist], nameList[hist], "l")
    leg .Draw("SAME")

    gPad.SetLogy(0)
    if isLog: gPad.SetLogy(1)
    gPad.SetRightMargin(0.02)
    gPad.SetTopMargin(0.15)
    gPad.SetLeftMargin(0.15)
    gPad.SetBottomMargin(0.022)
    gPad.RedrawAxis()
    gPad.Update()

    ## Now ratios on the bottom panel
    bot_pad.cd()

    ## Skip ratList[0] as everything is a ratio w.r.t that
    ratList[1] .Draw("][ HIST")
    ratList[1] .SetMaximum(1.5)
    ratList[1] .SetMinimum(0.5)

    ratList[1] .GetYaxis().SetTitle("Ratio w.r.t. "+nameList[0])
    ratList[1] .GetYaxis().CenterTitle(1)
    ratList[1] .GetXaxis().CenterTitle(0)
    ratList[1] .GetYaxis().SetTitleOffset(0.85)    
    ratList[1] .GetXaxis().SetNdivisions(505)
    ratList[1] .GetXaxis().SetTickLength(histList[0].GetXaxis().GetTickLength()*ratio)
    ratList[1] .GetXaxis().SetTitleSize(titleSize*ratio)
    ratList[1] .GetXaxis().SetLabelSize(labelSize*ratio)
    ratList[1] .GetYaxis().SetTitleSize(titleSize*ratio)
    ratList[1] .GetYaxis().SetLabelSize(labelSize*ratio)

    for x in reversed(range(1, len(histList))):
        ratList[x].SetLineWidth(3)
        ratList[x].SetLineColor(colzList[x])
        ratList[x].Draw("][ HIST SAME")

    midline = TLine(ratList[1].GetXaxis().GetBinLowEdge(1), 1, ratList[1].GetXaxis().GetBinUpEdge(ratList[1].GetNbinsX()), 1)
    midline .SetLineWidth(3)
    midline .SetLineColor(ROOT.kBlack)
    midline .SetLineStyle(11)
    midline .Draw("LSAME")
    
    ## Save
    gPad  .RedrawAxis()
    gPad  .SetRightMargin(0.02)
    gPad  .SetTopMargin(0.00)
    gPad  .SetBottomMargin(0.25)
    gPad  .SetLeftMargin(0.15)
    can   .Update()
    can .SaveAs("plots/"+outPlotName)

   
def make_generator_comp_by_mode(outPlotName, inFileList, nameList, colzList, \
                                       plotVar="q0", binning="100,0,5", cut="cc==1", \
                                       labels="q_{0} (GeV); d#sigma/dq_{0} (#times 10^{-38} cm^{2}/nucleon)",
                                       isShape=False, maxVal=None, modeSplit="QELike"):
    isLog = False

    modeList = []
    modeNameList = []

    
    can     .cd()
    top_pad = TPad("top_pad", "top_pad", 0, 0.4, 1, 1)
    top_pad .Draw()
    bot_pad = TPad("bot_pad", "bot_pad", 0, 0, 1, 0.4)
    bot_pad .Draw()
    top_pad .cd()
    ratio = 0.6/0.4

    titleSize = 0.05
    labelSize = 0.04

    if (modeSplit=="QELike"):
        modeList = ["abs(Mode)!=0", "abs(Mode)==1", "abs(Mode)==2", "abs(Mode)>2"]
        modeNameList = ["Total", "CCQE", "CC2p2h", "CC#pi abs."]
    elif (modeSplit=="CCInc"):
        modeList = ["abs(Mode)!=0", "abs(Mode)==1", "abs(Mode)==2", "abs(Mode)>10 && abs(Mode)<21", "abs(Mode)>21"]
        modeNameList = ["Total", "CCQE", "CC2p2h", "CCSPP", "CCDIS"]       
    elif (modeSplit=="DUNETopo"):
        modeList = ["abs(Mode)!=0",\
                    "Sum$(abs(pdg) == 211)==0 && Sum$(abs(pdg) == 2112)==0",\
                    "Sum$(abs(pdg) == 211)>0  && Sum$(abs(pdg) == 2112)==0",\
                    "Sum$(abs(pdg) == 211)==0  && Sum$(abs(pdg) == 2112)>0",\
                    "Sum$(abs(pdg) == 211)>0  && Sum$(abs(pdg) == 2112)>0"]
        modeNameList = ["Total", "CC0#pi^{+/-}0n", "CCN#pi^{+/-}0n","CCp#pi^{+/-}Nn", "CCN#pi^{+/-}Nn"]  
    elif (modeSplit=="T2KTopo"):
        modeList = ["abs(Mode)!=0",\
                    "Sum$(abs(pdg) == 211)==0 && Sum$(abs(pdg) == 111)==0",\
                    "Sum$(abs(pdg) == 211)>0  && Sum$(abs(pdg) == 111)==0",\
                    "Sum$(abs(pdg) == 211)==0  && Sum$(abs(pdg) == 111)>0",\
                    "Sum$(abs(pdg) == 211)>0  && Sum$(abs(pdg) == 111)>0"]
        modeNameList = ["Total", "CC0#pi^{+/-}", "CCN#pi^{+/-}0pi^{0}","CCp#pi^{+/-}Npi^{0}", "CCN#pi^{+/-}Npi^{0}"] 

    i=-1

    #print(modeNameList)
    
    ## Loop over the input files and make the histograms
    for inFileName in inFileList:

        ## Global counter for which file we're processing
        i=i+1

        ## Uncomment to only process GENIE 10a
        #if(i>0): break

        ## Modify to use glob
        inTree, inFlux, inEvt, nFiles = get_chain(inFileName)
    
        j=-1
        totHistInt=0;
        histList = []
        ratList  = []
        for mode in modeList:
            j=j+1
            inTree.Draw(plotVar+">>this_hist"+str(i)+str(j)+"("+binning+")", "("+cut+")*("+mode+")*fScaleFactor*1E38")
            thisHist = gDirectory.Get("this_hist"+str(i)+str(j)+"")
            thisHist .SetDirectory(0)

            ## Deal with different numbers of files
            thisHist.Scale(1./nFiles)

            if(j==0): totHistInt=thisHist.Integral()

            ## Allow for shape option
            if (isShape): thisHist .Scale(1/totHistInt)
            else: thisHist.Scale(1E-38)

            ## Retain for use
            thisHist .SetNameTitle("thisHist"+str(i)+str(j), "thisHist"+str(i)+str(j)+";"+labels)
            histList .append(thisHist)

        ## Sort out the ratio hists
        nomHist = histList[0].Clone()
        for hist in histList:
            rat_hist = hist.Clone()
            rat_hist .Divide(nomHist)
            ratList  .append(rat_hist)
            
        ## Get the maximum value
        if not maxVal:
            maxVal   = 0
            for hist in histList:
                if hist.GetMaximum() > maxVal:
                    maxVal = hist.GetMaximum()        
            maxVal = maxVal*1.1
            
        ## Actually draw the histograms
        histList[0].Draw("HIST")
        histList[0].SetMaximum(maxVal)

        ## Unify title/label sizes
        histList[0] .GetYaxis().SetTitleSize(titleSize)
        histList[0] .GetYaxis().SetLabelSize(labelSize)
        histList[0] .GetYaxis().SetTitleOffset(1.4)
        
        ## Suppress x axis title and labels
        histList[0] .GetXaxis().SetTitle("")
        histList[0] .GetXaxis().SetTitleSize(0.0)
        histList[0] .GetXaxis().SetLabelSize(0.0)
        
        if not isLog: histList[0].SetMinimum(0)
        for x in reversed(range(len(histList))):
            histList[x].SetLineWidth(3)
            histList[x].SetLineColor(colzList[x])
            histList[x].Draw("HIST SAME")

        
        ## Now make a legend
        dim = [0.2, 0.85, 0.98, 1.00]
        leg = TLegend(dim[0], dim[1], dim[2], dim[3], "", "NDC")
        leg .SetShadowColor(0)
        leg .SetFillColor(0)
        leg .SetLineWidth(0)
        leg .SetTextSize(0.036)
        leg .SetNColumns(3)
        leg .SetLineColor(kWhite)
        for hist in range(len(histList)):
            leg .AddEntry(histList[hist], modeNameList[hist], "l")
        #    print(modeNameList[hist])
        leg .Draw("SAME")
        leg.Print()

        gPad.SetLogy(0)
        if isLog: gPad.SetLogy(1)
        gPad.SetRightMargin(0.02)
        gPad.SetTopMargin(0.15)
        gPad.SetLeftMargin(0.15)
        gPad.SetBottomMargin(0.022)
        gPad.RedrawAxis()
        gPad.Update()



        ## Now ratios on the bottom panel
        bot_pad.cd()

        ## Skip ratList[0] as everything is a ratio w.r.t that
        ratList[1] .Draw("][ HIST")
        ratList[1] .SetMaximum(1.1)
        ratList[1] .SetMinimum(0.0)

        ratList[1] .GetYaxis().SetTitle("Ratio w.r.t. "+modeNameList[0])
        ratList[1] .GetYaxis().CenterTitle(1)
        ratList[1] .GetXaxis().CenterTitle(0)
        ratList[1] .GetYaxis().SetTitleOffset(0.85)    
        ratList[1] .GetXaxis().SetNdivisions(505)
        ratList[1] .GetXaxis().SetTickLength(histList[0].GetXaxis().GetTickLength()*ratio)
        ratList[1] .GetXaxis().SetTitleSize(titleSize*ratio)
        ratList[1] .GetXaxis().SetLabelSize(labelSize*ratio)
        ratList[1] .GetYaxis().SetTitleSize(titleSize*ratio)
        ratList[1] .GetYaxis().SetLabelSize(labelSize*ratio)

        for x in reversed(range(1, len(histList))):
            ratList[x].SetLineWidth(3)
            ratList[x].SetLineColor(colzList[x])
            ratList[x].Draw("][ HIST SAME")

        midline = TLine(ratList[1].GetXaxis().GetBinLowEdge(1), 1, ratList[1].GetXaxis().GetBinUpEdge(ratList[1].GetNbinsX()), 1)
        midline .SetLineWidth(3)
        midline .SetLineColor(ROOT.kBlack)
        midline .SetLineStyle(11)
        midline .Draw("LSAME")
        
        ## Save
        gPad  .RedrawAxis()
        gPad  .SetRightMargin(0.02)
        gPad  .SetTopMargin(0.00)
        gPad  .SetBottomMargin(0.25)
        gPad  .SetLeftMargin(0.15)
        can   .Update()
        can .SaveAs("plots/"+nameList[i]+"_"+outPlotName)

        #for x in range(len(histList)):
        #    histList[x].Delete()

        #for x in range(len(ratList)):
        #    ratList[x].Delete()

        histList.clear()
        ratList.clear() 

def make_T2K_W_plots(inputDir="inputs/"):

    nameList = ["GENIE 10a",\
                #"GENIE 10b",\
                #"GENIE 10c",\
                #"CRPA",\
                #"SuSAv2",\
                "NEUT",\
                "NuWro"\
                ]
    #colzList = [9000, 9001, 9002, 9003, 9004, 9006, 9005]
    #colzList = [1, 2, 3, 4, 7, 8, 11, 6]
    colzList = [1, kkBlue, kkCyan, kkTeal, kkOrange, kkRed, kkMagenta, kkGray]
    
    ## QE reco
    qe_cut = "cc==1 && Sum$(abs(pdg) > 100 && abs(pdg) < 2000)==0 && Sum$(abs(pdg) > 2300 && abs(pdg) < 100000)==0"

    ## Loop over configs
    for det in ["T2KND", "T2KSK_osc"]:
        for flux in ["FHC_numu", "RHC_numubar"]:
            ## These files can be found here (no login required): https://portal.nersc.gov/project/dune/data/2x2/simulation
            inFileList = [inputDir+"/"+det+"_"+flux+"_H2O_GENIEv3_G18_10a_00_000_1M_*_NUISFLAT.root",\
                          #inputDir+"/"+det+"_"+flux+"_H2O_GENIEv3_G18_10b_00_000_1M_*_NUISFLAT.root",\
                          #inputDir+"/"+det+"_"+flux+"_H2O_GENIEv3_G18_10c_00_000_1M_*_NUISFLAT.root",\
                          #inputDir+"/"+det+"_"+flux+"_H2O_GENIEv3_CRPA21_04a_00_000_1M_*_NUISFLAT.root",\
                          #inputDir+"/"+det+"_"+flux+"_H2O_GENIEv3_G21_11a_00_000_1M_*_NUISFLAT.root",\
                          inputDir+"/"+det+"_"+flux+"_H2O_NEUT562_1M_*_NUISFLAT.root",\
                          inputDir+"/"+det+"_"+flux+"_H2O_NUWRO_LFGRPA_1M_*_NUISFLAT.root"\
                          ]
            
            make_generator_comp(det+"_"+flux+"_H2O_W_0pi_gencomp.png", inFileList, nameList, colzList, "W", "40,0.5,1.5", qe_cut, \
                                "W (GeV); d#sigma/dW (#times 10^{-38} cm^{2}/nucleon)", False)

            make_generator_comp(det+"_"+flux+"_H2O_W_CCinc_gencomp.png", inFileList, nameList, colzList, "W", "40,0.5,3", "cc==1", \
                                "W (GeV); d#sigma/dW (#times 10^{-38} cm^{2}/nucleon)", False)  

            make_generator_comp_by_mode(det+"_"+flux+"_H2O_W_0pi_modecomp.png", inFileList, nameList, colzList, "W", "40,0.5,1.5", qe_cut, \
                                "W (GeV); d#sigma/dW (#times 10^{-38} cm^{2}/nucleon)", False, None, "QELike")

            make_generator_comp_by_mode(det+"_"+flux+"_H2O_W_0pi_T2KTopocomp.png", inFileList, nameList, colzList, "W", "40,0.5,1.5", qe_cut, \
                                "W (GeV); d#sigma/dW (#times 10^{-38} cm^{2}/nucleon)", False, None, "T2KTopo")

            #make_generator_comp_by_mode(det+"_"+flux+"_H2O_W_CCinc_modecomp.png", inFileList, nameList, colzList, "W", "40,0,3", "cc==1", \
            #                    "W (GeV); d#sigma/dE_{#nu}^{rec, had} (#times 10^{-38} cm^{2}/nucleon)", False, None, "CCInc")
        
            
def make_DUNE_W_plots(inputDir="inputs/"):

    nameList = ["GENIE 10a",\
                #"GENIE 10b",\
                #"GENIE 10c",\
                #"CRPA",\
                #"SuSAv2",\
                "NEUT",\
                "NuWro"\
                ]
    #colzList = [9000, 9001, 9002, 9003, 9004, 9006, 9005]
    #colzList = [1, 2, 3, 4, 7, 8, 11, 6]
    colzList = [1, kkBlue, kkCyan, kkTeal, kkOrange, kkRed, kkMagenta, kkGray]

    
    ## QE reco
    ehad_cut = "cc==1"
    enuhad = "ELep + Sum$((abs(pdg)==11 || (abs(pdg)>17 && abs(pdg)<2000))*E) + Sum$((abs(pdg)>2300 &&abs(pdg)<10000)*E) + Sum$((abs(pdg)==2212)*(E - sqrt(E*E - px*px - py*py - pz*pz)))"

    ## Loop over configs
    for det in ["DUNEND", "DUNEFD_osc"]:
        for flux in ["FHC_numu", "RHC_numubar"]:
            ## These files can be found here (no login required): https://portal.nersc.gov/project/dune/data/2x2/simulation
            inFileList = [inputDir+"/"+det+"_"+flux+"_Ar40_GENIEv3_G18_10a_00_000_1M_*_NUISFLAT.root",\
                          #inputDir+"/"+det+"_"+flux+"_Ar40_GENIEv3_G18_10b_00_000_1M_*_NUISFLAT.root",\
                          #inputDir+"/"+det+"_"+flux+"_Ar40_GENIEv3_G18_10c_00_000_1M_*_NUISFLAT.root",\
                          #inputDir+"/"+det+"_"+flux+"_Ar40_GENIEv3_CRPA21_04a_00_000_1M_*_NUISFLAT.root",\
                          #inputDir+"/"+det+"_"+flux+"_Ar40_GENIEv3_G21_11a_00_000_1M_*_NUISFLAT.root",\
                          inputDir+"/"+det+"_"+flux+"_Ar40_NEUT562_1M_*_NUISFLAT.root",\
                          inputDir+"/"+det+"_"+flux+"_Ar40_NUWRO_LFGRPA_1M_*_NUISFLAT.root"\
                          ]
            

            #make_generator_comp(det+"_"+flux+"_Ar40_W_CCinc_gencomp.png", inFileList, nameList, colzList, "W", "40,0.5,3", "cc==1", \
            #                                  "W (GeV); d#sigma/dW (#times 10^{-38} cm^{2}/nucleon)", False)   
            
            make_generator_comp_by_mode(det+"_"+flux+"_Ar40_W_CCinc_modecomp.png", inFileList, nameList, colzList, "W", "40,0.5,3", "cc==1", \
                                "W (GeV); d#sigma/dW (#times 10^{-38} cm^{2}/nucleon)", False, None, "CCInc")

            #make_generator_comp_by_mode(det+"_"+flux+"_Ar40_W_CCinc_topocomp.png", inFileList, nameList, colzList, "W", "40,0.5,3", "cc==1", \
            #                    "W (GeV); d#sigma/dW (#times 10^{-38} cm^{2}/nucleon)", False, None, "DUNETopo")
            
if __name__ == "__main__":

    inputDir="/global/cfs/cdirs/dune/users/cwilk/MC_IOP_review/*/"
    #make_T2K_W_plots(inputDir)
    make_DUNE_W_plots(inputDir)
