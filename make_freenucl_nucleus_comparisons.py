import ROOT
import os
from ROOT import gStyle, TGaxis, TPad, TLine, gROOT, TH1, TColor, TCanvas, TFile, TH1D, gPad, TLegend, kWhite, gDirectory, gEnv
from glob import glob

## Use double precision for TTree draw
gEnv.SetValue("Hist.Precision.1D", "double")

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
kkBlue    = TColor(9000,   0/255., 119/255., 187/255.)
kkCyan    = TColor(9001,  51/255., 187/255., 238/255.)
kkTeal    = TColor(9002,   0/255., 153/255., 136/255.)
kkOrange  = TColor(9003, 238/255., 119/255.,  51/255.)
kkRed     = TColor(9004, 204/255.,  51/255.,  17/255.)
kkMagenta = TColor(9005, 238/255.,  51/255., 119/255.)
kkGray    = TColor(9006, 187/255., 187/255., 187/255.)

can = TCanvas("can", "can", 600, 800)
can .cd()

can_small = TCanvas("can_small", "can_small", 600, 600)

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

def make_generator_comp_noratio(outPlotName, inFileList, legHeader, nameList, colzList, lineList, \
                                plotVarList=None, binning="100,0,5", cutList=None, \
                                labels="q_{0} (GeV); d#sigma/dq_{0} (#times 10^{-38} cm^{2}/nucleon)",
                                isShape=False, maxVal=None, legPosRight=True, saveFile=None):
    
    ## Skip files that already exist
    if os.path.isfile("plots/"+outPlotName):
        print("Skipping plots/"+outPlotName, "which already exists!")
        return
    
    isLog = False
    histList = []
    
    can_small.cd()

    titleSize = 0.055
    labelSize = 0.05

    nhists = len(inFileList)
    
    ## Loop over the input files and make the histograms
    for n in range(nhists):

        inFileName = inFileList[n]
        
        ## Modify to use glob
        inTree, inFlux, inEvt, nFiles = get_chain(inFileName)
        
        inTree.Draw(plotVarList[n]+">>this_hist("+binning+")", "("+cutList[n]+")*fScaleFactor*1E38")
        thisHist = gDirectory.Get("this_hist")
        thisHist .SetDirectory(0)

        ## Deal with different numbers of files
        thisHist.Scale(1./nFiles, "width")

        ## Allow for shape option
        if isShape: thisHist .Scale(1/thisHist.Integral())

        ## Retain for use
        thisHist .SetNameTitle(nameList[n], nameList[n]+";"+labels)
        histList .append(thisHist)

    ## Get the maximum value
    if not maxVal:
        maxVal   = 0
        for hist in histList:
            if hist.GetMaximum() > maxVal:
                maxVal = hist.GetMaximum()        
        maxVal = maxVal*1.1
        
    ## Actually draw the histograms
    histList[0].Draw("CHIST")
    histList[0].SetMaximum(maxVal)

    ## Unify title/label sizes
    histList[0] .GetYaxis().SetTitleSize(titleSize)
    histList[0] .GetYaxis().SetLabelSize(labelSize)
    histList[0] .GetYaxis().SetTitleOffset(1.3)
    
    ## Suppress x axis title and labels
    histList[0] .GetXaxis().SetTitleSize(titleSize)
    histList[0] .GetXaxis().SetLabelSize(labelSize)
    
    if not isLog: histList[0].SetMinimum(0)
    for x in reversed(range(len(histList))):
        histList[x].SetLineWidth(3)
        histList[x].SetLineColor(colzList[x])
        histList[x].SetLineStyle(lineList[x])
        histList[x].Draw("CHIST SAME")

    
    ## Now make a legend
    dim = [0.65, 0.6, 0.85, 0.95]

    if legPosRight==False:
        dim[0]=0.22
        dim[2]=0.40

    leg = TLegend(dim[0], dim[1], dim[2], dim[3], "", "NDC")
    leg .SetHeader(legHeader)
    leg .SetShadowColor(0)
    leg .SetFillColor(0)
    leg .SetLineWidth(0)
    leg .SetTextSize(0.05)
    leg .SetLineColor(kWhite)
    for hist in range(len(histList)):
        leg .AddEntry(histList[hist], nameList[hist], "l")
    leg .Draw("SAME")

    gPad.SetLogy(0)
    if isLog: gPad.SetLogy(1)
    gPad.SetRightMargin(0.03)
    gPad.SetTopMargin(0.02)
    gPad.SetLeftMargin(0.15)
    gPad.SetBottomMargin(0.15)
    gPad.RedrawAxis()
    gPad.Update()
    can_small .SaveAs("plots/"+outPlotName)

    ## Optionally save the histograms to a file
    if saveFile:
        outFile = TFile(saveFile, "RECREATE")
        outFile .cd()
        for hist in histList: hist.Write()
        outFile .Close()


