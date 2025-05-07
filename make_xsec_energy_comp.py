import ROOT
import os
from ROOT import gStyle, TGaxis, TPad, TLine, gROOT, TH1, TColor, TCanvas, TFile, TH1D, gPad, TLegend, kWhite, gDirectory, gEnv
from glob import glob

from plotting_functions import get_chain, make_two_panel_plot
## def make_generator_comp(outPlotName, inFileList, nameList, colzList, \
##                         plotVar="q0", binning="100,0,5", cut="cc==1", \
## 			labels="q_{0} (GeV); d#sigma/dq_{0} (#times 10^{-38} cm^{2}/nucleon)",
##                         legDim=[0.65, 0.5, 0.85, 0.93], yLimits=[0, None], yRatLimits=[0.4, 1.6], isShape=False):

## In this case, ignore hydrogen...
def get_targ_label(targ):
    if targ == "Ar40": return "^{40}Ar"
    if targ == "C8H8": return "^{12}C"
    if targ == "H2O": return "^{16}O"
    print("Unknown target", targ)
    return targ

## This is to remove hydrogen from the /nucleon cross sections NUISANCE produces...
def get_targ_norm(inString):
    if "C8H8" in inString: return 13/12.
    if "H2O" in inString: return  18/16.
    return 1.

## This is a copy of "make_generator_comp" with a very custom normalization
def make_generator_custom_norm_comp(outPlotName, inFileList, nameList, colzList, \
                                    cut="cc==1", \
                                    legDim=[0.65, 0.5, 0.85, 0.93], yLimits=[0, None], yRatLimits=[0.4, 1.6]):
    
    ## This now only works for XSEC as a function of Enu
    plotVar = "Enu_true"
    labels="E_{#nu}^{true} (GeV); #sigma(E_{#nu}^{true}) (#times 10^{-38} cm^{2}/nucleon)"

    ## This is hard-coded in the binning file
    binning="100,0,5"

    ## Skip files that already exist
    if os.path.isfile("plots/"+outPlotName):
	print("Skipping plots/"+outPlotName, "which already exists!")
        return

    histList = []
    ratList  = []

    ## Loop over the input files and make the histograms
    for inFileName in inFileList:

        ## Modify to use glob
        inTree, inFlux, inEvt, nFiles = get_chain(inFileName)

        ## Correct for hydrogen in some of the samples
	targNorm = get_targ_norm(inFileName)

        inTree.Draw(plotVar+">>this_hist("+binning+")", "InputWeight*("+cut+")*fScaleFactor*1E38")
	thisHist = gDirectory.Get("this_hist")
        thisHist .SetDirectory(0)

        ## Deal with different numbers of files
        ## Some funky normalization to get around some hardcoded NUISANCE stuff that assumes flux-averaged cross sections
        thisHist.Scale(targNorm*inFlux.Integral("width")/float(nFiles), "width")

	for x in range(5, thisHist.GetNbinsX()+1):
            this_val  = thisHist.GetBinContent(x)
            this_flux = inFlux.GetBinContent(x-4)
            thisHist .SetBinContent(x, this_val/this_flux)

        thisHist .Rebin(2)
        thisHist .Scale(0.5)
            
        ## Retain for use
	thisHist .SetNameTitle("thisHist", "thisHist;"+labels)
        histList .append(thisHist)

    ## Sort out the plot colours
    for x in range(len(histList)): histList[x].SetLineColor(colzList[x])

    ## Sort out the ratio hists
    nomHist = histList[0].Clone()
    for hist in histList:
        rat_hist = hist.Clone()
	rat_hist .Divide(nomHist)
	ratList  .append(rat_hist)

    ## This makes the plots in a standard form
    make_two_panel_plot(outPlotName, histList, ratList, nameList, legDim, yLimits, yRatLimits)


            
def make_xsec_energy_comp_plots(inputDir="inputs/", flav="numu", targ="Ar40", sample="ccinc", isOverEnu=False, minMax=None):

    nameList = ["GENIE 10a",\
                "CRPA",\
                "SuSAv2",\
                "NEUT",\
                "NuWro"\
                ]
    colzList = [9000, 9003, 9004, 9006, 9005]
    
    cut = "cc==1 && tgta != 1 && tgt != 1000010010 && Enu_true > 0.2"
    sample_label = "CCINC"
    if sample == "cc0pi":
        cut += "&& Sum$(abs(pdg) > 100 && abs(pdg) < 2000)==0 && Sum$(abs(pdg) > 2300 && abs(pdg) < 100000)==0"
        sample_label = "CC0#pi"
    if sample == "ccqe":
        cut += "&& abs(Mode)==1"
        sample_label = "CCQE"
    if sample == "2p2h":
        cut += "&& abs(Mode)==2"
        sample_label = "2p2h"

    ## Loop over configs
    det="falling_5GeV"
    
    ## These files can be found here (no login required): https://portal.nersc.gov/project/dune/data/2x2/simulation
    inFileList = [inputDir+"/"+det+"_"+flav+"_"+targ+"_GENIEv3_G18_10a_00_000_1M_*_NUISFLAT.root",\
                  inputDir+"/"+det+"_"+flav+"_"+targ+"_GENIEv3_CRPA21_04a_00_000_1M_*_NUISFLAT.root",\
                  inputDir+"/"+det+"_"+flav+"_"+targ+"_GENIEv3_G21_11a_00_000_1M_*_NUISFLAT.root",\
                  inputDir+"/"+det+"_"+flav+"_"+targ+"_NEUT562_1M_*_NUISFLAT.root",\
                  inputDir+"/"+det+"_"+flav+"_"+targ+"_NUWRO_LFGRPA_1M_*_NUISFLAT.root"\
                  ]

    outFileName = det+"_"+flav+"_"+targ+"_Enu_"+sample+"_gencomp.pdf"
    make_generator_custom_norm_comp(outFileName, inFileList, nameList, colzList, cut, [0.65, 0.06, 0.93, 0.45])

    
if __name__ == "__main__":

    inputDir="/global/cfs/cdirs/dune/users/cwilk/MC_IOP_review/*/"

    # for targ in ["Ar40"]: #, "C8H8", "H2O"]:
    for flav in ["numu"]: #, "nue", "nuebar"]:
        #make_xsec_energy_comp_plots(inputDir, flav, "Ar40", "ccinc")
        #make_xsec_energy_comp_plots(inputDir, flav, "H2O", "cc0pi")
        #make_xsec_energy_comp_plots(inputDir, flav, "C8H8", "cc0pi")
        make_xsec_energy_comp_plots(inputDir, flav, "Ar40", "2p2h")
	make_xsec_energy_comp_plots(inputDir, flav, "H2O", "2p2h")
	make_xsec_energy_comp_plots(inputDir, flav, "C8H8", "2p2h")

        
        
            #make_xsec_energy_comp_plots(inputDir, flav, targ, "ccinc", True)
            #make_xsec_energy_comp_plots(inputDir, flav, targ, "cc0pi")
            

