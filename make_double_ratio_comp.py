import ROOT
import os
from array import array
from ROOT import gStyle, TGaxis, TPad, TLine, gROOT, TH1, TColor, TCanvas, TFile, TH1D, gPad, TLegend, kWhite, gDirectory, gEnv
from glob import glob

from plotting_functions import make_generator_double_ratio_comp
## The double ratio is (A/B)/(C/D)
## def make_generator_double_ratio_comp(outPlotName, inFileListA, inFileListB, inFileListC, inFileListD, \
##                                      nameList, colzList, plotVar, binning, cut="cc==1", \
##                                      labels="q_{0} (GeV); d#sigma/dq_{0} (#times 10^{-38} cm^{2}/nucleon)",
##                                      legDim=[0.65, 0.5, 0.85, 0.93], yLimits=[0, None], yRatLimits=[0.4, 1.6]):
    
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

def get_flav_label(flav):
    label = "#nu"
    if "bar" in flav: label = "#bar{"+label+"}"
    if "mu" in flav: label += "_{#mu}"
    if "tau" in flav: label += "_{#tau}"
    if "e" in flav: label += "_{e}"
    return label

## In this case, ignore hydrogen...
def get_targ_label(targ):
    if targ == "Ar40": return "^{40}Ar"
    if targ == "C8H8": return "^{12}C"
    if targ == "H2O": return "^{16}O"
    print("Unknown target", targ)
    return targ


def make_flav_double_ratio_plots(inputDir="inputs/", flavA="nuebar", flavB="numubar", \
                                 flavC="nue", flavD="numu", targ="Ar40", sample="ccinc", yLimits=[0,None]):

    nameList = ["GENIE 10a",\
                "CRPA",\
                "SuSAv2",\
                "NEUT 580",\
                "NuWro"\
                ]
    colzList = [9000, 9003, 9004, 9006, 9005]
    
    cut = "cc==1 && tgta != 1 && tgt != 1000010010 && Enu_true > 0.12"
    sample_label = "CCINC"
    if sample == "cc0pi":
        cut += "&& Sum$(abs(pdg) > 100 && abs(pdg) < 2000)==0 && Sum$(abs(pdg) > 2300 && abs(pdg) < 100000)==0"
        sample_label = "CC0#pi"
        
    det  = "one_over_2GeV"

    ## As FSI doesn't make any difference, use all GENIEv3_G18 models as one...
    inFileListA = [inputDir+"/"+det+"_"+flavA+"_"+targ+"_GENIEv3_G18_10*_00_000_1M_*_NUISFLAT.root",\
                   inputDir+"/"+det+"_"+flavA+"_"+targ+"_GENIEv3_CRPA21_04a_00_000_1M_*_NUISFLAT.root",\
                   inputDir+"/"+det+"_"+flavA+"_"+targ+"_GENIEv3_G21_11a_00_000_1M_*_NUISFLAT.root",\
                   inputDir+"/"+det+"_"+flavA+"_"+targ+"_NEUT580_1M_*_NUISFLAT.root",\
                   inputDir+"/"+det+"_"+flavA+"_"+targ+"_NUWRO_LFGRPA_1M_*_NUISFLAT.root"\
                   ]

    inFileListB = [inputDir+"/"+det+"_"+flavB+"_"+targ+"_GENIEv3_G18_10*_00_000_1M_*_NUISFLAT.root",\
                   inputDir+"/"+det+"_"+flavB+"_"+targ+"_GENIEv3_CRPA21_04a_00_000_1M_*_NUISFLAT.root",\
                   inputDir+"/"+det+"_"+flavB+"_"+targ+"_GENIEv3_G21_11a_00_000_1M_*_NUISFLAT.root",\
                   inputDir+"/"+det+"_"+flavB+"_"+targ+"_NEUT580_1M_*_NUISFLAT.root",\
                   inputDir+"/"+det+"_"+flavB+"_"+targ+"_NUWRO_LFGRPA_1M_*_NUISFLAT.root"\
                   ]

    inFileListC = [inputDir+"/"+det+"_"+flavC+"_"+targ+"_GENIEv3_G18_10*_00_000_1M_*_NUISFLAT.root",\
                   inputDir+"/"+det+"_"+flavC+"_"+targ+"_GENIEv3_CRPA21_04a_00_000_1M_*_NUISFLAT.root",\
                   inputDir+"/"+det+"_"+flavC+"_"+targ+"_GENIEv3_G21_11a_00_000_1M_*_NUISFLAT.root",\
                   inputDir+"/"+det+"_"+flavC+"_"+targ+"_NEUT580_1M_*_NUISFLAT.root",\
                   inputDir+"/"+det+"_"+flavC+"_"+targ+"_NUWRO_LFGRPA_1M_*_NUISFLAT.root"\
                   ]

    inFileListD = [inputDir+"/"+det+"_"+flavD+"_"+targ+"_GENIEv3_G18_10*_00_000_1M_*_NUISFLAT.root",\
                   inputDir+"/"+det+"_"+flavD+"_"+targ+"_GENIEv3_CRPA21_04a_00_000_1M_*_NUISFLAT.root",\
                   inputDir+"/"+det+"_"+flavD+"_"+targ+"_GENIEv3_G21_11a_00_000_1M_*_NUISFLAT.root",\
                   inputDir+"/"+det+"_"+flavD+"_"+targ+"_NEUT580_1M_*_NUISFLAT.root",\
                   inputDir+"/"+det+"_"+flavD+"_"+targ+"_NUWRO_LFGRPA_1M_*_NUISFLAT.root"\
                   ]

    ## Initial fluxes used have 0.02 GeV binning from 0.1 to 2 GeV
    # xList = [0, 0.12, 0.16, 0.2, 0.24, 0.28, 0.32, 0.38, 0.44, 0.6, 0.7, 0.8, 1.0]
    xList = [0.11, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0]

    make_generator_double_ratio_comp("plots/"+det+"_double_flav_ratio_"+targ+"_enu_"+sample+"_gencomp_NEWNEUT.pdf",
                                     inFileListA, inFileListB, inFileListC, inFileListD, \
                                     nameList, colzList, "Enu_true", xList, cut, \
                                     "E_{#nu}^{true} (GeV); ("+get_flav_label(flavA)+"/"+get_flav_label(flavB)+")/("+get_flav_label(flavC)+"/"+\
                                     get_flav_label(flavD)+") "+ get_targ_label(targ)+" "+sample_label+" ratio",
                                     [0.65, 0.5, 0.85, 0.93], yLimits, yRatLimits=[0.6, 1.15])
    
if __name__ == "__main__":

    inputDir="/global/cfs/cdirs/dune/users/cwilk/MC_IOP_review/*/"
    targ="Ar40"
    sample="ccinc"
    make_flav_double_ratio_plots(inputDir, "nuebar", "numubar", "nue", "numu", targ, sample, [0.75, 1.35])

    targ="H2O"
    sample="cc0pi"
    make_flav_double_ratio_plots(inputDir, "nuebar", "numubar", "nue", "numu", targ, sample, [0.75, 1.35])

    targ="H2O"
    sample="ccinc"
    make_flav_double_ratio_plots(inputDir, "nuebar", "numubar", "nue", "numu", targ, sample, [0.75, 1.35])