def make_q0_breakdown_CC_DUNE(inputDir="inputs/"):

    nameList = ["CC-INC",\
                "CC-1p1h",\
                "CC-2p2h",\
                "CC-RPP",\
                "CC-SIS",\
                "CC-DIS"]
    colzList = [9000, 9001, 9002, 9003, 9006, 9005]
    lineList = [1, 1, 1, 1, 1, 1]
    cutList = ["cc==1", \
	       "cc==1 && abs(Mode) == 1 && Sum$(abs(pdg) > 3000 && abs(pdg) < 5000)==0", \
               "cc==1 && abs(Mode) == 2", \
               "cc==1 && (abs(Mode)==11 || abs(Mode)==12 || abs(Mode)==13)", \
               "cc==1 && abs(Mode)==21",\
               "cc==1 && abs(Mode)==26"]
    targ = "Ar40"
    binning="100,0,2.5"

    var_list=["q0", "q0", "q0", "q0", "q0", "q0"]
    
    ## DUNE ND
    det = "DUNEND"
    model="GENIEv3_G18_10a_00_000"
    for flux in ["FHC_numu", "RHC_numubar"]:
        flux_string = "#nu_{#mu}"
        if flux == "RHC_numubar": flux_string =	"#bar{#nu}_{#mu}"	
        inFileList = [inputDir+"/"+det+"_"+flux+"_"+targ+"_"+model+"_1M_*_NUISFLAT.root",\
                      inputDir+"/"+det+"_"+flux+"_"+targ+"_"+model+"_1M_*_NUISFLAT.root",\
                      inputDir+"/"+det+"_"+flux+"_"+targ+"_"+model+"_1M_*_NUISFLAT.root",\
                      inputDir+"/"+det+"_"+flux+"_"+targ+"_"+model+"_1M_*_NUISFLAT.root",\
                      inputDir+"/"+det+"_"+flux+"_"+targ+"_"+model+"_1M_*_NUISFLAT.root",\
                      inputDir+"/"+det+"_"+flux+"_"+targ+"_"+model+"_1M_*_NUISFLAT.root"]
        
        make_generator_comp_noratio(det+"_"+flux+"_Ar40_CC_"+model+"_q0_noratio.png", inFileList, flux_string+"-^{40}Ar", \
                                    nameList, colzList, lineList, var_list, binning, cutList, \
                                    "q_{0} (GeV); d#sigma/dq_{0} (#times 10^{-38} cm^{2}/nucleon)", False)

def make_W_breakdown_CC_DUNE(inputDir="inputs/"):

    nameList = ["CC-INC",\
                "CC-1p1h",\
                "CC-2p2h",\
		"CC-RPP",\
                "CC-SIS",\
                "CC-DIS"]
    colzList = [9000, 9001, 9002, 9003, 9006, 9005]
    lineList = [1, 1, 1, 1, 1, 1]
    cutList = ["cc==1", \
	       "cc==1 && abs(Mode) == 1 && Sum$(abs(pdg) > 3000 && abs(pdg) < 5000)==0", \
	       "cc==1 && abs(Mode) == 2", \
	       "cc==1 && (abs(Mode)==11 || abs(Mode)==12 || abs(Mode)==13)", \
	       "cc==1 && abs(Mode)==21",\
               "cc==1 && abs(Mode)==26"]
    targ = "Ar40"
    binning="80,0,4"

    var_list=["W", "W", "W", "W", "W", "W"]

    det = "DUNEND"
    model="GENIEv3_G18_10a_00_000"
    for flux in ["FHC_numu", "RHC_numubar"]:
        flux_string = "#nu_{#mu}"
        if flux == "RHC_numubar": flux_string =	"#bar{#nu}_{#mu}"
	inFileList = [inputDir+"/"+det+"_"+flux+"_"+targ+"_"+model+"_1M_*_NUISFLAT.root",\
                      inputDir+"/"+det+"_"+flux+"_"+targ+"_"+model+"_1M_*_NUISFLAT.root",\
                      inputDir+"/"+det+"_"+flux+"_"+targ+"_"+model+"_1M_*_NUISFLAT.root",\
                      inputDir+"/"+det+"_"+flux+"_"+targ+"_"+model+"_1M_*_NUISFLAT.root",\
                      inputDir+"/"+det+"_"+flux+"_"+targ+"_"+model+"_1M_*_NUISFLAT.root",\
                      inputDir+"/"+det+"_"+flux+"_"+targ+"_"+model+"_1M_*_NUISFLAT.root"]

	make_generator_comp_noratio(det+"_"+flux+"_Ar40_CC_"+model+"_W_noratio.png", inFileList, flux_string+"-^{40}Ar", \
                                    nameList, colzList, lineList, var_list, binning, cutList, \
                                    "W (GeV); d#sigma/dW (#times 10^{-38} cm^{2}/nucleon)", False)

        
