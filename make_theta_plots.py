import ROOT
import os
from ROOT import gStyle, TGaxis, TPad, TLine, gROOT, TH1, TColor, TCanvas, TFile, TH1D, gPad, TLegend, kWhite, gDirectory, gEnv
from glob import glob

from plotting_functions import get_chain, make_two_panel_plot

## Use double precision for TTree draw
gEnv.SetValue("Hist.Precision.1D", "double")

## No need to see the plots appear here
gROOT.SetBatch(1)
gStyle.SetLineWidth(3)
gStyle.SetOptStat(0)
gStyle.SetOptTitle(0)
gStyle.SetOptFit(0)
TGaxis.SetMaxDigits(4)

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


## This is a copy of "make_generator_comp" with a very custom normalization
def make_generator_custom_norm_comp(outPlotName, inFileList, nameList, colzList, \
                                    plotVar="q0", binning="100,0,5", cut="cc==1", \
                                    labels="q_{0} (GeV); d#sigma/dq_{0} (#times 10^{-38} cm^{2}/nucleon)",
                                    legDim=[0.65, 0.5, 0.85, 0.93], yLimits=[0, None], yRatLimits=[0.4, 1.6]):
    
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

        inTree.Draw(plotVar+">>this_hist("+binning+")", "InputWeight*("+cut+")*fScaleFactor*1E38")
        thisHist = gDirectory.Get("this_hist")
        thisHist .SetDirectory(0)

        ## Deal with different numbers of files
        thisHist.Scale(1./nFiles, "width")

	## Custom normalisation (bin 1 has a value of 1)
        thisHist .Scale(1/thisHist.GetBinContent(1))

        ## Retain for use
	thisHist .SetNameTitle("thisHist", "thisHist;"+labels)
        histList .append(thisHist)

    ## Sort out the plot colours
    for x in range(len(histList)): histList[x].SetLineColor(colzList[x])

    ## Sort out the ratio hists
    nomHist = histList[0].Clone()
    # nomHist .Rebin(2)
    for hist in histList:
        rat_hist = hist.Clone()
	# rat_hist .Rebin(2)
	rat_hist .Divide(nomHist)
	ratList  .append(rat_hist)

    ## This makes the plots in a standard form
    make_two_panel_plot(outPlotName, histList, ratList, nameList, legDim, yLimits, yRatLimits)


def make_T2K_theta_plots(inputDir="inputs/"):

    nameList = ["GENIE 10a",\
                "CRPA",\
                "SuSAv2",\
                "NEUT",\
                "NuWro"\
                ]
    colzList = [9000, 9003, 9004, 9006, 9005]
    
    ## QE reco
    qe_cut = "cc==1 && Sum$(abs(pdg) > 100 && abs(pdg) < 2000)==0 && Sum$(abs(pdg) > 2300 && abs(pdg) < 100000)==0 && Sum$(pdg==2212) > 0"

    ## Loop over configs
    det = "T2KND"
    for flux in ["FHC_numu", "RHC_numubar"]:
        ## These files can be found here (no login required): https://portal.nersc.gov/project/dune/data/2x2/simulation
        inFileList = [inputDir+"/"+det+"_"+flux+"_H2O_GENIEv3_G18_10a_00_000_1M_*_NUISFLAT.root",\
                      inputDir+"/"+det+"_"+flux+"_H2O_GENIEv3_CRPA21_04a_00_000_1M_*_NUISFLAT.root",\
                      inputDir+"/"+det+"_"+flux+"_H2O_GENIEv3_G21_11a_00_000_1M_*_NUISFLAT.root",\
                      inputDir+"/"+det+"_"+flux+"_H2O_NEUT562_1M_*_NUISFLAT.root",\
                      inputDir+"/"+det+"_"+flux+"_H2O_NUWRO_LFGRPA_1M_*_NUISFLAT.root"\
                      ]
        
        make_generator_custom_norm_comp(det+"_"+flux+"_H2O_theta_scaled_gencomp.pdf", inFileList, nameList, colzList, "acos(CosLep)*180/pi", "60,0,180", qe_cut, \
                                        "#theta_{#mu} (degrees); Scaled cross section")
        

def make_DUNE_theta_plots(inputDir="inputs/"):

    nameList = ["GENIE 10a",\
                "CRPA",\
                "SuSAv2",\
                "NEUT",\
                "NuWro"\
                ]
    colzList = [9000, 9003, 9004, 9006, 9005]
    
    ## QE reco
    ccinc = "cc==1"

    ## Loop over configs
    det = "DUNEND"
    for flux in ["FHC_numu", "RHC_numubar"]:
        ## These files can be found here (no login required): https://portal.nersc.gov/project/dune/data/2x2/simulation
        inFileList = [inputDir+"/"+det+"_"+flux+"_Ar40_GENIEv3_G18_10a_00_000_1M_*_NUISFLAT.root",\
                      inputDir+"/"+det+"_"+flux+"_Ar40_GENIEv3_CRPA21_04a_00_000_1M_*_NUISFLAT.root",\
                      inputDir+"/"+det+"_"+flux+"_Ar40_GENIEv3_G21_11a_00_000_1M_*_NUISFLAT.root",\
                      inputDir+"/"+det+"_"+flux+"_Ar40_NEUT562_1M_*_NUISFLAT.root",\
                      inputDir+"/"+det+"_"+flux+"_Ar40_NUWRO_LFGRPA_1M_*_NUISFLAT.root"\
                      ]
        make_generator_custom_norm_comp(det+"_"+flux+"_Ar40_theta_scaled_gencomp.pdf", inFileList, nameList, colzList, "acos(CosLep)*180/pi", "60,0,180", ccinc, \
                                        "#theta_{#mu} (degrees); Scaled cross section")

if __name__ == "__main__":

    inputDir="/global/cfs/cdirs/dune/users/cwilk/MC_IOP_review/*/"
    make_T2K_theta_plots(inputDir)
    make_DUNE_theta_plots(inputDir)

