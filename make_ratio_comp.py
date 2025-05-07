import ROOT
import os
from ROOT import gStyle, TGaxis, TPad, TLine, gROOT, TH1, TColor, TCanvas, TFile, TH1D, gPad, TLegend, kWhite, gDirectory, gEnv
from glob import glob

from plotting_functions import make_generator_ratio_comp
# make_generator_ratio_comp(outPlotName, inFileNumList, inFileDenList, nameList, colzList, \
#                           plotVar="q0", binning="100,0,5", cut="cc==1", \
#                           labels="q_{0} (GeV); d#sigma/dq_{0} (#times 10^{-38} cm^{2}/nucleon)",
#                           legDim=[0.65, 0.5, 0.85, 0.93], yLimits=[0, None], yRatLimits=[0.4, 1.6]):
#

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

can = TCanvas("can", "can", 600, 1000)
can .cd()

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
    
def make_flav_ratio_plots(inputDir="inputs/", flav1="nue", flav2="numu", targ="Ar40", sample="ccinc", minMax=[0.6, 1.4]):

    nameList = ["GENIE 10a",\
                "CRPA",\
                "SuSAv2",\
                "NEUT",\
                "NuWro"\
                ]
    colzList = [9000, 9003, 9004, 9006, 9005]
    
    cut = "cc==1 && tgta != 1 && tgt != 1000010010"

    if "nue" in flav1 or "nue" in flav2:
        cut += "&& Enu_true > 0.11"
    
    sample_label = "CCINC"
    if sample == "cc0pi":
        cut += "&& Sum$(abs(pdg) > 100 && abs(pdg) < 2000)==0 && Sum$(abs(pdg) > 2300 && abs(pdg) < 100000)==0"
        sample_label = "CC0#pi"
        
    det  = "falling_5GeV"

    inFileNumList = [inputDir+"/"+det+"_"+flav1+"_"+targ+"_GENIEv3_G18_10a_00_000_1M_*_NUISFLAT.root",\
                     inputDir+"/"+det+"_"+flav1+"_"+targ+"_GENIEv3_CRPA21_04a_00_000_1M_*_NUISFLAT.root",\
                     inputDir+"/"+det+"_"+flav1+"_"+targ+"_GENIEv3_G21_11a_00_000_1M_*_NUISFLAT.root",\
                     inputDir+"/"+det+"_"+flav1+"_"+targ+"_NEUT562_1M_*_NUISFLAT.root",\
                     inputDir+"/"+det+"_"+flav1+"_"+targ+"_NUWRO_LFGRPA_1M_*_NUISFLAT.root"\
                     ]

    inFileDenList = [inputDir+"/"+det+"_"+flav2+"_"+targ+"_GENIEv3_G18_10a_00_000_1M_*_NUISFLAT.root",\
                     inputDir+"/"+det+"_"+flav2+"_"+targ+"_GENIEv3_CRPA21_04a_00_000_1M_*_NUISFLAT.root",\
                     inputDir+"/"+det+"_"+flav2+"_"+targ+"_GENIEv3_G21_11a_00_000_1M_*_NUISFLAT.root",\
                     inputDir+"/"+det+"_"+flav2+"_"+targ+"_NEUT562_1M_*_NUISFLAT.root",\
                     inputDir+"/"+det+"_"+flav2+"_"+targ+"_NUWRO_LFGRPA_1M_*_NUISFLAT.root"\
                     ]    

    make_generator_ratio_comp(det+"_"+flav1+"_over_"+flav2+"_"+targ+"_enu_"+sample+"_gencomp.pdf", inFileNumList, inFileDenList, \
                              nameList, colzList, "Enu_true", "40,0,5", cut, \
                              "E_{#nu}^{true} (GeV); "+get_flav_label(flav1)+"/"+get_flav_label(flav2)+" "+get_targ_label(targ)+" "+sample_label+" ratio", \
                              legDim=[0.65, 0.5, 0.85, 0.93], yLimits=minMax, yRatLimits=[0.8, 1.2])

    