def make_q0_breakdown_NC_DUNE(inputDir="inputs/"):

    nameList = ["NC-INC", \
                "NC-1p1h", \
                "NC-2p2h", \
                "NC-SPP", \
                "NC-DIS"\
                ]
    colzList = [9000, 9001, 9002, 9003, 9005]
    lineList = [1, 1, 1, 1, 1]
    cutList = ["cc==0", \
               "cc==0 && (abs(Mode)==51 || abs(Mode)==52)",\
               "cc==0 && abs(Mode)==53",\
               "cc==0 && (abs(Mode)==31 || abs(Mode)==32 || abs(Mode)==33 || abs(Mode)==34)",\
               "cc==0 && (abs(Mode)==41 || abs(Mode)==46)"\
               ]
    targ = "Ar40"
    binning="100,0,2.5"

    var_list=["q0", "q0", "q0", "q0", "q0"]

    ## DUNE ND
    det = "DUNEND"
    model="GENIEv3_G18_10a_00_000"
    for flux in ["FHC_numu", "RHC_numubar"]:
        flux_string = "#nu_{#mu}"
        if flux == "RHC_numubar": flux_string =	"#bar{#nu}_{#mu}"
        
	inFileList = [inputDir+"/"+det+"_"+flux+"_"+targ+"_"+model+"_1M_*_NUISFLAT.root",\
                      inputDir+"/"+det+"_"+flux+"_"+targ+"_"+model+"_1M_*_NUISFLAT.root",\
                      inputDir+"/"+det+"_"+flux+"_"+targ+"_"+model+"_1M_*_NUISFLAT.root",\
                      inputDir+"/"+det+"_"+flux+"_"+targ+"_"+model+"_1M_*_NUISFLAT.root",\
                      inputDir+"/"+det+"_"+flux+"_"+targ+"_"+model+"_1M_*_NUISFLAT.root"\
                      ]

	make_generator_comp_noratio(det+"_"+flux+"_Ar40_NC_"+model+"_q0_noratio.png", inFileList, flux_string+"-^{40}Ar",
                                    nameList, colzList, lineList, var_list, binning, cutList, \
                                    "q_{0} (GeV); d#sigma/dq_{0} (#times 10^{-38} cm^{2}/nucleon)", False)
        
def make_W_breakdown_CC_nucl(inputDir="inputs/"):

    nameList = ["CC-INC",\
	        "CC-QE",\
	        "CC-SPP",\
                "CC-DIS"]
    colzList = [9000, 9001,9003, 9005]
    lineList = [1, 1, 1, 1, 1]
    cutList = ["cc==1", \
               "cc==1 && abs(Mode) == 1 && Sum$(abs(pdg) > 3000 && abs(pdg) < 5000)==0", \
               "cc==1 && (abs(Mode)==11 || abs(Mode)==12 || abs(Mode)==13)", \
               "cc==1 && (abs(Mode)==21 || abs(Mode) == 26)"]
    binning="80,0,4"
    var_list=["W", "W", "W", "W", "W"]
    det = "DUNEND"
    model="GENIEv3_G18_10a_00_000"

    for flux in ["FHC_numu", "RHC_numubar"]:
        flux_string = "#nu_{#mu}"
        if flux == "RHC_numubar": flux_string = "#bar{#nu}_{#mu}"
        
        for targ in ["neutron", "proton"]:
	    inFileList = [inputDir+"/"+det+"_"+flux+"_"+targ+"_"+model+"_1M_*_NUISFLAT.root",\
                          inputDir+"/"+det+"_"+flux+"_"+targ+"_"+model+"_1M_*_NUISFLAT.root",\
                          inputDir+"/"+det+"_"+flux+"_"+targ+"_"+model+"_1M_*_NUISFLAT.root",\
                          inputDir+"/"+det+"_"+flux+"_"+targ+"_"+model+"_1M_*_NUISFLAT.root"]

            
            
	    make_generator_comp_noratio(det+"_"+flux+"_"+targ+"_CC_"+model+"_W_noratio.png", inFileList, flux_string+"-^{40}Ar", \
                                        nameList, colzList, lineList, var_list, binning, cutList, \
                                        "W (GeV); d#sigma/dW (#times 10^{-38} cm^{2}/nucleon)", False)

def make_q0_breakdown_CC_nucl(inputDir="inputs/"):

    nameList = ["CC-INC",\
                "CC-QE",\
		"CC-RPP",\
                "CC-SIS",\
                "CC-DIS"]
    colzList = [9000, 9001, 9003, 9006, 9005]
    lineList = [1, 1, 1, 1, 1]
    cutList = ["cc==1", \
               "cc==1 && abs(Mode) == 1 && Sum$(abs(pdg) > 3000 && abs(pdg) < 5000)==0", \
               "cc==1 && (abs(Mode)==11 || abs(Mode)==12 || abs(Mode)==13)", \
               "cc==1 && abs(Mode)==21", \
               "cc==1 && abs(Mode)==26"]
    binning="100,0,2.5"
    var_list=["q0", "q0", "q0", "q0", "q0", "q0"]
    det = "DUNEND"
    model="GENIEv3_G18_10a_00_000"

    for flux in ["FHC_numu", "RHC_numubar"]:
        flux_string = "#nu_{#mu}"
        if flux == "RHC_numubar": flux_string =	"#bar{#nu}_{#mu}"
        
	for targ in ["neutron", "proton"]:
            inFileList = [inputDir+"/"+det+"_"+flux+"_"+targ+"_"+model+"_1M_*_NUISFLAT.root",\
                          inputDir+"/"+det+"_"+flux+"_"+targ+"_"+model+"_1M_*_NUISFLAT.root",\
                          inputDir+"/"+det+"_"+flux+"_"+targ+"_"+model+"_1M_*_NUISFLAT.root",\
                          inputDir+"/"+det+"_"+flux+"_"+targ+"_"+model+"_1M_*_NUISFLAT.root",\
                          inputDir+"/"+det+"_"+flux+"_"+targ+"_"+model+"_1M_*_NUISFLAT.root"]

            make_generator_comp_noratio(det+"_"+flux+"_"+targ+"_CC_"+model+"_q0_noratio.png", inFileList, flux_string+"-"+str(targ), \
                                        nameList, colzList, lineList, var_list, binning, cutList, \
                                        "q_{0} (GeV); d#sigma/dq_{0} (#times 10^{-38} cm^{2}/nucleon)", False)

            
def make_q0_breakdown_NC_nucl(inputDir="inputs/"):

    nameList = ["NC-INC", \
                "NC-EL", \
                "NC-SPP", \
                "NC-DIS"\
		]
    colzList = [9000, 9001, 9003, 9005]
    lineList = [1, 1, 1, 1, 1]
    cutList = ["cc==0", \
               "cc==0 && (abs(Mode)==51 || abs(Mode)==52)",\
               "cc==0 && (abs(Mode)==31 || abs(Mode)==32 || abs(Mode)==33 || abs(Mode)==34)",\
	       "cc==0 && (abs(Mode)==41 || abs(Mode)==46)"\
	       ]
    binning="100,0,2.5"
    var_list=["q0", "q0", "q0", "q0", "q0"]
    det = "DUNEND"
    model="GENIEv3_G18_10a_00_000"
    
    for flux in ["FHC_numu", "RHC_numubar"]:
        flux_string = "#nu_{#mu}"
        if flux == "RHC_numubar": flux_string =	"#bar{#nu}_{#mu}"
        
        for targ in ["neutron", "proton"]:
            
            inFileList = [inputDir+"/"+det+"_"+flux+"_"+targ+"_"+model+"_1M_*_NUISFLAT.root",\
                          inputDir+"/"+det+"_"+flux+"_"+targ+"_"+model+"_1M_*_NUISFLAT.root",\
                          inputDir+"/"+det+"_"+flux+"_"+targ+"_"+model+"_1M_*_NUISFLAT.root",\
                          inputDir+"/"+det+"_"+flux+"_"+targ+"_"+model+"_1M_*_NUISFLAT.root"\
                          ]
            
	    make_generator_comp_noratio(det+"_"+flux+"_"+targ+"_NC_"+model+"_q0_noratio.png", inFileList, flux_string+"-"+str(targ), \
                                        nameList, colzList, lineList, var_list, binning, cutList, \
                                        "q_{0} (GeV); d#sigma/dq_{0} (#times 10^{-38} cm^{2}/nucleon)", False)