def make_targ_ratio_plots(inputDir="inputs/", targ1="C8H8", targ2="H2O", flav="numu", sample="ccinc"):

    nameList = ["GENIE 10a",\
                "CRPA",\
                "SuSAv2",\
                "NEUT",\
                "NuWro"\
                ]
    colzList = [9000, 9003, 9004, 9006, 9005]
    
    cut = "cc==1 && tgta != 1 && tgt != 1000010010"
    if "nue" in flav: cut += "&& Enu_true > 0.11"

    sample_label = "CCINC"
    if sample == "cc0pi":
        cut += "&& Sum$(abs(pdg) > 100 && abs(pdg) < 2000)==0 && Sum$(abs(pdg) > 2300 && abs(pdg) < 100000)==0"
        sample_label = "CC0#pi"

    det  = "falling_5GeV"

    inFileNumList = [inputDir+"/"+det+"_"+flav+"_"+targ1+"_GENIEv3_G18_10a_00_000_1M_*_NUISFLAT.root",\
                     inputDir+"/"+det+"_"+flav+"_"+targ1+"_GENIEv3_CRPA21_04a_00_000_1M_*_NUISFLAT.root",\
                     inputDir+"/"+det+"_"+flav+"_"+targ1+"_GENIEv3_G21_11a_00_000_1M_*_NUISFLAT.root",\
                     inputDir+"/"+det+"_"+flav+"_"+targ1+"_NEUT562_1M_*_NUISFLAT.root",\
                     inputDir+"/"+det+"_"+flav+"_"+targ1+"_NUWRO_LFGRPA_1M_*_NUISFLAT.root"\
                     ]

    inFileDenList = [inputDir+"/"+det+"_"+flav+"_"+targ2+"_GENIEv3_G18_10a_00_000_1M_*_NUISFLAT.root",\
                     inputDir+"/"+det+"_"+flav+"_"+targ2+"_GENIEv3_CRPA21_04a_00_000_1M_*_NUISFLAT.root",\
                     inputDir+"/"+det+"_"+flav+"_"+targ2+"_GENIEv3_G21_11a_00_000_1M_*_NUISFLAT.root",\
                     inputDir+"/"+det+"_"+flav+"_"+targ2+"_NEUT562_1M_*_NUISFLAT.root",\
                     inputDir+"/"+det+"_"+flav+"_"+targ2+"_NUWRO_LFGRPA_1M_*_NUISFLAT.root"\
                     ]    
    
    make_generator_ratio_comp(det+"_"+targ1+"_over_"+targ2+"_"+flav+"_enu_"+sample+"_gencomp.pdf", inFileNumList, inFileDenList, \
                              nameList, colzList, "Enu_true", "20,0,5", cut, \
                              "E_{#nu}^{true} (GeV);"+get_flav_label(flav)+" "+get_targ_label(targ1)+"/"+get_targ_label(targ2)+" "+sample_label+" ratio", \
                              legDim=[0.65, 0.06, 0.93, 0.45], yLimits=[0.65, 1.25], yRatLimits=[0.75, 1.25])

if __name__ == "__main__":

    inputDir="/global/cfs/cdirs/dune/users/cwilk/MC_IOP_review/*/"
    # for targ in ["Ar40", "H2O"]:
    #     for sample in ["ccinc"]:
    #         make_flav_ratio_plots(inputDir, "nue", "numu", targ, sample, [0.9, 1.9])
    #         make_flav_ratio_plots(inputDir, "nuebar", "numubar", targ, sample, [0.9, 1.9])
            # make_flav_ratio_plots(inputDir, "nuebar", "nue", targ, sample, [0, 0.8])
            # make_flav_ratio_plots(inputDir, "numubar", "numu", targ, sample, [0, 0.8])

    for flav in ["numu", "numubar"]: #, "nue", "nuebar"]:
        for sample in ["ccinc", "cc0pi"]:
            make_targ_ratio_plots(inputDir, "Ar40", "C8H8", flav, sample)
            make_targ_ratio_plots(inputDir, "H2O", "C8H8", flav, sample)