def make_Enu_breakdown_CC_nucl(inputDir="inputs/"):

    nameList = ["CC-INC",\
                "CC-QE",\
                "CC-SPP",\
		"CC-DIS"]
    colzList = [9000, 9001,9003, 9005]
    lineList = [1, 1, 1, 1, 1]
    cutList = ["cc==1", \
               "cc==1 && abs(Mode) == 1", \
               "cc==1 && (abs(Mode)==11 || abs(Mode)==12 || abs(Mode)==13)", \
	       "cc==1 && (abs(Mode)==21 || abs(Mode) == 26)"]
    binning="80,0,4"
    var_list=["Enu_true", "Enu_true", "Enu_true", "Enu_true", "Enu_true"]
    det = "DUNEND"
    model="GENIEv3_G18_10a_00_000"

    for flux in ["FHC_numu", "RHC_numubar"]:
        flux_string = "#nu_{#mu}"
        if flux == "RHC_numubar": flux_string =	"#bar{#nu}_{#mu}"
        
	for targ in ["neutron", "proton"]:
            inFileList = [inputDir+"/"+det+"_"+flux+"_"+targ+"_"+model+"_1M_*_NUISFLAT.root",\
                          inputDir+"/"+det+"_"+flux+"_"+targ+"_"+model+"_1M_*_NUISFLAT.root",\
                          inputDir+"/"+det+"_"+flux+"_"+targ+"_"+model+"_1M_*_NUISFLAT.root",\
                          inputDir+"/"+det+"_"+flux+"_"+targ+"_"+model+"_1M_*_NUISFLAT.root"]

            make_generator_comp_noratio(det+"_"+flux+"_"+targ+"_CC_"+model+"_Enu_noratio.png", inFileList, flux_string+"-"+str(targ), \
                                        nameList, colzList, lineList, var_list, binning, cutList, \
                                        "E_{#nu} (GeV); d#sigma/dE_{#nu} (#times 10^{-38} cm^{2}/nucleon)", False)

def make_Enu_breakdown_NC_nucl(inputDir="inputs/"):

    nameList = ["NC-INC", \
                "NC-EL", \
                "NC-SPP", \
                "NC-DIS"\
                ]
    colzList = [9000, 9001, 9003, 9005]
    lineList = [1, 1, 1, 1, 1]
    cutList = ["cc==0", \
               "cc==0 && (abs(Mode)==51 || abs(Mode)==52)",\
               "cc==0 && (abs(Mode)==31 || abs(Mode)==32 || abs(Mode)==33 || abs(Mode)==34)",\
               "cc==0 && (abs(Mode)==41 || abs(Mode)==46)"\
               ]
    binning="80,0,4"
    var_list=["Enu_true", "Enu_true", "Enu_true", "Enu_true", "Enu_true"]
    det = "DUNEND"
    model="GENIEv3_G18_10a_00_000"

    for flux in ["FHC_numu", "RHC_numubar"]:
        flux_string = "#nu_{#mu}"
        if flux == "RHC_numubar": flux_string =	"#bar{#nu}_{#mu}"
        
        for targ in ["neutron", "proton"]:

            inFileList = [inputDir+"/"+det+"_"+flux+"_"+targ+"_"+model+"_1M_*_NUISFLAT.root",\
                          inputDir+"/"+det+"_"+flux+"_"+targ+"_"+model+"_1M_*_NUISFLAT.root",\
                          inputDir+"/"+det+"_"+flux+"_"+targ+"_"+model+"_1M_*_NUISFLAT.root",\
                          inputDir+"/"+det+"_"+flux+"_"+targ+"_"+model+"_1M_*_NUISFLAT.root"\
                          ]

            make_generator_comp_noratio(det+"_"+flux+"_"+targ+"_NC_"+model+"_Enu_noratio.png", inFileList, flux_string+"-"+str(targ), \
                                        nameList, colzList, lineList, var_list, binning, cutList, \
					"E_{#nu} (GeV); d#sigma/dE_{#nu} (#times 10^{-38} cm^{2}/nucleon)", False)

            
if __name__ == "__main__":

    inputDir="/global/cfs/cdirs/dune/users/cwilk/MC_IOP_review/*/"
    make_q0_breakdown_CC_DUNE(inputDir)
    make_q0_breakdown_NC_DUNE(inputDir)
    
    make_q0_breakdown_CC_nucl(inputDir)
    make_q0_breakdown_NC_nucl(inputDir)

    ## make_W_breakdown_CC_DUNE(inputDir)
    ## make_W_breakdown_CC_nucl(inputDir)
    
    ## make_Enu_breakdown_CC_nucl(inputDir)
    ## make_Enu_breakdown_NC_nucl(inputDir)
